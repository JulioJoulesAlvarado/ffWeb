
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


datastore_client = datastore.Client()

#takes Vegas.csv and pulls out team name and expected TD's
def createVegas(week, bucket_name):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    
    
    vegas_doc = week+"Vegas.csv"
    blob=bucket.get_blob(vegas_doc)
    file=blob.download_as_string()
    
    
    lines = file.decode("ASCII").split('\n')
    
    i=0
    for line in lines:
        columns=line.split(',')
        
        if i>0:
            if(len(columns)>1):
                teamname=columns[8]
                t=datastore.Entity(key=datastore_client.key('Team'))
                x=float(columns[6])
                x=x/7
                
                t.update({
                   'team':teamname+week,
                  'TDs': x,
                })
                datastore_client.put(t)
        i=i+1

#takes Deffense.csv and pulls out teams. Queries for a team. Pulls average info and creates the league average  
def createDefense(week, bucket_name):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    
    
    defense_doc = week+"Defense.csv"
    blob=bucket.get_blob(defense_doc)
    file=blob.download_as_string()

    lines = file.decode("ASCII").split('\n')
    
    league_pass_avg=0
    league_rush_avg=0
    i=0
    for line in lines:
        columns=line.split(',')
        
        if i>0:
            if(len(columns)>1):
                teamname=columns[9]
                
                #find entity
                query=datastore_client.query(kind='Team')
                query.add_filter('team','=',teamname+week)
                results=list(query.fetch())
                
                if(len(results)!=0):
                    front=results[0]
                    
                    front.update({
                        'pass_avg_allowed':float(columns[1]),
                        'rush_avg_allowed': float(columns[2]),
                    })
                    
                    datastore_client.put(front)
                
                league_pass_avg=(league_pass_avg)+float(columns[1])
                league_rush_avg=(league_rush_avg)+float(columns[2]) 
        i=i+1

    t=datastore.Entity(key=datastore_client.key('League'))
    t.update({
        'week':week,
        'pass_avg': league_pass_avg/32,
        'rush_avg': league_rush_avg/32,
    })
    datastore_client.put(t)

#pulls out teams average offense data. pulls out avg rush yds/tds and pass yds/tds
def createTeamOffense(week, bucket_name):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    
    
    defense_doc = week+"Offense.csv"
    blob=bucket.get_blob(defense_doc)
    file=blob.download_as_string()

    lines = file.decode("ASCII").split('\n')    
    i=0
    for line in lines:
        columns=line.split(',')
        
        if i>0:
            if(len(columns)>1):
                teamname=columns[9]
                
                #find entity
                query=datastore_client.query(kind='Team')
                query.add_filter('team','=',teamname+week)
                results=list(query.fetch())
                
                if(len(results)!=0):
                    front=results[0]
                    
                    front.update({
                        'pass_avg':float(columns[1]),
                        'rush_avg': float(columns[2]),
                        'pass_TD_avg':float(columns[3]),
                        'rush_TD_avg': float(columns[4]),
                    })
                    
                    datastore_client.put(front)           
        i=i+1

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
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    
    
    player_doc = week+position+".csv"
    blob=bucket.get_blob(player_doc)
    file=blob.download_as_string()
    
    lines = file.decode("ASCII").split('\n')
    i=0
    for line in lines:
        columns=line.split(',')
        if i>0:
            if(len(columns)>1):
                player_name=columns[1]
                player_team=getOpponent(columns[2])
                player=datastore.Entity(key=datastore_client.key('Player'))
                
                player.update({
                    'name':player_name,
                    'position':position,
                    'week':week,
                    'team':player_team,
                    'expectedScore':0,
                    'salary':60000,
                })
                datastore_client.put(player)         
                if position =='QB':
                    numgames=float(columns[15])/float(columns[16])
                    player.update({
                        'numgames':numgames,
                        'average_pass_yds':(float(columns[6])/numgames),
                        'average_rush_yds':(float(columns[12])/numgames),
                        'average_rec_yds':0,
                        'average_receptions':0,               
                        'average_pass_tds':(float(columns[7])/numgames),
                        'average_rec_tds':0,
                        'average_rush_tds':(float(columns[13])/numgames),
                    })
                    datastore_client.put(player)
                elif position == 'RB':
                    numgames=float(columns[11])/float(columns[12])
                    player.update({
                        'numgames':numgames,
                        'average_pass_yds':0,
                        'average_rush_yds':(float(columns[4])/numgames),
                        'average_rec_yds':(float(columns[8])/numgames),
                        'average_receptions':(float(columns[7])/numgames),                   
                        'average_pass_tds':0,
                        'average_rec_tds':(float(columns[9])/numgames),
                        'average_rush_tds':(float(columns[5])/numgames),
                    })
                    datastore_client.put(player)
                else:
                    numgames=float(columns[11])/float(columns[12])
                    player.update({
                        'average_pass_yds':0,
                        'average_rush_yds':0,
                        'average_rec_yds':(float(columns[4])/numgames),
                        'average_receptions':(float(columns[3])/numgames),
                        'numgames':(numgames),
                        'average_pass_tds':0,
                        'average_rec_tds':(float(columns[5])/numgames),
                        'average_rush_tds':0,
                    })
                    datastore_client.put(player)
        i=i+1

