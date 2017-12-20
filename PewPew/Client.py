import sys
from time import sleep
from PodSixNet.Connection import connection, ConnectionListener
from Space import Space
import pygame.math
Vec = pygame.math.Vector2
from math import atan2,cos,sin,degrees,radians
from Space import X_DIM,Y_DIM

GRAVITY = 8

class Client(ConnectionListener, Space):
    # Client extends the listener and the model of the game so it acts as both.
    def __init__(self, host, port):
        self.Connect((host, port))
        self.ready = False
        Space.__init__(self)

    def Loop(self):
        # main client loop. Monitors network and once the game has started it allows moves.
        self.Pump()
        connection.Pump()
        if self.ready:
            self.player_move()
        self.events()
        self.draw()
        sleep(1/60)

    def send_action(self, action):
        # sends a specified action to the server
        if self.player == 0:
            return
        if self.player == 1:
            player = self.p1
        else:
            player = self.p2
        Pos = [player.Pos.x,player.Pos.y]
        angle = player.angle
        connection.Send({"action": action, "p": 'p'+str(self.player), "p_pos": Pos,'ang':angle})



    def player_move(self):
        # updates the local player. It begins by checking for mousebutton presses before pointing the local player's ship
        # at the mouse. Then the force is calculated and the position, velocity, and acceleration are updated
        if self.player == 0:
            return
        elif self.player == 1:
            player = self.p1
        elif self.player == 2:
            player = self.p2
        weapon_fired = False
        player.engine_firing, weapon_fired = self.check_input()
        if weapon_fired and player.weapon_cooldown == 0:
            self.send_action('fire')
            player.weapon_cooldown = 120
        elif player.weapon_cooldown > 0:
            player.weapon_cooldown = player.weapon_cooldown - 1
        mouse_dir = pygame.mouse.get_pos()
        mouse_dir = mouse_dir - player.Pos
        player.angle = degrees(atan2(-mouse_dir.y, mouse_dir.x))%360

        # force calculations begin

        force = Vec(0, 0)
        if player.engine_firing:
            force = Vec(cos(radians(player.angle)), -sin(radians(player.angle)))
            force.scale_to_length(player.engine_power)
        my_sum = Vec(0, 0)
        if self.planet_list:
            for planet in self.planet_list:
                temp = (planet.Pos + Vec(planet.radius, planet.radius)) - player.Pos
                inverse_square = 1 / temp.length_squared()
                temp.scale_to_length(inverse_square * GRAVITY * planet.radius)
                my_sum = temp
        force = my_sum + force
        if player.weaponAcc.length_squared() > 0.00001:
            player.weaponAcc.scale_to_length((player.weaponAcc.length() - (1 / 120)))
            # since this will be called 60 times per second to have the pulse last 2 seconds
        else:
            player.weaponAcc = Vec(0, 0)

        #physics updates begin

        player.Acc = force + player.weaponAcc
        player.Pos += player.Vel + 0.5 * player.Acc
        player.Vel += player.Acc
        player.rotate(player.angle)
        self.send_action('move')


####
#### Network callback functions begin, all callback functions have form Network_*. Where * is some defined action that
#### was sent in the dictionary

    def Network_init(self, data):
        # Called when connection is first established. Assigns player number and sets starting
        # position
        if data["p"] == 'p1':
            self.player = 1
            print("player 1 connected")
            # Send position to server
            self.p1.Pos = Vec(50,Y_DIM/2)
            self.send_action('move')
        elif data["p"] == 'p2':
            self.player = 2
            print('player 2 connected')
            # Send position to server
            self.p2.Pos = Vec(X_DIM - 50,Y_DIM/2)
            self.send_action('move')
        elif data["p"] == 'full':
            print('max number of players reached')
            self.playersLabel = "Waiting for free slot in server"
        else:
            sys.stderr.write("ERROR: data from server was unreadable")
            sys.stderr.write(data)
            sys.stderr.flush()
            sys.exit(1)

    def Network_ready(self, data):
        # Notifies client that the server is ready to begin
        self.ready = True

    def Network_player_left(self, data):
        # Notifies client that the other client has left
        self.playersLabel = "Other player left server"
        self.ready = False
        if self.player == 1:
            self.p1.Pos = Vec(50,Y_DIM/2)
            self.send_action('move')
        else:
            self.p2.Pos = Vec(X_DIM - 50, Y_DIM / 2)
            self.send_action('move')

    def Network_move(self, data):
        # Updates the position of the non-local player
        position = data['p_pos']
        player = data['p']
        angle = data['ang']
        if player == 'p1' and self.player != 1:
            self.p1.update(position,angle)
        elif player == 'p2' and self.player != 2:
            self.p2.update(position,angle)
        elif player in ('p1', 'p2'):  # This is client's position coming back from player
            pass
        else:
            sys.stderr.write("ERROR: Couldn't update player movement information.\n")
            sys.stderr.write(str(data) + "\n")
            sys.stderr.flush()
            sys.exit(1)

    def Network_kill(self, data):
        # Notifies the client of a kill event and closes the game window if the client was the one who was killed
        player = data['p']
        if player == 'p1' and self.player == 1:
            sys.exit(0)
        elif player == 'p2' and self.player == 2:
            sys.exit(0)

    def Network_fire(self, data):
        # Notifies the client that another client has fired a weapon
        player = data['p']
        pos = data['p_pos']
        self.weapon_list.append({'p':player,'p_pos':pos,'radius':10})

    def Network_hit(self, data):
        # Notifies the client of a hit event. If the player hit was the local client, the weapon acceleration is set
        Pos = Vec(data['p_pos'][0],data['p_pos'][1])
        for weapon in self.weapon_list:
            if weapon['p_pos'][0] == data['p_pos'][0] and weapon['p_pos'][1] == data['p_pos'][1]:
                self.weapon_list.remove
        if data['p'] == 'p1' and self.player == 1:
            player = self.p1
            temp = player.Pos - Pos
            temp.scale_to_length(0.25)
            player.weaponAcc = temp
        elif data['p'] == 'p2' and self.player == 2:
            player = self.p2
            temp =   player.Pos - Pos
            temp.scale_to_length(1)
            player.weaponAcc = temp





    def Network(self, data):
        # Generic callback function that ignores any undefined actions in the dictionary sent by the server
        pass


    def Network_connected(self, data):
        # sent when the network is connected
        self.statusLabel = "Connected"

    def Network_error(self, data):
        # Notifies client of fatal network error
        self.ready = False
        import traceback
        traceback.print_exc()
        self.statusLabel = data['error'][1]
        connection.Close()

    def Network_disconnected(self, data):
        # Notifies the client that it has been disconnected from the server
        self.statusLabel = "Disconnected"
        self.playersLabel = "No other players"
        self.ready = False


# get command line argument of server, port
if len(sys.argv) != 2:
    print("Usage:", sys.argv[0], "host:port")
    print("e.g.", sys.argv[0], "localhost:31425")
else:
    host, port = sys.argv[1].split(":")
    c = Client(host, int(port))
    while 1:
        c.Loop()
        sleep(1/60)


