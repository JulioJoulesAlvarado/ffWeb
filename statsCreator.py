
import random
import math
from operator import add


import os
import datetime
import re
from flask import Flask, render_template, request, make_response, url_for,redirect
import csv
from database import *

import hashlib


app = Flask(__name__)

from google.cloud import datastore
from google.cloud import storage

from Player import *
from QB import *
from RB import *
from WR import *
from TE import *


datastore_client = datastore.Client()

#takes Vegas.csv and pulls out team name and expected TD's
def createVegas(week, bucket_name):    
    vegas_doc = week+"Vegas.csv"
    
    file=serveFile(vegas_doc,bucket_name)
    lines = file.decode("ASCII").split('\n')
    
    args=['team','TDs']
    
    
    for line in lines[1:]:
        columns=line.split(',')
                
        if(len(columns)>1):
            argsVals=[columns[8]+week,float(columns[6])/7]
            insertIntoDatabase('Team',args, argsVals)

#takes Deffense.csv and pulls out teams. Queries for a team. Pulls average info and creates the league average  
def createDefense(week, bucket_name):

    defense_doc = week+"Defense.csv"
    
    file=serveFile(defense_doc, bucket_name)
    lines = file.decode("ASCII").split('\n')
    
    league_pass_avg=0
    league_rush_avg=0
    
    
    teamArgs=['pass_avg_allowed','rush_avg_allowed']
    
    for line in lines[1:]:
        columns=line.split(',')
        
        if(len(columns)>1):
            teamname=columns[9]               
            #find entity
            results=queryDatabase('Team',['team'],[teamname+week])
                
            if(len(results)!=0):
                front=results[0]
                teamArgsVals=[float(columns[1]),float(columns[2])]
                    
                updateData(front, teamArgs, teamArgsVals)
                
            league_pass_avg=(league_pass_avg)+float(columns[1])
            league_rush_avg=(league_rush_avg)+float(columns[2]) 
       
    
    leagueArgs=['week','pass_avg','rush_avg']
    leagueArgsVals=[week,league_pass_avg/32,league_rush_avg/32]
    
    insertIntoDatabase('League', leagueArgs, leagueArgsVals)


#pulls out teams average offense data. pulls out avg rush yds/tds and pass yds/tds
def createTeamOffense(week, bucket_name):
    
    defense_doc = week+"Offense.csv"
    file=serveFile(defense_doc,bucket_name)
    lines = file.decode("ASCII").split('\n')    
    
    teamArgs=['pass_avg','rush_avg','pass_TD_avg','rush_TD_avg']
    
    for line in lines[1:]:
        columns=line.split(',')
        
        
        if(len(columns)>1):
            teamname=columns[9]
                
            #find entity
            results=queryDatabase('Team',['team'],[teamname+week])
            
            if(len(results)!=0):
                front=results[0]
                    
                teamArgsVals=[float(columns[1]),float(columns[2]),float(columns[3]),float(columns[4])]
                updateData(front, teamArgs, teamArgsVals)           

#some data has weird team names. Translate it to make it consistent for database purpose        
def getOpponent(opp):
    if opp =='GB':
        return 'GNB'
    if opp =='KC':
        return 'KAN'
    if opp=='LA':
        return 'LAR'
    if opp == 'NO':
        return 'NOR'
    if opp == 'NE':
        return 'NWE'
    if opp == 'SD':
        return 'SDG'
    if opp == 'SF':
        return 'SFO'
    if opp == 'TB':
        return 'TAM'
    else:
        return opp

