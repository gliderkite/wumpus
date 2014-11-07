#! /usr/bin/env python


import random

from enumeration import Status, Entity, Action
from motion import turn, move_forward




class Room:
  """Represents a single room of the cave."""

  def __init__(self, wumpus=Status.Absent, pit=Status.Absent, gold=Status.Absent):
    """Initializes the Room status.
    By default the room is safe and without gold."""
    self.wumpus = wumpus
    self.pit = pit
    self.gold = gold

  def __repr__(self):
    """Returns the string representation of this instance."""
    return str([self.wumpus.value, self.pit.value, self.gold.value])


  def is_safe(self, danger=None):
    """Returns True if the room doesn't contains neither the Wumpus nor a pit."""
    if danger is None:
      return self.wumpus == Status.Absent and self.pit == Status.Absent
    if danger == Entity.Wumpus:
      return self.wumpus == Status.Absent
    if danger == Entity.Pit:
      return self.pit == Status.Absent
    # invalid danger argument
    raise ValueError
  
  def is_dangerous(self, danger=None):
    """Returns True if the room may contain either the Wumpus or a pit."""
    if danger is None:
      return self.wumpus == Status.LikelyPresent or self.pit == Status.LikelyPresent
    if danger == Entity.Wumpus:
      return self.wumpus == Status.LikelyPresent
    if danger == Entity.Pit:
      return self.pit == Status.LikelyPresent
    # invalid danger argument
    raise ValueError

  def is_deadly(self, danger=None):
    """Returns True if the room contains either the Wumpus or a pit."""
    if danger is None:
      return self.wumpus == Status.Present or self.pit == Status.Present
    if danger == Entity.Wumpus:
      return self.wumpus == Status.Present
    if danger == Entity.Pit:
      return self.pit == Status.Present
    # invalid danger argument
    raise ValueError

  @property
  def is_explored(self):
    """Returns True is the room was already explored."""
    assert self.gold != Status.LikelyPresent
    return self.gold != Status.Unknown

  @property
  def is_unexplored(self):
    """Returns True is the room is not explored."""
    return not self.is_explored



class Agent:
  """Represents the agent exploring the cave."""

  def __init__(self):
    """Initializes the agent with default parameters."""
    self.location = (0, 0)
    self.direction = 1
    self.has_gold = False
    self.has_arrow = True

  def __repr__(self):
    """Returns the string representation of this instance."""
    return str([self.location, self.direction, self.has_gold, self.has_arrow])
  

  def perform(self, action, cave):
    """Performs an action."""
    kind, rotations = action
    if kind == Action.Move:
      # moves the agent
      for steps in rotations:
        self.direction = turn(self.direction, steps)
        self.location = move_forward(self.location, self.direction)
    elif kind == Action.Shoot:
      pass
    elif kind == Action.TakeGold:
      cave[self.location].gold = Status.Absent
      self.has_gold = True



class Knowledge:
  """Represents the agent's knowledge about the cave."""
  
  def __init__(self, size=(4, 4)):
    """Initializes a new instance of the Knowledge class."""
    self.size = size
    # initially the agent knowns nothing
    w, h = self.size
    status = Status.Unknown, Status.Unknown, Status.Unknown
    self._rooms = [[Room(*status) for x in range(w)] for y in range(h)]
    # the cave entry is safe and without gold
    self._rooms[0][0] = Room()

  def __repr__(self):
    """Returns the string representation of this instance."""
    width, height = self.size
    plant = ''
    y = 0
    while y < height:
      x = 0
      while x < width:
        plant += '{}\t'.format(self._rooms[y][x])
        x += 1
      plant += '\n' if y != height - 1 else ''
      y += 1
    return plant

  def __getitem__(self, location):
    """Gets the room in location."""
    x, y = location
    return self._rooms[y][x]

  def __setitem__(self, location, value):
    """Sets the room in location."""
    x, y = location
    self._rooms[y][x] = value


  def rooms(self, condition=None):
    """Returns a generator of cells indexes that comply with the condition."""
    y = 0
    for path in self._rooms:
      x = 0
      for room in path:
        if condition is None or condition(room):
          yield x, y
        x += 1
      y += 1

  @property
  def explored(self):
    """Returns a generator of indexes of already explored rooms."""
    return self.rooms(lambda r: r.is_explored)

  @property
  def unexplored(self):
    """Returns a generator of indexes of unexplored rooms."""
    return self.rooms(lambda r: not r.is_explored)



class Cave(Knowledge):
  """Represents the cave where the Wumpus lives."""

  def __init__(self, size=(4, 4)):
    """Initializes a new instance of the Cave class."""
    self.size = size
    # the cave contains a matrix of rooms
    w, h = self.size
    self._rooms = [[Room() for x in range(w)] for y in range(h)]
    unsafe = [(x, y) for x in range(w) for y in range(h) if (x, y) != (0, 0)]
    # plcae the Wumpus
    x, y = random.choice(unsafe)
    self._rooms[y][x].wumpus = Status.Present
    # place the gold
    x, y = random.choice(unsafe)
    self._rooms[y][x].gold = Status.Present
    # place pits (with probability 0.2)
    for x, y in unsafe:
      if random.random() <= 0.2:
        self._rooms[y][x].pit = Status.Present

  