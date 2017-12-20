from sys import exit
from os import environ
import pygame
import math
from random import randrange
Vec = pygame.math.Vector2

# Define some colors
BLACK = (0,   0,   0)
WHITE = (255, 255, 255)
GREEN = (0, 255,   0)
RED = (255,   0,   0)
BLUE = (0,   0, 255)

X_DIM = 1000
Y_DIM = 700
SCREENSIZE = (X_DIM, Y_DIM)
environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
screen = pygame.display.set_mode(SCREENSIZE)
bg_image = pygame.image.load("background.png")
bg_image = pygame.transform.scale(bg_image, (X_DIM, Y_DIM))

class Ship(pygame.sprite.Sprite):
    #Model of ship. Contains spatial and image locatoin about the ship
    def __init__(self):
        super(Ship,self).__init__()
        self.Pos = Vec(100,100)
        self.Vel = Vec(0,0)
        self.Acc = Vec(0,0)
        self.angle = 0
        self.engine_firing = False
        self.engine_power = 0.1
        self.image_original = pygame.image.load("p2.png")
        self.image_original.set_colorkey([0, 0, 0])
        self.rect_original = self.image_original.get_rect()
        self.image = pygame.Surface([self.rect_original.x, self.rect_original.y])
        self.radius = 20
        self.rect = self.image_original.get_rect()
        self.rect.center = [self.rect.x + (self.rect.width) / 2, self.rect.y + (self.rect.height) / 2]
        self.weapon_cooldown = 0
        self.weaponAcc = Vec(0, 0)


    def rotate(self, angle):
        # Rotates the image which produces a new rectangular image with unknown dimensions
        # This is done to prevent quality loss from succesive rotations.
        self.rect.center = (self.Pos[0], self.Pos[1])
        self.rect.x = self.Pos[0] - self.rect.width/2
        self.rect.y = self.Pos[1] - self.rect.height/2
        orig_rect = self.image_original.get_rect()
        rot_image = pygame.transform.rotate(self.image_original, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        self.image = rot_image
        self.angle = angle

    def update(self,Pos,angle):
        # Sets a new position and angle for ship. Typically only called for the ship that is controlled by the other
        # client
        self.Pos = [Pos[0],Pos[1]]
        self.angle = angle
        self.rotate(self.angle)

    def draw(self,screen):
        # draws the ship onto the given surface
        screen.blit(self.image, self.rect)

    def set_p1(self, p1):
        #sets the ships image
        if p1:
            self.set_graphic(True)
        else:
            self.set_p2(True)

    def set_p2(self, p2):
        # sets the ships image
        if p2:
            self.set_graphic(False)
        else:
            self.set_p1(True)


    def set_graphic(self, p1):
        #loads a unique image for each player
        if p1:
            self.image = pygame.image.load("p1.png")
        else:
            self.image = pygame.image.load("p2.png")
        self.image_original = self.image
        self.rect = self.image.get_rect()

class Planet(pygame.sprite.Sprite):
    # Model of a planet. Contains all spatial and image information.
    def __init__(self, Pos, radius):
        super(Planet, self).__init__()
        self.Pos = Pos
        self.image_original = pygame.image.load("planet4.png")
        self.image_original = pygame.transform.scale(self.image_original, (radius * 2, radius * 2))
        self.rect_original = self.image_original.get_rect()
        self.image_original.set_colorkey([0, 0, 0])
        self.rect_original.x = self.Pos.x
        self.rect_original.y = self.Pos.y
        self.image = self.image_original
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = self.Pos.x
        self.rect.y = self.Pos.y
        self.rect.center = [self.rect.x + self.rect.w / 2, self.rect.y + self.rect.h / 2]
        self.radius = radius
        self.center = Vec(self.Pos.x + self.radius,self.Pos.y + self.radius)

    def draw(self,screen):
        # Draws planet to the given surface
        screen.blit(self.image_original,(int(self.Pos.x - self.radius),int(self.Pos.y - self.radius)))


class Space(object):
    # Main model used by the client.
    def __init__(self):
        self.statusLabel = "Connecting"
        self.playersLabel = "Waiting for player"
        self.player_list = pygame.sprite.Group()
        self.planet_list = pygame.sprite.Group()
        temp = Planet(Vec(370,220),130)
        self.weapon_list = []
        self.planet_list.add(temp)
        self.p1 = Ship()
        self.p1.set_p1(True)
        self.p1.set_graphic(True)
        self.p2 = Ship()
        self.p2.set_graphic(False)
        self.p2.set_p2(True)
        self.player = 0
        self.player_list.add(self.p1,self.p2)


    def check_input(self):
        # checks for mouse presses on the left and right mouse buttons.
        # LMB       scroll wheel        RMB
        # mouse[0]  mouse[1]            mouse[2]
        mouse = pygame.mouse.get_pressed()
        if mouse[2]:
            weapon_fired = True
        else:
            weapon_fired = False
        if mouse[0]:
            engine_firing = True
        else:
            engine_firing = False
        return engine_firing,weapon_fired

    def events(self):
        # handles pygame event queue which is not used but must be cleared once per game loop to prevent freezing.
        # checks for quitting conditions
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    exit(0)
            if event.type == pygame.QUIT:
                exit(0)

    def draw(self):
        # draws everything on screen in the following order Black scree -> background -> ships -> weapons -> planets
        screen.fill(BLACK)
        screen.blit(bg_image,[0,0])
        self.player_list.draw(screen)
        for weapon in self.weapon_list:
            pygame.draw.circle(screen,WHITE,[int(weapon['p_pos'][0]),int(weapon['p_pos'][1])], int(weapon['radius']),int(5))
            weapon['radius'] = weapon['radius']+5
            if weapon['radius'] > 120:
                self.weapon_list.remove(weapon)
        self.planet_list.draw(screen)
        pygame.display.flip()
