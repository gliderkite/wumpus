#! /usr/bin/env python3


import sys
import random

from enumeration import Goal
from entity import Room, Agent, Knowledge, Cave
from knowledge import perceive, tell, update, ask




def shoot(world, location, direction, size=(4, 4)):
  
  x, y = location
  width, height = size

  if direction == 0:
    # follow above cells
    i = y
    while i >= 0:
      if world[i][x][WUMPUS] == PRESENT:
        return True
      i -= 1
  elif direction == 1:
    # follow right cells
    i = x
    while i < width:
      if world[y][i][WUMPUS] == PRESENT:
        return True
      i += 1
  elif direction == 2:
    # follow below cells
    i = y
    while i < height:
      if world[i][x][WUMPUS] == PRESENT:
        return True
      i += 1
  else:
    # follow left cells
    i = x
    while i >= 0:
      if world[y][i][WUMPUS] == PRESENT:
        return True
      i -= 1

  # the arrow doesn't hit the Wumpus
  return False



if __name__ == '__main__':
  
  # init random seed
  random.seed(int(sys.argv[1]))
  # define entities
  cave = Cave()
  kb = Knowledge()
  agent = Agent()

  # while the agent is seeking gold
  while True: 

    print('Cave:\n{}\n'.format(cave))
    print('Agent:\n{}\n'.format(agent))

    perceptions = perceive(cave, agent.location)
    if perceptions is None:
      print('The agent died\n')
      break
    print('Perceptions:\n{}\n'.format(perceptions))

    tell(kb, perceptions, agent.location)
    print('Knowledge:\n{}\n'.format(kb))

    update(kb, agent.location)
    print('Knowledge updated:\n{}\n'.format(kb))

    goal = Goal.SeekGold if not agent.has_gold else Goal.BackToEntry
    action = ask(kb, agent.location, agent.direction, goal)
    print('Action:\n{} {}\n'.format(*action))

    input('Next?')
    agent.perform(action, cave)

    if agent.has_gold and agent.location == (0, 0):
      break

  print('Game Over')