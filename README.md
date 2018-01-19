# Documentation is a work in progress
# Ceng-356
initial code commit. Workin copy, uncommented
#TODO comment, fix program flow

## Instructions

#### 1. 
  To run Pew-Pew pygame must be installed on your computer. Installation files and instructions can be found [here](https://www.pygame.org/wiki/GettingStarted)
#### 2. 
  A server must be started before the clients. To run the server run Server.py from the command line with a single argument formatted like this:
        <host>:<port>
Typically ran of localhost
  
#### 3.
  The client is started nearly the same way as the server. To run the run CLient.py with the following argument:
    <host>:<port>
  ex. localhost:40000
  Once two separate clients are connected the game starts
  
#### The game
The goal of the game is to cause the other player to crash into the planet. The planet has gravity which scales with the size of the planet. Your ship will point towards the mouse and will accelerate towards the mouse when LMB is pressed. Each ship has a weapon mapped to the RMB on a two second cooldown. The weapon expands out from the initial point of use in a circle, if the enemy ship is hit it will be accelerated in the direction of the hit.

## Other
