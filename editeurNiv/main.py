import pygame
import csv

csv.Dialect.delimiter = ";"

#screen = pygame.display.set_mode((400,400))

def nouveauNiv(nom,taille):
    with open('csv/a.csv', 'w', newline='',encoding='UTF-8') as csvfile:
        fieldnames = ['first_name', 'last_name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect='unix')

        writer.writeheader()
        writer.writerow({'first_name': 'Baked', 'last_name': 'Beans'})
        writer.writerow({'first_name': 'Lovely', 'last_name': 'Spam'})
        writer.writerow({'first_name': 'Wonderful', 'last_name': 'Spam'})
