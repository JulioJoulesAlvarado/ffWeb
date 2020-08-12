from Player import *

class QB(Player):
    def __init__(self, name, position, team, week, expectedScore=0,expectedTDs=0, salary = 60000,numgames=1,pass_yds=0,rush_yds=0, rec_yds=0, receptions=0, pass_tds=0, rec_tds=0,rush_tds=0):
        self.name=name
        self.position=position
        self.team=team
        self.week=week
        self.expectedScore=expectedScore
        self.expectedTDs=expectedTDs
        self.salary=salary
        self.numgames=numgames
        self.average_pass_yds=pass_yds/numgames
        self.average_rush_yds=rush_yds/numgames
        self.average_rec_yds=0
        self.average_receptions=0
        self.average_pass_tds=pass_tds/numgames
        self.average_rec_tds=0
        self.average_rush_tds=rush_tds/numgames
    def calcExpectation(self,salary,team,opp,league):
        self.salary=salary
        self.expectedTDs=team['TDs']*(team['pass_TD_avg']/(team['pass_TD_avg']+team['rush_TD_avg']))/(team['pass_TD_avg']+.00001)*.66*(self.average_pass_tds)+team['TDs']*(team['rush_TD_avg']/(team['pass_TD_avg']+team['rush_TD_avg']))/(team['rush_TD_avg']+.00001)*(self.average_rush_tds)
        pass_mult= opp['pass_avg_allowed']/league['pass_avg']
        rush_mult= opp['rush_avg_allowed']/league['rush_avg']
        pass_TD_mult=opp['pass_TD_avg']/(opp['pass_TD_avg']+opp['rush_TD_avg'])
        rush_TD_mult=opp['rush_TD_avg']/(opp['pass_TD_avg']+opp['rush_TD_avg'])
        self.expectedScore=self.average_pass_yds*pass_mult/25+self.average_rush_yds*rush_mult/10+self.average_rec_yds*pass_mult/10+self.expectedTDs*6+self.average_receptions*.5