#! /usr/bin/env python3


import random
import queue
import sys




# values used to index the array status of each cell
WUMPUS, RAVINE, GOLD = 0, 1, 2

# value used to denote a cell status
PRESENT, ABSENT, PROBABLE, UNKNOWN = 1, 0, 2, -1

# delta used to move the ant and reach its neighbors (clockwise)
DELTA = (0, -1), (1, 0), (0, 1), (-1, 0)

# value used to denote an agent
LOCATION, DIRECTION, HAS_GOLD = 0, 1, 2




def is_safe(cell, danger=None):
  """Returns True if the cell doesn't contains neither the Wumpus nor a ravine.
  Otherwise returns False.
  If the danger is specified check only if the agent is protected against the
  given danger."""
  if danger is None:
    return cell[WUMPUS] == ABSENT and cell[RAVINE] == ABSENT
  else:
    return cell[danger] == ABSENT


def is_dangerous(cell, danger=None):
  """Returns True if the cell may contain the Wumpus or a ravine.
  Otherwise returns False.
  If the danger is specified check only if the agent may be hurted by the given
  danger."""
  if danger == None:
    return cell[WUMPUS] == PROBABLE or cell[RAVINE] == PROBABLE
  else:
    return cell[danger] == PROBABLE


def is_deadly(cell, danger=None):
  """Returns True if the cell contains the Wumpus or a ravine.
  Otherwise returns False.
  If the danger is specified check only if the agent will be hurted by the given
  danger."""
  if danger == None:
    return cell[WUMPUS] == PRESENT or cell[RAVINE] == PRESENT
  else:
    return cell[danger] == PRESENT


def is_unexplored(cell):
  """Returns True is the cell was not explored yet.
  That is: the agent don't known if there is gold there."""
  return cell[GOLD] == UNKNOWN


def is_explored(cell):
  """Returns True is the cell was explored.
  That is: the agent known if there is gold there."""
  return cell[GOLD] == ABSENT or cell[GOLD] == PRESENT


def cells(kb, condition=None):
  """Returns a generator of cells indexes that comply with the condition."""
  y = 0
  for row in kb:
    x = 0
    for c in row:
      if condition is None or condition(c):
        yield x, y
      x += 1
    y += 1


def unexplored(kb):
  """Returns a generator of unexplored cells indexes."""
  return cells(kb, is_unexplored)


def explored(kb):
  """Returns a generator of already explored cells indexes."""
  return cells(kb, is_explored)
  




def place_wumpus(world, available):
  """Places a Wumpus in the world.
  Chooses a random cell between those available."""
  x, y = random.choice(available)
  world[x][y][WUMPUS] = PRESENT


def place_gold(world, available):
  """Places a gold ingot in the world.
  Chooses a random cell between those available."""
  x, y = random.choice(available)
  world[x][y][GOLD] = PRESENT


def place_ravines(world, available, p=0.2):
  """Places ravines in the world.
  The probability that a cell contains a ravine is the one given."""
  for x, y in available:
    if random.random() <= p:
      world[x][y][RAVINE] = PRESENT


def neighbors(location, size=(4, 4)):
  x, y = location
  width, height = size
  #  above cell
  if y - 1 >= 0:
    yield x, y - 1
  # right cell
  if x + 1 < width:
    yield x + 1, y
  # below cell
  if y + 1 < height:
    yield x, y + 1
  # left cell
  if x - 1 >= 0:
    yield x - 1, y





def neighbor(location, direction, size=(4, 4)):
  """Get the neighbor according to the given location and direction."""
  x, y = agent[LOCATION]
  width, height = size
  dx, dy = DELTA[direction]
  # check if the neighbor is inside the world
  if 0 <= x + dx < width and 0 <= y + dy < height:
    return x + dx, y + dy


def turn(agent, steps):
  """Turns the agent changing its direction.
  There are 4 possible directions (as the number of neighboring cells not diagonal).
  Negative steps represent a counterclockwise rotation; otherwise positive steps
  represent a clockwise rotation.
  """
  agent[DIRECTION] = (agent[DIRECTION] + steps) % 4


def turn_counterclockwise(agent):
  """Turns the agent counterclockwise."""
  turn(agent, -1)


