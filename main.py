import pygame 
import pygame.freetype
from pygame.locals import *
import os
import copy
import numpy
import traceback
from random import randint
from screeninfo import get_monitors
pygame.init()
vec = pygame.math.Vector2

"""
La class Menu s'occupe de tout ce qui s'affiche à l'écran avant carte animé, c'est à dire gestion des touches de la résolution etc
"""

class Menu:
    def __init__(self,screen,font) -> None:
        self.settingsDict = {'Chargements' : None,'ShowFPS' : None} 
        self.font = font
        self.screen = screen
        self.screenSize = self.screen.get_size()
        self.quotient = self.screenSize[0] / 1920
        self.fullscreen = False
        self.etat = True
        self.position = 'main'
        self.cooldown = 0
        self.COOLDOWN = 5
        self.stop1ou2 = 1
        self.trouve = []
        
        #S'il manque le fichier de sauvegarde pour une raison x ou y le programme en créer un nouveau 
        if not 'settings.txt' in os.listdir():
            self.txtSettings([False,True])

        #récupère les données de la sauvegarde associée aux réglages définie à un moment données par l'utilisateur
        self.videoRegDict = {}
        with open ('settings.txt','r') as txt:
            c = -1
            l = list(self.settingsDict)
            for ligne in txt:
                if ligne != '':
                    c += 1
                    
                    ligne = ligne[:-1]
                    if 'False' in ligne:
                        ligne = False
                    elif 'True' in ligne:
                        ligne = True
                        
                    self.settingsDict[l[c]] = ligne
                
        listdirVanilla = os.listdir('vids_vanilla') #récupère la liste de tout les dossiers contenants les images constituant les différentes vidéos "vanilla", c'est-à-dire les premières, les orignials
        listdirVanilla.sort() #trie la liste car os ne le fait pas par défault (pourquoi ? aucune idée)
        
        self.dictVanilla = {i:os.listdir(f'vids_vanilla/{i}') for i in listdirVanilla} #organise toutes les images, la clef est le nom de dossier, trouvé dans listdirVanilla (exemple : 1 fond vanilla) et les valeurs sont les images
        self.dictVanillaOriginal = copy.deepcopy(self.dictVanilla) 
        self.nameDictVanilla = copy.deepcopy(self.dictVanilla)
        
        for clef in self.dictVanilla: 
            self.dictVanilla[clef].sort() 
    
        """
        ici même chose mais pour les images "spéciales". 
        Exemple, une image qui est au départ rouge mais quand et en contact avec le cuseur devient bleue, l'image vanilla sera la rouge et le bleu sera la spéciale.
        """
        self.dictSpe = {i:os.listdir(f'vids_special/{i}') for i in os.listdir('vids_special')} 
        self.dictSpeOriginal = copy.deepcopy(self.dictSpe)
        self.nameDictSpe = copy.deepcopy(self.dictSpe)
        for clef in self.dictSpe:
            self.dictSpe[clef].sort()
        
        self.menuIMGoriginal = {name : pygame.image.load(f'assets/menu/{name}').convert_alpha() for name in os.listdir('assets/menu')} #Les quelques images autre que les images vidéos sont chargé ici
        self.menuIMG = {}
        self.chargementIMG() #et son redimentionné ici (ligne 117)

        self.load = False
        if self.settingsDict['Chargements']: #Information récupérée ligne 35, correspond à si l'utilisateur veut avoir des chargements pour avoir une meilleure expérience visuelle ou non
            self.chargementMethode() #Si oui toutes les imes sont chargé dans cette méthode
            self.load = True
        
        self.inverse = False
        self.clefactuel = 0
        self.fade = 0
        self.flip = False
        
        #si aucun fichier de sauvegarde pour les touches n'a été trouvé le programme en crée un nouveau avec les touches par défault
        self.listeTouches = ['Gauche','Droite','Saut','Attaque']
        if not 'touches.txt' in os.listdir():
            self.txtTouches([1073741904,1073741903,1073741906,32]) #code pygame des touches

        self.touchesDict = {}
        with open ('touches.txt','r') as txt: 
            c = -1
            for ligne in txt:
                if ligne != '':
                    c += 1
                    if c != len(self.listeTouches) -1:
                        ligne = ligne[:-1]
                    self.touchesDict[self.listeTouches[c]] = int(ligne)
        
        self.plusagauche = self.screenSize[0]
        self.changeKey = [False,None,None,False]
        self.doubleTouche = ''
        self.tpsAffichageDB = 0
        self.inverseDB = False

        self.selectSave = None
        self.cSauv = 0
        self.lancementSansSave = False
        self.compteurSansSave = 0

        if self.settingsDict['Chargements']:
            self.stop = False
        else:
            self.stop = True

        self.chargement = False

    """
    Redimentionne les images n'appartenant pas à une vidéo
    """
    def chargementIMG(self):
        self.dictSize = {
            'engrenage.png' : (0.000014,2),
            'chargement.png' : (1,None),
            'case vert.png' : (0.00007,2),
            'logo.png' : (0.00022,1),
            'pintendo blanc logo.png' : (0.000105,2),
            'pintendo logo.png' : (0.000105,2),
        }

        for image in self.menuIMGoriginal:
            if self.dictSize[image][1] != None:
                scale = (self.menuIMGoriginal[image].get_size()[0] * round(self.dictSize[image][0] * self.screenSize[0],self.dictSize[image][1]),self.menuIMGoriginal[image].get_size()[1] * round(self.dictSize[image][0] * self.screenSize[0],self.dictSize[image][1]))
            else:
                scale = self.screenSize
            self.menuIMG[image] = pygame.transform.scale(self.menuIMGoriginal[image],scale)

    """
    Lance une page de chargements avec un indicateur de progression (barre blanche et pourcentage de l'action effectué)
    """
    def chargementMethode(self,load = False):
        if not load:
            self.load = True
        self.fade = 0
        c2 = 0
        for clef in self.dictVanilla:
            longeur = len(self.dictVanilla[clef]) * 2
            c = -1
            for i in self.dictVanilla[clef]:
                c += 1
                if self.menuIMG['chargement.png'].get_size()[0] != self.screenSize[0]:
                    self.menuIMG['chargement.png'] = pygame.transform.scale(self.menuIMGoriginal['chargement.png'],self.screenSize)
                surface = self.menuIMG['chargement.png']
                surface.set_alpha(c2/2.5)
                self.screen.fill((0,0,0))
                self.screen.blit(surface,(0,0))
                if not load:
                    if not 'Surface' in str(i):
                        if 'clic' in clef:
                            self.dictSpeOriginal[clef][c] = pygame.image.load(f'vids_special/{clef}/{i}').convert_alpha()
                            self.dictSpe[clef][c] = pygame.transform.scale(self.dictSpeOriginal[clef][c],self.screenSize)

                        self.dictVanillaOriginal[clef][c] = pygame.image.load(f'vids_vanilla/{clef}/{i}').convert_alpha()
                        self.dictVanilla[clef][c] = pygame.transform.scale(self.dictVanillaOriginal[clef][c],self.screenSize)
                    
                else:
                    if 'clic' in clef:
                        if not 'png' in str(self.dictSpe[clef][c]):
                            self.dictSpe[clef][c] = pygame.transform.scale(self.dictSpeOriginal[clef][c],self.screenSize)
                    
                    if not 'png' in str(self.dictVanilla[clef][c]) and not 'jpg' in str(self.dictVanilla[clef][c]):
                        self.dictVanilla[clef][c] = pygame.transform.scale(self.dictVanillaOriginal[clef][c],self.screenSize)

                
                barre = pygame.Surface((int(self.screenSize[0] * c2/longeur),int(self.screenSize[1] * 0.05)))
                barre.fill('white')
                try:
                    self.screen.blit(jeu.font.render(f'{round(c2/longeur * 100,1)}%',True,(255,255,255)),(0,0))
                except NameError:
                    self.screen.blit(self.font.render(f'{round(c2/longeur * 100,1)}%',True,(255,255,255)),(0,0))

                self.screen.blit(barre,(0,self.screenSize[1] - self.screenSize[1] * 0.05 ))

                
                pygame.display.flip()
                
                c2 += 1
        
        self.chargementIMG()

    """
    Méthode intermédiaire permettant au code d'être plus claire, la class possède un attribut "position" qui 
    appele différente méthode.  
    """
    def on_est_ou(self):
        if self.position == 'main': #Affiche la page principale (celle avec la planète qui tourne)
            self.cooldown += 1
            self.main()
        elif self.position == 'Réglages Vidéos': 
            self.cooldown += 1
            self.video()
        elif self.position == 'jouer': #C'est pas vraiment jouer en réalité ça lance seulement la page de choix de monde 
            jeu.classPos = ''
            jeu.position = 'choix monde'
            jeu.stopClicable = self.settingsDict['Chargements']
            jeu.sauvegarde = jeu.dicoInstru(jeu.get_txt(f'sauvegardes/save{self.cSauv}.txt'))
        
        elif self.position == 'Touches':
            self.cooldown += 1
            self.touches()
        
        if self.settingsDict['ShowFPS']:
            self.screen.blit(jeu.font2.render(f'{int(jeu.clock.get_fps())} FPS',True,(255,255,255)),(0,self.screenSize[1] - jeu.police * 0.6))

    """
    Méthode principale 
    """
    def main(self):
        self.x,self.y = pygame.mouse.get_pos()

        try:
            if self.fade < 255:
                self.fade += 5
            for clef in self.dictVanilla:
                if not self.settingsDict['Chargements']:
                    if not 'Surface' in str(self.dictVanilla[clef][self.clefactuel]):
                        self.dictVanillaOriginal[clef][self.clefactuel] = pygame.image.load(f'vids_vanilla/{clef}/{self.nameDictVanilla[clef][self.clefactuel]}').convert_alpha()
                        surface = pygame.transform.scale(self.dictVanillaOriginal[clef][self.clefactuel],self.screenSize)
                        self.dictVanilla[clef][self.clefactuel] = surface
                        
                        if 'clic' in clef:
                            self.dictSpeOriginal[clef][self.clefactuel] = pygame.image.load(f'vids_special/{clef}/{self.nameDictSpe[clef][self.clefactuel]}').convert_alpha()
                            self.dictSpe[clef][self.clefactuel] = pygame.transform.scale(self.dictSpeOriginal[clef][self.clefactuel],self.screenSize)
                    else:
                        surface = self.dictVanilla[clef][self.clefactuel]
                else:
                    surface = self.dictVanilla[clef][self.clefactuel]
                    surface.set_alpha(self.fade)
                curseur_mask = pygame.mask.from_surface(pygame.Surface((self.screenSize[0],1)))
                surface_mask = pygame.mask.from_surface(surface)
                if surface_mask.overlap(curseur_mask, (self.x -self.screenSize[0]/2,self.y )) and 'clic' in clef and not self.chargement:
                    if pygame.mouse.get_pressed()[0] and self.cooldown > self.COOLDOWN and self.cSauv != 0:
                        self.cooldown = 0
                        self.position = 'jouer'
                        jeu.useMemory = self.settingsDict['Chargements']
                        
                    elif pygame.mouse.get_pressed()[0] and self.cooldown > self.COOLDOWN:
                        self.lancementSansSave = True
                        
                    else:
                        if self.settingsDict['Chargements']:
                            self.dictSpe[clef][self.clefactuel].set_alpha(self.fade)
                        surface = self.dictSpe[clef][self.clefactuel]
                
                decalage = self.screenSize[1] * 0.15
                self.screen.blit(self.menuIMG['logo.png'],(0,self.screenSize[1] * 0.5 - self.menuIMG['logo.png'].get_size()[1] + decalage))
                self.screen.blit(self.menuIMG['pintendo blanc logo.png'],(self.menuIMG['pintendo blanc logo.png'].get_size()[0] * 0.22,self.screenSize[1] * 0.35 + self.menuIMG['pintendo blanc logo.png'].get_size()[1] * 0.5 + decalage))
                self.screen.blit(surface,(0,0))

            
            sauvListe = [None] * 3
            for i in os.listdir('sauvegardes'):
                sauvListe[int(i[-5])-1] = i
            c = 0
            for saves in sauvListe:
                if saves == None:
                    savesSTR = "New Save"
                else:
                    savesSTR = saves[:-4]
                save,savetxt,select = self.menuIMG['case vert.png'],jeu.font2.render(savesSTR,True,(255,255,255)),jeu.font2.render(str(self.selectSave),True,(255,255,255))
                saveRect,saveTxtRect = save.get_rect(),savetxt.get_rect()
                saveRect.x,saveRect.y = saveRect.width * c,self.screenSize[1] * 0.1
                saveTxtRect.x,saveTxtRect.y = saveRect.center[0] - saveTxtRect.width*0.5,saveRect.center[1] - saveTxtRect.height *0.5

                if self.chargement != 1 and saveRect.left < pygame.mouse.get_pos()[0] < saveRect.right and saveRect.top < pygame.mouse.get_pos()[1] < saveRect.bottom and self.stop1ou2 != 2 or (self.stop1ou2 == 2 and c == self.cSauv -1): 
                    if pygame.mouse.get_pressed()[0] and self.cooldown > self.COOLDOWN and not self.chargement:
                        self.cooldown = 0
                        self.cSauv = c + 1
                        if saves == None:
                            self.nouvelle_sauvegarde(['Europe'],['rennes'],[5]*4,0,0)
                            self.selectSave = f'save{self.cSauv}'
                        else:
                            self.selectSave = saves[:-4]
                    elif pygame.mouse.get_pressed()[2] and self.cooldown > self.COOLDOWN and saves != None:
                        self.cSauv = c + 1
                        self.cooldown = 0
                        self.chargement = True
                        self.stop1ou2 = 2
                        

                    savetxt = jeu.font2.render(savesSTR,True,(200,0,0))
                    saveRect.y += saveRect.height * 0.1
                    saveTxtRect.y += saveRect.height * 0.1
                
                self.screen.blit(save,saveRect)
                self.screen.blit(savetxt,saveTxtRect)
                self.screen.blit(select,(self.screenSize[0] - select.get_rect().width,0))
                c += 1
        except:
            text = "Erreur d'affichage"
            self.screen.blit(jeu.font2.render(text,True,(255,255,255)),(0,0))
            
        if not self.stop:
            
            anim = jeu.font.render('Stop animation',True,(255,255,255))
            animRect = anim.get_rect()
            animRect.x = self.screenSize[0] - animRect.width - jeu.police * 1.5

            if animRect.left < self.x < animRect.right and animRect.top < self.y < animRect.bottom :
                anim = jeu.font.render('Stop animation',True,(255,0,0))
                if pygame.mouse.get_pressed()[0] and self.cooldown > self.COOLDOWN:
                    self.cooldown = 0
                    self.stop = True
            
            self.screen.blit(anim,animRect)

            if not self.inverse:
                self.clefactuel += 1
                if self.clefactuel ==len(self.dictVanilla[list(self.dictVanilla)[0]])-1:
                    self.inverse = True
            else:
                self.clefactuel -= 1
                if self.clefactuel == 0:
                    self.inverse = False
        else:
            anim = jeu.font.render('Run animation',True,(255,255,255))
            animRect = anim.get_rect()
            animRect.x = self.screenSize[0] - animRect.width - jeu.police * 1.5

            if animRect.left < self.x < animRect.right and animRect.top < self.y < animRect.bottom :
                anim = jeu.font.render('Run animation',True,(255,0,0))
                if pygame.mouse.get_pressed()[0] and self.cooldown > self.COOLDOWN:
                    self.cooldown = 0
                    self.stop = False
            
            self.screen.blit(anim,animRect)

        
        reglage = self.menuIMG['engrenage.png']
        reglageRect = reglage.get_rect()
       
        if reglageRect.left <= self.x <= reglageRect.right and reglageRect.top <= self.y <= reglageRect.bottom and self.stop1ou2 != 2:
            if not self.flip:
                self.menuIMG['engrenage.png'] = pygame.transform.flip(self.menuIMG['engrenage.png'],True,True)
                self.flip = True
                
            if pygame.mouse.get_pressed()[0] and self.cooldown > self.COOLDOWN:
                if not self.chargement:
                    self.chargement = True
                    self.stop1ou2 = 1
                else:
                    self.chargement = False
                self.cooldown = 0
        
        else:
            if self.flip:
                self.flip = False
                self.menuIMG['engrenage.png'] = pygame.transform.flip(self.menuIMG['engrenage.png'],True,True)
        if self.chargement and self.stop1ou2 == 1:
            surface = pygame.Surface(self.screenSize)
            surface.fill('black')
            surface.set_alpha(200)
            self.screen.blit(surface,(0,0))
            reglages = ['Réglages Vidéos','Touches']

            c = -1
            for reglage in reglages:
                c += 1
                reg = jeu.font.render(reglage,True,(255,255,255))
                regRect = reg.get_rect()
                regRect.x,regRect.y = self.screenSize[0] * 0.5 - regRect.width * 0.5, self.screenSize[1] * 0.5 - regRect.height * 0.5 - regRect.height * c

                if regRect.left < self.x < regRect.right and regRect.top < self.y < regRect.bottom :
                    if pygame.mouse.get_pressed()[0] and self.cooldown > self.COOLDOWN:
                        self.cooldown = 0
                        self.position = reglage
                    reg = jeu.font.render(reglage,True,(0,255,0))
                
                
                self.screen.blit(reg,regRect)
        self.screen.blit(self.menuIMG['engrenage.png'],(0,0))

        if self.chargement and self.stop1ou2 == 2:
            surface = pygame.Surface(self.screenSize)
            surface.set_alpha(240)
            self.screen.blit(surface,(0,0))

            texte = jeu.font.render(f"Voulez-vous vraiment supprimer save{self.cSauv} ?",True,(255,255,255))
            possibilite = ['Oui','Non']

            c = -1
            for posi in possibilite:
                c += 1
                font = jeu.font2.render(posi,True,(255,255,255))
                fontRect = font.get_rect()
                fontRect.x,fontRect.y = texte.get_rect().center[0] - fontRect.width*2 + fontRect.width*4 * c, self.screenSize[1] * 0.5

                if fontRect.left < self.x < fontRect.right and fontRect.top < self.y < fontRect.bottom:
                    font = jeu.font2.render(posi,True,(0,0,200))
                    if pygame.mouse.get_pressed()[0] and self.cooldown > self.COOLDOWN:
                        self.cooldown = 0
                        if 'Oui' == posi:
                            os.remove(f'sauvegardes/save{self.cSauv}.txt')
                        self.chargement = False
                        self.stop1ou2 = 0
                        self.selectSave = None
                        self.cSauv = 0

                self.screen.blit(font,fontRect)
            self.screen.blit(texte,(self.screenSize[0] * 0.5 - texte.get_size()[0] * 0.5,self.screenSize[1] * 0.5 - texte.get_size()[1]))
        
        if self.lancementSansSave and not self.chargement:
            if self.compteurSansSave < 255:
                self.compteurSansSave += 1
            else:
                self.compteurSansSave = 0
                self.lancementSansSave = False
            
            font = jeu.font2.render('Veuillez selectioner une sauvegarde',True,(255,255,255))
            ombre = jeu.font2.render('Veuillez selectioner une sauvegarde',True,(0,0,0))
            
            font.set_alpha(self.compteurSansSave *5)
            ombre.set_alpha(self.compteurSansSave *5)

            self.screen.blit(ombre,(round(0.0013 * self.screenSize[0]),self.screenSize[1] * 0.75 + round(0.002 *self.screenSize[0])))
            self.screen.blit(font,(0,self.screenSize[1] * 0.75))

    def nouvelle_sauvegarde(self,mondes : list,niveaux : list,vies : list,score : int,pieces : int):
        with open(f"sauvegardes/save{self.cSauv}.txt", "w") as save:
            save.write(f'M:{mondes}\nN:{niveaux}\nV:{vies}\nS:{[score,pieces]}')
    
    def video(self):
        self.screen.fill('black')
        self.x,self.y = pygame.mouse.get_pos()
        retour = jeu.font2.render('Retour',True,(255,255,255))
        rrect = retour.get_rect()
        if rrect.left < self.x < rrect.right and rrect.top < self.y < rrect.bottom or pygame.key.get_pressed()[pygame.K_ESCAPE]:
            if (pygame.mouse.get_pressed()[0] or pygame.key.get_pressed()[pygame.K_ESCAPE]) and self.cooldown > self.COOLDOWN:
                self.cooldown = 0
                if self.trouve == []:
                    self.txtSettings(self.settingsDict.values())
                    if self.settingsDict['Chargements'] and not self.load:
                        self.chargementMethode()
                    self.position = 'main'
                else:
                    self.trouve = []
            retour = jeu.font2.render('Retour',True,(0,0,255))
        
        self.screen.blit(retour,rrect)
        resolutions = [0.5,0.75,'fullscreen']
        reglages = {'Résolution' : resolutions,'Réglages lié aux Chargements': [f'Chargements : {self.settingsDict["Chargements"]} (/!\ va entrainer un écran de chargement)',f'Affichez les FPS : {self.settingsDict["ShowFPS"]}']}
        compteur = -1
        if self.trouve == []:
            for reglage in reglages:
                compteur += 1
                reg = jeu.font.render(str(reglage),True,(255,255,255))
                regRect = reg.get_rect()
                regRect.x,regRect.y = self.screenSize[0] * 0.5 - regRect.width * 0.5,self.screenSize[1] * 0.5 - len(list(reglages)) / 2 * regRect.height + compteur * regRect.height

                if regRect.left < self.x < regRect.right and regRect.top < self.y < regRect.bottom:
                    reg = jeu.font.render(reglage,True,(0,255,0))
                    if pygame.mouse.get_pressed()[0] and self.cooldown > self.COOLDOWN:
                        self.cooldown = 0
                        regRect.y = 0
                        reg = jeu.font.render(reglage,True,(255,255,255))
                        self.trouve = reglage
                        break

                self.screen.blit(reg,regRect)
        
        compteur = -1
        if self.trouve != []:
            for i in reglages[self.trouve]:
                reglage = jeu.font.render(str(self.trouve),True,(255,255,255))
                reglageRect = reglage.get_rect()
                reglageRect.x,reglageRect.y = self.screenSize[0] * 0.5 - reglageRect.width * 0.5,self.screenSize[1]*0.1
                compteur += 1
                if self.trouve == 'Résolution': 
                    if i != 'fullscreen':
                        text = str(get_monitors()[0].width * i)+'x' + str(get_monitors()[0].height * i)
                        
                    else:
                        text = str(i)

                else:
                    text = str(i)
                    
                font = jeu.font2.render(text,True,(255,255,255))
                fontRect = font.get_rect()
                
                fontRect.x,fontRect.y = self.screenSize[0] * 0.5 - fontRect.width * 0.5,self.screenSize[1] * 0.5 - len(reglages[self.trouve]) / 2 * fontRect.height + compteur * fontRect.height
                if fontRect.left < self.x < fontRect.right and fontRect.top < self.y <fontRect.bottom:
                    font = jeu.font2.render(text,True,(0,0,255))
                    if  pygame.mouse.get_pressed()[0] and self.cooldown > self.COOLDOWN:
                        self.cooldown = 0
                        if self.trouve == 'Résolution':
                            if i != 'fullscreen':
                                self.width , self.height = get_monitors()[0].width * i ,get_monitors()[0].height * i
                                self.screen = pygame.display.set_mode((self.width, self.height))
                                jeu.res = i
                            else:
                                self.screen = pygame.display.set_mode((0,0),FULLSCREEN)
                                self.width,self.height = self.screen.get_size()
                                jeu.res = 1
                                
                            
                            self.screenSize = self.screen.get_size()
                            jeu.screenSize = self.screen.get_size()
                            jeu.police = int(self.screenSize[0] * 0.05)
                            jeu.font = pygame.font.SysFont('Bahnschrift', jeu.police)
                            jeu.font2 = pygame.font.SysFont('Bahnschrift', int(jeu.police*0.5))
                            jeu.font3 = pygame.font.SysFont('Bahnschrift', int(jeu.police*0.7))
                            jeu.font4 = pygame.font.SysFont('Bahnschrift', int(jeu.police*0.3))
                            self.chargementMethode(True)
                        elif self.trouve == "Réglages lié aux Chargements":
                            if 'Chargements' in i:
                                if self.settingsDict['Chargements']:
                                    jeu.useMemory = False
                                    self.settingsDict['Chargements'] = False
                                else:
                                    jeu.useMemory = True
                                    self.settingsDict['Chargements'] = True
                                    
                            
                            elif 'FPS' in i:
                                if self.settingsDict["ShowFPS"]:
                                    self.settingsDict["ShowFPS"] = False
                                else:
                                    self.settingsDict["ShowFPS"] = True
                
                if reglageRect.left < self.x < reglageRect.right and reglageRect.top < self.y < reglageRect.bottom:
                    reglage = jeu.font.render(self.trouve,True,(0,255,0))
                    if pygame.mouse.get_pressed()[0]:
                        self.trouve = []
                        break
                
                self.screen.blit(font,fontRect)
                self.screen.blit(reglage,reglageRect)

    def touches(self):
        self.x,self.y = pygame.mouse.get_pos()
        self.screen.fill('black')
        
        retour = jeu.font2.render('Retour',True,(255,255,255))
        rrect = retour.get_rect()
        if rrect.left < self.x < rrect.right and rrect.top < self.y < rrect.bottom or pygame.key.get_pressed()[pygame.K_ESCAPE]:
            if pygame.mouse.get_pressed()[0] or pygame.key.get_pressed()[pygame.K_ESCAPE] and self.cooldown > self.COOLDOWN:
                self.cooldown = 0
                self.position = 'main'
                self.txtTouches(self.touchesDict.values())
            retour = jeu.font2.render('Retour',True,(0,0,255))
        self.screen.blit(retour,rrect)
        
        
        c = -1

        if self.doubleTouche != '':
            if not self.inverseDB:
                if self.tpsAffichageDB < 255:
                    self.tpsAffichageDB += 6
                else:
                    self.inverseDB = True
            
            else:
                if self.tpsAffichageDB > 0:
                    self.tpsAffichageDB -= 6
                else:
                    self.doubleTouche = ''
                    self.inverseDB = False

        dbTouche = jeu.font2.render(self.doubleTouche,True,(0,150,0))
        dbTouche.set_alpha(self.tpsAffichageDB)
        self.screen.blit(dbTouche,(0,self.screenSize[1] - jeu.police))
        for touche in self.touchesDict:
            c += 1
            toucheF = jeu.font3.render(touche,True,(255,255,255))
            toucheFR = toucheF.get_rect()
            toucheFR.x,toucheFR.y = self.screenSize[0] * 0.5 - toucheFR.width * 0.5 - self.screenSize[0] * 0.1, self.screenSize[1] * 0.5 + toucheFR.height * c - toucheFR.height * len(self.listeTouches) / 2
            
            assignement = jeu.font3.render(str(pygame.key.name(self.touchesDict[touche])),True,(255,255,255))
            assignementRect = assignement.get_rect()
            assignementRect.x,assignementRect.y = self.screenSize[0] * 0.5 , copy.deepcopy(toucheFR.y)

            if assignementRect.left < self.x < assignementRect.right and assignementRect.top < self.y < assignementRect.bottom:
                if not self.changeKey[0]:
                    assignement = jeu.font2.render('Cliquez pour changer la touche',True,(255,0,0))
                    assignementRect = assignement.get_rect()
                    assignementRect.x,assignementRect.y = self.screenSize[0] * 0.5 , copy.deepcopy(toucheFR.y)
                
                    if pygame.mouse.get_pressed()[0] and self.cooldown > self.COOLDOWN:
                        self.cooldown = 0
                        self.changeKey[0],self.changeKey[2],self.changeKey[3] = True,(assignementRect.top,assignementRect.bottom),touche
                else:
                    assignement = jeu.font2.render('Pressez une touche du clavier',True,(0,0,200))
                    assignementRect = assignement.get_rect()
                    assignementRect.x,assignementRect.y = self.screenSize[0] * 0.5 , copy.deepcopy(toucheFR.y)

                    if self.touchesDict[touche] == self.changeKey[1] or not self.changeKey[2][0] < self.y < self.changeKey[2][1]:
                        self.changeKey[0] = False


            if toucheFR.x < self.plusagauche:
                self.plusagauche = toucheFR.x
            border = pygame.Rect(self.plusagauche,toucheFR.y,self.screenSize[0] - self.plusagauche - (self.screenSize[0] - assignementRect.right) , toucheFR.height)
            pygame.draw.rect(self.screen,"gray",border,2)
            
            self.screen.blit(toucheF,toucheFR)
            self.screen.blit(assignement,assignementRect)
            
    def txtTouches(self,liste):
        if 'touches.txt' in os.listdir():
            os.remove('touches.txt')
        with open('touches.txt','w') as txt:
            for i in liste:
                txt.write(f'{i}\n')
    
    def txtSettings(self,liste):
        if 'settings.txt' in os.listdir():
            os.remove('settings.txt')
        with open('settings.txt','w') as txt:
            for i in liste:
                txt.write(f'{i}\n')
    
    def update(self):
        self.on_est_ou()
        pygame.display.flip()

