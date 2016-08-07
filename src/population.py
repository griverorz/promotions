import numpy.random as rand


class Population(object):
    '''
    Define the population of the simulation.

    Currently 99 individuals from Beta(2, 2).
    '''
    def __init__(self):
        self.population = rand.beta(2, 2, 99)
        
        

