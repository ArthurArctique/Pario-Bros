Une information par ligne --> int 

ordre (par ligne):

1:Gauche
2:Droite
3:Saut
4:Attaque

L'entier est l'index dans la liste pygame.key.get_pressed() correspondant à la touche demandé, pour trouver une touche : 

for event in pygame.event.get():
	if event.type == pygame.KEYDOWN:
		print(event.key)

et appuyer manuellement sur une touche du clavier