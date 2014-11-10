#! /usr/bin/env python3


import sys
import random

from enumeration import Goal, Entity
from entity import Room, Agent, Knowledge, Cave
from knowledge import perceive, tell, update, ask



if __name__ == '__main__':
  
  deaths = 0
  n = 100 if len(sys.argv) == 1 else int(sys.argv[1]) + 1
  i = 0 if len(sys.argv) == 1 else int(sys.argv[1])
  while i < n:

    # init random seed
    #random.seed(i)
    # define entities
    cave = Cave()
    kb = Knowledge()
    agent = Agent()

    # while the agent is seeking gold
    while True: 

      if len(sys.argv) > 1:
        print('Cave:\n{}\n'.format(cave))
        print('Agent:\n{}\n'.format(agent))

      perceptions = perceive(cave, agent.location)
      if perceptions is None:
        if len(sys.argv) > 1:
          print('The agent died\n')
        #print(i, end=' ')
        deaths += 1
        break

      if len(sys.argv) > 1:
        print('Perceptions:\n{}\n'.format(perceptions))

      tell(kb, perceptions, agent.location)
      if len(sys.argv) > 1:
        print('Knowledge:\n{}\n'.format(kb))

      update(kb, agent.location)
      if len(sys.argv) > 1:
        print('Knowledge updated:\n{}\n'.format(kb))

      goal = Goal.SeekGold if not agent.has_gold else Goal.BackToEntry
      action = ask(kb, agent.location, agent.direction, goal)
      if len(sys.argv) > 1:
        print('Action:\n{} {}\n'.format(*action))

      if len(sys.argv) > 1:
        input('Next?')
      
      agent.perform(action, cave, kb)

      if agent.has_gold and agent.location == (0, 0):
        break

    if len(sys.argv) > 1:
      print('Game Over')
    i += 1

  print('Success rate:', (n - deaths) / n, '%')