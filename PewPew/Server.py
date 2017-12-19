import sys
import os
import pygame
from collections import deque
from time import sleep
from Space import Ship
from PodSixNet.Server import Server
from PodSixNet.Channel import Channel
from Space import Planet
Vec = pygame.math.Vector2


class ServerChannel(Channel):

    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)
        self.id = str(self._server.next_id())
        self._player_pos = [0,0]
        self.p1 = None
        self.player = 0
        self.weapon_list = []
        self.sprite = Ship()


    def pass_on(self, data):
        self._server.send_to_all(data)

    def Close(self):
        self._server.delete_player(self)


    def Network_move(self, data):
        self.sprite.Pos = Vec(data['p_pos'][0],data['p_pos'][1])
        self.pass_on(data)

    def Network_fire(self,data):
        pos = data['p_pos']
        player = data['p']
        self.weapon_list.append({'p_pos':pos, 'p':player,'radius':10})
        self.pass_on(data)


class SpaceServer(Server):
    channelClass = ServerChannel
    def __init__(self, *args, **kwargs):

        self.id = 0
        Server.__init__(self, *args,**kwargs)
        self.p1 = None
        self.p2 = None
        self.planet_list = pygame.sprite.Group()
        self.ready = False
        temp = Planet(Vec(370, 220), 130)
        self.planet_list.add(temp)
        self.weapon_list = []
        self.player_list = pygame.sprite.Group()
        self.waiting_player_list = deque()
        print('server launched')


    def Connected(self, channel, addr):
        if self.p1 and self.p2:
            channel.Send({"action": "init", "p": "full"})
            self.waiting_player_list.append(channel)
        else:
            self.add_player(channel,addr)

    def next_id(self):
        self.id += 1
        return self.id

    def add_player(self,player,addr):
        if self.p1 is None:
            self.p1 = player
            player.player = 1
            player.addr = addr
            print("player 1 (" + str(player.addr) + ")")
        elif self.p1 and self.p2 is None:
            self.p2 = player
            player.player = 2
            player.addr = addr
            print("player 2 (" + str(player.addr) + ")")
        else:
            sys.stderr.write("ERROR:Client data was fatally incorrect")
            sys.stderr.flush()
            sys.exit(1)
            # If only P1, tell client they're P1
        if self.p2 is None:
            player.Send({"action": "init", "p": 'p1'})
            # Else if P2, notify P2 and send position data
            self.player_list.add(self.p1.sprite)

        else:
            self.p2.Send({"action": "init", "p": 'p2'})
            self.send_to_all({"action": "ready"})
            # Only send position data from P1 -> P2
            loc = [self.p1.sprite.Pos.x,self.p1.sprite.Pos.y]
            angle = self.p1.sprite.angle
            self.send_to_all({"action": "move", "p": "p1", "p_pos": loc,"ang":angle})
            self.player_list.add(self.p2.sprite)
            self.ready = True
            return

    def delete_player(self, player):
        self.ready = False
        if self.p1 is player:
            self.p1 = None
            self.send_to_all({"action": "player_left"})
            print("player 1 left (" + str(player.addr) + ")")
        elif self.p2 is player:
            self.p2 = None
            self.send_to_all({"action": "player_left"})
            print("player 2 left (" + str(player.addr) + ")")
        elif player in self.waiting_player_list:
            self.waiting_player_list.remove(player)
        else:
            print("ERROR: deleting player cannot be completed")
            # Pull waiting player from queue
        if self.waiting_player_list:
            self.add_player(self.waiting_player_list.popleft())

    def collision_detection(self):
        self.weapon_list = []
        self.weapon_list = self.p1.weapon_list + self.p2.weapon_list
        for planet in self.planet_list:
            Pos1 =  self.p1.sprite.Pos
            rad1 = self.p1.sprite.radius
            if self.distance(Pos1, planet.center) < (rad1 + planet.radius):
                pass
                data = {'action': 'kill', 'p':'p1'}
                self.send_to_all(data)

            Pos2 = self.p2.sprite.Pos
            rad2 = self.p2.sprite.radius
            if self.distance(Pos2, planet.center) < (rad2 + planet.radius):
                pass
                data = {'action': 'kill', 'p':'p2'}
                self.send_to_all(data)



        for weapon in self.weapon_list:
            rWeapon = False
            weapon['radius'] = weapon['radius'] + 5
            wPos = Vec(weapon['p_pos'][0],weapon['p_pos'][1])
            if weapon['p'] == 'p1':
                if self.distance(wPos, self.p2.sprite.Pos) < (weapon['radius'] + self.p2.sprite.radius):
                    data = {'action':'hit','p_pos':[wPos.x,wPos.y],'p':'p2'}
                    self.send_to_all(data)
                    rWeapon = True
            elif weapon['p'] == 'p2':
                if self.distance(wPos, self.p1.sprite.Pos) < (weapon['radius'] + self.p1.sprite.radius):
                    data = {'action':'hit','p_pos':[wPos.x,wPos.y],'p':'p1'}
                    self.send_to_all(data)
                    rWeapon = True
            if weapon['radius'] > 120:
                rWeapon = True
            if rWeapon is True:
                if weapon in self.p1.weapon_list:
                    self.p1.weapon_list.remove(weapon)
                elif weapon in self.p2.weapon_list:
                    self.p2.weapon_list.remove(weapon)


    def distance(self, PosA, PosB):
        temp = PosA - PosB
        distance = temp.length()
        return distance


    def send_to_all(self, data):
        """
        Send data to all connected clients.
        :param data: Data to send
        :return: None
        """
        if self.p1 is not None:
            self.p1.Send(data)
        if self.p2 is not None:
            self.p2.Send(data)


    def launch_server(self):
        """
        Main server loop.
        :return: None
        """
        while True:
            self.Pump()
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        exit(0)
                if event.type == pygame.QUIT:
                    exit(0)
            if self.ready:
                if self.p1 is not None and self.p2 is not None:
                    self.collision_detection()
                sleep(1/60) # 0.01, 0.0001?

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
screen = pygame.display.set_mode((1, 1))

# get command line argument of server, port
if len(sys.argv) != 2:
    print("Usage:", sys.argv[0], "host:port")
    print ("e.g.", sys.argv[0], "localhost:31425")
else:
    host, port = sys.argv[1].split(":")
    s = SpaceServer(localaddr=(host, int(port)))
s.launch_server()
