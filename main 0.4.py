import pygame 
vec = pygame.math.Vector2
class Jeu :
    
    def __init__(self) -> None:
        self.width , self.height = 720,480
        self.screen = pygame.display.set_mode((self.width,self.height))
        self.world = World(self.screen)
        self.clock = pygame.time.Clock()

    def update(self):
        self.screen.fill("black")
        self.world.update()
        pygame.display.flip()
        self.clock.tick(60)

class Entity:
    def __init__(self,screen,blockliste,entite) -> None:
        self.screen = screen
        self.blockliste = blockliste
        self.decalage = 0
        self.entite = entite
        self.joueur = False
        self.pos = vec((10, 360))
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        self.FRIC = -0.12
        self.ACC = 0.5
        if self.entite == 0:
            self.joueur = True
            self.rect = pygame.Rect(50,50,32,64)
            self.image = pygame.transform.scale(pygame.image.load('assets/Mario.png'),(32,64))
            
        else:
            self.rect = pygame.Rect(50,50,32,32)
            self.image = pygame.transform.scale(pygame.image.load('assets/brique.png'),(32,32))
            self.ACC -= 0.25
        
    def draw(self):
        self.rect.x -= self.decalage
        self.screen.blit(self.image,self.rect)

    def collisionDown(self):
        for e in self.blockliste.values():
            for i in e :
                if pygame.Rect.colliderect(self.rect, i) == True:
                    return (True,i)
        return (False,0)

    def jump(self):
        if self.joueur == True:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                if self.collisionDown()[0]:
                    self.vel.y = -15

    def move(self):
        self.acc = vec(0,0.5)
        if self.joueur == True:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT]:
                self.acc.x = self.ACC
            if keys[pygame.K_LEFT]:
                self.acc.x = -self.ACC
        else:
            self.acc.x = self.ACC
            
        self.acc.x += self.vel.x * self.FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        self.rect.midbottom = self.pos

    def inputs(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

    def gravity(self):
        if self.vel.y > 0:
            if self.collisionDown()[0]:
                self.vel.y = 0
                self.pos.y = self.collisionDown()[1].top + 1

    def update(self):
        self.draw()
        self.move()
        self.inputs()
        self.jump()
        self.gravity()

class World:
    def __init__(self,screen) -> None:
        self.width , self.height = 720,480
        self.screen = screen
        self.world = self.get_world()
        self.blockSize = 32
        self.decalage = 0
        self.briqueimg = pygame.transform.scale(pygame.image.load('assets/brique.png'),(32,32))


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

        self.mario = Entity(self.screen,self.blockliste,0)
        self.monstre = Entity(self.screen,self.blockliste,1)

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

        for e in self.liste:
            if e[2] == '#':
                rect = pygame.Rect(e[1]*self.blockSize-self.decalage, e[0]*self.blockSize, self.blockSize, self.blockSize)
                self.screen.blit(self.briqueimg,rect)
            elif e[2] == '?':
                rect = pygame.Rect(e[1]*self.blockSize-self.decalage, e[0]*self.blockSize, self.blockSize, self.blockSize)
                pygame.draw.rect(self.screen, "yellow", rect ,2)   


    def scrolling(self):
        if self.mario.rect.x-self.decalage > self.width*0.75:
            self.decalage += self.mario.vel[0]
            self.mario.decalage += self.mario.vel[0]
            self.monstre.decalage += self.mario.vel[0]

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
        self.monstre.update()
        self.mario.update()
        

   

jeu = Jeu()
while True :
    jeu.update()