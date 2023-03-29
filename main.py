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
                    jeu.res = i
                elif i == 'retour':
                    self.position = 'main'
                else:
                    self.screen = pygame.display.set_mode((0,0),FULLSCREEN)
                    jeu.res = 1
            self.screen.blit(image,imagerect)
            c += 1


    def update(self):
        self.on_est_ou()
        pygame.display.flip()

class Jeu:
    def __init__(self) -> None:
        self.width , self.height = get_monitors()[0].width * 0.75,get_monitors()[0].height * 0.75
        self.screen = pygame.display.set_mode((int(self.width),int(self.height)))
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
        self.res = 0.75
        self.menuIMG = {img: pygame.image.load(f'assets/menu/{img}') for img in os.listdir('assets/menu')} #est-ce que c'est pas magnifique ça, toutes les images load en une ligne
        for clef in self.menuIMG:
            if 'carte' in clef:
                self.menuIMG[clef] = pygame.transform.scale(self.menuIMG[clef],(self.screen.get_size()[0]*2,self.screen.get_size()[1]))
            elif 'niveau' in clef:
                self.menuIMG[clef] = pygame.transform.scale(self.menuIMG[clef],(self.screen.get_size()[1]/20,self.screen.get_size()[1]/20))
        
    
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
        #self.screen.blit(self.menuIMG[f'{self.monde} carte.png'],(0,0))
        self.screen.fill('black')
        c = 0
        for niveau in self.listeMondes[self.monde]:
            niveautxt = self.font.render(f"{niveau}",True,(255,255,255))
            niveaurect = niveautxt.get_rect()
            niveaurect.y = niveaurect.height * c
            if niveaurect.left <= pygame.mouse.get_pos()[0] <= niveaurect.right and niveaurect.top <= pygame.mouse.get_pos()[1] <= niveaurect.bottom and pygame.mouse.get_pressed()[0] and self.cooldown > self.COOLDOWN:
                self.cooldown = 0
                self.classDict['monde'] = World(self.screen,f'{self.monde}/{niveau}',f'sauvegardes/save{self.cSauv}.txt',self.res)
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
            save.write(f'M:{mondes}\nN:{niveaux}\nV:{vies}\nS:{[score,pieces]}')
    
    def nbJoueurs(self):
        self.screen.fill('black')
        for i in range(1,5):
            itxt = self.font.render(str(i),True,(255,255,255))
            iRect = itxt.get_rect()
            iRect.y = iRect.height * (i-1)
            if iRect.left < pygame.mouse.get_pos()[0] < iRect.right and iRect.top < pygame.mouse.get_pos()[1] < iRect.bottom and pygame.mouse.get_pressed()[0] and self.cooldown > self.COOLDOWN:
                self.nouvelle_sauvegarde(['plains'],['plains-1'],[5]*4,0,0)
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

    def Affichefps(self):
        test = self.font.render("fps : "+str(round(self.clock.get_fps())),True,(255,255,255))
        self.screen.blit(test,(500,0))


    def update(self):

        self.on_est_ou()
        if self.classPos != '':
            self.classDict[self.classPos].update()
        self.inputs()
        self.Affichefps()
        pygame.display.flip()
        self.clock.tick(60)

