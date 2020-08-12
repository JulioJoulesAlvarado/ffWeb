<b>This is a website that generates a Daily Fantasy Football Lineup based on preferences</b>

<b>3 Big Files</b>

main: runs the website. Directory info, login, signup, and calls other functions
<p>
statsCreator: takes the csv's with data and transforms them into stats for the database.
</p>
<p>
database: handles all of the dataentry, updating, and delition from cloud
</p>
<p>
Player: Class for Player. instantiates player with stats and has method to convert it into something the database can process.
</p>
<p>
QB,RB,WR,TE: Inherit from PLayer. Only update is each individual class calculates expected Scores differently.
</p>
<p>
geneticAlgo: takes user preferences and generates a lineup using the database
</p>
<p>
<b>HTML pages are in /templates</b>

<b>Examples of CSV files are in csv folder</b>
</p>
