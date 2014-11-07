#! /usr/bin/env python


import enum

from motion import neighbors
from entity import Status, Entity



class Action(enum.Enum):
  """Enumeration of agent feasible actions."""
  Move = 0
  Shoot = 1
  TakeGold = 2


class Goal(enum.Enum):
  """Enumerates agent's goals."""
  SeekGold = 0
  BackToEntry = 1



def perceive(kb, loc):
  """Returns a tuple containing the agent local perceptions.
  Returns None if the agent has been killed by the Wumpus or falling in a pit."""
  # check if there is a pit or the Wumpus in this cell
  if kb[loc].pit == Status.Present or kb[loc].wumpus == Status.Present:
    # the agent has been killed and there are no perceptions
    return None
  # build perceptions
  wumpus, pit, gold = (Status.Absent,) * 3
  # look neighboring cells to update perceptions
  for room in [kb[loc] for x, y in neighbors(loc)]:
    # check if the wumpus is in this room
    if room.wumpus == Status.Present:
      wumpus = Status.Present
    elif room.wumpus == Status.LikelyPresent and wumpus != Status.Present:
      wumpus = Status.LikelyPresent
    # check if pits are in this room
    if room.pit == Status.Present:
      pit = Status.Present
    elif room.pit == Status.LikelyPresent and pit != Status.Present:
      pit = Status.LikelyPresent
  # check if the gold is in this cell
  if kb[loc].gold == Status.Present:
    gold = Status.Present  
  # returns perceptions as tuple
  return wumpus, pit, gold


def tell(kb, perceptions, loc):
  """Update knowledge according to the given perception and location."""
  # the agent is alive and perceived something therefore:
  # there are neither pits nor the Wumpus in this room
  kb[loc].wumpus = kb[loc].pit = Status.Absent
  wumpus, pit, gold = perceptions
  # iterate over not safe neighboring rooms
  for room in (kb[l] for l in neighbors(loc) if not kb[l].is_safe()):
    # check how many neighboring rooms may contain the Wumpus and then pits
    w = len([kb[l] for l in neighbors(loc) if not kb[l].is_safe(Entity.Wumpus)])
    p = len([kb[l] for l in neighbors(loc) if not kb[l].is_safe(Entity.Pit)])
    # parse Wumpus perception
    if room.wumpus != Status.Absent:
      if wumpus == Status.Absent:
        room.wumpus = Status.Absent
      elif wumpus == Status.LikelyPresent:
        # if in all neighboring rooms there is only one Wumpus, since this
        # is the room where the Wumpus was parceived, ans since the Wumpus can't
        # move, then the Wumpus has to be right in this room
        if w == 1:
          room.wumpus = Status.Present
      elif room.wumpus == Status.Unknown:
        room.wumpus = Status.Present if w == 1 else Status.LikelyPresent
    # parse pit perception
    if room.pit != Status.Absent:
      if pit == Status.Absent:
        room.pit = Status.Absent
      elif pit == Status.LikelyPresent:
        # if in all neighboring rooms there is only one pit, since this
        # is the room where the pit was parceived, ans since the pit can't
        # move, then the pit has to be right in this room
        if p == 1:
          room.pit = Status.Present
      elif room.pit == Status.Unknown:
        room.pit = Status.Present if p == 1 else Status.LikelyPresent
  # parse gold perception
  kb[loc].gold = gold


def update(kb, loc):
  """Update the knowledge."""
  # update the knowledge according to all the already explored cells
  for l in [x for x in kb.explored() if x != loc]:
    tell(kb, perceive(kb, l), l)


def ask(kb, loc, goal):
  """Returns an action according to the current state of the knowledge.
  The action is a tuple: the first element is the type of the action, while
  the second element is a list of movement if the type is Action.Move,
  otherwise is None."""
  # if the agent is seeking gold
  if goal == Goal.SeekGold:
    # check if this room contains the gold
    if kb[loc].gold == Status.Present:
      return Action.TakeGold, None
    # list of actions to perform
    actions = []
    # get the first neighbor cell safe and unexplored (if any)
    safe_and_unexplored = lambda r: r.is_safe() and r.is_unexplored
    safe = next(l for l in neighbors(loc) if safe_and_unexplored(kb[l]), None)
    if safe:
      actions.append(turn_steps(agent[LOCATION], agent[DIRECTION], safe))
      return tuple(actions)
    # get the first cell safe and unexplored
    safe = next(((x, y) for x, y in unexplored(kb) if is_safe(kb[y][x])), None)
    if safe:
      path = safe_path(kb, agent[LOCATION], safe)
      return path_to_actions(agent, path)
    # get a random unexplored cell that may contain the Wumpus but no ravines
    unsafe = [(x, y) for x, y in unexplored(kb) if is_safe(kb[y][x], RAVINE) 
              and is_dangerous(kb[y][x], WUMPUS)]
    if unsafe:
      print(unsafe)
      #raise NotImplementedError()
    # get a random unexplored cell that may contain a ravine but no the Wumpus
    unsafe = [(x, y) for x, y in unexplored(kb) if is_safe(kb[y][x], WUMPUS)
              and is_dangerous(kb[y][x], RAVINE)]
    if unsafe:
      choice = random.choice(unsafe)
      actions.append(turn_steps(agent[LOCATION], agent[DIRECTION], choice))
      return tuple(actions)
    # get a random unexplored cell that may contain either the Wumpus or ravines
    unsafe = [(x, y) for x, y in unexplored(kb) if is_dangerous(kb[y][x])]
    if unsafe:
      print(unsafe)
      raise NotImplementedError()
  elif goal == Goal.BackToEntry:
    # back to the entry
    path = safe_path(kb, agent[LOCATION], (0, 0))
    return path_to_actions(agent, path)
  # can't find an action
  return None
    
