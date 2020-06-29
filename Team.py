class Team():

    def __init__ (self,name):   
        
        self.team_name = name
        
        self.avg_pass_allowed=0 #defensive stats
        self.avg_rush_allowed=0
        self.pass_multiplier= 0 #compared to leage average
        self.rush_multiplier= 0   #compared to League Average

        self.avg_off_pass_tds=0 #offensive stats
        self.avg_off_rush_tds=0
        self.rush_perc=0
        self.pas_perc=0
        
        self.expected_tds=0 

    def set_name(self,name):       
        self.team_name=name

    def name(self):
        return self.team_name
#defensive Stats
    def set_average_pass_allowed(self,yards):       
        self.avg_pass_allowed=yards  

    def set_average_rush_allowed(self,yards):
        self.avg_rush_allowed =yards

    def set_pass_mult(self,league):
        self.pass_multiplier= self.avg_pass_allowed/league

    def set_rush_mult(self,league):
        self.rush_multiplier= self.avg_rush_allowed/league

#offensive stats
    def set_average_pass_tds(self,tds):
        self.avg_off_pass_tds=tds

    def set_average_rush_tds(self,tds):
        self.avg_off_rush_tds=tds

    def set_percent_pass(self):
        self.pass_perc=self.avg_off_pass_tds / (self.avg_off_pass_tds+self.avg_off_rush_tds)

    def set_percent_rush(self):
        self.rush_perc=self.avg_off_rush_tds / (self.avg_off_pass_tds+self.avg_off_rush_tds)
    
    #expected performance
    def set_expected_tds(self,tds):
        self.expected_tds=tds

    def expected_tds(self,tds):
        return self.expected_tds