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
    # parse Wumpus perception
    if room.wumpus != Status.Absent:
      if wumpus == Status.Absent:
        room.wumpus = Status.Absent
      elif wumpus == Status.LikelyPresent:
        # check if this is the only place where the Wumpus may be
        if len([r for r in near if r.is_dangerous(Entity.Wumpus)]) == 1:
          room.wumpus = Status.Present
      elif room.wumpus == Status.Unknown:
        if any(r.is_deadly(Entity.Wumpus) for r in near):
          # the agent knows the Wumpus location -> it can't be in this room
          room.wumpus = Status.Absent
        elif all(r.is_safe(Entity.Wumpus) for r in near if r != room):
          # all others neighbors are safe -> the Wumpus must be in this room
          room.wumpus = Status.Present
        else:
          room.wumpus = Status.LikelyPresent
    # parse pit perception
    if room.pit != Status.Absent:
      if pit == Status.Absent:
        room.pit = Status.Absent
      elif pit == Status.LikelyPresent:
        # check if this is the only place where the pit may be
        if len([r for r in near if r.is_dangerous(Entity.Pit)]) == 1:
          room.pit = Status.Present
      elif room.pit == Status.Unknown:
        if all(r.is_safe(Entity.Pit) for r in near if r != room):
          # all others neighbors are safe -> the pit must be in this room
          room.pit = Status.Present
        else:
          room.pit = Status.LikelyPresent
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
  or Shoot, otherwise None."""
  # if the agent is seeking gold
  if goal == Goal.SeekGold:
    # check if this room contains the gold
    if kb[loc].gold == Status.Present:
      return Action.Grab, None
    # get the first neighbor room safe and unexplored (if any)
    state = lambda r: r.is_safe() and r.is_unexplored
    dest = next((l for l in neighbors(loc) if state(kb[l])), None)
    if dest:
      return Action.Move, (spins(loc, direction, dest),)
    # get any room safe and unexplored (if the agent can reach it)
    state = lambda r, l: r.is_safe() and any(kb[x].is_explored for x in neighbors(l))
    dest = next((l for l in kb.unexplored if state(kb[l], l)), None)
    if dest:
      path = known_path(kb, loc, dest)
      return Action.Move, path_to_spins(path, direction)
    # get a neighboring room that (may) contain the Wumpus but no pits
    state = lambda r: r.is_safe(Entity.Pit) and r.is_unsafe(Entity.Wumpus)
    dest = next((l for l in neighbors(loc) if state(kb[l])), None)
    if dest:
      return Action.Shoot, spins(loc, direction, dest)
    # get a room that may contain the Wumpus but no pits
    state = lambda r: r.is_safe(Entity.Pit) and r.is_unsafe(Entity.Wumpus)
    dest = next((l for l in kb.unexplored if state(kb[l])), None)
    if dest:
      # get a neighbor explored cell
      dest = next((l for l in neighbors(dest) if kb[l].is_explored))
      path = known_path(kb, loc, dest)
      return Action.Move, path_to_spins(path, direction)
    # get a neighboring room that may contain the Wumpus
    state = lambda r: r.is_dangerous(Entity.Wumpus)
    dest = next((l for l in neighbors(loc) if state(kb[l])), None)
    if dest:
      return Action.Shoot, spins(loc, direction, dest)
    # get a random room that may contain a ravine
    rooms = [l for l in kb.unexplored if kb[l].is_dangerous(Entity.Pit)]
    if rooms:
      dest = random.choice(rooms)
      path = known_path(kb, loc, dest)
      return Action.Move, path_to_spins(path, direction)
    # get an unexplored cell
    dest = next((l for l in kb.unexplored), None)
    if dest:
      path = known_path(kb, loc, dest)
      return Action.Move, path_to_spins(path, direction)
  elif goal == Goal.BackToEntry:
    # back to the entry
    path = known_path(kb, loc, (0, 0))
    return Action.Move, path_to_spins(path, direction)
  # unable to find an action
  return None
