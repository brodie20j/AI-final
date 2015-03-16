# greedyTeam.py
# Created By Jonathan Brodie and John Blake
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
      self.food=0


    def registerInitialState(self, gameState):
      self.start = gameState.getAgentPosition(self.index)
      CaptureAgent.registerInitialState(self, gameState)

    def chooseAction(self, gameState):
      actions = gameState.getLegalActions(self.index)

      #A greedy agent NEVER stops
      if 'Stop' in actions: actions.remove('Stop')
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
      """
      Evaluates the state based on the features of the state
      """
      prevGhost=[a for a in [state.getAgentState(i) for i in self.getOpponents(state)] if not a.isPacman and a.getPosition() != None]
      prevFood=self.getFood(state).asList()
      successor = self.getSuccessor(state, action)
      myState = successor.getAgentState(self.index)
      myPos = myState.getPosition()
      total=0
      if not successor in self.explored:
        total+=20

      #if the successor state is start, don't take this action
      if myPos == self.start:
        self.food=0
        total-=100

      foodList = self.getFood(successor).asList()# Compute distance to the nearest food

      if myState.isPacman:#If we are on offense...

        if len(prevFood) > len(foodList):
          total+=10
          self.food+=1
        if len(foodList) > 0: # This should always be True,  but better safe than sorry
          minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
          total+=-1*minDistance
        if self.food > 3:
          if (len(self.getFoodYouAreDefending(successor).asList()) > 0):
            minDistance = min([self.getMazeDistance(myPos, food) for food in self.getFoodYouAreDefending(successor).asList()])
          total+=-20*minDistance
      else:#if we are on defense
        if self.getScore(state) < self.getScore(successor):
          total+=20
        prev= [a for a in [state.getAgentState(i) for i in self.getOpponents(state)] if a.isPacman and a.getPosition() != None]
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
        if len(prev) > len(invaders):
          total+=50
        if len(invaders) > 0:
          dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
          minDistance = min(dists)
          total+=-1*minDistance
        elif len(foodList) > 0: # This should always be True,  but better safe than sorry
          minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
          total+=-1*minDistance

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