class Jeu:
    def __init__(self) -> None:
        self.useMemory = False
        self.FPS = 24 #de toute façon l'oeil humain ne vois pas à plus de 24 fps ;) 
        self.width , self.height = get_monitors()[0].width * 0.75,get_monitors()[0].height * 0.75
        self.screen = pygame.display.set_mode((int(self.width),int(self.height)))
        self.windowName = pygame.display.set_caption("Super Pario Bros")
        img = pygame.image.load('assets/monstres/champi.png')
        pygame.display.set_icon(img)
        self.screenSize = self.screen.get_size()
        self.police = int(self.screenSize[0] * 0.05)
        self.font = pygame.font.SysFont('Bahnschrift', self.police)
        self.font2  = pygame.font.SysFont('Bahnschrift', int(self.police * 0.5))
        self.font3  = pygame.font.SysFont('Bahnschrift', int(self.police * 0.7))
        self.font4 = pygame.font.SysFont('Bahnschrift', int(self.police * 0.3))
        self.classDict = {'menu' : Menu(self.screen,self.font2),'monde' : None}
        self.clock = pygame.time.Clock()
        self.villesEU = {'rennes' : [(255,0,0)],'londres' : [(255,255,0)],'copenhague' : [(0,255,255)],'st-petersbourg' : [(255,0,255)],'athenes' : [(0,255,0)],'paris' : [(0,0,255)]}
        for ville in self.villesEU:
            self.villesEU[ville].append(f'{ville}.txt')
            if not 'paris' in ville:
                self.villesEU[ville].append(os.listdir(f'Europe/assets'))

            #else:
            #    self.villesEU[ville].append(os.listdir(f'Europe/special/{ville}/assets'))
            # J'ai pas les fichier donc ça plante
        
        
        self.allWorlds = {'Europe' : self.villesEU,'Moyen-orient' : None,'Amérique du nord' : None,'Amérique du sud' : None}  
        
        self.noMemory = {}
        for monde in self.allWorlds:
            if monde == 'Europe':
                self.noMemory[monde] = os.listdir(f'{monde}/vids/carte')
                self.noMemory[monde].sort()

        self.mask = {name : None for name in self.villesEU}
        self.sauvegarde = {}
        self.world = 'Europe'
        self.memoire = {}
        self.compteurIMG = 0
        self.inverse = False
        self.position = ''
        self.classPos = 'menu'
        self.monde = ''
        self.cooldown = 0
        self.COOLDOWN = 5
        self.joueur = {}
        self.res = 0.75
        self.fade = 0
        self.information = 'rennes'
        self.stop = False
        self.stopClicable = False
        self.rainbow = 0
        self.inverseRainbow = False

        self.scrollActivate = False
        self.imagesMondes = {}
        self.carteMonde = None
    
    def chargement(self,chemin,load = False):
        """Charge des images dans la mémoire"""
        self.fade = 0
        c2 = 0
        if not load:
            self.memoire[chemin] = [os.listdir(chemin),os.listdir(chemin)]
        c = -1
        for images in os.listdir(chemin):
            c += 1
            self.screen.fill((c2,0,0))
            self.screen.blit(self.font2.render(f'loading {chemin}/{images} (dernière images : {os.listdir(chemin)[-1]})',True,(255,255,255)),(0,0))
            pygame.display.flip()
            if not load:
                self.memoire[chemin][0][c] = pygame.image.load(f'{chemin}/{images}').convert_alpha()
                self.memoire[chemin][1][c] = pygame.transform.scale(self.memoire[chemin][0][c],self.screenSize)
            c2 += 1       
    
    def inputs(self):
        """recupere les interactions que le joueur fait et quitte le jeu si on appuye sur la croix"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit() 
            if self.classDict['menu'].changeKey[0]:
                if event.type == pygame.KEYDOWN:
                
                    if not event.key in self.classDict['menu'].touchesDict.values():
                        self.classDict['menu'].touchesDict[self.classDict['menu'].changeKey[3]] = event.key
                    else:
                        self.classDict['menu'].doubleTouche = f'"{pygame.key.name(event.key)}" est déjà assigné, pressez une autre touche'
                    self.classDict['menu'].changeKey[0] = False
        
    def carte(self):
        """charge et affiche la carte de sélection des niveaux"""
        try:
            if self.fade < 255:
                self.fade += 5
            self.x,self.y = pygame.mouse.get_pos()
            if not self.useMemory:
                try : 
                    if not len(self.memoire[f'{self.world}/vids/carte']) == len(self.noMemory[self.world]) and not self.stop:
                        surface = pygame.transform.scale(pygame.image.load(f'{self.world}/vids/carte/{self.noMemory[self.world][self.compteurIMG]}'),self.screenSize)
                    
                        self.memoire[f'{self.world}/vids/carte'].append(surface)
                        if not self.classDict['menu'].settingsDict['Chargements'] and not self.stopClicable:
                            self.stop = True
                    else:
                        if self.stop:
                            surface = self.memoire[f'{self.world}/vids/carte'][self.compteurIMG-2]
                        else:
                            surface = self.memoire[f'{self.world}/vids/carte'][self.compteurIMG]
                except KeyError:
                    self.memoire[f'{self.world}/vids/carte'] = []
                
            else:
                surface = self.memoire[f'{self.world}/vids/carte'][1][self.compteurIMG]
                surface.set_alpha(self.fade)
            
            self.screen.blit(surface,(0,0))
            curseur_mask = pygame.mask.from_surface(pygame.Surface((10,10)))
            
            for villes in self.allWorlds[self.world]:
                villeMask = pygame.mask.from_threshold(surface,self.allWorlds[self.world][villes][0],(10, 10, 10,255))
                if villeMask.overlap(curseur_mask, (self.x ,self.y)) :
                    taille = round(self.screenSize[0] * 0.01)
                    pygame.draw.arc(self.screen,(255,255,255),pygame.Rect(self.x-taille,self.y-taille,taille*2,taille*2),0,180,int(taille / 3))
                    
                    if pygame.mouse.get_pressed()[0] and self.cooldown > self.COOLDOWN:
                        self.cooldown = 0
                        self.information = villes
                    
            fond = pygame.font.SysFont('Bahnschrift', int(self.screenSize[0] * 0.018)).render(self.information[:1].upper()+self.information[1:],True,self.villesEU[self.information][0])
            self.screen.blit(fond,(self.screenSize[0]*0.07 ,self.screenSize[1]*0.09))
            self.screen.blit(self.font.render(self.information[:1].upper()+self.information[1:],True,(10,10,10)),(self.screenSize[0]*0.07,self.screenSize[1]*0.09))
        except:
            pass

        
        if not self.stop:
            if not self.inverse:
                self.compteurIMG += 1
                if self.compteurIMG == len(self.noMemory[self.world])-1:
                    self.inverse = True
            else:
                self.compteurIMG -= 1
                if self.compteurIMG == 0:
                    self.inverse = False
        
        if not self.inverseRainbow:
            if self.rainbow < 255:
                self.rainbow += 1 
            else:
                self.inverseRainbow = True
        else:
            if self.rainbow > 0:
                self.rainbow -= 1
            else:
                self.inverseRainbow = False
        
        if self.information in self.sauvegarde['N']:
            startLVL = self.font4.render(f'Appuyez sur la touche "{pygame.key.name(self.classDict["menu"].touchesDict["Saut"])}" du clavier pour lancer {self.information[:1].upper()+self.information[1:]}',True,(100,self.rainbow,self.rainbow))
            
        else:
            if not 'paris' in self.information:
                villeAfinir = list(self.allWorlds[self.world])[list(self.allWorlds[self.world]).index(self.information)-1]
                
                startLVL = self.font4.render(f"Finissez d'abord {villeAfinir} pour lancer {self.information[:1].upper()+self.information[1:]}",True,(100,self.rainbow,self.rainbow))
            else:
                startLVL = self.font4.render(f"^^",True,(100,self.rainbow,self.rainbow))
        startLVLRect = startLVL.get_rect()

        if pygame.key.get_pressed()[self.classDict["menu"].touchesDict["Saut"]] and self.cooldown > self.COOLDOWN * 2 and self.information in self.sauvegarde['N']:
            self.cooldown = 0
            self.classDict['monde'] = World(self.screen,f'{self.world}/{self.information}.txt',self.sauvegarde,self.information)
            self.classPos = 'monde'
            self.position = ''
            self.FPS = 60

        #self.screen.blit(ombre,((0,(self.screenSize[1] - startLVLRect.height ) + 0.0025*startLVLRect.height)))
        self.screen.blit(startLVL,(0,self.screenSize[1] - startLVLRect.height))

        possible = ['Stop Animation','Run Animation']
        if not self.stop:
            possible = possible[0]
        else:
            possible = possible[1]
        stop = jeu.font2.render(possible,True,(255,255,255))
        stopRect = stop.get_rect()
        stopRect.x = self.screenSize[0] - stopRect.width - stopRect.width *0.05
        if stopRect.left < self.x < stopRect.right and stopRect.top < self.y < stopRect.bottom:
            stop = jeu.font2.render(possible,True,(255,0,0))
            if pygame.mouse.get_pressed()[0] and self.cooldown > self.COOLDOWN:
                self.cooldown = 0
                if not self.stop:
                    self.stopClicable = False
                    self.stop = True
                else:
                    self.stopClicable = True
                    self.stop = False
        self.screen.blit(stop,stopRect)

    def choixMonde(self):
        """charge et affiche la carte de selection des mondes """
        if self.carteMonde == None:
            self.carteMonde = pygame.transform.scale(pygame.image.load('assets/world/others/monde.png').convert_alpha(),self.screenSize)
            self.screen.fill('lightblue')
            self.screen.blit(self.carteMonde,(0,0))
            pygame.display.flip()

            self.carteMondeC = pygame.transform.scale(pygame.image.load('assets/world/others/monde couleurs.png').convert_alpha(),self.screenSize)
            size = round(self.screenSize[0] * 0.0002,2)
            for monde in ['Europe','Moyen-orient','Amérique du nord','Amérique du sud']:
                self.imagesMondes[monde] = pygame.image.load(f'assets/world/others/{monde}.png')
                self.imagesMondes[monde] = pygame.transform.scale(self.imagesMondes[monde],(int(self.imagesMondes[monde].get_size()[0] * size),int(self.imagesMondes[monde].get_size()[1] * size)))
        
        self.x,self.y = pygame.mouse.get_pos()
        colorCode = {'Europe' : (255,0,0),'Moyen-orient' : (0,255,0),'Amérique du nord' : (0,0,255),'Amérique du sud' : (255,0,255)}
        self.screen.fill('lightblue')
        self.screen.blit(self.carteMonde,(0,0))
        if pygame.key.get_pressed()[K_ESCAPE]:
            self.position = ''
            self.classPos = 'menu'
            self.FPS = 24
            self.classDict['menu'].position = 'main'

        for monde in colorCode:

            mask = pygame.mask.from_threshold(self.carteMondeC,colorCode[monde],(10,10,10,255))
            curseur = pygame.mask.from_surface(pygame.Surface((1,1)))

            outline = mask.outline(10)
            
            maskZoneClicable = mask.to_surface()
            maskZoneClicable.set_colorkey((0,0,0))
            maskZoneClicable.set_alpha(75)
            if mask.overlap(curseur,(self.x,self.y)):
                self.screen.blit(maskZoneClicable,(0,0),None)
                pygame.draw.lines(self.screen,(255,255,255),False,outline,2)
                self.screen.blit(self.imagesMondes[monde],(self.screenSize[0] - self.imagesMondes[monde].get_size()[0],self.screenSize[1] * 0.5 - self.imagesMondes[monde].get_size()[1] * 0.5))
                if monde in self.sauvegarde['M']:
                    self.screen.blit(self.font2.render(f'Cliquez pour lancer {monde}',True,(0,150,0)),(0,0))
                    if pygame.mouse.get_pressed()[0] and self.cooldown > self.COOLDOWN:
                        self.cooldown = 0
                        self.position = 'carte'
                        self.world = monde
                        if self.classDict['menu'].settingsDict['Chargements']:
                            self.chargement(f'{monde}/vids/carte')
                else:
                    self.screen.blit(self.font2.render(f"Débloquez d'abord {list(self.allWorlds)[list(self.allWorlds).index(monde) -1]} ",True,(200,0,0)),(0,0))
                          
    def get_txt(self,chemin):
        """renvoie dans une liste , le contenu d'un fichier txt"""
        file = open(f'{chemin}', 'r')
        data = file.read()
        liste = data.split("\n")
        file.close()
        return liste

    def dicoInstru(self,liste):
        """récupere les valeurs du fichier txt correspondant au différents bloc et a leur caractéristique et les stoque dans un dictionnaire"""
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
                    elif lettre != ',' and lettre != ']' and lettre != ':' and lettre != ' ' and lettre != '"' and lettre != "'":
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
        """Renvoie true si elt est est un float , False sinon"""
        try:
            float(elt)
            return True
        except ValueError:
            return False
        
    def on_est_ou(self):
        """En fonction de l'écran qui doit etre afficher , appelle les fonctions correspondantes a celui ci et afficher les fps si le joueur l'a selectionné dans les options"""
        if self.position == 'choix monde':
            self.choixMonde()
            self.cooldown += 1
        if self.position == 'carte':
            self.cooldown += 1
            self.carte()
        
        if self.classDict['menu'].settingsDict['ShowFPS']:
            self.screen.blit(jeu.font2.render(f'{int(self.clock.get_fps())} FPS',True,(0,0,0)),(0,self.screenSize[1] - self.police))
        
    def update(self):
        """fonction qui appelle toute les fonctions nécessaire au bon fonctionnement de la classe"""
        self.on_est_ou()
        if self.classPos != '':
            self.classDict[self.classPos].update()
        self.inputs()
        pygame.display.flip()
        self.clock.tick(self.FPS)