#pulls from Fanduel.csv
# I generate expectation here because fanduel is first csv to include opponents. 
# I pull salary info, and then use opponent field to create expected TDs and expected stats
def addSalaries(week, bucket_name):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    
    
    player_doc = week+"Fanduel.csv"
    blob=bucket.get_blob(player_doc)
    file=blob.download_as_string()
    
    lines = file.decode("ASCII").split('\n')
    i=0
                            
    query=datastore_client.query(kind='League')
    query.add_filter('week','=',week)
    results=list(query.fetch())
    league=results[0]
    
    for line in lines:
        columns=line.split(',')
        if i>0:
            if len(columns)>1:
                    if columns[10] != 'O' and columns[10]!='IR' and columns[10] != 'D' and columns[10]!='Q':
                        prospect= (columns[2]+ ' '+columns[4])
                        opponentName=getOpponent(columns[10])
                        teamName=getOpponent(columns[9])
                        #search for own team and opponent team
                        
                        query=datastore_client.query(kind='Team')
                        query.add_filter('team','=',teamName+week)
                        results=list(query.fetch())
                
                        if(len(results)!=0):
                            team=results[0]
                    
                        query=datastore_client.query(kind='Team')
                        query.add_filter('team','=',opponentName+week)
                        results=list(query.fetch())
                
                        if(len(results)!=0):
                            opp=results[0]    
                        salary = float(columns[7])
                        
                        query=datastore_client.query(kind='Player')
                        query.add_filter('name','=',prospect)
                        query.add_filter('week','=',week)
                        results=list(query.fetch())
                        
                        if columns[1]=='QB':
                            if len(results)>0:
                                player=results[0]
                                expectedTDs=team['TDs']*(team['pass_TD_avg']/(team['pass_TD_avg']+team['rush_TD_avg']))/(team['pass_TD_avg']+.00001)*.66*(player['average_pass_tds'])+team['TDs']*(team['rush_TD_avg']/(team['pass_TD_avg']+team['rush_TD_avg']))/(team['rush_TD_avg']+.00001)*(player['average_rush_tds'])
                                pass_mult= opp['pass_avg_allowed']/league['pass_avg']
                                rush_mult= opp['rush_avg_allowed']/league['rush_avg']
                                pass_TD_mult=opp['pass_TD_avg']/(opp['pass_TD_avg']+opp['rush_TD_avg'])
                                rush_TD_mult=opp['rush_TD_avg']/(opp['pass_TD_avg']+opp['rush_TD_avg'])
                                expectedScore=player['average_pass_yds']*pass_mult/25+player['average_rush_yds']*rush_mult/10+player['average_rec_yds']*pass_mult/10+expectedTDs*6+player['average_receptions']*.5
                                player.update({
                                    'expectedScore':expectedScore,
                                    'expectedTDs': expectedTDs,
                                    'salary':float(columns[7]),
                                })
                                datastore_client.put(player)                                
                        elif columns[1] == 'RB' or columns[1]=='WR' or columns[1]=='TE':
                            if len(results)>0:
                                pass_mult= opp['pass_avg_allowed']/league['pass_avg']
                                rush_mult= opp['rush_avg_allowed']/league['rush_avg']
                                pass_TD_mult=opp['pass_TD_avg']/(opp['pass_TD_avg']+opp['rush_TD_avg'])
                                rush_TD_mult=opp['rush_TD_avg']/(opp['pass_TD_avg']+opp['rush_TD_avg'])
                                player=results[0]
                                expectedTDs=team['TDs']*pass_TD_mult/ (team['pass_TD_avg']+.00001)* (player['average_rec_tds']+team['TDs']*rush_TD_mult/(team['rush_TD_avg']+.00001)*(player['average_rush_tds']))
                                
                               
                                expectedScore=player['average_pass_yds']*pass_mult/25+player['average_rush_yds']*rush_mult/10+player['average_rec_yds']*pass_mult/10+expectedTDs*6+player['average_receptions']*.5
                                player.update({
                                    'expectedScore':expectedScore,
                                    'expectedTDs': expectedTDs,
                                    'salary':float(columns[7]),
                                })
                                datastore_client.put(player)
        i=i+1    

#pulled from main. Each of these works on a spreadsheet to generate Entities        
def generateData(week, bucket_name):
    createVegas(week, bucket_name)
    createDefense(week, bucket_name)
    createTeamOffense(week,bucket_name)
    createPlayers('QB', week, bucket_name)
    createPlayers('RB', week, bucket_name)
    createPlayers('WR', week, bucket_name)
    createPlayers('TE', week, bucket_name)
    addSalaries(week,bucket_name)
    