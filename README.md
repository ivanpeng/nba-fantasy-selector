nba-fantasy-selector
====================

Simple Fantasy draft selector

This project provides a simple UI and optimization tool for selecting your NBA fantasy team on draft day. The UI will allow you to enter players, and which fantasy teams they have been drafted on, followed by selecting the next best available player, depending on your team in which role to fill.

Setting up the data:
Data set up is currently in progress. Currently, all data is in CSV tables, and is loaded onto the DB one time. The tables are stored on a local MySQL DB and are accessed through DAOs which handle the backend of the data reading. After running the load scripts for the CSV files, the fantasy table needs to be populated. Currently, there is no engine for that either.

Using the program:
On draft day, the UI will open up, and you may track which fantasy team drafts which player with the UI entry form. When it gets to your turn, you will close the program, and then reopen it, enter the fantasy team and round number, and hit optimize. This will determine the best player suited for your team. At the first few rounds, you're just trying to pick the best player available.

Algorithm:
So far, a simple algorithm of grading players is used. Each player is compared against the league average stat in each category, and measured how much above or below they are, in terms of percentages. Then, they are tallied for some total percentage calculation, and then ranked based on that. Surprisingly, this simple percentage calculation works pretty well. The top 3 ranking for a standard no-turnover draft league goes LBJ, KD, Steph Curry, James Harden, CP3 (ESPN's rankings goe KD, LBJ, James Harden, CP3, Steph Curry). After a certain amount of rounds, it finds the stats that you are lacking, and tries to push the weaker stats as far up as they can, as the key to a fantasy team is balance across all stat categories.
One bug in the algorithm is that it deals with percentages and hard numbers the same way. One of the main stats is FG%, and PTS. The former is a percentage, and the latter is a number. You can never be more than 10% above league average, whereas you can double (or even triple) the league average in points scored. So it becomes a challenge to weight it properly. 


Things to do:
- load script for first time use
- more functional UI and overriding of spring's auto caching
- DB table organization and pivoting. Right now, stats are divided into ugly columns, and organization of fantasy teams is pretty bad as well. There are too many tables, and stats should be more consolidated into one table and pivoting should be utilized more.
- more advanced stats, and factoring teams and positions into the project
- machine learning on development of stats. This isn't about scouting out the best players. This is about trying to figure out the best way to win fantasy basketball, which is a lot easier. We can figure out the best metric of that over historical data and what indicators are the best, given statistical uncertainty.
