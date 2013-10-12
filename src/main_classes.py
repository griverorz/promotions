#! /usr/bin/python

""" MAIN CLASSES """

import helper_functions
import sys
import random
import itertools
import numpy as np
from collections import defaultdict
from copy import deepcopy
from igraph import Graph

class Soldier(object):
    """ A soldier """

    id_generator = itertools.count(1)
    
    def __init__(self, rank, seniority, age, quality, ideology, unit):
        self.id = next(self.id_generator)
        self.rank = rank
        self.seniority = seniority
        self.age = age
        self.quality = quality
        self.ideology = ideology
        self.unit = unit
        self.alive = True
        self.utility = (age - rank)*quality*seniority

    def __str__(self):
        chars = 'ID: '+ str(self.id) +                    \
                '\nRank: ' +  str(self.rank) +            \
                '\nSeniority: ' + str(self.seniority) +   \
                '\nAge: ' + str(self.age) +               \
                '\nQuality: ' + str(self.quality) +       \
                '\nIdeology: ' + str(self.ideology) +     \
                '\nUnit: ' + str(self.unit)
        return chars
        
    def report(self):
        return({'id': self.id,
                'rank': self.rank,
                'age': self.age,
                'quality': self.quality,
                'ideology': self.ideology,
                'unit': self.unit,
                'seniority': self.seniority})
    
    def pass_time(self, topage):
        self.age += 1
        self.seniority += 1
        if self.age > topage:
            self.kill()
        elif self.rank is 1:
            prob = float(self.age)/float(topage + 1)
            to_kill = int(np.random.binomial(1, prob, 1))
            if to_kill is 1:
                self.kill()
        
    def will_retire(self, topage):
        if self.age == topage:
            return(True)
        else:
            return(False)
    
    def is_candidate(self, ordered, rank_open, topage, slack = 1):
        isc = False
        if ordered is False:
            if self.rank < rank_open and self.age < topage and self.alive:
                isc = True
        elif ordered is True:
            if self.rank == (rank_open - slack) and self.age < topage and self.alive:
                isc = True
        return isc
        
    def promote(self, rank_open = None):
        if rank_open is None:
            self.rank += 1
        else:
            self.rank = rank_open
        self.seniority = 0

    def kill(self):
        self.alive = False

    def reuse(self, unit):
        self.age = 1 + int(round(np.random.gamma(1, 2, 1)))
        self.rank = 1
        self.quality = random.uniform(0, 1)
        self.ideology = random.uniform(-1, 1)
        self.seniority = 1
        self.unit = unit
        self.id = next(self.id_generator)
        self.alive = True


class Ruler(object):
    """ The ruler """
    def __init__(self, ideology):
        self.ideology = ideology

    def __str__(self):
        characteristics = "\nIdeology: " + str(self.ideology)
        return characteristics


