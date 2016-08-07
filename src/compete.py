from numpy.linalg import norm
from collections import Counter


class Compete:
    '''
    Given a population and the two parties, make them compete in ideological
    proximity to the median.

    Individuals in the population vote for the closest candidate.

    The `compete` function returns the index of the winner.
    '''
    def __init__(self, population, army0, army1):
        self.ruler0 = army0["Ruler"].ideology
        self.ruler1 = army1["Ruler"].ideology
        self.population = population

    @staticmethod
    def dist(x, y):
        return norm(x - y)
        
    def compete(self):
        tally = Counter([0 if Compete.dist(i, self.ruler0) < Compete.dist(i, self.ruler1)
                         else 1 for i in self.population])
        return tally.most_common(1)[0][0]