def turn_clockwise(agent):
  """Turns the agent clockwise."""
  turn(agent, 1)


def move_forward(agent):
  """Moves the agent forword according to its current location and direction."""
  agent[LOCATION] = neighbor(agent[LOCATION], agent[DIRECTION])


def turn_steps(source, direction, destination):
  """Computes the number of steps needed to have the destination cell ahead."""
  
  # check if source and destination are neighbors
  if not source in neighbors(destination):
    raise ValueError('Source and Destination must be neighbors.')
  
  # computes the delta as locations difference
  delta = tuple([a - b for a, b in zip(destination, source)])
  return DELTA.index(delta) - direction




def safe_path_rec(kb, location, goal, path, visited):
  """Depth-first search that builds a safe and already explore dpath to goal."""
  
  # check if the location and the goal are the same
  if location == goal:
    return True

  # generator of explored (but not yet visited by the search) neighbors
  neighborhood = ((x, y) for x, y in neighbors(location) if (x, y) not in visited 
                  and (is_explored(kb[y][x]) or (x, y) == goal))

  # iterate over each neighbor
  for n in neighborhood:
    # add the node to the path
    path.append(n)
    visited.add(n)
    # recursive call
    if safe_path_rec(kb, n, goal, path, visited):
      return True
    # this node does not lead to the goal
    visited.remove(n)
    path.remove(n)


def safe_path(kb, location, goal):
  """Returns a safe path to goal."""

  # check if the location and the goal are the same
  if location == goal:
    return tuple()

  path = [location]
  visited = set()
  visited.add(location)

  # implement a depth-first search
  safe_path_rec(kb, location, goal, path, visited)

  # return the path or None if the path wasn't found
  if len(path) > 0:
    return tuple(path)


def path_to_actions(agent, path):
  """Gets the list of actions that an agent has to perform to follow the path."""
  
  # check the presence of a valid path
  if path is None or not path or path[0] != agent[LOCATION]:
    raise ValueError('Invalid path')
  
  actions = []
  direction = agent[DIRECTION]

  # follow the path and compute the steps needed to turn and then move forword
  # the agent in order to reach the last location of the path
  i = 0
  while i < len(path) - 1:
    steps = turn_steps(path[i], direction, path[i + 1])
    actions.append(steps)
    direction = (direction + steps) % 4
    i += 1
  
  return tuple(actions)




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


def perceive(kb, location):
  """Returns a tuple containing the perceptions accorging to the knowledge
  and the given location.
  Returns None if the agent has been killed by the Wumpus or falling in a ravine."""
  
  x, y = location
  
  # check there is a ravine or the Wumpus in this cell (if yes no perceptions)
  if kb[y][x][RAVINE] == PRESENT or kb[y][x][WUMPUS] == PRESENT:
    return None
  
  perceptions = [0] * 3
  
  # look neighboring cells to compute perceptions
  for cell in [kb[y][x] for x, y in neighbors(location)]:
    
    # check if the wumpus is here
    if cell[WUMPUS] == PRESENT:
      perceptions[WUMPUS] = PRESENT
    elif cell[WUMPUS] == PROBABLE and perceptions[WUMPUS] != PRESENT:
      perceptions[WUMPUS] = PROBABLE
    
    # check if ravines are here
    if cell[RAVINE] == PRESENT:
      perceptions[RAVINE] = PRESENT
    elif cell[RAVINE] == PROBABLE and perceptions[RAVINE] != PRESENT:
      perceptions[RAVINE] = PROBABLE
  
  # check if the gold is in this cell
  if kb[y][x][GOLD] == PRESENT:
    perceptions[GOLD] = PRESENT  
  
  return tuple(perceptions)


