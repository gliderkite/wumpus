# Hunt the Wumpus
A Python module that allows to play with the original [Hunt the Wumpus](http://en.wikipedia.org/wiki/Hunt_the_Wumpus) [text-based](http://en.wikipedia.org/wiki/Text-based_game) game.


## How to Play
The agent is located in a cave with 16 rooms (a 4x4 grid). The goal is to find the gold in one of this room and return to the the entry. But the cave contains also the Wumpus, a beast that eats anyone that enters its room, and zero or more pits, that will trap anyone who enters the room except for the Wumpus.

The agent can perceive several information according to its current location:

1. In the square containing the wumpus and in the directly (not diagonal) adjacent squares, the agent will perceive a Stench.
2. In the squares directly adjacent to a pit, the agent will perceive a Breeze.
3. In the square where gold is, the agent will perceive a Glitter.
4. When the wumpus is killed, it emits a Scream that can be perceived anywhere in the cave.

The agent can perform five different action:

1. A simple move Forward.
2. A simple Turn Left by 90°.
3. A simple Turn Right by 90°.
4. The action Grab can be used to pick up gold when in the same room as gold.
5. The action Shoot can be used to fire an arrow in a straight line in the current direction the agent is facing. The arrow continues until it hits and kills the wumpus or hits a wall.

![wumpus image](http://i57.tinypic.com/2zovsit.jpg)


## Requirements
In order to play with Hunt the Wumpus you have to download and install [Python (3.X version)](https://www.python.org/downloads/).


## Launch the game
Once you have correctly installed Python you can simply run the script by typing (on Unix-based systems):
```bash
./wumpus.py
```
You can also let the Artificial Intelligence module play for you by appending the argument `-ai`:
```bash
./wumpus.py -ai
```
Finally if you want to play with the same configuration several times you can specify the seed used:
```bash
./wumpus.py -seed 0
```