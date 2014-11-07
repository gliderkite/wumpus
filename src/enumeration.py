#! /usr/bin/env python


import enum


class Status(enum.Enum):
  """Enumerations used to denote the Room status."""
  Unknown = -1
  Absent = 0
  Present = 1
  LikelyPresent = 2


class Entity(enum.Enum):
  """Entities enumeration."""
  Wumpus = 0
  Pit = 1
  Gold = 2


class Action(enum.Enum):
  """Enumeration of agent feasible actions."""
  Move = 0
  Shoot = 1
  TakeGold = 2


class Goal(enum.Enum):
  """Enumerates agent's goals."""
  SeekGold = 0
  BackToEntry = 1