class Players:
    def __init__(self,screen,blockRECT,name,joueur,touches,ville) -> None:
        self.ville = ville
        self.touches = touches
        self.screen = screen
        self.blockRECT = blockRECT
        self.playerSize = self.screen.get_size()[0] * 0.00005
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
        self.min_jumpspeed = round(jeu.screenSize[0] * 0.003)
        self.prev_key = pygame.key.get_pressed()
        self.est_mort = False
        self.rectScreen = self.screen.get_rect()
        self.timer = 0
        self.cooldown = 0
        
        self.COOLDOWN = round(self.screen.get_size()[0]*0.0138)
        
        self.etats = {"grand":'Pario.png',"petit":"Pario.png","feu":"ParioFeu.png","etoile":"etoile.png"}
        for etat in self.etats:
            if etat == 'petit':
                image = pygame.transform.scale(self.etats['grand'],((self.height * (self.playerSize*0.5) ,self.width * (self.playerSize *0.5))))
            else:
                image = pygame.transform.scale(pygame.image.load(f'assets/players/{self.etats[etat]}').convert_alpha(),(self.height * self.playerSize ,self.width * self.playerSize))
            self.etats[etat] = image
        
        self.etat = ""
        self.lastEtat = "petit"
        self.sizeOri = self.playerSize
        self.changeSkin("petit")
        

        self.spriteFB = pygame.image.load(f'{jeu.world}/assets/others/fireball.png')

        self.bouleDeFeu = []
        self.asupprimer = []

        self.last_dir = 'right'
        self.dir = 'right'
        
        self.invincible = False
        self.touchable = True
        self.touchableTimer = 0

    def touchTimer(self):
        # fonction qui sert a creer une intervalle de temps mimine pour se faire toucher 2 fois en une demi-seconde
        self.touchableTimer +=1
        if self.touchableTimer > 60*3:
            self.touchableTimer = 0
            return True  
    
    def retouchable(self):
        #fonction permettant de ne pas se faire one-shot avec un monstre
        if not self.touchable:
            if self.touchTimer():
                self.touchable = True
         
    def toucher(self):
        # fonction qui regarde l'etat du joueur pour changer son état ou le tuer si sous l'etat petit
        if self.touchable :  
            if self.etat == "petit":
                self.est_mort = True
            elif self.etat == 'grand':
                self.touchable = False
                self.etat = "petit"

            elif self.etat == 'feu':
                self.touchable = False
                self.etat = "grand"
            
            
            self.changeSkin(self.etat)              
    
    def powerUse(self):
        # modifie les parametres et permet d'obtenir les pouvoirs
        if self.etat == "feu":
            if pygame.key.get_pressed()[self.touches['Attaque']] and self.cooldown > self.COOLDOWN:
                self.cooldown = 0
                self.bouleDeFeu.append(BouleDeFeu(self.screen,self.blockRECT,self.pos,self.decalage,numpy.sign(self.speedHori),self.ville,self.spriteFB))
        
        if self.etat == "etoile":
            self.invincible = True
            if self.timerfunc():
                self.etat = self.lastEtat
                self.invincible = False
                self.changeSkin(self.etat)
                
    def changeSkin(self,taille):
        #fonction permettant le changement de l'image du joueur selon son etat
        self.lastEtat = self.etat
        self.image = self.etats[taille]
        
        if taille == "petit":
            self.playerSize = self.sizeOri/2
        else:
            self.playerSize = self.sizeOri
        
        rectAvt = copy.deepcopy(self.rect)

        if taille != 'petit':
            self.rect = self.image.get_rect()
        if self.check_collision(self.rect.x,self.rect.y)[0] and taille != 'petit':
            self.rect = rectAvt 
            return False
        
        self.rect.width,self.rect.height = self.height * self.playerSize,self.width * self.playerSize
        self.etat = taille
        self.timer = 0
        return True
    
    def draw(self):
        #permet l'affichage de l'image du joueur       
        self.rect.x -= self.decalage
        rect2 = self.rect.copy()
        rect2[2] /= 16
        rect2[0] += rect2[2]*8
        
        if self.rect.colliderect(self.rectScreen):
            self.screen.blit(self.image,self.rect)
            """
            if self.etat != 'petit':
                self.screen.blit(self.image,self.rect)  
            else:
                self.screen.blit(self.image,(self.rect.x + (self.width * self.playerSize) *0.5,(self.rect.y + self.height * self.playerSize) *1.025 ))   
            """
    
    def animation(self):
        #permet de modifier le sens de l'image selon la direction choisi par le joueur
        if self.last_dir == "right" and self.dir == "left":
            self.image = pygame.transform.flip(self.etats[self.etat], 1, 0)
        elif self.last_dir == "left" and self.dir == "right":
            self.image = self.etats[self.etat]

    def deplacement(self):
        #fonction permettant le mouvement du joueur selon les touches utilisés, la map ,la gravité
        self.speedHori *= 0.88
        onground = self.check_collision(0, 1)[0]

        key = pygame.key.get_pressed()
        
        if key[self.touches['Gauche']] and self.joueur and not jeu.classDict['monde'].finito and self.ville != 'st-petersbourg':
            self.last_dir = self.dir
            self.dir = "left"
            
            if self.pos[0] > 100:
                self.speedHori = -self.speed
            
        elif key[self.touches['Droite']] and self.joueur and not jeu.classDict['monde'].finito and self.ville != 'st-petersbourg':
            self.last_dir = self.dir
            self.dir = "right"
            self.speedHori = self.speed

        if key[self.touches['Saut']] and onground and self.joueur and not jeu.classDict['monde'].finito and self.ville != 'st-petersbourg':
            self.speedVerti = -self.jumpspeed

        if self.prev_key[self.touches['Saut']] and not key[self.touches['Saut']] and not jeu.classDict['monde'].finito and self.ville != 'st-petersbourg':
            if self.speedVerti < -self.min_jumpspeed:
                self.speedVerti = -self.min_jumpspeed


        self.prev_key = key

        if not onground:
            self.speedVerti += self.gravity 

        if onground and self.speedVerti > 0:
            self.speedVerti = 0

        self.move(self.speedHori, self.speedVerti)

    def check_collision(self, x, y, general=True , plusPetit = False):
        #Verification des collisions joueur/map
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
                        if i[2][13]:
                            self.invincible = True
                            jeu.classDict['monde'].finito = True
                        tempo = copy.deepcopy(i)
                        if i[2][8] and tempo[2][9]:
                            tempo[2][9] = False
                            self.blockRECT[e][c] = tempo
                            self.augmenterPiece()

                        if general != False: 
                            
                            test = self.check_collision(0, -1, False , True)
                            if i[2][2] and not i[2][5] and self.speedVerti < 0 and test[0]:
                                tempo[2][5] = True
                                world = jeu.classDict['monde']
                                
                                if tempo[2][11] != None:
                                    if self.etat == "petit" and tempo[2][11] == "fireflower" :
                                        world.monstre["champi"+str(world.nb_monstre)] = Mobs(self.screen,self.blockRECT,"champi.png",[i[0][0],i[0][1]],"champi"+str(world.nb_monstre),True,False)
                                        world.nb_monstre +=1
                                    else:
                                        world.monstre[tempo[2][11]+str(world.nb_monstre)] = Mobs(self.screen,self.blockRECT,tempo[2][11]+".png",[i[0][0],i[0][1]],tempo[2][11]+str(world.nb_monstre),True,False)
                                        world.nb_monstre +=1
                                else:
                                    self.augmenterPiece()
                                        
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
    
    def augmenterPiece(self):
        #fonction permettant d'augmenter d'une vie la sauvegarde du joueur si son nombre de piece atteint 100
        jeu.classDict['monde'].sauvegarde['S'][0] += 1
        if jeu.classDict['monde'].sauvegarde['S'][0] >= 100:
            jeu.classDict['monde'].sauvegarde['S'][0] = 0
            for index in range(len(jeu.classDict['monde'].sauvegarde['V'])):
                jeu.classDict['monde'].sauvegarde['V'][index] += 1
            
    def move(self,x,y):
        #fonction qui cree le mouvement de l'image sur l'ecran
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
        
    def timerfunc(self):
        self.timer +=1
        if self.timer > 60*10:
            self.timer = 0
            return True

    def fireBallUpdate(self):
        #boucle des entités boule de feu permettant de les crées sous l'etat mario de feu
        for b in self.bouleDeFeu:
            if b.asupprimer :
                self.asupprimer.append(b)
            b.update()
        for b in self.asupprimer:
            self.bouleDeFeu.remove(b)
        self.asupprimer = []
    
    def update(self):
        #boucle player avec les diverses fonctions pour la taille, le deplacement, les pouvoirs, ...
        self.cooldown += 1 
        self.deplacement()
        self.animation()
        self.powerUse()
        self.fireBallUpdate()
        self.retouchable()
        self.draw()
        
