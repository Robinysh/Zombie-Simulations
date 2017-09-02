# Zombie Apocalypse Simulation
## Current Assumptions/Implementation
* Zombies move in a brownian motion
* Humans wont move unless they see a zombie
* Humans have a limited range of sight
* Humans get infected once they touch a zombie
* Humans dont breed or die
* Zombies dont die (or breed, if thats a concern)

## TODO
* Update the searching algorithm if anyone knows other kdtree implementation that allows updating without reconstructing the whole tree, or other better data structures. I think that might be the performance bottleneck right now.
* Might implemented grid based velocity update as an approximation to increase humans movement performance.