class Army(Soldier):
    """ A collection of soldiers """

    def __init__(self, ruler, top_age, unit_size, top_rank):
        """ Generates army of size N (at the base level) with K levels. 
        Each unit being of size U """
        self.N = unit_size**top_rank
        self.top_age = top_age
        self.unit_size = unit_size
        self.top_rank = top_rank
        self.ruler_ideology = ruler.ideology
        if self.N % self.unit_size is not 0:
            print('Wrong dimensions')
        self.soldiers = populate_army(self.top_age, self.top_rank, self.unit_size)

    def __str__(self):
        chars = "Soldiers: " + str(self.N) + \
                "\nTop age: " + str(self.top_age) + \
                "\nUnit size: " + str(self.unit_size) + \
                "\nTop rank: " + str(self.top_rank) 
        return chars
        
    def get_rank(self, rank):
        rank_list = [i for i in self.soldiers if i.rank == rank]
        return(rank_list)

    def rank_dist(self):
        ranks = [i.rank for i in self.soldiers if i.alive]
        rankd = defaultdict(int)
        for ind in ranks:
            rankd[ind] += 1
        return(rankd)

    def up_for_retirement(self):
        avail_list = []
        topage = self.top_age
        for i in self.soldiers:
            avail_list.append(i.will_retire(topage))
        retirees = [val for pos, val in enumerate(self.soldiers) 
                    if avail_list[pos] and val.rank > 1]        
        ## sort them by rank
        retirees = sorted(retirees, key = lambda x: x.rank, reverse = True)
        return(retirees)

    def up_for_promotion(self, constraints, open_rank, slack = 1):
        ### methods
        # random, quality, proximity, seniority
        ### constraints
        # ordered
        known_constraints = {
            ## ordered, seniority
            'ordered': True,
            'none': False
        }
        ordered = known_constraints[constraints]
        pool_list = []
        topage = self.top_age
        for i in self.soldiers:
            pool_list.append(i.is_candidate(ordered, open_rank, topage, slack))
        candidates = [val for pos, val in enumerate(self.soldiers) 
                      if pool_list[pos] is True]
        return(candidates)            

    def lookupid(self, value):
        id_army = [i.id for i in self.soldiers]
        idx = id_army.index(value)
        return idx

    def promote(self, method, constraints, openpos):
        unavail = []
        while len(openpos) > 0:
            open_rank = openpos[0].rank
            pool = deepcopy(self.up_for_promotion(constraints, open_rank, slack = 1))
            pool = list(set(pool).difference(set(unavail)))
            
            while not pool:
                slack = 2
                print("No one is up! Looking in the next rank.")
                pool = self.up_for_promotion(constraints, open_rank, slack)
                slack += 1

            if method is "seniority":
                refval = max([i.seniority for i in pool])
                id_pool = [i.id for i in pool if i.seniority is refval][0]
                idx = self.lookupid(id_pool)
            if method is "quality":
                refval = max([i.quality for i in pool])
                id_pool = [i.id for i in pool if i.quality is refval][0]
                idx = self.lookupid(id_pool)
            if method is "ideology":
                ideologies = [(i.ideology - self.ruler_ideology) for i in pool]
                refval = min(ideologies)
                idx = ideologies.index(refval)
                id_pool = pool[idx].id
                idx = self.lookupid(id_pool)
            if method is "random":
                refval = random.choice([i.id for i in pool])
                ids = [i.id for i in self.soldiers]
                idx = ids.index(refval)

            tmp = deepcopy(self.soldiers[idx])
            self.soldiers[idx].promote(open_rank)
            self.soldiers[idx].unit = openpos[0].unit 
            unavail.append(self.soldiers[idx])

            openpos.pop(0)

            if tmp.rank > 1:
                openpos.append(tmp)
                openpos = sorted(openpos,
                                       key = lambda x: x.rank,
                                       reverse = True)

    def reuse_officers(self):
        dead_soldiers, dead_officers = [], []
        for i in self.soldiers:
            if not i.alive:
                if i.rank is 1:
                    dead_soldiers.append(i)
                else:
                    dead_officers.append(i)

        idle_codes = [i.unit for i in dead_soldiers]
        
        for i, officer in enumerate(dead_officers):
            idx = self.soldiers.index(officer)
            self.soldiers[idx].reuse(idle_codes[i])              

    def reuse_soldiers(self):
        dead_soldiers = []
        for i in self.soldiers:
            if not i.alive:
                if i.rank is 1:
                    dead_soldiers.append(i)

        idle_codes = [i.unit for i in dead_soldiers]
        
        for i, soldier in enumerate(dead_soldiers):
            idx = self.soldiers.index(soldier)
            uu = self.soldiers[idx].unit
            self.soldiers[idx].reuse(uu)

    def recruit(self):
        self.reuse_officers()
        self.reuse_soldiers()
    
    def network(self, distance = 1/5.):
        tr = self.unit_size
        nw = np.zeros((tr, tr), int)
        generals = self.get_rank(self.top_rank)
        for i in range(len(generals)):
            for j in range(i):
                if i is j:
                    nw[i, j] = 0
                else:
                    if generals[i].ideology - generals[j].ideology < distance:
                        nw[i, j], nw[j, i] = 1, 1
                    else:
                        nw[i, j], nw[j, i] = 0, 0
        return Graph.Adjacency(nw.tolist()).as_undirected()

    def pass_time(self):
        for i in self.soldiers:
            Soldier.pass_time(i, self.top_age)
    