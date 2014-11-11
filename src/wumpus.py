#! /usr/bin/env python3

from __future__ import print_function

import sys
import random

from enumeration import Goal, Status, Action
from entity import Room, Agent, Knowledge, Cave
from knowledge import perceive, tell, update, ask



def print_intro():
  print('Hunt the Wumpus')
  print('MIT License (MIT)')
  print('Copyright (c) 2014 gliderkite\n')


def print_actions():
  print('1) Move forward')
  print('2) Turn left')
  print('3) Turn right')
  print('4) Grab')
  print('5) Shoot')


def print_perceptions(perceptions):
  wumpus, pit, gold = perceptions
  if wumpus == Status.Present:
    print('You perceived a stench.')
  if pit == Status.Present:
    print('You perceived a breeze.')
  if gold == Status.Present:
    print('You perceived a glitter.')
  if perceptions == (Status.Absent,) * 3:
    print('No perceptions.')
  print()


def parse_action(action):
  if action == 1:
    return Action.Move, (0,)
  elif action == 2:
    return Action.Turn, -1
  elif action == 3:
    return Action.Turn, 1
  elif action == 4:
    return Action.Grab, None
  elif action == 5:
    return Action.Shoot, None


def print_cave(loc):
  print(' __________________')
  y = 0
  while y < 4:
    x = 0
    while x < 4:
      print('|_X_|' if (x, y) == loc else '|___|', end='')
      x += 1
    print()
    y += 1
  print()



if __name__ == '__main__':
  # init seed
  if '-seed' in sys.argv:
    seed = int(sys.argv[sys.argv.index('-seed') + 1])
    random.seed(seed)
  # define entities
  cave = Cave()
  kb = Knowledge()
  agent = Agent()
  # display introduction
  print_intro()
  # run the game
  while True:
    #print('Cave:\n{}\n'.format(cave))
    print('Agent:\n{}'.format(agent))
    print_cave(agent.location)
    # perceive in current location
    perceptions = perceive(cave, agent.location)
    if perceptions is None:
      print('You died.')
      break
    #print('Perceptions:\n{}\n'.format(perceptions))
    print_perceptions(perceptions)
    if '-ai' in sys.argv:
      tell(kb, perceptions, agent.location)
      #print('Knowledge:\n{}\n'.format(kb))
      update(kb, agent.location)
      #print('Knowledge updated:\n{}\n'.format(kb))
      goal = Goal.SeekGold if not agent.has_gold else Goal.BackToEntry
      action = ask(kb, agent.location, agent.direction, goal)
      print('Action:\n{} {}\n'.format(*action))
      input('Next?')
    else:
      print_actions()
      action = int(input('Choice? '))
      print()
      action = parse_action(action)
    # perform the action
    if agent.perform(action, cave, kb):
      print('You perceived a scream.\n')
    # check if the game is over
    if agent.has_gold and agent.location == (0, 0):
      print_cave(agent.location)
      print('You win!')
      break
