import pygame 
from pygame.locals import *
import os
import copy
import numpy
from screeninfo import get_monitors
pygame.init()
vec = pygame.math.Vector2

class Menu:
    def __init__(self,screen) -> None:
        self.screen = screen
        self.font = pygame.font.SysFont('Arial', 32)
        self.fullscreen = False
        self.etat = True
        self.position = 'main'
        self.cooldown = 0
        self.COOLDOWN = 30    
    def on_est_ou(self):
        if self.position == 'main':
            self.cooldown += 1
            self.main()
        elif self.position == 'optionRes':
            self.cooldown += 1
            self.optionRes()
        elif self.position == 'jouer':
            jeu.classPos = ''
            jeu.position = 'saves'
   
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
        
        if  resRect.x <= self.x <= resRect.width and resRect.y <= self.y <= resRect.height and pygame.mouse.get_pressed()[0] and self.cooldown > self.COOLDOWN:
            self.position = 'optionRes'
            self.cooldown = 0
        if  jouerRect.left <= self.x <= jouerRect.right and jouerRect.y <= self.y <= jouerRect.bottom and pygame.mouse.get_pressed()[0] and self.cooldown > self.COOLDOWN:
            self.position = 'jouer'
            self.cooldown = 0
        
        
        self.screen.blit(res,resRect)
        self.screen.blit(jouer,jouerRect)
    
    def optionRes(self):
        self.screen.fill('blue') # elle est pour toi celle la Maelan 
        l = [0.25,0.5,0.75,'fullscreen','retour']
        c = 0
        for i in l:
            if i != 'fullscreen' and i != 'retour':
                image = self.font.render(str(get_monitors()[0].width * i)+'x' + str(get_monitors()[0].height * i),True,(255,255,255))
            else:
                image = self.font.render(str(i),True,(255,255,255))
            imagerect = image.get_rect()
            imagerect.y = imagerect.bottom * c 
            if imagerect.left <= pygame.mouse.get_pos()[0] <= imagerect.right and imagerect.top <= pygame.mouse.get_pos()[1] <= imagerect.bottom and pygame.mouse.get_pressed()[0] and self.cooldown > self.COOLDOWN:
                self.cooldown = 0
                if i != 'fullscreen' and i != 'retour':
                    self.width , self.height = get_monitors()[0].width * i ,get_monitors()[0].height * i
                    self.screen = pygame.display.set_mode((self.width, self.height))
                elif i == 'retour':
                    self.position = 'main'
                else:
                    self.screen = pygame.display.set_mode((0,0),FULLSCREEN)
            self.screen.blit(image,imagerect)
            c += 1


    def update(self):
        self.on_est_ou()
        pygame.display.flip()

