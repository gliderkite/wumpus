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
LOCATION, DIRECTION, HAS_GOLD, IS_ALIVE = 0, 1, 2, 3




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
  delta = tuple([a - b for a, b in zip(destination, source)])
  return DELTA.index(delta) - direction





def unexplored(kb):
  """Returns a generator of indexes of unexplored cells."""
  y = 0
  for row in kb:
    x = 0
    for c in row:
      if is_unexplored(c):
        yield x, y
      x += 1
    y += 1


def safe_path(location, goal, kb):
  # check if the location and the goal are the same
  if location == goal:
    return tuple()
  # build the FIFO data structure and the explores set of locations
  explored = set()
  path = []
  fifo = queue.Queue()
  fifo.put(location)
  # while there is an unexplored neighbor
  while not fifo.empty():
    loc = fifo.get()
    explored.add(loc)
    path.append(loc)
    # for each neighboring safe cell
    for x, y in ((x, y) for x, y in neighbors(loc) if (x, y) not in explored
                  and is_safe(kb[y][x])):
      # check if the goal is reached
      if (x, y) == goal:
        path.append(goal)
        return tuple(path)
      elif not is_unexplored(kb[y][x]):
        fifo.put((x, y))
  # path not found
  return None


def path_to_actions(agent, path):
  """Gets the list of actions that an agent has to perform to follow the path."""
  # check the presence of a valid path
  if path is None or not path or path[0] != agent[LOCATION]:
    raise ValueError('Invalid path')
  actions = []
  direction = agent[DIRECTION]
  i = 0
  # follow the path and compute the steps needed to turn and then move forword
  # the agent in order to reach the last location of the path
  while i < len(path) - 1:
    steps = turn_steps(path[i], direction, path[i + 1])
    actions.append(steps)
    direction = (direction + steps) % 4
    i += 1
  return tuple(actions)





def perceive(knowledge, location):
  """Returns a tuple containing the perceptions accorging to the knowledge
  and the given location.
  Returns None if the agent has been killed by the Wumpus or falling in a ravine."""
  x, y = location
  # check there is a ravine or the Wumpus in this cell (if yes no perceptions)
  if knowledge[y][x][RAVINE] == PRESENT or knowledge[y][x][WUMPUS] == PRESENT:
    return None
  perceptions = [0] * 3
  # look neighboring cells to compute perceptions
  for cell in [knowledge[y][x] for x, y in neighbors(location)]:
    # check if the wumpus or ravines are present
    if cell[WUMPUS] == PRESENT:
      perceptions[WUMPUS] = cell[WUMPUS]
    if cell[RAVINE] == PRESENT:
      perceptions[RAVINE] = PRESENT
  # check if the gold is in this cell
  if knowledge[y][x][GOLD] == PRESENT:
    perceptions[GOLD] = PRESENT  
  return tuple(perceptions)


def tell(agent, kb, perceptions):
  """Update agent knowledge base according to the given perception."""
  loc = agent[LOCATION]
  x, y = loc
  # the agent is alive and perceived something therefore:
  # there are no ravines or the Wumpus in this cell
  kb[y][x][WUMPUS] = kb[y][x][RAVINE] = ABSENT
  # iterate over not safe neighboring cells
  for c in [kb[y][x] for x, y in neighbors(loc) if not is_safe(kb[y][x])]:
    # parse wumpus perception
    c[WUMPUS] = ABSENT if not perceptions[WUMPUS] else PROBABLE
    # parse ravine perception
    c[RAVINE] = ABSENT if not perceptions[RAVINE] else PROBABLE
  # parse gold perception
  kb[y][x][GOLD] = ABSENT if not perceptions[GOLD] else PRESENT


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
      path = safe_path(agent[LOCATION], safe, kb)
      return path_to_actions(agent, path)
    # get a random unexplored cell that may contain the Wumpus but no ravines
    unsafe = [(x, y) for x, y in unexplored(kb) if is_safe(kb[y][x], RAVINE) 
              and is_dangerous(kb[y][x], WUMPUS)]
    if unsafe:
      print(unsafe)
      pass
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
      pass
  else:
    # back to the entry
    path = safe_path(agent[LOCATION], (0, 0), kb)
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
  kb = [[[UNKNOWN] * 3 for x in range(4)] for y in range(4)]
  # the entry if safe
  kb[0][0] = [ABSENT] * 3
  # place initial entities (wumpus, gold and ravines)
  place_wumpus(world, available)
  place_gold(world, available)
  place_ravines(world, available)

  display(world)
  print()

  while not agent[GOLD]:
    print('Agent:', end=' ')
    print(agent)
    p = perceive(world, agent[LOCATION])
    if p is None:
      print('The agent died')
      break
    print('Perception:', end=' ')
    print(p)
    print()
    tell(agent, kb, p)
    display(kb)
    print()
    input('Next?')
    actions = ask(agent, kb)
    perform(agent, actions)

  print(agent)