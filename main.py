# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python37_render_template]
import os
import datetime
import re
from flask import Flask, render_template, request, make_response, url_for,redirect
from statsCreator import *
from werkzeug.utils import secure_filename
import hashlib
from geneticAlgo import *
from database import *


app = Flask(__name__)

from google.cloud import datastore
from google.cloud import storage


datastore_client = datastore.Client()
Positions = ["QB","RB","WR","TE"]
Data=["Offense","Defense", "Vegas","Fanduel"]

###valid_username, valid_password, valid_email used for signup.
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return USER_RE.match(username)
    
PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return PASS_RE.match(password)
    
EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

#created password hash. Used md5 because quick. Update to random key+other hash later.
def hash_str(s):
    s=str(s)
    return hashlib.md5(s.encode()).hexdigest()
 
#for password hashing 
def make_secure(s):
    x= hashlib.md5(s.encode())
    return s+'|'+x.hexdigest()

#method used by every page to confirm username cookie is correct
def isSignedIn(s):
    if s == None:
        return False
    pre=s[0:s.find('|')]
    if valid_username(pre) and check_secure(s)==pre:
        return True
    else:
        return False

#returns username if hash is correct
def check_secure(h):
    if h == None:
        return False
    pre=h[0:h.find('|')]
    if h== pre+'|'+hash_str(pre):
        return pre
    return None 

#for my admin pages. Admin pages generate data for database
def isAdmin(username):  
    if check_secure(username)=="mcjoules":
        return True
    return False

#Uploads a file to the bucket on google cloud storage  
def upload_blob(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )


#checks if position, offense, defense, and vegas csv are in google cloud storage to generate all data
def weekReady(week):
    storage_client = storage.Client()
    bucket=storage_client.get_bucket("virtual-indexer-278501.appspot.com")
    for pos in Positions:
        if bucket.get_blob(week+pos+".csv")== None:
            return pos
    for d in Data:
        if bucket.get_blob(week+d+".csv")== None:
            return d
    return "True"
    
@app.route('/')
def root():
    return redirect('/home')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    elif request.method=='POST':   
        user=request.form["username"]
        passw=request.form["password"]      
        bools = dict(username=user)
        
        correct= True
        if(valid_username(user) is None):  
            correct=False
            bools['userBool']="That's not a valid username."
        if(valid_password(passw) is None):
            correct=False
            bools['passwordBool']="That wasn't a valid password."        
        if(correct is True):
            query = datastore_client.query(kind='User')
            query.add_filter('username','=', user)
            users=list(query.fetch())
            
            if( len(users) == 0):
                bools['userBool']="Invalid Login"
                return render_template("login.html",**bools)
            else:
                front=users[0]
                if front['username'] != user or passw!= front['password']:
                    correct=False
                    bools['userBool']="Invalid Login"
                    return render_template("login.html",**bools)
                else:
                    user_safe=str(make_secure(user))
                    
                    if(isAdmin(user_safe)):                
                        resp=make_response(redirect(url_for('upload')))
                        resp.set_cookie('username', user_safe)
                        return resp
                    else:
                        resp=make_response(redirect(url_for('home')))
                        resp.set_cookie('username', user_safe)
                        return resp                
        else:
            return render_template("login.html",**bools)
                

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    
    if request.method == 'GET':
        return render_template("sign.html")
    
    elif request.method == 'POST':
        user=request.form["username"]
        passw=request.form["password"]
        verif=request.form["verify"]
        mail=request.form["email"]
        
        bools = dict(username=user, email=mail)
        
        correct= True
        
        if(valid_username(user) is None):  
            correct=False
            bools['userBool']="That's not a valid username."
        if(valid_password(passw) is None):
            correct=False
            bools['passwordBool']="That wasn't a valid password."
        else:
            if verif!=passw:
                correct=False
                bools['verifyBool']="Your passwords didn't match."
        if not valid_email(mail):
            correct=False
            bools['emailBool']="That's not a valid email."
                   
        #add to database if not taken
        #check if in database
        #if is return error, else hash password. then put in database.
        
        if(correct is True):
            users=queryDatabase('User',['username'],[user])
            
            if(len(users) > 0):
                bools['userBool']="That user already exists."
                return render_template("sign.html", **bools)
            else:      
                insertIntoDatabase('User',['username','password','email'],[user,passw,mail])
                
                user_safe=str(make_secure(user))
                bools['userBool']="Created Entry."
                resp=make_response(render_template("sign.html",**bools))
                resp.set_cookie('username', user_safe)
                return resp
                
        else:
            return render_template("sign.html",**bools)
            
