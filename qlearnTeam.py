# qlearnTeam.py
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
               first = 'QLearningAgent', second = 'QLearningAgent'):
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

class QLearningAgent(CaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at baselineTeam.py for more details about how to
    create an agent as this is the bare minimum.
    """
    def __init__( self, index ):
      self.observationHistory = []
      self.index = index
      #Q-Learning variables
      self.epsilon=0.2
      self.alpha=0.8
      self.discount=1.0
      self.offenseweights =util.Counter()
      self.defenseweights =util.Counter()

      self.food=0
      self.timer=util.Counter()
      self.timer['total']=0
      self.prevAction=None


    def registerInitialState(self, gameState):
      """
      This method handles the initial setup of the
      agent to populate useful fields (such as what team
      we're on).

      A distanceCalculator instance caches the maze distances
      between each pair of positions, so your agents can use:
      self.distancer.getDistance(p1, p2)

      IMPORTANT: This method may run for at most 15 seconds.
      """
      CaptureAgent.registerInitialState(self, gameState)

      self.start = gameState.getAgentPosition(self.index)
      self.startPos=gameState.getAgentState(self.index).getPosition()
      
    #return -1 if never visited
    def getLastVisitedTime(self, state):
      if self.timer[state]!=0:
        return self.timer[state]
      else:
        return -1

    def chooseAction(self, state):
        """
          Compute the action to take in the current state.  With
          probability self.epsilon, we should take a random action and
          take the best policy action otherwise.  Note that if there are
          no legal actions, which is the case at the terminal state, you
          should choose None as the action.
        """
        # Pick Action
        legalActions = state.getLegalActions(self.index)

        action = None
        if util.flipCoin(self.epsilon):

          action=random.choice(legalActions)

        else:
          action=self.getPolicy(state)
        
        successor = self.getSuccessor(state, action)
        self.timer['total']=self.timer['total']+1
        self.update(state, action, successor, self.getReward(state,action))
        return action
    def getQValue(self, state, action):
      #get the list of features
      stateFeatures=self.getFeatures(state,action)
      stateWeights=self.getWeights(state,action)
      mySum=0
      for feature in stateFeatures:

        mySum=mySum+(stateFeatures[feature] * stateWeights[feature])
      return mySum
    def computeActionFromQValues(self, state):
      actionList=state.getLegalActions(self.index)
      bestAction=None
      bestValue=None
      for action in actionList:
        tempValue=self.getQValue(state,action)
        #print action
        #print tempValue
        if tempValue > bestValue or bestValue == None:
          bestValue=tempValue
          bestAction=action

      self.prevAction=bestAction
      #print "Best action:"+bestAction
      return bestAction

    def computeValueFromQValues(self, state):
      """
        Returns max_action Q(state,action)
        where the max is over legal actions.  Note that if
        there are no legal actions, which is the case at the
        terminal state, you should return a value of 0.0.
      """
      actionList=state.getLegalActions(self.index)
      bestValue=None

      if not actionList:
        return 0.0

      for action in actionList:
        tempValue=self.getQValue(state,action)

        if tempValue > bestValue or bestValue == None:
          bestValue=tempValue

      return bestValue
    def update(self, state, action, nextState, reward):

      stateFeatures=self.getFeatures(state,action)
      currentValues=self.getWeights(state,action)
      nextAction=self.computeActionFromQValues(nextState)
      if nextAction==None:
        successorQValue=0
      else:
        successorQValue=self.getQValue(nextState,nextAction)
      difference=(reward+self.discount*successorQValue)-self.getQValue(state, action)
      for feature in stateFeatures.keys():
        currentValues[feature]=currentValues[feature]+(self.alpha*difference*stateFeatures[feature])
      myState=state.getAgentState(self.index)
      if myState.isPacman:
        self.offenseweights=currentValues
      else:
        self.defenseweights=currentValues

    def getFeatures(self,gameState,action):
      features = util.Counter()
      successor = self.getSuccessor(gameState, action)
      foodList = self.getFood(successor).asList()    

      myState = successor.getAgentState(self.index)
      myPos = myState.getPosition()

      if myState.isPacman:
        features['onOffense']=1
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        invaders = [a for a in enemies if (not a.isPacman) and a.getPosition() != None]
        if len(invaders) > 0:
          dists=[]
          for invader in invaders:
            dists.append(self.getMazeDistance(myPos,invader.getPosition()))
          features['ghostDistance'] = min(dists)
        features['successorScore'] = abs(len(foodList)-len(self.getFood(gameState).asList()))
        if action == Directions.STOP: features['stop'] = 1

        if len(foodList) > 0: # This should always be True,  but better safe than sorry
          myPos = successor.getAgentState(self.index).getPosition()
          minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
          features['distanceToFood'] = minDistance
      else:
        features['successorScore'] = self.getScore(successor)-self.getScore(gameState)
        if features['successorScore'] > 4:
          features['successorScore']=2^(features['successorScore'])
        elif features['successorScore'] < -4:
          features['successorScore']=-2^(features['successorScore'])

        features['onDefense'] = 1
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
        features['numInvaders'] = len(invaders)
        if len(invaders) > 0:
          dists=[]
          for invader in invaders:
            dists.append(self.getMazeDistance(myPos,invader.getPosition()))
          features['invaderDistance'] = min(dists)

        if action == Directions.STOP: features['stop'] = 1
        rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
        if action == rev: features['reverse'] = 1
      return features

    def getWeights(self,gameState,action):
      myState=gameState.getAgentState(self.index)
      if myState.isPacman:
        weights= self.offenseweights
      else:
        weights= self.defenseweights
      return weights


    def getPolicy(self, state):
      return self.computeActionFromQValues(state)

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

    def getReward(self, state, action):
      """
      Computes a reward given the features and weights
      """
      features = self.getFeatures(state, action)
      weights = self.getWeights(state,action)
      return features * weights
      
    def getOnOffense(self, state,action):
      successor = self.getSuccessor(state, action)
      myState = successor.getAgentState(self.index)
      return myState.isPacman
    def getOnDefense(self, state,action):
      successor = self.getSuccessor(state, action)
      myState = successor.getAgentState(self.index)
      return not myState.isPacman

