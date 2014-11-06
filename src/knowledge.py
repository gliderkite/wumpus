#! /usr/bin/env python


from motion import neighbors
from entity import Status, Entity



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



def update(kb, location):
  """Update the knowledge."""
  # update the knowledge according to all the already explored cells
  for loc in [l for l in explored(kb) if l != location]:
    perceptions = perceive(kb, loc)
    tell(kb, perceptions, loc)