#pulls player from QB.csv, WR.csv, te.csv, or Rb.csv
#generates averages but not expectation yet      
def createPlayers(position, week, bucket_name):
    player_doc = week+position+".csv"
    file=serveFile(player_doc, bucket_name)
    
    lines = file.decode("ASCII").split('\n')
   
    players={}
    for line in lines[1:]:
        columns=line.split(',')
        
        if(len(columns)>1):
            player_name=columns[1]
            player_team=getOpponent(columns[2])
            expectedScore=0
            expectedTDs=0
            salary=60000
                     
            if position =='QB':
                numgames=float(columns[15])/float(columns[16])            
                pass_yds=float(columns[6])
                rush_yds=float(columns[12])
                rec_yds=0
                receptions=0               
                pass_tds=float(columns[7])
                rec_tds=0
                rush_tds=float(columns[13])
            
                player=QB(player_name,position,player_team,week,expectedScore,expectedTDs,salary,numgames,pass_yds,rush_yds,rec_yds,receptions, pass_tds,rec_tds,rush_tds)
                    
            elif position == 'RB':
                numgames=float(columns[11])/float(columns[12])
                pass_yds=0
                rush_yds=float(columns[4])
                rec_yds=float(columns[8])
                receptions=float(columns[7])                  
                pass_tds=0
                rec_tds=float(columns[9])
                rush_tds=float(columns[5])
                    
                player=RB(player_name,position,player_team,week,expectedScore,expectedTDs,salary,numgames,pass_yds,rush_yds,rec_yds,receptions, pass_tds,rec_tds,rush_tds)
                
            elif position == 'WR':
                numgames=float(columns[11])/float(columns[12])
                pass_yds=0
                rush_yds=0
                rec_yds=(float(columns[4]))
                receptions=(float(columns[3]))      
                pass_tds=0
                rec_tds=(float(columns[5]))
                rush_tds=0                    
                
                player=WR(player_name,position,player_team,week,expectedScore,expectedTDs,salary,numgames,pass_yds,rush_yds,rec_yds,receptions, pass_tds,rec_tds,rush_tds)
                
            elif position == 'TE':
                numgames=float(columns[11])/float(columns[12])
                pass_yds=0
                rush_yds=0
                rec_yds=(float(columns[4]))
                receptions=(float(columns[3]))      
                pass_tds=0
                rec_tds=(float(columns[5]))
                rush_tds=0

                player=TE(player_name,position,player_team,week,expectedScore,expectedTDs,salary,numgames,pass_yds,rush_yds,rec_yds,receptions, pass_tds,rec_tds,rush_tds)
            players[player_name]=player
    return players

#pulls from Fanduel.csv
# I generate expectation here because fanduel is first csv to include opponents. 
# I pull salary info, and then use opponent field to create expected TDs and expected stats
def addSalariesExpectation(week, bucket_name,QBs, RBs,WRs, TEs):
    player_doc = week+"Fanduel.csv"
    file=serveFile(player_doc, bucket_name)
    
    lines = file.decode("ASCII").split('\n')
        
    results=queryDatabase('League',['week'],[week])
    league=results[0]
    
    for line in lines[1:]:
        columns=line.split(',')
        
        if len(columns)>1:
                if columns[10] != 'O' and columns[10]!='IR' and columns[10] != 'D' and columns[10]!='Q':
                    prospect= (columns[2]+ ' '+columns[4])
                    opponentName=getOpponent(columns[10])
                    teamName=getOpponent(columns[9])
                    #search for own team and opponent team
                        
                    results=queryDatabase('Team', ['team'],[teamName+week])                
                    if(len(results)!=0):
                        team=results[0]
                
                    results=queryDatabase('Team', ['team'],[opponentName+week])               
                    if(len(results)!=0):
                        opp=results[0]   
                            
                    salary = float(columns[7])
                        
                    if columns[1]=='QB' or columns[1] == 'RB' or columns[1]=='WR' or columns[1]=='TE':
                        player = None
                        if columns[1] == 'QB':
                            if prospect in QBs:
                                player=QBs[prospect]
                        elif columns[1]== 'RB':
                            if prospect in RBs:
                                player=RBs[prospect]
                        elif columns[1]== 'WR':
                            if prospect in WRs:
                                player=WRs[prospect]
                        elif columns[1]== 'TE':
                            if prospect in TEs:
                                player=TEs[prospect]
                                
                        if player != None:
                            player.calcExpectation(float(columns[7]),team,opp,league)    

#pulled from main. Each of these works on a spreadsheet to generate Entities        
def generateData(week, bucket_name):
    createVegas(week, bucket_name)
    createDefense(week, bucket_name)
    createTeamOffense(week,bucket_name)
    
    QBs=createPlayers('QB', week, bucket_name)
    RBs=createPlayers('RB', week, bucket_name)
    WRs=createPlayers('WR', week, bucket_name)
    TEs=createPlayers('TE', week, bucket_name)
    
    addSalariesExpectation(week,bucket_name,QBs,RBs,WRs,TEs)
    
    addDictToDatabase('Player', QBs)
    addDictToDatabase('Player', RBs)
    addDictToDatabase('Player', WRs)
    addDictToDatabase('Player', TEs)
    
    
    