import pygame ,numpy

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
        self.rect = pygame.Rect(50,50,32,64)
        self.blockliste = blockliste
        self.decalage = 0
        self.speed = 4
        self.entite = entite
        self.joueur = False
        if self.entite == 0:
            self.joueur = True
            self.pos = vec((10, 360))
            self.rect = pygame.Rect(50,50,32,64)
            self.image = pygame.transform.scale(pygame.image.load('assets/Mario.png'),(32,64))
            
        else:
            self.pos = vec((150,450))
            self.rect = pygame.Rect(50,50,32,64)
            self.image = pygame.transform.scale(pygame.image.load('assets/Luigi.png'),(32,64))
            self.speed = 3
        
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
            self.vel.y = -15

    def updateTuto(self):
        self.speedHori = 0
        onground = self.check_collision(0, 1)
        # check keys
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            self.speedHori = -self.speed
        elif key[pygame.K_RIGHT]:
            self.speedHori = self.speed

        if key[pygame.K_UP] and onground:
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
        for e in self.blockliste.values():
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
                
    
    def recharge(self):
        if self.mario.rect.x < 0 and self.mario.rect.y > 1500 :
            self.mario.pos = vec((200, 0))

    def scrolling(self):
        
        if self.mario.rect.x-self.mario.decalage >= self.width*0.75-self.decalage:     
            self.decalage += self.mario.speedHori
            self.mario.decalage = self.decalage

        if self.mario.rect.x-self.mario.decalage <= self.width*0.25-self.decalage and self.decalage>0:     
            self.decalage += self.mario.speedHori
            self.mario.decalage = self.decalage

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
        self.recharge()
        self.scrolling()
        self.draw_on_screen()
        self.mario.update()
        

   

jeu = Jeu()
while True :
    jeu.update()

