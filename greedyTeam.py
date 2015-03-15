# greedy.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'GreedyAgent', second = 'GreedyAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class GreedyAgent(CaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at baselineTeam.py for more details about how to
    create an agent as this is the bare minimum.
    """
    def __init__( self, index ):
      self.observationHistory = []
      self.index = index
      self.explored=[]


    def registerInitialState(self, gameState):
      self.start = gameState.getAgentPosition(self.index)
      CaptureAgent.registerInitialState(self, gameState)

    def chooseAction(self, gameState):
      """
      Picks among actions randomly.
      """
      actions = gameState.getLegalActions(self.index)

      bestaction=None
      bestval=float("-inf")
      for action in actions:
        temp=self.evaluate(gameState,action)
        if bestaction is None:
          bestaction=action
          bestval=temp
        elif bestval<temp:
          bestaction=action
          bestval=temp
      if self.getSuccessor(gameState,bestaction) not in self.explored:
        self.explored.append(self.getSuccessor(gameState,bestaction))
      return bestaction

    def evaluate(self,state,action):
      successor = self.getSuccessor(state, action)
      myState = successor.getAgentState(self.index)
      myPos = myState.getPosition()
      total=0
      if not successor in self.explored:
        total+=20

      foodList = self.getFood(successor).asList()# Compute distance to the nearest food
      if myState.isPacman:
        if len(self.getFood(state).asList()) > len(foodList):
          total+=10
        if len(foodList) > 0: # This should always be True,  but better safe than sorry
          minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
          total+=-1*minDistance
      else:
        prev= [a for a in [state.getAgentState(i) for i in self.getOpponents(state)] if a.isPacman and a.getPosition() != None]
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
        if len(prev) > len(invaders):
          total+=10
        if len(invaders) > 0:
          dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
          minDistance = min(dists)
          total+=-1*minDistance

        elif len(foodList) > 0: # This should always be True,  but better safe than sorry
          minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
          total+=-1*minDistance
      print "Action:"+action
      print total
      return total
    def getSuccessor(self, gameState, action):
      """
      Finds the next successor which is a grid position (location tuple).
      """
      successor = gameState.generateSuccessor(self.index, action)
      pos = successor.getAgentState(self.index).getPosition()
      if pos != util.nearestPoint(pos):
        # Only half a grid position was covered
        return successor.generateSuccessor(self.index, action)
      else:
        return successor
