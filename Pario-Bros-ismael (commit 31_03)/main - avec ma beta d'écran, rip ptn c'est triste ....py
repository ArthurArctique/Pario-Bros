import pygame 
from pygame.locals import *
import ctypes
import os
import copy
import numpy

vec = pygame.math.Vector2

class Jeu :
    def __init__(self) -> None:
        self.jeu = False
        self.menu = True
        self.fullscreen = False
        self.changement = False
        self.firstResize = True
        self.screen = pygame.display.set_mode((0,0), FULLSCREEN)
        self.width , self.height = self.screen.get_size()[0] * 0.75,self.screen.get_size()[1] * 0.75
        self.UTILE = self.width
        self.screen = pygame.display.set_mode((self.width,self.height),RESIZABLE)
        self.world = World(self.screen)
        self.clock = pygame.time.Clock()
    
    def inputs(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.fullscreen:
                        self.screen = pygame.display.set_mode((self.width,self.height))
                    self.menu = False
                    self.jeu = True
                if event.key == pygame.K_F11 and not self.fullscreen and not self.jeu:

                    self.fullscreen = True
                    self.screen = pygame.display.set_mode((0,0), FULLSCREEN)
                    self.width, self.height = self.screen.get_size()
                    self.changement = True
                elif event.key == pygame.K_F11 and self.fullscreen and not self.jeu:
                    self.screen = pygame.display.set_mode((self.screen.get_size()[0]*0.75,self.screen.get_size()[1]*0.75),RESIZABLE)   
                    self.width, self.height = self.screen.get_size()
                    self.fullscreen = False
                    self.changement = True
            
            if event.type == VIDEORESIZE and not self.fullscreen and self.menu:
                    if self.firstResize:
                        self.firstResize = False
                        break
                    self.changement = True
                    if event.dict['size'][0] / self.width != 1 and event.dict['size'][1] / self.height != 1:
                        pass
                    
                    elif event.dict['size'][0] / self.width != 1:
                        self.height *= event.dict['size'][0] / self.width
                        self.width = event.dict['size'][0]
                        
                    
                    elif event.dict['size'][1] / self.height != 1:
                        self.width *= event.dict['size'][1] / self.height
                        self.height = event.dict['size'][1]
                    self.width = int(self.width)
                    self.height = int(self.height)
                    self.screen = pygame.display.set_mode((self.width,self.height),RESIZABLE)
            
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
                
        if self.changement and not self.firstResize:   
            
            self.world.blockSize = self.height / 15
            for i in self.world.briqueimg:
                self.world.briqueimg[i] = pygame.transform.scale(self.world.briqueimgOrigignal[i], (self.height / 15, self.height / 15))
            
            for i in self.world.players:
                quotient = self.width / self.world.width
                self.world.players[i].vitesse = quotient * 0.75
                self.world.players[i].qJump = quotient  
                self.world.players[i].image = pygame.transform.scale(self.world.players[i].original, ((self.world.players[i].original.get_size()[0] * self.world.players[i].playerSize) * quotient, (self.world.players[i].original.get_size()[1] *  self.world.players[i].playerSize)* quotient ))
                self.world.players[i].rect.width = self.world.players[i].image.get_rect().width
                self.world.players[i].rect.height = self.world.players[i].image.get_rect().height
                self.world.players[i].updateSc = True
                self.world.players[i].pos.x *= quotient
            self.world.updateBL = True
            self.changement = False
                

            

    def update(self):
        if self.menu:
            self.screen.fill("black")
            self.inputs()
        if self.jeu:
            self.screen.fill("black")
            self.world.update()
            self.inputs()
        pygame.display.flip()
        self.clock.tick(60)

class Entity:
    def __init__(self,screen,blockRECT,name,joueur) -> None:
        self.qJump = 1
        self.screen = screen
        self.blockRECT = blockRECT
        self.playerSize = 0.04
        self.decalage = 0
        self.speed = 4
        self.joueur = joueur
        if joueur:
            self.original = pygame.image.load('assets/players/{}'.format(name))
            self.joueur = True
            self.pos = vec((10, 360))
        else:
            self.original = pygame.image.load('assets/monstres/{}'.format(name))
            self.pos = vec((150,450))
            self.speed = 3
        
        self.height, self.width = self.original.get_size()
        self.image = pygame.transform.scale(self.original,(self.height * self.playerSize,self.width *self.playerSize))
        self.rect = self.image.get_rect()
        self.pos = vec((200, 0))
        self.jumpspeed = 20
        self.speedVerti = 0
        self.speedHori = 0
        self.gravity = 1
        self.min_jumpspeed = 4
        self.prev_key = pygame.key.get_pressed()
            

    def draw(self):
        self.rect.x -= self.decalage
        self.screen.blit(self.image,self.rect)

    def jump(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.vel.y = -self.screen.get_size()[1] / 20

    def updateTuto(self):
        self.speedHori = 0
        onground = self.check_collision(0, 1)
        # check keys
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.joueur:
            self.speedHori = -self.speed
        elif key[pygame.K_RIGHT] and self.joueur:
            self.speedHori = self.speed

        if key[pygame.K_UP] and onground and self.joueur:
            self.speedVerti = -self.jumpspeed

        # variable height jumping
        if self.prev_key[pygame.K_UP] and not key[pygame.K_UP]:
            if self.speedVerti < -self.min_jumpspeed:
                self.speedVerti = -self.min_jumpspeed

        self.prev_key = key

        # gravity
        if self.speedVerti < 10 and not onground:  # 9.8 rounded up
            self.speedVerti += self.gravity

        if onground and self.speedVerti > 0:
            self.speedVerti = 0

        # movement
        self.move(self.speedHori, self.speedVerti)

    def inputs(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

    def check_collision(self, x, y):
        collide = False
        self.pos += [x,y]
        self.rect.midbottom = self.pos
        for e in self.blockRECT.values():
            for i in e :
                if pygame.Rect.colliderect(self.rect, i) == True:
                    collide = True
        self.pos += [-x,-y]
        self.rect.midbottom = self.pos
        return collide
    
    def move(self,x,y):
        dx = x
        dy = y
        
        while self.check_collision(0, dy):
            dy -= numpy.sign(dy)

        while self.check_collision(dx, dy):
            dx -= numpy.sign(dx)
        
        self.pos += [dx,dy]

        self.rect.midbottom = self.pos

    def update(self):
        self.inputs()
        self.updateTuto()
        self.draw()
        

class World:
    def __init__(self,screen) -> None:
        self.updateBL = False
        self.tqt = 0
        self.width , self.height = screen.get_size()[0],screen.get_size()[1]
        self.screen = screen
        self.world = self.get_txt('world')
        self.blockSize = screen.get_size()[1]/15
        self.decalage = 0
        self.briqueimgOrigignal = {}
        self.briqueimg = {}
        self.players = {}
        self.instruDict = {}
        self.monstre = {}
        self.dicoInstru(self.get_txt('block'))
        
        for name in os.listdir('assets/world'):
            self.briqueimgOrigignal[name] = pygame.transform.scale(pygame.image.load('assets/world/{}'.format(name)),(self.blockSize,self.blockSize))
            self.briqueimg[name] = pygame.transform.scale(pygame.image.load('assets/world/{}'.format(name)),(self.blockSize,self.blockSize))
        


        self.liste = []
        self.elementIntoListe()
        self.blockRECT = {"#":[],"?":[]}
        for e in self.liste:
            if e[2] == '#':
                rect = pygame.Rect(e[1]*self.blockSize-self.decalage, e[0]*self.blockSize, self.blockSize, self.blockSize)
                self.blockRECT["#"].append(rect)
            elif e[2] == '?':
                rect = pygame.Rect(e[1]*self.blockSize-self.decalage, e[0]*self.blockSize, self.blockSize, self.blockSize)
                self.blockRECT["?"].append(rect)
        
        for name in os.listdir('assets/players'):
            self.players[name] = Entity(self.screen,self.blockRECT,name,True)
        for name in os.listdir('assets/monstres'):
            self.monstre[name] = Entity(self.screen,self.blockRECT,name,False)

    def get_txt(self,nom):
        file = open(f'{nom}.txt', 'r')
        data = file.read()
        liste = data.split("\n")
        file.close()
        return liste
    
    def dicoInstru(self,liste):
        for i in liste:
            c = 0
            on_liste = False
            chaineCAr = ""
            for lettre in i:
                if c == 0:
                    self.instruDict[i[0]] = []
                    c = 1
                    continue
                else:
                    if lettre == '[':
                        continue
                    elif lettre != ',' and lettre != ']' and lettre != ':' and lettre != '':
                        chaineCAr = chaineCAr + lettre
                    if lettre == ']' or lettre == ',':
                        self.instruDict[i[0]].append(chaineCAr)
                        chaineCAr = ''
                        if lettre == ']':
                            break

    
    def elementIntoListe(self):
        for ligne in range(len(self.world)):
            if self.world[ligne] != '':
                for e in range(len(self.world[ligne])):
                    if self.world[ligne][e] == '#':
                        self.liste.append([ligne,e,'#'])
                    elif self.world[ligne][e] == '?':
                        self.liste.append([ligne,e,'?'])

    def draw_on_screen(self):
        if self.updateBL:
            self.blockRECT["#"] = []
            self.blockRECT["?"] = []
        for e in self.liste:   
            if e[2] == '#':
                if not self.updateBL:
                    rect = pygame.Rect(e[1]*self.blockSize-self.decalage, e[0]*self.blockSize, self.blockSize, self.blockSize)
                    self.screen.blit(self.briqueimg['brique.png'],rect)
                else:
                    rect = pygame.Rect(e[1]*self.blockSize, e[0]*self.blockSize, self.blockSize, self.blockSize)
                    self.blockRECT["#"].append(rect)
                    
                
            elif e[2] == '?':
                rect = pygame.Rect(e[1]*self.blockSize-self.decalage, e[0]*self.blockSize, self.blockSize, self.blockSize)
                if self.updateBL:
                    self.blockRECT["?"].append(rect)
                self.decalage *= self.width / self.screen.get_size()[0]
                pygame.draw.rect(self.screen, "yellow", rect ,2)   
        self.updateBL = False


    def scrolling(self):
        for name in self.players:
            if self.players[name].rect.x-self.players[name].decalage >= self.width*0.75-self.decalage:     
                self.decalage += self.players[name].speedHori
                self.players[name].decalage = self.decalage

            if self.players[name].rect.x-self.players[name].decalage <= self.width*0.25-self.decalage and self.decalage>0:     
                self.decalage += self.players[name].speedHori
                self.players[name].decalage = self.decalage
            


    def inputs(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            self.decalage +=5
            self.players['Mario.png'].decalage +=5
        if keys[pygame.K_q]:
            self.decalage -=5
            self.players['Mario.png'].decalage -=5



    def update(self):
        self.inputs()
        self.scrolling()
        self.draw_on_screen()
        for personnage in self.players:
            self.players[personnage].update()
        for monstres in self.monstre:
            self.monstre[monstres].update()
        

   

jeu = Jeu()
while True :
    jeu.update()