#! /usr/bin/env python


import random

from enumeration import Status, Entity, Action, Goal
from motion import neighbors, spins, known_path, path_to_spins



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
  for room in [kb[l] for l in neighbors(loc)]:
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
  near = [kb[l] for l in neighbors(loc)]
  # iterate over not safe neighboring rooms
  for room in (r for r in near if not r.is_safe()):
    # check how many neighboring rooms may contain the Wumpus and then pits
    p = len([r for r in near if not r.is_safe(Entity.Pit)])
    # parse Wumpus perception
    if room.wumpus != Status.Absent:
      if wumpus == Status.Absent:
        room.wumpus = Status.Absent
      elif wumpus == Status.LikelyPresent:
        # if in all neighboring rooms there is only one Wumpus, since this
        # is the room where the Wumpus was parceived, ans since the Wumpus can't
        # move, then the Wumpus has to be right in this room
        if len([r for r in near if r.is_dangerous(Entity.Wumpus)]) == 1:
          room.wumpus = Status.Present
      elif room.wumpus == Status.Unknown:
        if any(r for r in near if r.is_deadly(Entity.Wumpus)):
          # the agent knows the Wumpus location -> it can't be in this room
          room.wumpus = Status.Absent
        elif all(r for r in near if r.is_safe(Entity.Wumpus) and r != room):
          # all others neighbors are safe -> the Wumpus must be in this room
          room.wumpus = Status.Present
        else:
          room.wumpus = Status.LikelyPresent
    # parse pit perception
    if room.pit != Status.Absent:
      if pit == Status.Absent:
        room.pit = Status.Absent
      elif pit == Status.LikelyPresent:
        # if in all neighboring rooms there is only one pit, since this
        # is the room where the pit was parceived, ans since a pit can't
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
  for l in [x for x in kb.explored]:
    tell(kb, perceive(kb, l), l)


def ask(kb, loc, direction, goal):
  """Returns an action according to the current state of the knowledge.
  The action is a tuple: the first element is the type of the action, while
  the second element is a list of movement if the type is Action.Move,
  otherwise is None."""
  # if the agent is seeking gold
  if goal == Goal.SeekGold:
    # check if this room contains the gold
    if kb[loc].gold == Status.Present:
      return Action.TakeGold, None
    # get the first neighbor room safe and unexplored (if any)
    state = lambda r: r.is_safe() and r.is_unexplored
    dest = next((l for l in neighbors(loc) if state(kb[l])), None)
    if dest:
      return Action.Move, (spins(loc, direction, dest),)
    # get any room safe and unexplored
    dest = next((l for l in kb.unexplored if kb[l].is_safe()), None)
    if dest:
      path = known_path(kb, loc, dest)
      return Action.Move, path_to_spins(path, direction)
    # get a random unexplored room that may contain the Wumpus but no pits
    state = lambda r: r.is_safe(Entity.Pit) and r.is_dangerous(Entity.Wumpus)
    rooms = [l for l in kb.unexplored if state(kb[l])]
    if rooms:
      print(rooms)
      raise NotImplementedError
    # get a random unexplored room that may contain a ravine but not the Wumpus
    state = lambda r: r.is_safe(Entity.Wumpus) and r.is_dangerous(Entity.Pit)
    rooms = [l for l in kb.unexplored if state(kb[l])]
    if rooms:
      dest = random.choice(rooms)
      path = known_path(kb, loc, dest)
      return Action.Move, path_to_spins(path, direction)
    # get a random unexplored room that may contain either the Wumpus or pits
    rooms = [l for l in kb.unexplored if kb[l].is_dangerous()]
    if rooms:
      print(rooms)
      raise NotImplementedError
  elif goal == Goal.BackToEntry:
    # back to the entry
    path = known_path(kb, loc, (0, 0))
    return Action.Move, path_to_spins(path, direction)
  # unable to find an action
  return None
    
