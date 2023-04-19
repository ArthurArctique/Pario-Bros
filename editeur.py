#206
import pygame
from pygame.locals import *
import os

screen = pygame.display.set_mode((1440,810))


def dicoInstru(chemin):
        file = open(chemin, 'r')
        data = file.read()
        liste = data.split("\n")
        file.close()
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
                        elif savoirSiFloat(chaineCAr) or savoirSiFloat(chaineCAr[1:]):
                            chaineCAr = float(chaineCAr)
                        dict_[i[0]].append(chaineCAr)
                        chaineCAr = ''
                        if lettre == ']':
                            break
        return dict_

def savoirSiFloat(elt):
    try:
        float(elt)
        return True
    except ValueError:
        return False

ligne = {ligne:[' ' for i in range(206)] for ligne in range(15)}

def txt():
    str_ = ''
    for i in os.listdir():
        str_ = str_ + i
    if not 'nivED' in str_:
        writeTXT('nivED0.txt')
    else:
        tempo = os.listdir()
        tempo.sort()
        a = []
        for i in tempo:
            if 'nivED' in i:
                a.append(i)
        tempo = int(a[-1][a[-1].index('.')-1])
        writeTXT(f'nivED{tempo+1}.txt')

def writeTXT(nom):
    chaineCar = ''
    first = True
    for l in ligne:
        if first:
            first = False
        else:
            chaineCar = chaineCar + '\n'
        
        for car in ligne[l]:
            chaineCar = chaineCar + car

    with open(nom,'w') as txt:
        txt.write(chaineCar)




info = dicoInstru('block.txt')
scale = 0.75

image = {}
for i in info:
    image[info[i][0]] = [pygame.transform.scale(pygame.image.load(f'Europe/rennes/assets/blocs/{info[i][0]}'),(int(810/15) * scale * info[i][6],int(810/15) * scale * info[i][6] )),i]

case = {}

for x in range(206):
    for y in range(15):
        case[(x,y)] = None

select = ''
decalage = 0
cooldown = 5
COOLDOWN = 5
groscooldown = 500
GROSCOOLDOWN = 500

while True:
    cooldown += 1
    groscooldown += 1
    screen.fill('lightblue')

    curseur = pygame.Surface((1,1)).get_rect()
    
    curseur.x,curseur.y = pygame.mouse.get_pos()

    if pygame.key.get_pressed()[K_SPACE] and groscooldown > GROSCOOLDOWN:
        groscooldown = 0
        txt()

    if pygame.mouse.get_pressed()[1]:
        if curseur.x > 740 and decalage < 7050:
            decalage += 50
        elif curseur.x < 700 and decalage > -100:
            decalage -= 50
    
    for j in range(206):
        for i in range(15):
            
            if not case[(j,i)]:
                surface = pygame.Surface((int(810/15) * scale,int(810/15) * scale))
            else:

                surface = case[(j,i)][0]
            rect = surface.get_rect()
            rect.y = int(810/15) *i * scale
            rect.x  = int(810/15) * j * scale - decalage

            if pygame.Rect.colliderect(rect,curseur):
                if not case[(j,i)]:
                    surface.fill('red')
                    surface.set_alpha(100)
                if pygame.mouse.get_pressed()[0] and cooldown > COOLDOWN and select:
                    cooldown = 0
                    case[(j,i)] = image[select]
                    ligne[i][j] = image[select][1]
                
                if case[(j,i)] and pygame.mouse.get_pressed()[2] and cooldown > COOLDOWN:
                    case[(j,i)] = None
                    ligne[i][j] = ' '
            
                screen.blit(surface,rect)
                print((j,i))

            if case[(j,i)]:
                screen.blit(surface,rect)
            pygame.draw.rect(screen,(255,255,255),rect,1)
    
    c = -1
    for i in image:
        c+= 1
        screen.blit(image[i][0],(int(810/15) * c,700))
        if int(810/15) * c < curseur.x < int(810/15) * c + int(810/15) and 700 < curseur.y < 700 + int(810/15):
            if pygame.mouse.get_pressed()[0] and cooldown > COOLDOWN:
                cooldown = 0
                select = i
            pygame.draw.rect(screen,(255,0,0),pygame.Rect(int(810/15) * c,700,int(810/15),int(810/15)),2)
        else:
            pygame.draw.rect(screen,(255,255,255),pygame.Rect(int(810/15) * c,700,int(810/15),int(810/15)),2)
        
    if select != '':
        screen.blit(image[select][0],(1300,700))
    pygame.display.flip()
    
    
    
    
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()