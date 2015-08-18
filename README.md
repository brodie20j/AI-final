# AI-final
AI Final Project.  Pacman tournament that pits the following different kinds of agents against each other:
-Baseline agents
-Greedy agents
-Q-learning agents
-Inference agents

We found inference agents strongly outperformed other kinds of agents.

The basic command to run the code is the following:

python capture.py

to specify red and blue teams, add either "-r" followed by the agent or "-b",
followed by the agent.

For example to run a red inference team against a blue greedy team:

python capture.py -r inferenceTeam -b greedyTeam

The team names for each agent we implemented are:
inferenceTeam -> inferenceTeam.py
greedyTeam -> greedyTeam.py
qlearnTeam -> qlearnTeam.py

The provided "Base line team" can be ran by "baselineTeam"
