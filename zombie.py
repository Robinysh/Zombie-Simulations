#!/usr/bin/python
import numpy as np
import math
from scipy import spatial
import matplotlib as mpl
from sys import exit
import pygame
from pygame.locals import *
import sys
import itertools

FPS = 30
SCREENWIDTH  = 1080
SCREENHEIGHT = 720

class Humans:
    def __init__(self):
        self.max_speed = 200000 
        self.view_distance = 200

class Zombies:
    def __init__(self):
        self.max_speed = 100
        self.attack_radius = 20
        self.view_distance = 100

class GameState:
    def __init__(self):
        pygame.init()
        self.FPSCLOCK = pygame.time.Clock()
        self.screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
        pygame.display.set_caption('Zombies')

        self.frame_count = 0
        self.time_step = 1./FPS
        self.humans = Humans()
        self.zombies = Zombies()
        self.humans.center = [[100,100], [400,400]]
        self.zombies.center = [[200,200]]
        self.humans.sigma = [400,400]
        self.zombies.sigma = [10,20]
        self.humans.population = [200,200]
        self.zombies.population = [100]

        self.gameInit()
        self.gameTerminal()

    def gameInit(self):
        self.createHumansPopulation()
        self.createZombiesPopulation()
        terminal = False
        while not terminal:
            self.update()
            terminal = self.checkTermination()
        
    def gameTerminal(self):
        raw_input("Press any key to end.") 
 
    def createHumansPopulation(self):
        self.humans.position = []
        
        for center, sigma, population in zip(self.humans.center, self.humans.sigma, self.humans.population):
            self.humans.position.append(np.random.multivariate_normal(center, sigma*np.eye(2), population))
        self.humans.position = np.vstack(self.humans.position)
        self.humans.velocity = np.zeros(self.humans.position.shape)

    def createZombiesPopulation(self):
        self.zombies.position = []
        for center, sigma, population in zip(self.zombies.center, self.zombies.sigma, self.zombies.population):
            self.zombies.position.append(np.random.multivariate_normal(center, sigma*np.eye(2), population))
        self.zombies.position = np.vstack(self.zombies.position)
        self.zombies.velocity = np.zeros(self.zombies.position.shape)

    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

    def update(self):
        self.handleEvents()
        self.frameStep()
        self.draw()
        pygame.display.update()
        self.FPSCLOCK.tick(FPS)

    def checkTermination(self):
        human_population = len(self.humans.position)   
        return human_population == 0

    def frameStep(self):
        self.constructKDTrees()
        self.updateHumansVelocities()
        self.updateZombiesVelocities()
        self.updateHumansPositions()
        self.updateZombiesPositions()
        self.biteHumans()

    def constructKDTrees(self):
        self.humans.kd_tree = self.createHumansKDTree()
        self.zombies.kd_tree = self.createZombiesKDTree()

    def biteHumans(self):
        bitten_list = self.searchBittenHumans()
        self.turnHumansIntoZombies(bitten_list)
   
    def updateHumansVelocities(self):
        list_of_near_zombies = self.humans.kd_tree.query_ball_tree(self.zombies.kd_tree, self.humans.view_distance)
        for i, (human_position, zombies_indicies) in enumerate(zip(self.humans.position, list_of_near_zombies)):
            if len(zombies_indicies) != 0: #Try removing if, for branch prediction optimization
                position_vectors = self.zombies.position[zombies_indicies] - human_position
                distances = np.sum(position_vectors**2,axis=1) 
                force_vectors = position_vectors/(distances**(3/2.))[:,np.newaxis] #Division applied along axis=0
                self.humans.velocity[i] = np.mean(force_vectors, axis=0)
            else:
                self.humans.velocity[i] = 0
        self.humans.velocity *= -self.humans.max_speed

    def updateZombiesVelocities(self):
        self.zombies.velocity = self.zombies.max_speed*np.random.multivariate_normal([0,0], np.eye(2), len(self.zombies.position))

    def updateHumansPositions(self):
        self.humans.position += self.time_step*self.humans.velocity

    def updateZombiesPositions(self):
        self.zombies.position += self.time_step*self.zombies.velocity

    def createHumansKDTree(self):
        return spatial.KDTree(self.humans.position)

    def createZombiesKDTree(self):
        return spatial.KDTree(self.zombies.position)

    def searchBittenHumans(self):
        list_of_near_zombies = self.humans.kd_tree.query_ball_tree(self.zombies.kd_tree, self.zombies.attack_radius)
        return np.where(map(lambda x: len(x)!=0, list_of_near_zombies))

    def turnHumansIntoZombies(self, bitten_list):
        if len(bitten_list) != 0: 
            self.zombies.position = np.vstack((self.zombies.position, self.humans.position[bitten_list]))  
            self.zombies.velocity = np.vstack((self.zombies.velocity, self.humans.velocity[bitten_list]))  
            self.humans.position = np.delete(self.humans.position, bitten_list, axis=0)        
            self.humans.velocity = np.delete(self.humans.velocity, bitten_list, axis=0)        

    def draw(self):
        pygame.draw.rect(self.screen, (255,255,255), (0, 0, SCREENWIDTH, SCREENWIDTH))
        for position in self.humans.position:
            pygame.draw.rect(self.screen, (255,0,0), (position[0], position[1], self.zombies.attack_radius/2.,self.zombies.attack_radius/2.))
        for position in self.zombies.position:
            pygame.draw.rect(self.screen, (0,0,0), (position[0], position[1], self.zombies.attack_radius/2.,self.zombies.attack_radius/2.))

if __name__ == '__main__':
    game = GameState()