def tell(kb, perceptions, location):
  """Update knowledge according to the given perception and location."""
  
  x, y = location
  # the agent is alive and perceived something therefore:
  # there are no ravines or the Wumpus in this cell
  kb[y][x][WUMPUS] = kb[y][x][RAVINE] = ABSENT

  # check if the Wumpus location is identified with certainty
  #wloc = any(kb[y][x] for x, y in neighbors(location) if is_deadly(kb[y][x], WUMPUS))

  # iterate over not safe neighboring cells
  for c in (kb[y][x] for x, y in neighbors(location) if not is_safe(kb[y][x])):
    
    # get near wumpus and ravines
    nw = [kb[y][x] for x, y in neighbors(location) if not is_safe(kb[y][x], WUMPUS)]
    nr = [kb[y][x] for x, y in neighbors(location) if not is_safe(kb[y][x], RAVINE)]
    
    if c[WUMPUS] != ABSENT:
      # parse wumpus perception
      if not perceptions[WUMPUS]:
        c[WUMPUS] = ABSENT
      elif perceptions[WUMPUS] == PROBABLE:
        # the Wumpus can't move, therefore if there is the probability to have
        # the Wumpus the same probability has to be in others neighbors, otherwise
        # the current cell is the one with the Wumpus
        if len(nw) == 1:
          c[WUMPUS] = PRESENT
      elif c[WUMPUS] != PRESENT:
        c[WUMPUS] = PRESENT if len(nw) == 1 else PROBABLE

    if c[RAVINE] != ABSENT:
      # parse ravine perception
      if not perceptions[RAVINE]:
        c[RAVINE] = ABSENT
      elif perceptions[RAVINE] == PROBABLE:
        # ravines can't move, therefore if there is the probability to have a
        # ravine the same probability has to be in others neighbors, otherwise
        # the current cell is the one with the ravine
        if len(nr) == 1:
          c[RAVINE] = PRESENT
      elif c[RAVINE] != PRESENT:
        c[RAVINE] = PRESENT if len(nr) == 1 else PROBABLE
  
  # parse gold perception
  kb[y][x][GOLD] = ABSENT if not perceptions[GOLD] else PRESENT


def update(kb, location):
  """Update the knowledge."""

  # update the knowledge according to all the already explored cells
  for loc in [l for l in explored(kb) if l != location]:
    perceptions = perceive(kb, loc)
    tell(kb, perceptions, loc)


def ask(agent, kb):
  """Returns an action according to the current state of the agent knowledge."""
  # check if this room contains the gold
  x, y = agent[LOCATION]
  if kb[y][x][GOLD] == PRESENT:
    agent[GOLD] = True
  # list of actions to perform
  actions = []

  # check if the agent is seeking gold
  if not agent[GOLD]:
    # get the first neighbor cell safe and unexplored (if any)
    safe = next(((x, y) for x, y in neighbors(agent[LOCATION]) 
                if is_safe(kb[y][x]) and is_unexplored(kb[y][x])), None)
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

  else:
    # back to the entry
    path = safe_path(kb, agent[LOCATION], (0, 0))
    return path_to_actions(agent, path)

  # can't find an action
  return None
    

def perform(agent, actions):
  """Performs a list of actions."""
  for steps in actions:
    if steps:
      turn(agent, steps)
    move_forward(agent)




def display(matrix):
  i = 0
  while i < 4:
    j = 0
    while j < 4:
      print(matrix[i][j], end='\t')
      j += 1
    print()
    i += 1



if __name__ == '__main__':
  random.seed(int(sys.argv[1]))
  # define the world and the cell available for ravines and the wumpus
  world = [[[ABSENT] * 3 for x in range(4)] for y in range(4)]
  available = [(x, y) for x in range(0, 4) for y in range(0, 4) if (x, y) != (0, 0)]
  #print(available)
  # agent location, direction and gold
  agent = [(0, 0), 1, False]
  # agent knowledge base
  known = [[[UNKNOWN] * 3 for x in range(4)] for y in range(4)]
  # the entry if safe
  known[0][0] = [ABSENT] * 3
  # place initial entities (wumpus, gold and ravines)
  place_wumpus(world, available)
  place_gold(world, available)
  place_ravines(world, available)

  while not agent[GOLD]:
    display(world)
    print()
    print('Agent:', end=' ')
    print(agent)
    p = perceive(world, agent[LOCATION])
    if p is None:
      print('The agent died')
      break
    print('Perception:', end=' ')
    print(p)
    print()
    tell(known, p, agent[LOCATION])
    display(known)
    print()
    print('Update knowledge:')
    update(known, agent[LOCATION])
    display(known)
    print()
    actions = ask(agent, known)
    print('Actions:', end=' ')
    print(actions)
    print()
    input('Next?')
    perform(agent, actions)


  print(agent)