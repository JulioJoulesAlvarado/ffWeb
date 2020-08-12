from Player import *
class RB(Player):
    def __init__(self, name, position, team, week, expectedScore=0, expectedTDs=0,salary = 60000,numgames=1,pass_yds=0,rush_yds=0, rec_yds=0, receptions=0, pass_tds=0, rec_tds=0,rush_tds=0):
        self.name=name
        self.position=position
        self.team=team
        self.week=week
        self.expectedScore=expectedScore
        self.expectedTDs=expectedTDs
        self.salary=salary
        self.numgames=numgames
        self.average_pass_yds=0
        self.average_rush_yds=rush_yds/numgames
        self.average_rec_yds=rec_yds/numgames
        self.average_receptions=receptions/numgames
        self.average_pass_tds=0
        self.average_rec_tds=rec_tds/numgames
        self.average_rush_tds=rush_tds/numgames