'''
Created on 2013-10-07

@author: Ivan
'''
class NBAStats:
    def __init__(self, *args, **kwargs):
        if (kwargs["type"] == ""):
            self.type = "Totals"
        else:
            self.type = "PerGame"
            
        if (len(args) == 18):
            # This per game; we want float numbers
            self.fgm = float(args[0])
            self.fga = float(args[1])
            self.fgp = args[2]
            self.fgm3 = float(args[3])
            self.fga3 = float(args[4])
            self.fgp3 = args[5]
            self.ftm = float(args[6])
            self.fta = float(args[7])
            self.ftp = args[8]
            self.orb = float(args[9])
            self.drb = float(args[10])
            self.trb = float(args[11])
            self.ast = float(args[12])
            self.stl = float(args[13])
            self.blk = float(args[14])
            self.tov = float(args[15])
            self.pf = float(args[16])
            self.pts = float(args[17])
            
        
    def __str__(self):
        return "Type: " + self.type + ", Pts: " + str(self.pts) 
    