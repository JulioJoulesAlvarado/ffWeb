import random
import math
from operator import add


import os
import datetime
import re
from flask import Flask, render_template, request, make_response, url_for,redirect
import csv

import hashlib


app = Flask(__name__)

from google.cloud import datastore
from google.cloud import storage

### This is the Lineup Generator. It uses a genetic algo to come up with a daily fantasy play. 

#Takes a Team and return it's projected Score
def  teamScore(team):
    if anyRepeats(team):
        return 0
    points=0 
    for key, value in team.items():
        for x in value:
            #print(x)
            points+=x['expectedScore']
    return points

#Takes a team and returns the total salary of players
def  teamSalary(team):
    cost=0 
    for key, value in team.items():
        for p in value:
            cost+=p['salary']
    return cost

#we need to avoid the same players being in the same lineup. Assign it a score of zero if it happens
def anyRepeats(team):
    if(team['RB'][0]['name']== team['RB'][1]['name'] or team['RB'][0]['name']==team['Flex'][0]['name'] or team['RB'][1]['name']==team['Flex'][0]['name']):
        return True
    if(team['WR'][0]['name']== team['WR'][1]['name'] or team['WR'][0]['name']==team['Flex'][0]['name'] or team['WR'][1]['name']==team['WR'][0]['name']):
        return True
    if(team['WR'][2]['name']== team['WR'][0]['name'] or team['WR'][2]['name']==team['Flex'][0]['name'] or team['WR'][2]['name']==team['WR'][1]['name']):
        return True
    if(team['TE'][0]['name']== team['Flex'][0]['name']):
        return True
    return False
    
#returns score of a team. Note: If team goes over budget, score is zero
def fitness(team,salary):
    expectedTeamPoints=teamScore(team)
    expectedTeamSalary=teamSalary(team)
    if expectedTeamSalary > salary:
        return 0
    else:
        return expectedTeamPoints

#returns Avg Score of population. 
def populationFitness(teams,salary):
    totalFitness=0
    for i in teams:
        totalFitness+=fitness(i,salary)
    return totalFitness/len(teams)


#randomly Creates a Team
def CreateRandomTeam(allPlayers):
    team= {
        'QB': random.sample(allPlayers['QBs'],1),
        'RB': random.sample(allPlayers['RBs'],2),
        'WR': random.sample(allPlayers['WRs'],3),
        'TE': random.sample(allPlayers['TEs'],1),
        'Flex':random.sample(allPlayers['Flex'],1),
    }
    
    return team

#randomly Creates Teams
def CreateTeams(numberOfTeams,allPlayers):
    teams=[]
    x=0
    while x < numberOfTeams:
        teamA=CreateRandomTeam(allPlayers)
        teams.append(teamA)
        x+=1
    return teams

#found it easier to work with arrays. This Turns an array back into a dict, which is what we return in the end
def array_to_dict(team_array):
    #print(team_array[6].name)
    team1={
        'QB':[team_array[0]],
        'RB':[team_array[1],team_array[2]],
        'WR':[team_array[3],team_array[4],team_array[5]],
        'TE':[team_array[6]],
        'Flex':[team_array[7]],
    }
    return team1

#creates childrem from parents
def sex(mom, dad):
    positions=['QB','RB','WR','TE','Flex']
    mother_array=[]
    father_array=[]
    for pos in range(len(positions)):
        for p in mom[positions[pos]]:
            mother_array.append(p)
    for pos in range(len(positions)):
        for p in dad[positions[pos]]:
            father_array.append(p)
    #print(mother_array)
    index=random.choice([1,3,6,7,8])
    childA=mother_array[0:index]+father_array[index:]
    childB=father_array[0:index]+mother_array[index:]
 
    child1=array_to_dict(childA)
    child2=array_to_dict(childB)

    children= [child1,child2]
    return children
    
def mutate(team,allPlayers):
    positions=['QB','RB','WR','TE','Flex']
    random_mutation= random.choice(positions)

    if random_mutation =='QB':
        team['QB']=random.sample(allPlayers['QBs'],1)
    if random_mutation =='RB':
        team['RB']= random.sample(allPlayers['RBs'],2)
    if random_mutation =='WR':
        team['WR']=random.sample(allPlayers['WRs'],3)
    if random_mutation =='TE':
        team['TE']=random.sample(allPlayers['TEs'],1)
    if random_mutation == 'Flex':
        team['Flex']=random.sample(allPlayers['Flex'],1)
    return team

def evolution(teams,allPlayers,salary, i, survival_rate=.4,random_select=.05, mutation_prob=.01):
    #grades all teams
    graded =[(fitness(team,salary),team) for team in teams]
    graded = sorted(graded, key = lambda tup: tup[0],reverse=True)


    gr=[x[1] for x in graded]
    #keeps the best
    retained=int(len(gr)*survival_rate)
    parents=gr[:retained]

    # randomly add other individuals to promote genetic diversity
    for individual in gr[retained:]:
        if random_select > random.random():
            parents.append(individual)

    # mutate some individuals
    for individual in parents:
        if mutation_prob > random.random():
            individual = mutate(individual,allPlayers)

    # crossover parents to create children
    parents_length = len(parents)
    desired_length = len(teams) - parents_length
    children = []
    while len(children) < desired_length:
        male = random.randint(0, parents_length-1)
        female = random.randint(0, parents_length-1)
        if male != female:
            male = parents[male]
            female = parents[female]
            babies = sex(male,female)
            for baby in babies:
                children.append(baby)
    parents.extend(children)
    
    return parents

# called by webpage
# returns final team from input of all players user opted to include  
# Process: 
#1. Creates A Bunch of random teams
#2. Undergoes various reproductive/evolution cycles to improve lineups
#3. There is fitness to remove the worst lineups
#4. Returns the nest at the end   
def genetic(allPlayers, salary):
    population1=CreateTeams(1000,allPlayers)
    
    lineup=[]
    history=[]
    fitness_history=[populationFitness(population1,salary)]

    #pretty sure I need to make population1 into population
    counter=0
    for i in range(40):
        population1=evolution(population1,allPlayers,salary,counter)
        fitness_round=populationFitness(population1,salary)
        fitness_history.append(fitness_round)
        valid_teams = [ team for team in population1 if teamSalary(team) <= salary]

        valid_teams = sorted(valid_teams, key=teamScore, reverse=True)
        
        if len(valid_teams) > 0:
            lineup.append(valid_teams[0])
        counter+=1
        
    #for hist in fitness_history:
     #   history.append(hist)
    for x in range(len(fitness_history)):
        print(fitness_history[x])

    lineup= sorted(lineup,key=teamScore, reverse=True)
    choice=lineup[0]
    

    #could also return most expensive lineup. Often pretty good too.
    #lineup= sorted(lineup,key=teamSalary, reverse=True)
    return choice
