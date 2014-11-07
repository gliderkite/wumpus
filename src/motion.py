#! /usr/bin/env python


# delta used to move the agent and reach its neighbors
DELTA = (0, -1), (1, 0), (0, 1), (-1, 0)



def neighbors(location, size=(4, 4)):
  """Returns a generetor for the neighboring rooms."""
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
  x, y = location
  width, height = size
  dx, dy = DELTA[direction]
  # check if the neighbor is inside the cave
  if 0 <= x + dx < width and 0 <= y + dy < height:
    return x + dx, y + dy


def turn(direction, steps):
  """Returns the new direction."""
  return (direction + steps) % len(DELTA)


def move_forward(location, direction):
  """Returns the new location."""
  return neighbor(location, direction)


def spins(source, direction, destination):
  """Gets the number of rotations needed to have the destination room ahead."""
  # check if source and destination are neighbors
  assert source in neighbors(destination)
  # computes the difference between locations
  diff = tuple([a - b for a, b in zip(destination, source)])
  rot = DELTA.index(diff) - direction
  rot = rot if rot != 3 else -1
  # returns the minimum number of spins (clockwise vs counterclockwise)
  return rot


def known_path_rec(kb, loc, dest, path, visited):
  """Depth-first search that builds an explored path to destination."""
  # check if the location and the destination are the same
  if loc == dest:
    return True
  # generator of explored (but not yet visited by the search) neighbors
  neighborhood = (l for l in neighbors(loc) if l not in visited 
                  and (kb[l].is_explored or l == dest))
  # iterate over each neighbor
  for n in neighborhood:
    # add the node to the path
    path.append(n)
    visited.add(n)
    # recursive call
    if known_path_rec(kb, n, dest, path, visited):
      return True
    # backtrack: this node does not lead to the destination
    visited.remove(n)
    path.remove(n)
  return False


def known_path(kb, loc, dest):
  """Returns an explored path to destination."""
  path = [loc]
  visited = set()
  visited.add(loc)
  # return the path or None if the path wasn't found
  if known_path_rec(kb, loc, dest, path, visited):
    return tuple(path)


def path_to_spins(path, direction):
  """Gets a list of spins that an agent has to perform to follow the path."""
  # check the presence of a valid path
  assert path is not None
  rotations = []
  # follow the path and compute the steps needed to turn and then move forword
  # the agent in order to reach the last location of the path
  i = 0
  while i < len(path) - 1:
    rot = spins(path[i], direction, path[i + 1])
    rotations.append(rot)
    direction = (direction + rot) % len(DELTA)
    i += 1
  return tuple(rotations)
