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
      self.epsilon=0.2
      self.alpha=0.6
      self.discount=0.8
      self.features={}
      self.weights ={}
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
        
        #If epsilon, return a random action, otherwise return an optimal
        #policy

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

      self.weights[(state,action)]=currentValues

    def getFeatures(self, gameState, action):
      if ((not ((gameState, action) in self.features)) or (abs(self.timer['total']-self.timer[gameState]) > 3)):
        #we haven't seen this state yet, create new features
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()
        self.timer[gameState]=self.timer['total']
        foodList = self.getFood(successor).asList()
        prevfoodList=self.getFood(gameState).asList()    

        if myPos==self.startPos:
          features['justEaten']=1
        else:
          features['justEaten']=0
        # Computes whether we're on defense (1) or offense (0)
        features['onDefense'] = 1
        if myState.isPacman: features['onDefense'] = 0


        # Computes distance to invaders we can see

        #Are we on offense or defense?
        if self.getOnDefense(gameState,action):
          features['successorScore'] = self.getScore(successor)-self.getScore(gameState)
          enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
          invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
          features['numInvaders'] = len(invaders)
          if len(invaders) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
            features['invaderDistance'] = min(dists)
          else:
            features['successorScore'] = self.getScore(successor)-self.getScore(gameState)#self.getScore(successor)
            # Compute distance to the nearest food
            if len(foodList) > 0: # This should always be True,  but better safe than sorry
              minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])

            features['distanceToFood'] = minDistance
          features['successorScore'] = self.getScore(successor)-self.getScore(gameState)
          if action == Directions.STOP: features['stop'] = 1
          rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
          if action == rev: features['reverse'] = 1
        else:
          features['successorScore']=abs(len(foodList)-len(self.getFood(gameState).asList()))
          features['onOffense']=1
          enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
          defenders = [a for a in enemies if (not a.isPacman) and a.getPosition() != None]
          if len(defenders) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in defenders]
            features['ghostDistance'] = min(dists)
  
          # Compute distance to the nearest food
          if len(foodList) > 0: # This should always be True,  but better safe than sorry
            myPos = successor.getAgentState(self.index).getPosition()
            minDistance=min([self.getMazeDistance(myPos, food) for food in foodList])
            if (len(foodList)) < (len(prevfoodList)):
              self.food+=1
            features['distanceToFood'] = minDistance
          features['totalFood']=self.food
        self.features[(gameState,action)]=features

      return self.features[(gameState,action)]
    def getWeights(self,state,action):
      if ((not ((state, action) in self.weights)) or (abs(self.timer['total']-self.timer[state]) > 10)):
        weights=util.Counter()
        successor=self.getSuccessor(state,action)
        myState=successor.getAgentState(self.index)
        myPos=myState.getPosition()
        self.timer[state]=self.timer['total']

        if self.getOnDefense(state,action):
          weights['droppedOffFood']=1000
          weights['justEaten']=-100
          weights['numInvaders']=-100
          weights['onDefense']=100
          weights['successorScore']=100
          weights['distanceToFood']= -1
          weights['invaderDistance']=-10
          weights['stop']=-100
          weights['reverse']=-2
        else:
          weights['dropOffFood']=-100
          weights['totalFood']=100
          weights['nearestPellet']=-0.5
          weights['onOffense']=1000
          weights['successorScore']=100
          weights['distanceToFood']= -1
          weights['ghostDistance']=-1
          weights['hasFood']=100
        self.weights[(state,action)]=weights
      return self.weights[(state,action)]


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