class Players:
    def __init__(self,screen,blockRECT,name,joueur) -> None:
        self.screen = screen
        self.blockRECT = blockRECT
        self.playerSize = self.screen.get_size()[0] * 0.00003
        self.decalage = 0
        self.speed = round(screen.get_size()[0] * 0.006)
        self.joueur = joueur
        self.original = pygame.image.load('assets/players/{}'.format(name))
        self.pos = vec((10, 360))
        self.height, self.width = self.original.get_size()
        self.image = pygame.transform.scale(self.original,(self.height * self.playerSize ,self.width * self.playerSize))
        self.rect = self.image.get_rect()
        self.pos = vec((200, 0))
        self.jumpspeed = self.screen.get_size()[1] * 0.031
        self.speedVerti = 0
        self.speedHori = 0
        self.gravity = self.screen.get_size()[1] * 0.0015
        self.min_jumpspeed = 4
        self.prev_key = pygame.key.get_pressed()
            

    def draw(self):
        self.rect.x -= self.decalage
        
        rect2 = self.rect.copy()
        rect2[2] /= 16
        rect2[0] += rect2[2]*8
        
        #pygame.draw.rect(self.screen, "blue", rect2,5)     #Pour verifier les collisions
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

        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.joueur and self.pos[0] > 100:
            self.speedHori = -self.speed
        elif key[pygame.K_RIGHT] and self.joueur:
            self.speedHori = self.speed

        if key[pygame.K_UP] and onground and self.joueur:
            self.speedVerti = -self.jumpspeed

        if self.prev_key[pygame.K_UP] and not key[pygame.K_UP]:
            if self.speedVerti < -self.min_jumpspeed:
                self.speedVerti = -self.min_jumpspeed

        self.prev_key = key

        if not onground:
            self.speedVerti += self.gravity 

        if onground and self.speedVerti > 0:
            self.speedVerti = 0

        self.move(self.speedHori, self.speedVerti)

    def check_collision(self, x, y, general=True , plusPetit = False):
        collide = False
        self.pos += [x,y]

        self.rect.midbottom = self.pos
        blocsPrincip = []
        
        for e in self.blockRECT:
            c = -1
            for i in self.blockRECT[e]:
                c += 1
                if not plusPetit:
                    if pygame.Rect.colliderect(self.rect, i[0]):
                        tempo = copy.deepcopy(i) #tout les jours fuck le systeme de pointage jsp quoi de python all my homis hate this shit heuresement que copy existe 
                        if i[2][8] and tempo[2][9]: 
                            tempo[2][9] = False
                            self.blockRECT[e][c] = tempo
                            jeu.classDict['monde'].sauvegarde['S'][0] += 1
                            if jeu.classDict['monde'].sauvegarde['S'][0] >= 100:
                                jeu.classDict['monde'].sauvegarde['S'][0] = 0
                                for index in range(len(jeu.classDict['monde'].sauvegarde['V'])):
                                    jeu.classDict['monde'].sauvegarde['V'][index] += 1

                        if general != False: 
                            
                            test = self.check_collision(0, -1, False , True)
                            if i[2][2] and not i[2][5] and self.speedVerti < 0 and test[0]:
                                tempo[2][5] = True
                
                        if i[2][1]: # i[2][1] --> True ou False, correspond a si le bloc est sensé avoir une collision ou non
                            self.blockRECT[e][c] = tempo
                            collide = True
                    
                else:
                    rect2 = self.rect.copy()
                    rect2[2] /= 16
                    rect2[0] += rect2[2]*8
                    
                    if pygame.Rect.colliderect(rect2, i[0]) and i[2][2] and not i[2][5] :
                        collide = True
                        blocsPrincip.append(i)
                    
        self.pos += [-x,-y]
        self.rect.midbottom = self.pos

        return (collide,blocsPrincip)
            
    
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

