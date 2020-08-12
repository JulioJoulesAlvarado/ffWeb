
import random
import math
from operator import add


import os
import datetime
import re
from flask import Flask, render_template, request, make_response, url_for,redirect
import csv
from google.cloud import datastore
from google.cloud import storage

datastore_client = datastore.Client()


#updateData
def updateData(query, argsName, argsVals):
    for (n,v) in zip(argsName, argsVals):
        query.update({
            n:v
        })
    datastore_client.put(query)    
    
#insert into Database
def insertIntoDatabase(objectKind, argsName, argsVals):
    x=datastore.Entity(key=datastore_client.key(objectKind))
    
    for (n,v) in zip(argsName, argsVals):
        x.update({
            n:v
        })
    datastore_client.put(x)
    
#remove from Database
def deleteFromDatabase(objectKind, argsName, argsVals):
    query = datastore_client.query(kind=objectKind)
    
    for (n,v) in zip(argsNames,argsVals):
        query.add_filter(n,'=',v)
    
    q=list(query.fetch())
    
    if len(q)>0:
        for data in q:
            datastore_client.delete(data.key)
            
#update in Database
def updateFromDatabase(objectKind, argsName, argsVals):
    deleteFromDatabase(objectKind, argsName, argsVals)
            
    insertIntoDatabase(objectKind, argsName, argsVals)

#query database
def queryDatabase(objectKind, argsNames, argsVals):
    query = datastore_client.query(kind=objectKind)
    
    for (n,v) in zip(argsNames,argsVals):
        query.add_filter(n,'=',v)

    q=list(query.fetch())
    return q

def serveFile(title, bucket_name):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)  
 
    blob=bucket.get_blob(title)
    file=blob.download_as_string()
    return file
    
#deletes a file from bucket on google cloud storage  
def delete_blob(bucket_name, blob_name):
    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()
    
def addDictToDatabase(objectKind, players):
    for player in players:
        data=players[player].toDatabaseFormat()
        insertIntoDatabase('Player', data[0],data[1])
  