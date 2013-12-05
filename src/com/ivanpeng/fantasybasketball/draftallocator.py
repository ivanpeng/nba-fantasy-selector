'''
This module is responsible for the UI on draft day for entering who goes where.

Created on 2013-10-05

@author: Ivan
'''
import MySQLdb
from Tkinter import *
from DefaultSelector import DefaultSelector

class Application(Frame):
    """ A GUI Application for determining who has been drafted """
    
    def __init__(self,master):
        """ Initialize the frame"""
        Frame.__init__(self, master)
        self.db = MySQLdb.connect(host="localhost", user="ivan", passwd="watershipdown", db="nba_db")
        self.grid()
        self.create_widgets()
    
    def create_widgets(self):
        """Create button, text and entry widgets"""
        self.fTeamLabel = Label(self, text="Enter the Fantasy Team Key: ")
        self.fTeamLabel.grid(row = 0, column = 0, columnspan = 2, sticky = W)

        self.fTeamKey = Entry(self)
        self.fTeamKey.grid(row=0, column=1, sticky=W)
                
        self.roundLabel = Label(self, text="Enter the round number: ")
        self.roundLabel.grid(row=1, column=0,sticky=W)
        
        self.round = Entry(self)
        self.round.grid(row=1, column=1, sticky=W)
        
        self.playerLabel = Label(self, text="Enter the player name (make sure spelling is right!): ")
        self.playerLabel.grid(row=2, column =0, columnspan = 2, sticky=W)
        
        self.playerName = Entry(self)
        self.playerName.grid(row=2, column =1, sticky=W)
        
        self.submit_button = Button(self, text = "Submit", command=self.submit)
        self.submit_button.grid(row=3, column=0, sticky=W)
        
        self.optimize_button= Button(self, text="Optimize", command=self.optimize_list)
        self.optimize_button.grid(row=3, column=1, sticky=W)
        
        self.text = Text(self, width = 35, height = 5, wrap = WORD)
        self.text.grid(row=4, column=0, sticky=W)

    def submit(self):
        """Call DB and add the data"""
        fTeamKey = self.fTeamKey.get()
        playerName = self.playerName.get()
        
        cur = self.db.cursor()
        cur.execute("select Player_Key from Player where Player_Name = '" + playerName + "'")
        playerList = cur.fetchone()
        playerKey = int(playerList[0])
        cur.execute("select Fantasy_Team_Name from Fantasy_Teams2 where Fantasy_Team_Key = " + fTeamKey)
        fTeamName = str(cur.fetchone()[0])
        if (playerKey is not None):
            print "update Player set Selected_Flag2 = " + str(fTeamKey) + " where Player_Key = " + str(playerKey)
            cur.execute("update Player set Selected_Flag2 = " + str(fTeamKey) + " where Player_Key = " + str(playerKey))
            message = "Player with name " + playerName + " and key " + str(playerKey) + " inserted into DB for fantasy team " + fTeamName
            # Should add functionality for confirming which team 
            self.db.commit()
        else:
            message = "Player not found. Please try again"
        self.text.delete(0.0, END)
        self.text.insert(0.0, message)
    
    def optimize_list(self):
        #Do internal processing for determining player to select
        statCategories = ["fgp", "ftp", "fgm3", "pts", "trb", "ast", "stl", "blk"]
        selector = DefaultSelector(statCategories = statCategories)
        selector.selectMaster(int(self.round.get()), int(self.fTeamKey.get()))
        self.text.delete(0.0, END)
        self.text.insert(0.0, "Optimizing the list for Fantasy Team " + self.fTeamKey.get())

        
# create the window
root = Tk()

#modify root window
root.title("Draft UI")
root.geometry("500x200")

app = Application(root)

#kick off the event loop
root.mainloop()

