# Documentation is a work in progress
# Ceng-356

## Instructions

#### 1. 
  To run Pew-Pew pygame must be installed on your computer. Installation files and instructions can be found [here](https://www.pygame.org/wiki/GettingStarted)
#### 2. 
  A server must be started before the clients. To run the server run Server.py from the command line with a single argument formatted like this:
  
        \<host\>:\<port\>
        
I've only ran this off of a localhost so no idea if it works for setting up a remote server.
  
#### 3.
  The client is started nearly the same way as the server. To run the run CLient.py with the following argument:
    \<host\>:\<port\>
  ex. localhost:40000
  Once two separate clients are connected the game starts
  
#### The game
The goal of the game is to cause the other player to crash into the planet. The planet has gravity which scales with the size of the planet. Your ship will point towards the mouse and will accelerate towards the mouse when LMB is pressed. Each ship has a weapon mapped to the RMB on a two second cooldown. The weapon expands out from the initial point of use in a circle, if the enemy ship is hit it will be accelerated in the direction of the hit.

## Resources and references

### Sprites and backgrounds
- [Ships - ](http://millionthvector.blogspot.ca/p/free-sprites.html)Created by MillionthVector
- Planets - Obtained off of a open source website. All planets were part of a larger composite image and my laptop with the original image is currently broken. I couldnt find anything reverse image searching with the parts or searching normally. Once laptop has been repaired will reverse image search to find creator or will replace assets.
- [Background - ](https://opengameart.org/content/space-background)Created by Cuzco

### Code
- [PodSixNet - ](https://github.com/chr15m/PodSixNet)Created by Chris McCormick
- [Pygame - ](https://www.pygame.org/news)Original author was Pete Shinners

#### To do
- Fix program flow. E.x. what happens when a player disconnects during a game
- Randomize number and location of planets. At the moment only a single planet is spawned and it is always in the same location.
- Improve how server/clients handle weapons. The problem here is that both clients and servers both hold data on how large the weapon radius is. This could potentially cause bizarre looking hit detection because of the asynchronicity of the server/client relationship.
- Switch non-critical network traffic ex. movement events from a TCP to UDP protocol. Keep TCP for events that must be received like weapon use, hit detection, death, and connection/disconnetion events.




