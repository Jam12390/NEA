# Blended - The 2D Skeleton Platformer Made For NEA

This is a skeleton 2D platformer I made during my time at Runshaw College for my Y2 NEA and the final build after NEA-Old.

## Features
- Physics System - A ground up physics system, including collisions, forces, etc. The basis for the whole game.
- Map Interpreter - A system which converts any .csv file consisting of numerical tile IDs into a map format interpretable by the game. Includes automatic collision detection too!
- Precompiled Pathing - Takes the map format and precompiles every node a given enemy can path to depending on its starting point.
- Pathing - An A* pathing algorithm which uses waypoints from the precompiled graph to achieve efficient pathing to the player.
- Extremely Basic Combat - Click to attack, if the weapon collides with an enemy, the enemy dies.
- Basic Inventory + Stat Modification - Based on HK and Dead Cells' inventory system. Includes auto text wrapping, screen dimming + pausing and item viewing + description.