class Mobs:
    def __init__(self,screen,blockRECT,name,pos,realName,ville,doitTuerJoueur = True) -> None:
        self.ville = ville
        self.screen = screen
        self.blockRECT = blockRECT
        self.playerSize = self.screen.get_size()[0] * 0.00003
        self.decalage = 0 
        if ville != 'paris':
            self.original = pygame.image.load('assets/monstres/{}'.format(name))
        else:
            self.original = pygame.image.load('assets/monstres_paris/{}'.format(name))
        self.speed = round(screen.get_size()[0] * 0.002083,2)
        self.name = name
        self.doitTuerJoueur = doitTuerJoueur
        self.height, self.width = self.original.get_size()
        self.image = pygame.transform.scale(self.original,(self.height * self.playerSize ,self.width * self.playerSize))
        
        #variable poru modifier la taille d'un certain type d'entité
        if self.name == "plant.png":
            self.image = pygame.transform.scale(self.original,(self.height * self.playerSize *2 ,self.width * self.playerSize*2))
        self.rect = self.image.get_rect()
        self.pos = vec(pos)
        self.pos.x += int(screen.get_size()[1]/15)
        self.jumpspeed = self.screen.get_size()[1] * 0.031
        self.speedVerti = 0
        self.speedHori = 0
        self.gravity = self.screen.get_size()[1] * 0.0015
        self.timer = randint(0,60)
        self.invisible = False
        self.est_mort = False
        self.realName = realName
        self.stop = False
        self.save = 0
        self.vol = False
        self.repetition = False
        self.affaibli = False
        self.phase = ""
        self.animCompteur = 0
        self.munition = False
        self.last_dir = 'right'
        self.dir = 'right'
        
        # variables permettant de modifier la direction de l'entité
        if self.name == "fireflower.png" or self.name == "plant.png":
            self.left = False
            self.right = False
        else:
            self.left = False
            self.right = True
        
        # differentes conditions selon le type du monstre
        if self.name == "pooka.png":
            self.repetition = True
        
        if self.name == "cannon.png":#cannon avec des missiles allant vers la droite
            self.vol = True
            self.munition = True
            self.last_dir = 'right'
            
        if self.name == "cannon1.png":#cannon avec des missiles allant vers la gauche
            self.vol = True
            self.munition = True
            self.left = True
            self.right = False
            self.last_dir = 'right'
            self.dir = 'left'
        
    def apparition(self):
        #fonction permettant les deux phases d'une plante tuyaux
        if self.name == "plant.png":
            if self.timerfunc():
                if self.invisible == False:
                    self.phase = 'entrer'
                    self.invisible = True
                else:
                    self.phase = 'sortir'
                    
                    self.invisible = False
           
    def animPlant(self) :
        """en fonction de l'état de la plante (entrer ou sorti) , la déplace sur l'axe y """
        if self.phase == "entrer":
            if self.animCompteur > round(self.screen.get_size()[0]*0.042):
                self.phase = ""
            else:
                self.animCompteur +=1

                
        if self.phase == "sortir":
            if self.animCompteur == 0:
                self.phase = ""
            else:
                self.animCompteur -=1
 
                
        self.rect.y += self.animCompteur
    
    def timerfunc(self):
        #fonction de temps permettant le delais des phases desplantes
        self.timer +=1
        if self.timer > 60*2:
            self.timer = 0
            return True
            
    def draw(self):
        # fonction permettant l'affichage de l'image de l'entite
        self.rect.x -= self.decalage
        if self.stop != True :
            self.screen.blit(self.image,self.rect)
                       
    def eviteLeSuicide(self):
        #fonction permettant aux pooka de ne pas tomber dans le vide meme sans protection en la redirigeant
        if self.name == "pooka.png":
            if not self.check_collision(3,3):
                self.right = False
                self.left = True

            if not self.check_collision(-3,3):
                self.right = True
                self.left = False

    def animation(self):
        #Permet le changement de sens de l'image de l'entite pour plus de realisme lors de ces demi tours
        if self.last_dir == "right" and self.dir == "left":
            self.image = pygame.transform.scale(pygame.transform.flip(self.original, 1, 0),(self.height * self.playerSize,self.width *self.playerSize))
        elif self.last_dir == "left" and self.dir == "right":
            self.image = pygame.transform.scale(self.original,(self.height * self.playerSize,self.width *self.playerSize))

    def deplacement(self):
        # fonction permettant à chaque categorie de monstre d'avoir un deplacement different et avoir des changements de sens si il y a une collision
        self.speedHori *= 0.88
        onground = self.check_collision(0, 1)

        if self.check_collision(1,0) and not self.munition:
            self.left = True
            self.right = False
            
        if self.check_collision(-1,0) and not self.munition:
            self.left = False
            self.right = True
        
        if self.check_collision(1,0) and self.munition:
            self.est_mort = True
            
        if self.check_collision(-1,0) and self.munition:
            self.est_mort = True
            
        if self.left:
            self.speedHori = -self.speed
            self.last_dir = self.dir
            self.dir = "left"
        
        elif self.right:
            self.speedHori = self.speed
            self.last_dir = self.dir
            self.dir = "right"
        
        else:
            self.speedHori = 0
        
        if not self.vol :
            
            if not onground:  
                self.speedVerti += self.gravity 
        self.move(self.speedHori, self.speedVerti)
    
    def actualise_rect(self):
        # definition des rectangles de l' entite permettant d'etre utiliser dans la collision avec le joueur pour savoir precisement quel endroit est touché
        self.rectHaut = self.rect.copy()

        self.rectHaut[2] = self.rect[2] *1.5

        self.rectHaut[0] -= self.rectHaut[2]/8

        self.rectHaut[3] = self.rect[3]/3
        self.rectHaut[1] = self.rect[1]-self.rectHaut[3]

        self.rectGauche = self.rect.copy()
        self.rectGauche[2] = self.rect[2]/2
        self.rectGauche[0] = self.rect[0] - self.rectGauche[2]

        self.rectDroit = self.rect.copy()
        self.rectDroit[2] = self.rect[2]/2
        self.rectDroit[0] = self.rect[0] + 2*self.rectDroit[2]

    def collisionJoueur(self,joueur):

        # fonction verifiant la collision des monstres avec le joueur dans les diverses possibilités(mario etoile,mario tape sur le cote,...)
        if self.doitTuerJoueur and not self.invisible : 
            if not self.affaibli:
                if self.name != 'plant.png' and pygame.Rect.colliderect(self.rectHaut, joueur.rect) and not self.est_mort and not pygame.Rect.colliderect(self.rect, joueur.rect) and not joueur.est_mort and joueur.speedVerti > 0 and not joueur.invincible:
                    # si le joueur arrive au-dessus du monstre
                    self.left = False
                    self.right = False
                    self.est_mort = True
                    print("ouch1")
                    joueur.speedVerti = -joueur.jumpspeed


                elif pygame.Rect.colliderect(self.rect, joueur.rect) and not self.est_mort and joueur.speedVerti <= 0:
                    #si le joueur arrive de cote
                    if not joueur.invincible or (self.name == 'plant.png' and not joueur.invincible):
                        joueur.toucher()
                    else:
                        self.est_mort = True
            else:#condition si le monstres est un koopa sous forme de carapace

                if not pygame.Rect.colliderect(self.rectGauche, joueur.rect) and not pygame.Rect.colliderect(self.rectDroit, joueur.rect) and pygame.Rect.colliderect(self.rectHaut, joueur.rect) and not self.est_mort:
                    self.left = False
                    self.right = False
                    joueur.speedVerti = -joueur.jumpspeed
                    
                    if joueur.invincible:
                        self.est_mort = True
                        print("ouch3")
        
                elif pygame.Rect.colliderect(self.rectGauche, joueur.rect) :
                    
                    if joueur.invincible:
                        self.est_mort = True
                        print("ouch4")
                    
                    elif not self.right and not self.left:
                        self.left = False
                        self.right = True
                    elif self.left and not joueur.invincible:
                        joueur.toucher()
                        
                elif pygame.Rect.colliderect(self.rectDroit, joueur.rect):
                    
                    if joueur.invincible:
                        self.est_mort = True
                        print("ouch5")
                        
                    elif not self.right and not self.left:
                        self.right = False
                        self.left = True
                    elif self.right and not joueur.invincible:
                        joueur.toucher()
                
                world = jeu.classDict['monde']
                
                for mobs in world.monstre:
                    if self != world.monstre[mobs]:
                        if world.monstre[mobs].doitTuerJoueur:
                            if pygame.Rect.colliderect(self.rect,world.monstre[mobs].rect):
                                world.monstre[mobs].est_mort = True
                            
        else:   
            fautmourrir = True
            if pygame.Rect.colliderect(self.rect, joueur.rect) and not self.est_mort:
                # Rencontres entre les diverses pouvoirs et le joueur qui va occasionner le changement de forme du joueur
                if self.name == "champi.png" and joueur.etat == "petit":
                    #verification d'un conctact block/joueur quand il grandis et le deplace d'un des deux cotés si il y a contact pour ne pas rester bloquer dans le block
                    
                    if joueur.check_collision(-int(self.screen.get_size()[1]/15),0):
                        joueur.pos.x += int(self.screen.get_size()[1]/15)
                        
                    if joueur.check_collision(int(self.screen.get_size()[1]/15),0):
                        joueur.pos.x -= int(self.screen.get_size()[1]/15)

                    avant = (copy.deepcopy(joueur.rect),joueur.image.copy())
                    if not joueur.changeSkin("grand"):
                        joueur.rect,joueur.image = avant
                        fautmourrir = False
                    

                elif self.name == "champi.png" and joueur.etat == "etoile" and joueur.lastEtat == "petit":
                    joueur.lastEtat = "grand"
                
                elif self.name == "champi.png" and joueur.etat == "etoile" and joueur.lastEtat == "petit":
                    joueur.lastEtat = "grand"
                    
                if self.name == "fireflower.png":
                    if joueur.etat == "etoile":
                        if joueur.lastEtat == "petit":
                            joueur.lastEtat = "grand"
                        else:
                            joueur.lastEtat = "feu"
                        
                    elif joueur.etat == "petit" :
                        avant = (copy.deepcopy(joueur.rect),joueur.image.copy())
                        if not joueur.changeSkin("grand"):
                            joueur.rect,joueur.image = avant
                            fautmourrir = False
                    else:
                        avant = (copy.deepcopy(joueur.rect),joueur.image.copy())
                        if not joueur.changeSkin("feu"):
                            joueur.rect,joueur.image = avant
                            fautmourrir = False

                if self.name == "star.png":
                    avant = (copy.deepcopy(joueur.rect),joueur.image.copy())
                    if not joueur.changeSkin("etoile"):
                        joueur.rect,joueur.image = avant
                        fautmourrir = False

                if self.name == "plant.png":
                    fautmourrir = False

                if fautmourrir:
                    self.est_mort = True
                
    def check_collision(self, x, y):
        #fonction regardant les collisions entre le joueur et la map
        collide = False
        self.pos += [x,y]
        self.rect.midbottom = self.pos

        screenSize = self.screen.get_size()
        for e in self.blockRECT:
            for i in self.blockRECT[e]:
                if pygame.Rect.colliderect(self.rect, i[0]):
                    if i[2][1]: # i[2][1] --> True ou False, correspond a si le bloc est sensé avoir une collision ou non
                        collide = True
         
        world = jeu.classDict['monde']
        key = "Pario.png"
        joueur = world.players[key]
        save = [joueur.rect[0],joueur.rect[1]]
        joueur.rect[0],joueur.rect[1] = joueur.pos


        
        joueur.rect.x -= self.decalage
        joueur.rect.x -= joueur.rect[2]/2
        joueur.rect.y -= joueur.rect[3]

        self.rect.x -= self.decalage
        self.actualise_rect()

        self.collisionJoueur(joueur)

        joueur.rect[0],joueur.rect[1] = save
                
        self.pos += [-x,-y]
        self.rect.midbottom = self.pos
        self.actualise_rect()
        return collide
              
    def move(self,x,y):
        # fonction permettant le mouvement de l'entité
        dx = x
        dy = y
        
        while self.check_collision(0, dy):
            dy -= numpy.sign(dy)

        while self.check_collision(dx, dy):
            dx -= numpy.sign(dx)
            
        self.pos += [dx,dy]
        self.rect.midbottom = self.pos
        
        if self.check_collision(0, -1):
            self.speedVerti = 0   
    
    def changement_forme(self):
        # fonction permettant le changement de forme du pooka en carapace si le joueur lui saute dessus et modifie les parametres de cette entité
        if self.est_mort:
            self.name = "carapace.png"
            if self.ville != 'paris':
                self.original = pygame.image.load(f'{jeu.world}/assets/others/{self.name}').convert_alpha()
            else:
                self.original = pygame.image.load(f'{jeu.world}/assets/paris_others/{self.name}').convert_alpha()
            self.image = pygame.transform.scale(self.original,(self.height * self.playerSize *2,self.width * self.playerSize))
            self.rect = self.image.get_rect()
            self.est_mort = False
            self.affaibli = True
            self.repetition = False
            self.vol = False
            self.speed = round(self.screen.get_size()[0] * 0.002083) *4
    
    def update(self):
        "fonction qui appelle toute les fonctions nécessaire au bon fonctionnement de la classe (est appeller a chaque image dans la classe world et ceux pour chaque monstre)"
        if self.est_mort :
            return self.realName
        self.eviteLeSuicide()
        self.deplacement()
        if not self.affaibli and self.repetition:
            self.changement_forme()
        self.animation()
        self.actualise_rect()
        self.apparition()
        self.animPlant()
        self.draw()
              