@app.route('/logout')
def logout():
    resp=make_response(redirect(url_for('login')))
    resp.set_cookie('username', "")
    return resp

# admin page to upload csv to buckets
@app.route('/upload',methods=['GET', 'POST'])   
def upload():
    if request.method == 'GET':
        username= request.cookies.get('username')
        if isAdmin(username):
            return render_template("adminPage.html")
        else:
            return redirect('/login')    
    elif request.method == 'POST':
        username= request.cookies.get('username')
        if isAdmin(username):
            week=request.form["week"]
            position=request.form["position"]
        
            bucket_name="virtual-indexer-278501.appspot.com"
            file=request.files["filePath"]
            
            #blob info
            source_file_name=secure_filename(file.filename)
            destination_blob_name=week+position+".csv"
            upload_blob(bucket_name, source_file_name, destination_blob_name)
            
            return render_template("adminPage.html")
        else:
            return redirect('/login')
    else:
        return redirect('/login')

# admin page to delete a csv from buckets
@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if request.method == 'GET':
        username= request.cookies.get('username')
        if isAdmin(username):
            return render_template("deleteAdminPage.html")
        else:
            return redirect('/login')
    elif request.method == 'POST':
        username= request.cookies.get('username')
        if isAdmin(username):
            week=request.form["week"]
            position=request.form["position"]
            
            #blob info
            bucket_name="virtual-indexer-278501.appspot.com"
            blob_name=week+position+".csv"
            
            delete_blob(bucket_name,blob_name)
            return render_template("deleteAdminPage.html")
        else:
            return redirect('/login')
    else:
        return redirect('/login')

#player can select players not to include in lineup generator
#this function returns those exclusions by position
#exclusion is it's own Entity to save in database rather than player
def doesPlayerHavePreferences(username,week, position):
    excluded=queryDatabase('excluded',['position','user','week'],[position,username,week])   
    if len(excluded)>0:
        return True
    return False

#Get lists the players you want to exclude based on position and week. 
#Two post options possible. 
#First Generates a lineup.
#Second saves which players you don't want included in your lineup generator
@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        username= request.cookies.get('username')
        if isSignedIn(username):
            #Doesn't load any positions unless GET included with List Preferences button
            if request.args.get('week') == None or request.args.get('position')== None:
                return render_template('home.html',username=check_secure(username), players= None)    
            else:
                w=request.args.get('week')
                p=request.args.get('position')
                
                #pulls all players of the position to Print
                query=datastore_client.query(kind='Player')
                query.add_filter('position','=',p)
                query.add_filter('week','=',w)
                query.add_filter('expectedScore','>',0)
                players=list(query.fetch())
                players=sorted(players, key=lambda player: player['name'])
                
                #checks if the user has made preferences. Pulls out exclusions if there are
                if doesPlayerHavePreferences(check_secure(username),w, p):

                    excluded=queryDatabase('excluded',['position','user','week'],[p,check_secure(username),w])
                    excluded=[ex['name'] for ex in excluded]
                    
                    return render_template('home.html',username=check_secure(username),week=w, position=p,players=players,excluded=excluded)
                else:              
                    return render_template('home.html',username=check_secure(username),week=w, position=p, players=players)                   
        else:
            return redirect('/login')
    if request.method == 'POST':
        username= request.cookies.get('username')
        week=request.args.get("week")
        if isSignedIn(username):        
            if 'Get Lineup' in request.form: 
                salary=request.form.get("salary")
                return redirect(url_for('.FullLineup',week=week,salary=salary))
            elif 'Submit Preferences' in request.form:
                position=request.args.get("position")
                
                #generates excludes. Puts them in database.
                excluded=request.form.getlist('excluded')
                updateExcludeList(excluded,check_secure(username),week,position)
                
                #gets players. sends to html form along with excluded to keep players checked and unchecked
                query=datastore_client.query(kind='Player')
                query.add_filter('position','=',position)
                query.add_filter('week','=',week)
                query.add_filter('expectedScore','>',0)
                players=list(query.fetch())
                players=sorted(players, key=lambda player: player['name'])                

                return render_template('home.html',week=week,position=position,players=players,excluded=excluded)
        else:
                return redirect('/login')

