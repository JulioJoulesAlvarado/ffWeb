class Player:
    def __init__(self, name, position, team, week, expectedScore=0, expectedTDs=0, salary = 60000,numgames=1,pass_yds=0,rush_yds=0, rec_yds=0, receptions=0, pass_tds=0, rec_tds=0,rush_tds=0):
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
        self.average_rec_yds=rec_yds/numgames
        self.average_receptions=receptions/numgames
        self.average_pass_tds=pass_tds/numgames
        self.average_rec_tds=rec_tds/numgame
        self.average_rush_tds=rush_tds/numgames
        
    def toDatabaseFormat(self):
        args=['name', 'position','team', 'week','expectedScore','expectedTDs','salary','numgames','average_pass_yds','average_rush_yds','average_rec_yds','average_receptions','average_pass_tds','average_rec_tds','average_rush_tds']
        argsVals=[self.name,self.position,self.team,self.week, self.expectedScore,self.expectedTDs,self.salary,self.numgames,self.average_pass_yds,self.average_rush_yds, self.average_rec_yds,self.average_receptions,self.average_pass_tds,self.average_rec_tds,self.average_rush_tds]
        return [args, argsVals]
      
    def calcExpectation(self,salary,team,opp,league):
        self.salary=salary
        pass_mult= opp['pass_avg_allowed']/league['pass_avg']
        rush_mult= opp['rush_avg_allowed']/league['rush_avg']
        pass_TD_mult=opp['pass_TD_avg']/(opp['pass_TD_avg']+opp['rush_TD_avg'])
        rush_TD_mult=opp['rush_TD_avg']/(opp['pass_TD_avg']+opp['rush_TD_avg'])                        
        self.expectedTDs=team['TDs']*pass_TD_mult/ (team['pass_TD_avg']+.00001)* (self.average_rec_tds)+team['TDs']*rush_TD_mult/(team['rush_TD_avg']+.00001)*(self.average_rush_tds)                            
        self.expectedScore=self.average_pass_yds*pass_mult/25+self.average_rush_yds*rush_mult/10+self.average_rec_yds*pass_mult/10+self.expectedTDs*6+self.average_receptions*.5
                           