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
    print "INITIALIZING SHIT"
    self.index = index
    self.epsilon=0
    self.alpha=0.2
    self.discount=0.8
    self.qValues=util.Counter()



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

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''

    self.start = gameState.getAgentPosition(self.index)
    "INITIALIZING SHIT"
    
    CaptureAgent.registerInitialState(self, gameState)

  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """

    '''
    You should change this in your own agent.
    '''

    return bestAction



  def getAction(self, state):
      """
        Compute the action to take in the current state.  With
        probability self.epsilon, we should take a random action and
        take the best policy action otherwise.  Note that if there are
        no legal actions, which is the case at the terminal state, you
        should choose None as the action.

        HINT: You might want to use util.flipCoin(prob)
        HINT: To pick randomly from a list, use random.choice(list)
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

      self.update(state, action, successor, self.getValue(state,action))
      print "choosing action"
      print action
      return action
  def getQValue(self, gameState, action):
    return self.qValues[(gameState,action)]

  def computeActionFromQValues(self, state):
      actionList=state.getLegalActions(self.index)
      bestAction=None
      bestValue=None
      for action in actionList:
        tempValue=self.getQValue(state,action)

        if tempValue > bestValue or bestValue == None or bestAction == Stop:
          bestValue=tempValue
          bestAction=action

      return bestAction
  def update(self, state, action, nextState, reward):
      """
        The parent class calls this to observe a
        state = action => nextState and reward transition.
        You should do your Q-Value update here

        NOTE: You should never call this function,
        it will be called on your behalf
      """
      "Compute the sample, then update the Q-Value"
      sample=(reward+self.discount*self.getValue(nextState,action))
      self.qValues[(state, action)]=(1-self.alpha)*self.qValues[(state,action)] + self.alpha*sample

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

  def getValue(self, state,action):
    """
    This function is tricky. It evaluates the current state.
    Things incorporated:
    -Living reward
    -food award
    -go further away from enemy award
    """
    successor = self.getSuccessor(state, action)
    myState = successor.getAgentState(self.index)
    print "Kenneth"
    if (myState.isPacman):
      enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
      invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
      if len(invaders) > 0:
        dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
        minDist = min(dists)
      enemyDistScore=0#1.0/(minDist*-1)

      foodList = self.getFood(successor).asList()
      # Compute distance to the nearest food

      if len(foodList) > 0: # This should always be True,  but better safe than sorry
        myPos = successor.getAgentState(self.index).getPosition()
        minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      foodDistScore=1.0/minDistance

      return (foodDistScore+foodList)
    else:
      successor = self.getSuccessor(state, action)


      enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
      invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
      if len(invaders) > 0:
        dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
        minDist = min(dists)
        return -1*minDist
      else:
        foodList = self.getFood(successor).asList()
        # Compute distance to the nearest food

        if len(foodList) > 0: # This should always be True,  but better safe than sorry
          myPos = successor.getAgentState(self.index).getPosition()
          minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
        return -1*minDistance