#should rename. This is an Admin page that takes all csv data files and converts it into database Entities     
@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'GET':
        username= request.cookies.get('username')
        if isAdmin(username):
            return render_template("generateWeek.html")
        else:
            return redirect('/login')
    elif request.method == 'POST':
        username= request.cookies.get('username')
        if isAdmin(username):
            week=request.form["week"]
            bools = dict(w=week)
            bucket_name="virtual-indexer-278501.appspot.com"
            
            week=request.form["week"]
            
            if weekReady(week)=="True":
                bools['weekBool']="Generating Player Data"
                generateData(week, bucket_name)
                return render_template("generateWeek.html",**bools)
            else:
                missing=weekReady(week)
                bools['weekBool']="All Data Not Available. Missing: "+missing
                return render_template("generateWeek.html",**bools)
        else:
            return redirect('/upload')
    else:
        return redirect('/upload')

###remaining used to generate Lineup. 

#returns a list of players with exclusions removed. Adds them all to a dict, which is used by the genetic algo
def createListsPlayers(username,week):
    QBs=playersWithPreferences(username, week, 'QB')
    RBs=playersWithPreferences(username, week, 'RB')    
    WRs=playersWithPreferences(username, week, 'WR')    
    TEs=playersWithPreferences(username, week, 'TE')
    flex=[]
    flex.extend(RBs)
    flex.extend(WRs)
    flex.extend(TEs)

    allPlayers={'QBs':QBs,'RBs':RBs,'WRs':WRs,'TEs':TEs,'Flex':flex}
    
    return allPlayers

#when a user submits preferences, I delete previous ones to keep the database consistent.
def deleteExcludes(username, week, position):
    excluded=queryDatabase('excluded',['position','user','week'],[position,username,week])
    
    if len(excluded)>0:
        for ex in excluded:
            datastore_client.delete(ex.key)
        
#this creates Entities for players the user does not want to include in generator. Deletes previous entities and adds these excluded players
def updateExcludeList(excluded,username,week,position):
    deleteExcludes(username, week,position)
    
    for exclude in excluded:
        insertIntoDatabase('excluded',['user','week','position','name'],[username,week,position,exclude])
        
#generates list of players that a user likes to include based on week and position
def playersWithPreferences(username, week, position):
    excluded=queryDatabase('excluded',['position','user','week'],[position,username,week])
    
    excluded=[ex['name'] for ex in excluded]
    
    query=datastore_client.query(kind='Player')
    query.add_filter('position','=',position)
    query.add_filter('week','=',week)
    query.add_filter('expectedScore','>',0)
    players=list(query.fetch())
    
    p=[]
    for player in players:
        if player['name'] not in excluded:
            p.append(player)
    return p
    
#takes users options, and sends to genetic algorithm to generate lineup
def generateFullLineup(username, week,salary):
    allPlayers=createListsPlayers(username, week)
    team=genetic(allPlayers,salary)
    return team


#returns one lineup from the lineup generator
#making salary set for now
#as weeks passs, i can change default week here    
@app.route('/fullLineup', methods=['GET'])
def FullLineup():    
    username= request.cookies.get('username')
    if request.args.get("salary")!= "":
        salary= float(request.args.get('salary'))
    else:
        salary=56000
    if isSignedIn(username):
        if 'week' in request.args:
            w=request.args['week']
        else:
            w="Week 1"
        team=generateFullLineup(check_secure(username),w,salary)
    
        return render_template('weeklyPlay.html',team=team, week=w)
    else:
        redirect('login')

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [START gae_python37_render_template]
