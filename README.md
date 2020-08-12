<b>This is a website that generates a Daily Fantasy Football Lineup based on preferences</b>

<b>3 Big Files</b>

main: runs the website. Directory info, login, signup, and calls other functions
<br>
statsCreator: takes the csv's with data and transforms them into stats for the database.
<br>
database: handles all of the dataentry, updating, and delition from cloud
<br>
Player: Class for Player. instantiates player with stats and has method to convert it into something the database can process.
<br>
QB,RB,WR,TE: Inherit from PLayer. Only update is each individual class calculates expected Scores differently.
<br>
geneticAlgo: takes user preferences and generates a lineup using the database

<b>HTML pages are in /templates</b>

<b>Examples of CSV files are in csv folder</b>
