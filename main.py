import pygame 
from pygame.locals import *
import ctypes
import os
import copy

"""
Problème avec le scroling et la redimention de l'écran, ne soyez pas étonné. Ah et c'est pas fini juste j'ai pas le temps de tout faire 
"""


vec = pygame.math.Vector2
class Jeu :
    def __init__(self) -> None:
        self.fullscreen = False
        
        squale = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1) # ça à l'air de fonctionner uniquement sur windows faudra tester sur linux
        """
        au pire version universelle : 
            self.screen = pygame.display.set_mode((0,0), FULLSCREEN)
            self.width , self.height = self.screen.get_size()[0] * 0.75,self.screen.get_size()[1] * 0.75
        """

        self.width , self.height = squale[0] * 0.75,squale[1] * 0.75
        self.screen = pygame.display.set_mode((self.width,self.height),RESIZABLE)
        self.world = World(self.screen)
        self.clock = pygame.time.Clock()
    
    def inputs(self):

        for event in pygame.event.get():
            if event.type == VIDEORESIZE and not self.fullscreen:
                
                if event.dict['size'][0] / self.width != 1 and event.dict['size'][1] / self.height != 1:
                    pass
                
                elif event.dict['size'][0] / self.width != 1:
                    self.height *= event.dict['size'][0] / self.width
                    self.width = event.dict['size'][0]
                
                elif event.dict['size'][1] / self.height != 1:
                    self.width *= event.dict['size'][1] / self.height
                    self.height = event.dict['size'][1]
                
                self.width = round(self.width)
                self.height = round(self.height)
                self.screen = pygame.display.set_mode((self.width,self.height),RESIZABLE)
                
                self.world.blockSize = self.height / 15
                
                for i in self.world.briqueimg:
                    self.world.briqueimg[i] = pygame.transform.scale(self.world.briqueimgOrigignal[i], (self.height / 15, self.height / 15))
                self.world.updateBL = True

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

    def update(self):
        self.screen.fill("black")
        self.world.update()
        self.inputs()
        pygame.display.flip()
        self.clock.tick(60)

class Entity:
    def __init__(self,screen,blockliste,name) -> None:
        self.screen = screen
        self.rect = pygame.Rect(50,50,32,64)
        self.blockliste = blockliste
        self.decalage = 0
        self.image = pygame.transform.scale(pygame.image.load('assets/players/{}'.format(name)),(32,64))

        self.pos = vec((10, 350))
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        self.FRIC = -0.12
        self.ACC = 0.5

    def draw(self):
        self.rect.x -= self.decalage
        self.screen.blit(self.image,self.rect)

    def collision(self):
        for e in self.blockliste.values():
            for i in e :
                if pygame.Rect.colliderect(self.rect, i) == True:
                    
                    
                    # par le bas
                    if self.rect.top <= i.top:
                        return (True,i,"bas")
                                        
                    # par le haut

                    if self.rect.top >= i.top:
                        return (True,i,"haut")
                    

                        
        return (False,0,"None")
    

    def jump(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            if self.collision()[0]:
                self.vel.y = -15

    def move(self):
        self.acc = vec(0,0.5)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            self.acc.x = self.ACC
        if keys[pygame.K_LEFT]:
            self.acc.x = -self.ACC

        self.acc.x += self.vel.x * self.FRIC
        self.vel += self.acc

#        self.vel.y = 0
#        self.acc.y = 0

        self.pos += self.vel + 0.5 * self.acc

        self.rect.midbottom = self.pos

    def gravity(self):
        
        collision = self.collision()
            
        if self.vel.y > 0:
            if collision[0] and collision[2] == "bas":
                self.vel.y = 0
                self.pos.y = collision[1].top + 1
                
        if self.vel.y < 0:
            if collision[0] and collision[2] == "haut":
                self.vel.y = 0
                self.pos.y = collision[1].bottom + self.rect[3]

    def update(self):
        self.draw()
        self.move()
        self.jump()
        self.gravity()
        

class World:
    def __init__(self,screen) -> None:
        self.updateBL = False
        self.width , self.height = 720,480
        self.screen = screen
        self.world = self.get_world()
        self.blockSize = screen.get_size()[1]/15
        self.decalage = 0
        self.briqueimgOrigignal = {}
        self.briqueimg = {}
        self.players = {}
        
        for name in os.listdir('assets/world'):
            self.briqueimgOrigignal[name] = pygame.transform.scale(pygame.image.load('assets/world/{}'.format(name)),(self.blockSize,self.blockSize))
            self.briqueimg[name] = pygame.transform.scale(pygame.image.load('assets/world/{}'.format(name)),(self.blockSize,self.blockSize))
        


        self.liste = []
        self.elementIntoListe()
        self.blockliste = {"#":[],"?":[]}
        for e in self.liste:
            if e[2] == '#':
                rect = pygame.Rect(e[1]*self.blockSize-self.decalage, e[0]*self.blockSize, self.blockSize, self.blockSize)
                self.blockliste["#"].append(rect)
            elif e[2] == '?':
                rect = pygame.Rect(e[1]*self.blockSize-self.decalage, e[0]*self.blockSize, self.blockSize, self.blockSize)
                self.blockliste["?"].append(rect)
        
        for name in os.listdir('assets/players'):
            self.players[name] = Entity(self.screen,self.blockliste,name)

    def get_world(self):
        file = open('world.txt', 'r')
        data = file.read()
        liste = data.split("\n")
        file.close()
        return liste
    
    def elementIntoListe(self):
        for ligne in range(len(self.world)):
            if self.world[ligne] != '':
                for e in range(len(self.world[ligne])):
                    if self.world[ligne][e] == '#':
                        self.liste.append([ligne,e,'#'])
                    elif self.world[ligne][e] == '?':
                        self.liste.append([ligne,e,'?'])

    def draw_on_screen(self):
        print(self.decalage)
        if self.updateBL:
            self.blockliste["#"] = []
            self.blockliste["?"] = []
        for e in self.liste:
            if e[2] == '#':
                rect = pygame.Rect(e[1]*self.blockSize-self.decalage, e[0]*self.blockSize, self.blockSize, self.blockSize)
                if self.updateBL:
                    self.blockliste["#"].append(rect)
                self.screen.blit(self.briqueimg['brique.png'],rect)
            elif e[2] == '?':
                rect = pygame.Rect(e[1]*self.blockSize-self.decalage, e[0]*self.blockSize, self.blockSize, self.blockSize)
                if self.updateBL:
                    self.blockliste["?"].append(rect)
                pygame.draw.rect(self.screen, "yellow", rect ,2)   
        self.updateBL = False


    def scrolling(self):
        for personnage in self.players:
            if self.players[personnage].rect.x-self.decalage > self.width*0.75:
                self.decalage += self.players[personnage].vel[0]
                self.players[personnage].decalage += self.players[personnage].vel[0]


    def inputs(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            self.decalage +=5
            self.mario.decalage +=5
        if keys[pygame.K_q]:
            self.decalage -=5
            self.mario.decalage -=5



    def update(self):
        self.inputs()
        self.scrolling()
        self.draw_on_screen()
        for personnage in self.players:
            self.players[personnage].update()
        

   

jeu = Jeu()
while True :
    jeu.update()