class World:
    def __init__(self,screen,chemin,sauv,name) -> None:
        self.name = name
        self.cooldown = 0
        self.COOLDOWN = 10
        self.quotient = screen.get_size()[0] / 1920
        self.width , self.height = screen.get_size()
        self.screen = screen
        self.world = jeu.get_txt(chemin)# blocks permettant la creation du niveau  
        self.blockSize = int(screen.get_size()[1]/15)
        self.decalage = 0
        self.imagesWorldOrigignal = {}
        self.imagesWorld = {}
        self.players = {}
        self.instruDict = jeu.dicoInstru(jeu.get_txt('block.txt'))
        self.sauvegarde = sauv
        self.sauv = sauv
        self.chemin = chemin
        self.monstre = {}
        self.chargement()
        self.compteur = 0
        self.monstre_spawn = []
        self.nb_monstre = 0
        self.toDeleteMonstre = []
        self.finito = False
        self.compteurEcrFin = 0
        self.TPSECRWIN = 4 #en secondes
        self.position_cannon = []
        self.timer = 0
        self.stop = []

        """
        Tout ce qui suis est fait pour le niveau spécial Tetris.
        """
        
        self.colonnes = 10
        self.lignes = 20
        size = 0.5
        self.case = int(self.screen.get_size()[1]/15) * size
        self.decalageCase = self.screen.get_size()[0] * 0.5 - self.case * self.colonnes * size

        self.formes = {'O' : [(255,255,0),[],[[] for i in range(3)]],'I' : [(0,0,255),[],[[] for i in range(3)]],'S' : [(255,0,0),[],[[] for i in range(3)]],'Z' : [(20,150,30),[],[[] for i in range(3)]],'L' : [(230,150,10),[],[[] for i in range(3)]],'J' : [(240,90,170),[],[[] for i in range(3)]],'T' : [(175,15,200),[],[[] for i in range(3)]]}

        for forme in self.formes:
            for i in range(4):
                if forme == 'O':
                    if i < 2:
                        rect = pygame.Rect(self.case * i,0,self.case,self.case)
                    else:
                        rect= pygame.Rect(self.case  * (i-2),self.case,self.case,self.case)
                    rect0 = rect1 = rect2 = copy.deepcopy(rect)
                
                elif forme == 'I':
                    rect = pygame.Rect(self.case,self.case * i,self.case,self.case)

                    rect0 = pygame.Rect(self.case * i- 2*self.case,-self.case,self.case,self.case)
                    rect1 = pygame.Rect(0,self.case * i,self.case,self.case)
                    rect2 = pygame.Rect(self.case * i- 2*self.case,0,self.case,self.case)
                
                elif forme == 'S':
                    if i < 2:
                        rect = pygame.Rect(self.case * i + self.case ,0,self.case,self.case)
                        rect0 = pygame.Rect(self.case,self.case *i,self.case,self.case)
                        rect1 = pygame.Rect(self.case * i + self.case ,self.case,self.case,self.case)
                        rect2 = pygame.Rect(0,self.case * i,self.case,self.case)
                    
                    else:
                        rect0 = pygame.Rect(self.case *2,self.case *(i-2) + self.case,self.case,self.case)
                        rect1 = pygame.Rect(self.case * (i-2),self.case *2,self.case,self.case)
                        rect2 = pygame.Rect(self.case,self.case + self.case * (i-2),self.case,self.case)
                        
                        rect = pygame.Rect(self.case * (i-2),self.case,self.case,self.case)
                      
                   
                elif forme == 'Z':
                    if i < 2:
                        rect = pygame.Rect(self.case * i ,0,self.case,self.case)

                        rect0 = pygame.Rect(self.case * 2 ,self.case * i,self.case,self.case)
                        rect1 = pygame.Rect(self.case * i ,self.case,self.case,self.case)
                        rect2 = pygame.Rect(self.case,self.case * i,self.case,self.case)
                    else:
                        rect = pygame.Rect(self.case * i - self.case,self.case,self.case,self.case)
                        rect0 = pygame.Rect(self.case  ,self.case * (i-1),self.case,self.case)
                        rect1 = pygame.Rect(self.case * i -self.case,self.case *2,self.case,self.case)
                        rect2 = pygame.Rect(0,self.case *(i-1),self.case,self.case)
                
                elif forme == 'L':
                    if i < 3:
                        rect = pygame.Rect(0,self.case * i,self.case,self.case)
                        rect0 = pygame.Rect(self.case * i,self.case,self.case,self.case)
                        rect1 = pygame.Rect(self.case,self.case * i,self.case,self.case)
                        rect2 = pygame.Rect(self.case * i,self.case,self.case,self.case)
                    else:
                        rect = pygame.Rect(self.case,self.case * (i-1),self.case,self.case)
                        rect0 = pygame.Rect(self.case *2,0,self.case,self.case)
                        rect1 = pygame.Rect(0,0,self.case,self.case)
                        rect2 = pygame.Rect(0,self.case * 2,self.case,self.case)

                
                elif forme == 'J':
                    if i < 3:
                        rect = pygame.Rect(self.case,self.case * i,self.case,self.case)
                        rect0 = pygame.Rect(self.case * i,self.case,self.case,self.case)
                        rect1 = pygame.Rect(self.case,self.case * i,self.case,self.case)
                        rect2 = pygame.Rect(self.case *i,self.case,self.case,self.case)

                    else:
                        rect = pygame.Rect(0,self.case * (i-1),self.case,self.case)
                        rect0 = pygame.Rect(self.case * 2,self.case *2,self.case,self.case)
                        rect1 = pygame.Rect(self.case *2,0,self.case,self.case)
                        rect2 = pygame.Rect(0,0,self.case,self.case)
                
                elif forme == 'T':
                    if i < 3:
                        rect = pygame.Rect(self.case * i,0,self.case,self.case)
                        rect0 = pygame.Rect(self.case,self.case * i,self.case,self.case)
                        rect1 = pygame.Rect(self.case * i,self.case ,self.case,self.case)
                        rect2 = pygame.Rect(self.case ,self.case * i,self.case,self.case)
                    else:
                        rect = pygame.Rect(self.case,self.case,self.case,self.case)
                        rect0 = pygame.Rect(self.case *2,self.case,self.case,self.case)
                        rect1 = pygame.Rect(self.case ,0 ,self.case,self.case)
                        rect2 = pygame.Rect(0,self.case ,self.case,self.case)
                
                rect.x += self.decalageCase + self.case * (self.colonnes * 0.5) - self.case

                rect0.x += self.decalageCase + self.case * (self.colonnes * 0.5) - self.case
                rect1.x += self.decalageCase + self.case * (self.colonnes * 0.5) - self.case
                rect2.x += self.decalageCase + self.case * (self.colonnes * 0.5) - self.case

                self.formes[forme][2][0].append(rect0)
                self.formes[forme][2][1].append(rect1)
                self.formes[forme][2][2].append(rect2)

                self.formes[forme][1].append(rect)

        self.next = copy.deepcopy(list(self.formes.values()))
        self.select = copy.deepcopy(self.next[0])
        self.compteurSel = 0
        self.ligneColl = []
        for ligne in range(self.lignes):

            self.ligneColl.append([pygame.Rect(self.decalageCase,self.case * ligne + self.case +self.case * 0.25,self.case * self.colonnes,self.case *0.5),ligne])

        self.enbas = 0
        self.adroite = 0
        self.agauche = self.screen.get_size()[0]
        self.stopSelect = False
        self.allCase = []
        self.tropbas = 0

        self.acc = 0
        self.ligneVide = []
        self.compteurNext = 0

        self.quaranteNeufAlinea3 = False

    def chargement(self):
        """Charge en memoire les différentes images qui seront afficher dans les niveaux"""
        c = 0
        self.screen.fill('black')
        if not 'paris' in self.name:
            txt = jeu.font.render(f"{jeu.world}-{self.name}",True,(255,255,255))
        else:
            txt = jeu.font.render(f"49 Alinéa 3",True,(255,255,255))
        self.screen.blit(txt,(self.screen.get_size()[0] *0.5 - txt.get_size()[0] *0.5,self.screen.get_size()[1] *0.5 - txt.get_size()[1] *0.5))
        pygame.display.flip()
        self.othersIMG = {}
        self.winIMG = pygame.transform.scale(pygame.image.load('assets/world/others/win.png'),(self.screen.get_size()[0] * 0.5,self.screen.get_size()[1] * 0.5))
        
        if not 'paris' in self.name:
            listdir = os.listdir(f'{jeu.world}/assets/others')
        else:
            listdir = os.listdir(f'{jeu.world}/assets/paris_others')
        
        for img in listdir:
            c += 1
            if 'fond' in img:
                self.othersIMG[img] = pygame.image.load(f'{jeu.world}/assets/others/{img}').convert_alpha()
                scale = self.othersIMG[img].get_size()
                self.othersIMG[img] = pygame.transform.scale(self.othersIMG[img],(scale[0]*self.quotient,scale[1]*self.quotient ))

            if 'win' in img:
                self.othersIMG[img] = pygame.transform.scale(pygame.image.load(f'{jeu.world}/assets/others/{img}').convert_alpha(),(self.screen.get_size()[0] * 0.5,self.screen.get_size()[1] * 0.5))
        
        if not 'paris' in self.name:
            listdir = os.listdir(f'{jeu.world}/assets/blocs')
        else:
            listdir = os.listdir(f'{jeu.world}/assets/paris_blocs')
        for name in listdir:
            c += 1
            if not 'paris' in self.name:
                self.imagesWorld[name] = pygame.image.load(f'{jeu.world}/assets/blocs/{name}').convert_alpha()
            else:
                self.imagesWorld[name] = pygame.image.load(f'{jeu.world}/assets/paris_blocs/{name}').convert_alpha()   
        for image in self.instruDict:
            c += 1
            self.imagesWorld[self.instruDict[image][0]] = pygame.transform.scale(self.imagesWorld[self.instruDict[image][0]],(self.blockSize * float(self.instruDict[image][6]), self.blockSize * float(self.instruDict[image][7])))
            if self.instruDict[image][2]:
                self.imagesWorld[self.instruDict[image][4]] = pygame.transform.scale(self.imagesWorld[self.instruDict[image][4]],(self.blockSize * float(self.instruDict[image][6]), self.blockSize * float(self.instruDict[image][7])))
        self.liste = []

        self.elementIntoListe()
        
        self.initialiseDicoBloc()
    
        self.players["Pario.png"] = Players(self.screen,self.blockRECT,"Pario.png",True,jeu.classDict['menu'].touchesDict,self.name)

    def initialiseDicoBloc(self):
        """Crée un dictionnaire qui va stocker en clé le symbole représentant un bloc dans le fichier txt qui décrit le niveaux et qui va mettre dans une liste associé a cette clé , tout les blocs lui correspondant
        ainsi que leur position et un rectangle"""
        self.blockRECT = {}
        for i in self.instruDict:
            self.blockRECT[i] = []
        for e in self.liste:
            for instru in self.instruDict:
                if e[2] == instru:
                    rect = pygame.Rect(e[1]* self.blockSize-self.decalage, e[0]*self.blockSize, self.blockSize * self.instruDict[instru][6], self.blockSize *  self.instruDict[instru][7])
                    self.blockRECT[instru].append([rect,instru,self.instruDict[instru]])

    def mort(self):
        """Si le joueur est mort , lui enleve une vie sur sa sauvegarde. Si le joueur n'a plus de vie , il pert la progression dans le mondes"""
        c = 0
        for i in self.players:
            if self.players[i].rect.y >= self.screen.get_size()[1] or self.players[i].est_mort:
                self.sauvegarde['V'][c] -= 1
                if self.sauvegarde['V'][c] <= 0 :
                    for ville in jeu.allWorlds[self.sauvegarde['M'][-1]]:
                        if ville in self.sauvegarde['N']:
                            self.sauvegarde['N'].remove(ville)
                    self.sauvegarde['N'].append(list(jeu.allWorlds[self.sauvegarde['M'][-1]])[0])
                    self.sauvegarde['V'][c] = 5
                    self.sauvegarde['S'] = [0,0]
                
                self.save()
                jeu.position = 'carte'
                jeu.classPos = ''
            c+=1

    def monstres(self):#fais apparaitre les monstres si proche du joueur sinon le rajoute a une liste d'attente et ajoute les lanceurs de missiles dans une liste pour connaitre leurs positions et savoir quand les faire fonctionner
        for name in self.blockRECT:
            if self.instruDict[name][10]:

                for i in range(len(self.blockRECT[name])):
                    if int(self.players["Pario.png"].pos[0]+1200) < self.blockRECT[name][i][0][0]:
                        self.monstre_spawn.append((self.instruDict[name][4],(self.blockRECT[name][i][0][0],self.blockRECT[name][i][0][1])))
                    else:
                        self.monstre[self.instruDict[name][4]+str(self.nb_monstre)] = Mobs(self.screen,self.blockRECT,self.instruDict[name][4],(self.blockRECT[name][i][0][0],self.blockRECT[name][i][0][1]),self.instruDict[name][4]+str(self.nb_monstre),self.name)
                        self.nb_monstre+=1
                        
            if name == "C" or name == "I":
                for i in range(len(self.blockRECT[name])):
                    self.position_cannon.append((self.instruDict[name][4],(self.blockRECT[name][i][0][0],self.blockRECT[name][i][0][1])))
                          
    def spawn(self):# fais apparaitre les monstres quand ils sont a une distance raisonnable du joueur
        if self.monstre_spawn != []:
            liste_supp = []
            for i in self.monstre_spawn:
                if int(self.players["Pario.png"].pos[0]+1200) > i[1][0]:
                    self.monstre[i[0]+str(self.nb_monstre)] = Mobs(self.screen,self.blockRECT,i[0],(i[1][0],i[1][1]),i[0]+str(self.nb_monstre),self.name)
                    self.nb_monstre+=1
                    liste_supp.append(self.monstre_spawn.index((i[0],(i[1][0],i[1][1]))))
            if liste_supp != []:
                for element in liste_supp:
                    self.monstre_spawn.pop(element)

    def spawn_missiles(self):
        # fonction qui permet de faire apparaitre les missiles si on peut voir le lanceur de missiles et d'arreter ces même lanceurs si ils sont trop loin
        if self.position_cannon != []:
            liste = []
            for i in self.position_cannon:
                if int(self.players["Pario.png"].pos[0]+1200) > i[1][0]:
                    if self.timerfunc():
                        self.monstre[i[0]+str(self.nb_monstre)] = Mobs(self.screen,self.blockRECT,i[0],(i[1][0],i[1][1]),i[0]+str(self.nb_monstre),self.name)
                        self.nb_monstre+=1
                if int(self.players["Pario.png"].pos[0]-1200) > i[1][0]:
                    self.stop.append((self.position_cannon.index((i[0],(i[1][0],i[1][1]))),i[0],(i[1][0],i[1][1])))
                    liste.append((self.position_cannon.index((i[0],(i[1][0],i[1][1]))),i[0],(i[1][0],i[1][1])))
            if liste != []:
                for element in  liste:
                    self.position_cannon.pop(element[0])
    
    def revenir_sur_ses_pas(self):
        # fonction de relancer les lanceurs de missiles si le joueur revient en arriere
        if self.stop != []:
            liste = []
            for i in self.stop:
                if int(self.players["Pario.png"].pos[0]-1200) < i[2][0]:
                    self.position_cannon.append((i[1],(i[2][0],i[2][1])))
                    liste.append(self.stop.index((i[0],i[1],(i[2][0],i[2][1]))))
            
            if liste != []:
                for element in liste:
                    self.stop.pop(element)
                
    def elementIntoListe(self):
        """Parcout la liste qui contient le fichier txt correspondant a un niveau et renvoie une liste avec le symbole du bloc ainsi que sa position """
        for ligne in range(len(self.world)):
            if self.world[ligne] != '':
                for e in range(len(self.world[ligne])):
                    for instru in self.instruDict:
                        if self.world[ligne][e] == instru:
                            self.liste.append([ligne,e,instru])

    def drawBackGround(self):
        #fonction peremttant l'affichage du fond
        self.screen.blit(self.othersIMG[f'fond.png'],(-self.decalage,-self.screen.get_size()[0]*0.07))

    def draw_on_screen(self):
        """Affiche sur l'écran les pieces et les vies , les blocs du niveaux , les fps , et si un niveau est terminé , débloque le prochain (Avec conditions spéciale pour un certain niveau) """
        
        txt = str(self.sauvegarde['S'][0])
        if len(txt) == 1:
            self.screen.blit(jeu.font2.render("Pieces : 0"+txt +f' Vie : {self.sauvegarde["V"][0]}',True,(255,255,255)),(0,0))
        else:
            self.screen.blit(jeu.font2.render("Pieces : "+txt+f' Vie : {self.sauvegarde["V"][0]}',True,(255,255,255)),(0,0))
            
        for keys in self.blockRECT :
            for i in self.blockRECT[keys]:
                if i[2][9]:
                    rect = pygame.Rect(i[0][0]-self.decalage, i[0][1], self.blockSize, self.blockSize)
                    if -self.decalage -1 <= rect.x <= self.screen.get_size()[0] + self.decalage:
                        
                        if not i[2][5]:
                            self.screen.blit(self.imagesWorld[self.instruDict[i[1]][0]],rect)
                        else:
                            self.screen.blit(self.imagesWorld[self.instruDict[i[1]][4]],rect)
        
        if self.finito:
            self.compteurEcrFin += 1
            screensize = self.screen.get_size()
            surface = pygame.Surface(screensize)
            surface.set_alpha(150)
            self.screen.blit(surface,(0,0))
            self.screen.blit(self.winIMG,(screensize[0] * 0.5 - screensize[0] * 0.5 * 0.5,screensize[1] * 0.5 - screensize[1] * 0.5 * 0.5))
        
        fps = round(jeu.clock.get_fps(),1)

        if self.compteurEcrFin / fps >= self.TPSECRWIN:
            jeu.position = 'carte'
            jeu.classPos = ''
            if not list(jeu.villesEU)[list(jeu.villesEU).index(self.name)+1] in self.sauv['N']:
                self.sauv['N'].append(list(jeu.villesEU)[list(jeu.villesEU).index(self.name)+1])
            
            self.save()
        
        if jeu.classDict['menu'].settingsDict['ShowFPS']:
            self.screen.blit(jeu.font2.render(str(fps),True,(255,255,255)),(0,self.screen.get_size()[1] - jeu.police))

    def scrolling(self):
        """
        fonction permettant le deplacement de l'ecran sur la map selon les deplacement du joueur
        """
        for name in self.players:
            if self.players[name].rect.x-self.players[name].decalage >= self.width*0.55-self.decalage:
                self.decalage += self.players[name].speedHori
                self.players[name].decalage = self.decalage
                for nameMonstre in self.monstre :
                    self.monstre[nameMonstre].decalage = self.decalage
                for boule in self.players[name].bouleDeFeu:
                    boule.decalage = self.decalage

            if self.players[name].rect.x-self.players[name].decalage <= self.width*0.45-self.decalage and self.decalage>0:     
                self.decalage += self.players[name].speedHori
                self.players[name].decalage = self.decalage
                for nameMonstre in self.monstre :
                    self.monstre[nameMonstre].decalage = self.decalage
                for boule in self.players[name].bouleDeFeu:
                    boule.decalage = self.decalage  

    def inputsMouse(self):
        """Récupere la position de la souris a tout moment et quand le joueur clique"""
        self.Mpos = pygame.mouse.get_pos()
        self.mouseDown = pygame.mouse.get_pressed()
    
    def save(self):
        """Supprime une sauvegarde et crée une nouvelle sauvegarde vide""" 
        os.remove(f'sauvegardes/save{jeu.classDict["menu"].cSauv}.txt')
        lVal = list(self.sauvegarde.values())
        jeu.classDict['menu'].nouvelle_sauvegarde(lVal[0],lVal[1],lVal[2],lVal[3][0],lVal[3][1])

    def special(self):
        """Gere le niveau spécial Tetris"""
        
        surface = pygame.Surface((int(self.colonnes * self.case),int(self.case * self.lignes)))
        surface.set_alpha(200)
        self.screen.blit(surface,(self.agauche,self.case))  

        c = -1
        for rect in self.select[1]:
            c += 1
            if self.stopSelect:
                self.allCase.append([copy.deepcopy(self.select[1][c]),copy.deepcopy(self.select[0])])
                if c == 3:
                    self.stopSelect = False
                    if not self.compteurSel == len(self.next)-1:
                        self.compteurSel += 1
                    else:
                        self.compteurSel = 0
                    
                    self.select = copy.deepcopy(self.next[self.compteurSel])
                    if self.compteurNext != len(self.next) -1:
                        self.compteurNext += 1
                    else:
                        self.compteurNext = 0
                    self.stopClone = False
                    

                continue
            
            plusAgauche = self.screen.get_size()[0]
            plusAdroite = 0
            peuadroite = True
            peuagauche = True
            
            c2 = -1
            for case in self.select[1]:
                c2 += 1

                rectcopy = copy.deepcopy(case)
                rectcopy.x -= self.case *0.5
                
                for rectAll in self.allCase:
                    if pygame.Rect.colliderect(rectcopy,rectAll[0]):
                        peuagauche = False

                
                if case.left < plusAgauche:
                    plusAgauche = copy.deepcopy(case.left)

                if case.right > plusAdroite:
                    plusAdroite = copy.deepcopy(case.right)
                
                rectcopy.x += self.case *0.5 *2
                for rectAll in self.allCase:
                    if pygame.Rect.colliderect(rectcopy,rectAll[0]):
                        peuadroite = False

            if pygame.key.get_pressed()[jeu.classDict['menu'].touchesDict['Gauche']] and self.cooldown > self.COOLDOWN and peuagauche:
                self.cooldown = 0       
                if plusAgauche > self.agauche:
                    for case in range(len(self.select[1])):
                        self.select[1][case].x -= self.case  
                    for other in range(3):
                        for i in range(4):
                            self.select[2][other][i].x -= self.case
            
            if pygame.key.get_pressed()[jeu.classDict['menu'].touchesDict['Droite']] and self.cooldown > self.COOLDOWN and peuadroite:
                self.cooldown = 0        
                if plusAdroite < self.adroite:
                    for case in range(len(self.select[1])):
                        self.select[1][case].x += self.case  
                    for other in range(3):
                        for i in range(4):
                            self.select[2][other][i].x += self.case
            

            if pygame.key.get_pressed()[jeu.classDict['menu'].touchesDict['Saut']] and self.cooldown > self.COOLDOWN:
                self.cooldown = 0
                collide = False
                for case in self.allCase:
                    for j in self.select[2][0]:
                        if pygame.Rect.colliderect(case[0],j) or j.left < self.agauche or j.right > self.adroite:
                            collide = True
                if not collide and self.select[0] != self.formes['O'][0]:
                    tempo = copy.deepcopy(self.select[2].pop(0))
                    self.select[2].append(copy.deepcopy(self.select[1]))
                    self.select[1] = tempo


            for other in range(3):
                self.select[2][other][c].y += self.case * (0.1+self.acc)
                    
            self.select[1][c].y += self.case * (0.1+self.acc)
            pygame.draw.rect(self.screen,self.select[0],rect)
            pygame.draw.rect(self.screen,(255,255,255),rect,1)


            if not self.select[1][c].y +1 < self.case * self.lignes and not self.stopSelect:
                self.stopSelect = True
                break
            
            for case in self.allCase:
                if pygame.Rect.colliderect(self.select[1][c],case[0]):
                    self.stopSelect = True
                    break
            else:
                continue
            break


        for rect in self.allCase:
            pygame.draw.rect(self.screen,rect[1],rect[0])
        
        for i in range(len(self.ligneColl)):
            liste = []
            for index in range(len(self.allCase)):
                if pygame.Rect.colliderect(self.allCase[index][0],self.ligneColl[i][0]):
                    liste.append(copy.deepcopy(self.allCase[index]))

            if len(liste) == self.colonnes:
                if not self.finito:
                    self.players['Pario.png'].speedHori = self.players['Pario.png'].speed * 40
                
                for carre in liste:
                    self.allCase.pop(copy.deepcopy(self.allCase.index(carre)))
                
                for case in self.allCase:
                    for j in range(1,i+1):
                        if pygame.Rect.colliderect(case[0],self.ligneColl[i-j][0]):
                            case[0].y += self.case
                    

        for colonne in range(self.colonnes):
            for ligne in range(self.lignes):
                rect = pygame.Rect((self.case * colonne) + self.decalageCase,self.case * ligne + self.case,self.case,self.case)
                
                if rect.bottom > self.enbas:
                    self.enbas = rect.bottom
                if rect.right > self.adroite:
                    self.adroite = rect.right
                if rect.left < self.agauche:
                    self.agauche = rect.left
                
                pygame.draw.rect(self.screen,(255,255,255),rect,1)
        

        for i in range(len(self.ligneColl)):
            c = 0
            for index in range(len(self.allCase)):
                if pygame.Rect.colliderect(self.allCase[index][0],self.ligneColl[i][0]):
                    if i == 0:
                        self.save()
                        jeu.position = 'carte'
                        jeu.classPos = ''
                    c += 1
                    self.allCase[index][0].y = self.ligneColl[i][0].center[1] - self.case *0.5
    
        self.screen.blit(jeu.font2.render(f"Gauche : {pygame.key.name(jeu.classDict['menu'].touchesDict['Gauche'])}, Droite : {pygame.key.name(jeu.classDict['menu'].touchesDict['Droite'])}",True,(255,255,255)),(0,int(jeu.police *0.5)))
        self.screen.blit(jeu.font2.render(f"Rotate : {pygame.key.name(jeu.classDict['menu'].touchesDict['Saut'])}",True,(255,255,255)),(0,int(jeu.police *0.5 *2)))
        self.screen.blit(jeu.font2.render("Suivant : ",True,(255,255,255)),(0,int(jeu.police *0.5 * 4.6)))
        

        for rect in self.next[self.compteurNext][1]:
                copie = rect.copy()
                copie.x -= jeu.screenSize[0] * 0.38
                copie.y += jeu.screenSize[1] * 0.2
                pygame.draw.rect(self.screen,self.next[self.compteurNext][0],copie)
                pygame.draw.rect(self.screen,(0,0,0),copie,1)
    
    def update(self):
        """fonction qui appelle toute les fonctions nécessaire au bon fonctionnement de la classe , appelle les fonction pour faire apparaitre les monstres
        gérer le scrolling de l'écran  """
        self.cooldown += 1
        if self.compteur < 1:
            self.monstres()
            self.compteur+=1
        self.spawn()
        self.spawn_missiles()
        self.revenir_sur_ses_pas()
        self.mort()
        self.inputsMouse()
        self.scrolling()
        self.drawBackGround()
        
        for personnage in self.players:
            self.players[personnage].update()
            
        if len(self.toDeleteMonstre) != 0:
            for e in self.toDeleteMonstre:
                self.monstre.pop(e)
            self.toDeleteMonstre = []
                
        for monstres in self.monstre:
            toDelete = self.monstre[monstres].update()
            if toDelete :
                self.toDeleteMonstre.append(toDelete)

        self.draw_on_screen()
        
        if self.name == 'st-petersbourg':
            self.special()
            self.acc += 0.000000005