class Jeu:
    def __init__(self) -> None:
        self.width , self.height = get_monitors()[0].width * 0.75,get_monitors()[0].height * 0.75
        self.screen = pygame.display.set_mode((self.width,self.height))
        self.classDict = {'menu' : Menu(self.screen),'monde' : None}
        self.font = pygame.font.SysFont('Arial', 32)
        self.clock = pygame.time.Clock()
        self.listeMondes = {'plains' : os.listdir('plains') } #,'desert' : os.listdir('desert')}
        self.position = ''
        self.classPos = 'menu'
        self.monde = ''
        self.cooldown = 0
        self.COOLDOWN = 10
        self.joueur = {}
        self.cSauv = 0
        
    
    def inputs(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        
    def window_world(self):
        self.screen.fill('black')
        c = 0
        for monde in self.listeMondes:
            mondetxt = self.font.render(f"{monde}",True,(255,255,255))
            monderect = mondetxt.get_rect()
            monderect.y = monderect.height * c
            if monderect.left <= pygame.mouse.get_pos()[0] <= monderect.right and monderect.top <= pygame.mouse.get_pos()[1] <= monderect.bottom and pygame.mouse.get_pressed()[0]  and self.cooldown > self.COOLDOWN:
                self.cooldown = 0
                self.position = 'niveau'
                self.monde = monde
            self.screen.blit(mondetxt,monderect)
            c += 1
    
    def window_niveau(self):
        self.screen.fill('black')
        c = 0
        for niveau in self.listeMondes[self.monde]:
            niveautxt = self.font.render(f"{niveau}",True,(255,255,255))
            niveaurect = niveautxt.get_rect()
            niveaurect.y = niveaurect.height * c
            if niveaurect.left <= pygame.mouse.get_pos()[0] <= niveaurect.right and niveaurect.top <= pygame.mouse.get_pos()[1] <= niveaurect.bottom and pygame.mouse.get_pressed()[0] and self.cooldown > self.COOLDOWN:
                self.cooldown = 0
                self.classDict['monde'] = World(self.screen,f'{self.monde}/{niveau}',f'sauvegardes/save{self.cSauv}.txt')
                self.position = ''
                self.classPos = 'monde'
            self.screen.blit(niveautxt,niveaurect)
            c += 1
    
    def saves(self):
        self.screen.fill('black')
        sauvListe = [None] * 3
        for i in os.listdir('sauvegardes'):
            sauvListe[int(i[-5])-1] = i
        c = 0
        for saves in sauvListe:
            savetxt = self.font.render(str(saves),True,(255,255,255))
            saveRect = savetxt.get_rect()
            saveRect.y = saveRect.height * c
            if saveRect.left < pygame.mouse.get_pos()[0] < saveRect.right and saveRect.top < pygame.mouse.get_pos()[1] < saveRect.bottom and pygame.mouse.get_pressed()[0] and self.cooldown > self.COOLDOWN:
                self.cooldown = 0
                if saves != None:
                    self.position = 'monde'
                    self.cSauv = c + 1
                else:
                    self.position = 'nbJoueurs'
                    self.cSauv = c + 1
            self.screen.blit(savetxt,saveRect)
            c += 1

    def nouvelle_sauvegarde(self,mondes : list,niveaux : list,vies : list,score : int,pieces : int):
        with open(f"sauvegardes/save{self.cSauv}.txt", "w") as save:
            save.write(f'M:{mondes}\nN:{niveaux}\nV:{vies}\nS:{score}\nP:{pieces}\n')
    
    def nbJoueurs(self):
        self.screen.fill('black')
        for i in range(1,5):
            itxt = self.font.render(str(i),True,(255,255,255))
            iRect = itxt.get_rect()
            iRect.y = iRect.height * (i-1)
            if iRect.left < pygame.mouse.get_pos()[0] < iRect.right and iRect.top < pygame.mouse.get_pos()[1] < iRect.bottom and pygame.mouse.get_pressed()[0] and self.cooldown > self.COOLDOWN:
                self.nouvelle_sauvegarde(['plains'],['plains-1'],[5]*4,[0],[0])
                self.position = 'monde'
            self.screen.blit(itxt,iRect)


    def on_est_ou(self):
        if self.position == 'saves':
            self.cooldown += 1
            self.saves()
        elif self.position == 'nbJoueurs':
            self.cooldown += 1
            self.nbJoueurs()
        elif self.position == 'monde':
            self.cooldown += 1
            self.window_world()
        elif self.position == 'niveau':
            self.cooldown += 1
            self.window_niveau()


    def update(self):
        self.on_est_ou()
        if self.classPos != '':
            self.classDict[self.classPos].update()
        self.inputs()
        pygame.display.flip()
        self.clock.tick(60)

class Entity:
    def __init__(self,screen,blockRECT,name,joueur) -> None:
        self.qJump = 1
        self.screen = screen
        self.blockRECT = blockRECT
        self.playerSize = self.screen.get_size()[0] * 0.00003
        self.decalage = 0
        self.speed = round(screen.get_size()[0] * 0.006) 
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
        self.image = pygame.transform.scale(self.original,(self.height * self.playerSize ,self.width * self.playerSize))
        self.rect = self.image.get_rect()
        self.pos = vec((200, 0))
        self.jumpspeed = self.screen.get_size()[1] * 0.031
        self.speedVerti = 0
        self.speedHori = 0
        self.gravity = self.screen.get_size()[1] * 0.0015
        print(self.gravity)
        self.min_jumpspeed = 4
        self.prev_key = pygame.key.get_pressed()
            

    def draw(self):
        self.rect.x -= self.decalage
        
        rect2 = self.rect.copy()
        rect2[2] /= 2
        #pygame.draw.rect(self.screen, "blue", rect2,5)
        
        
        #pygame.draw.rect(self.screen, "red", self.rect,5)
        self.screen.blit(self.image,self.rect)
    
    def animation(self):
        if self.speedHori > 0:
            self.image = pygame.transform.scale(self.original,(self.height * self.playerSize,self.width *self.playerSize))
        else:
            self.image = pygame.transform.scale(pygame.transform.flip(self.original, 1, 0),(self.height * self.playerSize,self.width *self.playerSize))

    def deplacement(self):
        self.speedHori *= 0.88
        onground = self.check_collision(0, 1)[0]
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

        if not onground:  # 9.8 rounded up
            self.speedVerti += self.gravity 

        if onground and self.speedVerti > 0:
            self.speedVerti = 0

        # movement
        self.move(self.speedHori, self.speedVerti)

    def check_collision(self, x, y, general=True , plusPetit = False):
        collide = False

        self.pos += [x,y]
        self.rect.midbottom = self.pos
        blocsPrincip = []
        for e in self.blockRECT.values():
            for i in e :
                
                if not plusPetit:
                    
                    if pygame.Rect.colliderect(self.rect, i[0]):
                        if general != False:
                            self.collideBlockSpe(i,'?',True,"0")
                        collide = True
                        blocsPrincip.append(i)
                else:
                    rect2 = self.rect.copy()
                    rect2[2] /= 2
                    if pygame.Rect.colliderect(rect2, i[0]):
                        if general != False:
                            self.collideBlockSpe(i,'?',True,"0")
                        collide = True
                        blocsPrincip.append(i)
                    
                    
        self.pos += [-x,-y]
        self.rect.midbottom = self.pos
        

            
        
        return (collide,blocsPrincip)            # enlever bP
    
    
    def collideBlockSpe(self,bloc,symbole,doitChanger,changement=""):         # a terminer pou verfier qu'on touche QUE le bloc mys
        if self.speedHori > 0:
            coll = self.check_collision(-7,-1,False)
        else:
            coll = self.check_collision(7,-1,False)
            
    
        
        if bloc[1] == symbole and self.speedVerti < 0 and coll[0] and not self.check_collision(0, -1, False , True)[0]:
            if doitChanger:
                liste = jeu.classDict['monde'].blockRECT[symbole]
                for i in range(len(liste)) :
                    if liste[i][0] == bloc[0]:
                        jeu.classDict['monde'].blockRECT[symbole][i][1] = changement
            return True
        else:
            return False
            
                    
        
    
    def move(self,x,y):
        dx = x
        dy = y
        
        while self.check_collision(0, dy)[0]:
            dy -= numpy.sign(dy)

        while self.check_collision(dx, dy)[0]:
            dx -= numpy.sign(dx)
        
        self.pos += [dx,dy]

        self.rect.midbottom = self.pos
        
        if self.check_collision(0, -1)[0]:
            self.speedVerti = 0

    def update(self):
        self.deplacement()
        self.animation()
        self.draw()
        

class World:
    def __init__(self,screen,chemin,sauv) -> None:
        self.updateBL = False
        self.width , self.height = screen.get_size()
        self.screen = screen
        self.world = self.get_txt(chemin)
        self.blockSize = screen.get_size()[1]/15
        self.decalage = 0
        self.briqueimgOrigignal = {}
        self.briqueimg = {}
        self.players = {}
        self.instruDict = self.dicoInstru(self.get_txt('block.txt'))
        self.sauvegarde = self.dicoInstru(self.get_txt(sauv))
        self.sauv = sauv
        self.monstre = {}
        self.font = pygame.font.SysFont('Arial',32)
        
        for name in os.listdir('assets/world'):
            self.briqueimgOrigignal[name] = pygame.transform.scale(pygame.image.load('assets/world/{}'.format(name)),(self.blockSize,self.blockSize))
            self.briqueimg[name] = pygame.transform.scale(pygame.image.load('assets/world/{}'.format(name)),(self.blockSize,self.blockSize))

        self.liste = []
        self.elementIntoListe()
        
        self.initialiseDicoBloc()
        
        for name in os.listdir('assets/players'):
            self.players[name] = Entity(self.screen,self.blockRECT,name,True)
        for name in os.listdir('assets/monstres'):
            self.monstre[name] = Entity(self.screen,self.blockRECT,name,False)
    

    def get_txt(self,chemin):
        file = open(f'{chemin}', 'r')
        data = file.read()
        liste = data.split("\n")
        file.close()
        return liste
    
    def initialiseDicoBloc(self):
        self.blockRECT = {}
        for i in self.instruDict:
            self.blockRECT[i] = []
        for e in self.liste:
            for instru in self.instruDict:
                if e[2] == instru:
                    rect = pygame.Rect(e[1]*self.blockSize-self.decalage, e[0]*self.blockSize, self.blockSize, self.blockSize)
                    if self.instruDict[instru][1]:
                        self.blockRECT[instru].append([rect,instru])

    def mort(self):
        c = 0
        for i in self.players:
            if self.players[i].rect.y >= self.screen.get_size()[1]:
                self.sauvegarde['V'][c] -= 1
                self.save()
                jeu.position = 'niveau'
                jeu.classPos = ''
            c+=1
    
    def dicoInstru(self,liste):
        dict_ = {}
        for i in liste:
            c = 0
            chaineCAr = ""
            for lettre in i:
                if c == 0:
                    dict_[i[0]] = []
                    c = 1
                    continue
                else:
                    if lettre == '[':
                        continue
                    elif lettre != ',' and lettre != ']' and lettre != ':' and lettre != '' and lettre != '"' and lettre != "'":
                        chaineCAr = chaineCAr + lettre
                    if lettre == ']' or lettre == ',':
                        
                        if chaineCAr == 'True':
                            chaineCAr = True
                        elif chaineCAr == 'False':
                            chaineCAr = False
                        elif chaineCAr == 'None' or chaineCAr == ' None':
                            chaineCAr = None
                        elif chaineCAr.isdigit() or chaineCAr[1:].isdigit():
                            chaineCAr = int(chaineCAr)
                        dict_[i[0]].append(chaineCAr)
                        chaineCAr = ''
                        if lettre == ']':
                            break
        return dict_
        

    
    def elementIntoListe(self):
        for ligne in range(len(self.world)):
            if self.world[ligne] != '':
                for e in range(len(self.world[ligne])):
                    for instru in self.instruDict:
                        if self.world[ligne][e] == instru:
                            self.liste.append([ligne,e,instru])


    def draw_on_screen(self):
        self.screen.fill('black')
        for keys in self.blockRECT :
            for i in self.blockRECT[keys]:
                rect = pygame.Rect(i[0][0]-self.decalage, i[0][1], self.blockSize, self.blockSize)
                self.screen.blit(self.briqueimg[self.instruDict[i[1]][0]],rect)

                      


    def scrolling(self):
        """
        C'est mieux un scrolling centré en vrai ? 
        """
        for name in self.players:
            if self.players[name].rect.x-self.players[name].decalage >= self.width*0.51-self.decalage:     
                self.decalage += self.players[name].speedHori
                self.players[name].decalage = self.decalage

            if self.players[name].rect.x-self.players[name].decalage <= self.width*0.49-self.decalage and self.decalage>0:     
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
    
    def save(self):
        os.remove(self.sauv)
        lVal = list(self.sauvegarde.values())
        print(lVal)
        jeu.nouvelle_sauvegarde(lVal[0],lVal[1],lVal[2],lVal[3],lVal[4])


    def update(self):
        self.mort()
        self.inputsMouse()
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