<b>This is a website that generates a Daily Fantasy Football Lineup based on preferences</b>

<b>Backend Files</b>

main.py: runs the website. Directory info, login, signup, and calls other functions
<p>
statsCreator.py: takes the csv's with data and transforms them into stats for the database.
</p>
<p>
database.py: handles all of the data entry, updating, and delition from cloud. Returns Queries in list format.
</p>
<p>
Player.py: Class for Player. Instantiates player with stats. Has method to convert Class into data for the database to process.
</p>
<p>
QB.py,RB.py,WR.py,TE.py: Inherits from PLayer. Only new method is each individual class calculates expected Scores differently.
</p>
<p>
geneticAlgo.py: takes user preferences and generates a lineup using the database and user preferences.
</p>
<p>
<b>HTML pages are in /templates</b>

<b>Examples of CSV files are in csv folder</b>
</p>