class Mobs:
    def __init__(self,screen,blockRECT,name,joueur) -> None:
        self.screen = screen
        self.blockRECT = blockRECT
        self.playerSize = self.screen.get_size()[0] * 0.00003
        self.decalage = 0
        self.speed = round(screen.get_size()[0] * 0.006) 
        self.joueur = joueur
        self.original = pygame.image.load('assets/monstres/{}'.format(name))
        self.speed = 3
        
        self.height, self.width = self.original.get_size()
        self.image = pygame.transform.scale(self.original,(self.height * self.playerSize ,self.width * self.playerSize))
        self.rect = self.image.get_rect()
        self.pos = vec((500, 0))
        self.jumpspeed = self.screen.get_size()[1] * 0.031
        self.speedVerti = 0
        self.speedHori = 0
        self.gravity = self.screen.get_size()[1] * 0.0015
        self.min_jumpspeed = 4
        self.left = False
        self.right = True
            

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
        onground = self.check_collision(0, 1)[0]

        if self.check_collision(1,0)[0]:
            self.left = True
            self.right = False
            
        if self.check_collision(-1,0)[0]:
            self.left = False
            self.right = True
        
        if self.left:
            self.speedHori = -self.speed
        elif self.right:
            self.speedHori = self.speed

        if not onground:  
            self.speedVerti += self.gravity 

        self.move(self.speedHori, self.speedVerti)

    def check_collision(self, x, y, general=True , plusPetit = False):
        collide = False
        self.pos += [x,y]

        self.rect.midbottom = self.pos
        blocsPrincip = []
        
        for e in self.blockRECT:
            for i in self.blockRECT[e]:
                if pygame.Rect.colliderect(self.rect, i[0]):
                    if i[2][1]: # i[2][1] --> True ou False, correspond a si le bloc est sensé avoir une collision ou non
                        collide = True
                    
                    
        self.pos += [-x,-y]
        self.rect.midbottom = self.pos
        

        return (collide,blocsPrincip)
            
    
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
    def __init__(self,screen,chemin,sauv,res) -> None:
        self.res = res
        self.quotient = screen.get_size()[0] / 1920
        self.width , self.height = screen.get_size()
        self.screen = screen
        self.world = self.get_txt(chemin)
        self.blockSize = int(screen.get_size()[1]/15)
        self.decalage = 0
        self.imagesWorldOrigignal = {}
        self.imagesWorld = {}
        self.players = {}
        self.instruDict = self.dicoInstru(self.get_txt('block.txt'))
        self.sauvegarde = self.dicoInstru(self.get_txt(sauv))
        self.sauv = sauv
        self.chemin = chemin
        self.monstre = {}
        self.font = pygame.font.SysFont('Arial',32)
        self.othersIMG = {img: pygame.image.load(f'assets/world/others/{img}').convert_alpha() for img in os.listdir('assets/world/others')}
        for i in self.othersIMG:
            if 'fond' in i:
                scale = self.othersIMG[i].get_size()
                self.othersIMG[i] = pygame.transform.scale(self.othersIMG[i],(scale[0]*self.quotient,scale[1]*self.quotient ))
        for name in os.listdir('assets/world/blocs'):
            self.imagesWorld[name] = pygame.image.load('assets/world/blocs/{}'.format(name)).convert_alpha()
        
        for image in self.instruDict:
            self.imagesWorld[self.instruDict[image][0]] = pygame.transform.scale(self.imagesWorld[self.instruDict[image][0]],(self.blockSize * float(self.instruDict[image][6]), self.blockSize * float(self.instruDict[image][7])))
            if self.instruDict[image][2]:
                self.imagesWorld[self.instruDict[image][4]] = pygame.transform.scale(self.imagesWorld[self.instruDict[image][4]],(self.blockSize * float(self.instruDict[image][6]), self.blockSize * float(self.instruDict[image][7])))
        self.liste = []
        self.elementIntoListe()
        
        self.initialiseDicoBloc()
        
        for name in os.listdir('assets/players'):
            self.players[name] = Players(self.screen,self.blockRECT,name,True)
        for name in os.listdir('assets/monstres'):
            self.monstre[name] = Mobs(self.screen,self.blockRECT,name,False)
    

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
                    rect = pygame.Rect(e[1]* self.blockSize-self.decalage, e[0]*self.blockSize, self.blockSize * self.instruDict[instru][6], self.blockSize *  self.instruDict[instru][7])
                    self.blockRECT[instru].append([rect,instru,self.instruDict[instru]])

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
                        elif self.savoirSiFloat(chaineCAr) or self.savoirSiFloat(chaineCAr[1:]):
                            chaineCAr = float(chaineCAr)
                        dict_[i[0]].append(chaineCAr)
                        chaineCAr = ''
                        if lettre == ']':
                            break
        return dict_
         
    def savoirSiFloat(self,elt) -> bool:
        try:
            float(elt)
            return True
        except ValueError:
            return False
        
    def elementIntoListe(self):
        for ligne in range(len(self.world)):
            if self.world[ligne] != '':
                for e in range(len(self.world[ligne])):
                    for instru in self.instruDict:
                        if self.world[ligne][e] == instru:
                            self.liste.append([ligne,e,instru])

    def draw_on_screen(self):
        a = self.chemin[:self.chemin.index('/')]
        self.screen.blit(self.othersIMG[f'{a}-fond.png'],(-self.decalage,-self.screen.get_size()[0]*0.07))
        self.screen.blit(self.font.render(str(self.sauvegarde['S'][0]),True,(255,255,255)),(0,0))
        for keys in self.blockRECT :
            for i in self.blockRECT[keys]:
                if i[2][9]:
                    rect = pygame.Rect(i[0][0]-self.decalage, i[0][1], self.blockSize, self.blockSize)

                    if not i[2][5]:
                        self.screen.blit(self.imagesWorld[self.instruDict[i[1]][0]],rect)
                    else:
                        self.screen.blit(self.imagesWorld[self.instruDict[i[1]][4]],rect)

                      


    def scrolling(self):
        """
        C'est mieux un scrolling centré en vrai ? 
        """
        for name in self.players:
            if self.players[name].rect.x-self.players[name].decalage >= self.width*0.55-self.decalage:
                self.decalage += self.players[name].speedHori
                self.players[name].decalage = self.decalage
                for nameMonstre in self.monstre :
                    self.monstre[nameMonstre].decalage = self.decalage

            if self.players[name].rect.x-self.players[name].decalage <= self.width*0.45-self.decalage and self.decalage>0:     
                self.decalage += self.players[name].speedHori
                self.players[name].decalage = self.decalage
                for nameMonstre in self.monstre :
                    self.monstre[nameMonstre].decalage = self.decalage
            


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
        jeu.nouvelle_sauvegarde(lVal[0],lVal[1],lVal[2],lVal[3][0],lVal[3][1])


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