class BouleDeFeu:
    # classe utilise pour les boules de feu crées par Mario feu
    def __init__(self,screen,blockRECT,pos,decalage,dir,ville,sprite) -> None:
        self.screen = screen
        self.blockRECT = blockRECT
        self.ville = ville
        self.pos = pos.copy()
        joueur = jeu.classDict['monde'].players["Pario.png"]
        self.pos[1]-= joueur.rect[3]/2.5
        self.rect = pygame.Rect(pos[0],pos[1],20,20)
        self.speedVerti = round(self.screen.get_size()[0]*0.0035)
        self.speedHori = round(self.screen.get_size()[0]*0.0105) * dir
        self.gravity = self.screen.get_size()[1] * 0.0015
        self.decalage = decalage
        self.limite = 0
        self.asupprimer = False
        self.sprite = pygame.transform.scale(sprite, (self.rect[2], self.rect[3]))

    def deplacement(self):
        #fonction définissant le mouvement de la boule de feu
        onground = self.check_collision(0, 1)
        
        if self.pos.x < 0 :
            self.asupprimer = True


        if self.pos.y < self.limite-round(self.screen.get_size()[0]*0.0347):
            self.speedVerti = round(self.screen.get_size()[0]*0.0035)


        if onground and self.speedVerti > 0:
            self.speedVerti = - round(self.screen.get_size()[0]*0.0035)
            self.limite = self.pos.y

        self.move(self.speedHori, self.speedVerti)

    def tueMob(self):
        #fonction qui tue le monstre si il rencontre une boule de feu et fais disparaitre cette boule de feu
        world = jeu.classDict['monde']
        for key in world.monstre:
            if pygame.Rect.colliderect(self.rect, world.monstre[key].rect):
                world.monstre[key].est_mort = True
                self.asupprimer = True

    def move(self,x,y):
        #fonction qui deplace l'entite et la supprime si elle rencontre un mur
        dx = x
        dy = y

        while self.check_collision(0, dy):
            dy -= numpy.sign(dy)

        while self.check_collision(dx, dy):
            dx -= numpy.sign(dx)


        self.pos += [dx,dy]

        self.rect.midbottom = self.pos
        

        if self.check_collision(0, -1):
            self.speedVerti = 0

        if self.check_collision(1, 0):
            self.asupprimer = True

        if self.check_collision(-1, 0):
            self.asupprimer = True

    def check_collision(self, x, y):
        #fonction verifiant les collisions entre les boules de feu et la map
        collide = False
        self.pos += [x,y]

        self.rect.midbottom = self.pos
        
        for e in self.blockRECT:
            for i in self.blockRECT[e]:
                if pygame.Rect.colliderect(self.rect, i[0]) and i[2][1] :
                    collide = True
                    
        self.pos += [-x,-y]
        self.rect.midbottom = self.pos

        return collide
    
    def draw(self):
        #fonction qui permet l'affichage de la boule de feu
        self.rect.x -= self.decalage
        self.screen.blit(self.sprite,self.rect)

    def update(self):
        self.deplacement()
        self.draw()     
        self.tueMob()
   
        
jeu = Jeu()
while True :
    jeu.update()



