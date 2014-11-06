#! /usr/bin/env python



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

