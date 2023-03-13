import pygame 
from pygame.locals import *
import os
import copy
import numpy
from screeninfo import get_monitors
pygame.init()
vec = pygame.math.Vector2

class Menu:
    def __init__(self) -> None:
        self.width , self.height = get_monitors()[0].width * 0.75,get_monitors()[0].height * 0.75
        self.screen = pygame.display.set_mode((self.width,self.height))
        self.font = pygame.font.SysFont('Arial', 32)
        self.fullscreen = False
        self.etat = True
        self.position = 'main'
    
    def on_est_ou(self):
        if self.position == 'main':
            self.main()
        elif self.position == 'optionRes':
            self.optionRes()
        elif self.position == 'jouer':
            self.etat = False
   
    def main(self):
        self.screen.fill('black')
        self.x,self.y = pygame.mouse.get_pos()
        
        """
        Biensur ça va pas rester comme ça vu qu'il y aura des images ça sera des formules et les 'main' 'optionRes' machin trucs seront récupéré avec le nom des fichier comme 
        les mobs joueurs etc 
        """
        res = self.font.render("Resolution", True, (255, 255, 255))
        resRect = res.get_rect()
       
        jouer = self.font.render("jouer", True, (255, 255, 255))
        jouerRect = res.get_rect()
        jouerRect.y += resRect.height
        
        if  resRect.x <= self.x <= resRect.width and resRect.y <= self.y <= resRect.height and pygame.mouse.get_pressed()[0]:
            self.position = 'optionRes'
        if  jouerRect.left <= self.x <= jouerRect.right and jouerRect.y <= self.y <= jouerRect.bottom and pygame.mouse.get_pressed()[0]:
            self.position = 'jouer'
        
        
        self.screen.blit(res,resRect)
        self.screen.blit(jouer,jouerRect)
    
    def optionRes(self):
        self.screen.fill('blue') # elle est pour toi celle la Maelan 

    def update(self):
        self.on_est_ou()
        pygame.display.flip()

class Jeu:
    def __init__(self) -> None:
        self.etat = False
        self.menu = Menu()
        self.clock = pygame.time.Clock()
        self.world = World(self.menu.screen)
        
    
    def inputs(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

    def update(self):
        if not self.menu.etat:
            self.world.update()
        else:
            self.menu.update()
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
        self.jumpspeed = self.screen.get_size()[1] / 39
        self.speedVerti = 0
        self.speedHori = 0
        self.gravity = 1
        self.min_jumpspeed = 4
        self.prev_key = pygame.key.get_pressed()
            

    def draw(self):
        self.rect.x -= self.decalage
        self.screen.blit(self.image,self.rect)

    def animation(self):
        if self.speedHori > 0:
            self.image = pygame.transform.scale(self.original,(self.height * self.playerSize,self.width *self.playerSize))
        else:
            self.image = pygame.transform.scale(pygame.transform.flip(self.original, 1, 0),(self.height * self.playerSize,self.width *self.playerSize))



    def deplacement(self):
        self.speedHori *= 0.88
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
                if pygame.Rect.colliderect(self.rect, i[0]):
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
        self.deplacement()
        self.animation()
        self.draw()
        

class World:
    def __init__(self,screen) -> None:
        self.updateBL = False
        self.width , self.height = screen.get_size()[0],screen.get_size()[1]
        self.screen = screen
        self.world = self.get_txt('monde1/niveau1')
        self.blockSize = screen.get_size()[1]/15
        self.decalage = 0
        self.briqueimgOrigignal = {}
        self.briqueimg = {}
        self.players = {}
        self.instruDict = {}
        self.monstre = {}
        self.position = 'monde'
        self.dicoInstru(self.get_txt('block'))
        self.font = pygame.font.SysFont('Arial',32)
        
        for name in os.listdir('assets/world'):
            self.briqueimgOrigignal[name] = pygame.transform.scale(pygame.image.load('assets/world/{}'.format(name)),(self.blockSize,self.blockSize))
            self.briqueimg[name] = pygame.transform.scale(pygame.image.load('assets/world/{}'.format(name)),(self.blockSize,self.blockSize))

        self.liste = []
        self.elementIntoListe()
        self.blockRECT = {}
        for i in self.instruDict:
            self.blockRECT[i] = []
        for e in self.liste:
            for instru in self.instruDict:
                if e[2] == instru:
                    rect = pygame.Rect(e[1]*self.blockSize-self.decalage, e[0]*self.blockSize, self.blockSize, self.blockSize)
                    if self.instruDict[instru][1]:
                        self.blockRECT[instru].append((rect,instru))
        
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
                        
                        if chaineCAr == 'True':
                            chaineCAr = True
                        elif chaineCAr == 'False':
                            chaineCAr = False
                        elif chaineCAr == 'None':
                            chaineCAr = None
                        self.instruDict[i[0]].append(chaineCAr)
                        chaineCAr = ''
                        if lettre == ']':
                            break
        

    
    def elementIntoListe(self):
        for ligne in range(len(self.world)):
            if self.world[ligne] != '':
                for e in range(len(self.world[ligne])):
                    for instru in self.instruDict:
                        if self.world[ligne][e] == instru:
                            self.liste.append([ligne,e,instru])


    def draw_on_screen(self):
        if self.updateBL:
            for instru in self.instruDict:
                self.blockRECT[instru] = []
        for e in self.liste:  
            for instru in self.instruDict: 
                if e[2] == instru:
                    if not self.updateBL:
                        rect = pygame.Rect(e[1]*self.blockSize-self.decalage, e[0]*self.blockSize, self.blockSize, self.blockSize)
                        self.screen.blit(self.briqueimg[self.instruDict[instru][0]],rect)
                    else:
                        rect = pygame.Rect(e[1]*self.blockSize, e[0]*self.blockSize, self.blockSize, self.blockSize)
                        self.blockRECT[instru].append((rect,instru))
                      
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
        
    def inputsMouse(self):
        self.Mpos = pygame.mouse.get_pos()
        self.mouseDown = pygame.mouse.get_pressed()

    def on_est_ou(self):
        if self.position == 'monde':
            self.screen.fill('black')
            monde = self.font.render("monde1",True,(255,255,255))
            monderect = monde.get_rect()
            if monderect.left <= self.Mpos[0] <= monderect.right and monderect.top <= self.Mpos[1] <= monderect.bottom and self.mouseDown[0]:
                self.position = 'niveau'
            self.screen.blit(monde,monderect)
        elif self.position == 'niveau':
            self.screen.fill('black')
            niveau = self.font.render("niveau1",True,(255,255,255))
            niveaurect = niveau.get_rect()
            niveaurect.y = 50
            if niveaurect.left <= self.Mpos[0] <= niveaurect.right and niveaurect.top <= self.Mpos[1] <= niveaurect.bottom and self.mouseDown[0]:
                self.position = 'jeu'
            self.screen.blit(niveau,niveaurect)
        elif self.position == 'jeu':
            self.screen.fill('black')
            self.inputs()
            self.scrolling()
            self.draw_on_screen()
            for personnage in self.players:
                self.players[personnage].update()
            for monstres in self.monstre:
                self.monstre[monstres].update()



    def update(self):
        self.inputsMouse()
        self.on_est_ou()
        
        
jeu = Jeu()
while True :
    jeu.update()