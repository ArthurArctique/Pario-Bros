import pygame
from pygame.locals import *
screen = pygame.display.set_mode((0, 0),pygame.FULLSCREEN)
tailleecr = screen.get_size()
screen = pygame.display.set_mode((tailleecr[0]*0.75, tailleecr[1]*0.75),RESIZABLE)
fullscreen = False
bluewall = pygame.image.load('assets/karmine.jpg')
imgsize = bluewall.get_size()
print(imgsize[0]*0.1)
bluewall = pygame.transform.scale(bluewall,(imgsize[0]*0.1,imgsize[1]*0.1))
imgsize = bluewall.get_size()
diff = (1,1)
while 1+1 == 2:
    x = screen.get_size()
    centre = screen.get_rect().center
    if fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    
    bluewall2 = pygame.transform.scale(bluewall,(imgsize[0]*diff[0],imgsize[1]*diff[1]))
    screen.fill((0,0,0))
    print(centre)
    screen.blit(bluewall,(centre[0]-(imgsize[0]/2),centre[1]-(imgsize[1]/2)))
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == VIDEORESIZE and not fullscreen:
            diff = (event.dict['size'][0]/x[0],event.dict['size'][1]/x[1])
            if diff[1] != 1 and diff[0] == 1:
                x = (diff[1]*x[0],diff[1]*x[1])
                diff = (diff[1],diff[1])
            elif diff[0] != 1 and diff[1] == 1:
                x = (diff[0]*x[0],diff[0]*x[1])
                diff = (diff[0],diff[0])
            screen = pygame.display.set_mode(x, RESIZABLE)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                if fullscreen:
                    fullscreen = False
                    screen = pygame.display.set_mode((x[0]*0.5, x[1]*0.5))
                else:
                    fullscreen = True
                
