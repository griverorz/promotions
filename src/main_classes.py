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
                '\nUnit: ' + str(self.unit) +             \
                '\nAlive: ' + str(self.alive)
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

    def is_candidate(self, openrank, topage, ordered, byunit = False, slack = 1):

        def _possible_superiors(code):
            out = []
            while len(str(code)) > 1:
                code = code/10
                out.append(code)
            return out

        is_sub = True
        if byunit:
            is_sub = openrank in _possible_superiors(self.unit)

        def _candidate(openrank, topage, ordered, slack):
            isc = False
            condalive = self.age < topage and self.alive
            if ordered is False:
                if self.rank < openrank and condalive:
                    isc = True
            elif ordered is True:
                if self.rank == (openrank - slack) and condalive: 
                    isc = True
            return isc

        isc = _candidate(openrank, topage, ordered, slack) and is_sub
        return isc

    def kill(self):
        self.alive = False

    def reuse(self):
        self.age = 1 + int(round(np.random.gamma(1, 2, 1)))
        self.rank = 1
        self.quality = random.uniform(0, 1)
        self.ideology = random.uniform(-1, 1)
        self.seniority = 1
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
    """ An ordered collection of soldiers """
    def __init__(self, unit_size, top_rank, top_age, id_ruler = 0):
        self.unit_size = unit_size
        self.top_rank = top_rank
        self.top_age = top_age
        self.units = generate_army_codes(self.top_rank, self.unit_size)
        self.data = dict.fromkeys(self.units)
        self.id_ruler = id_ruler
        self.data["Ruler"] = self.id_ruler

    def fill(self):
        for unit in self.units:
            rr = self.unit_to_rank(unit)
            refbase = (self.top_rank + 1) - rr
            refscale = self.top_age - 1
            aa = int(round(np.random.beta(rr, refbase, 1) * refscale + 1))
            ss = random.choice(range(min(aa, rr), max(aa, rr) + 1))
            qq = random.uniform(0, 1)
            ii = random.uniform(-1, 1)
            self.data[unit] = Soldier(rr, ss, aa, qq, ii, unit)
        self.data['Ruler'] = Ruler(self.id_ruler)

    def __str__(self):
        chars = "Soldiers: " + str(len(self.data)) + \
                "\nUnit size: " + str(self.unit_size) + \
                "\nTop rank: " + str(self.top_rank)
        return chars

    def __getitem__(self, key):
        return self.data[key]

    def unit_to_rank(self, unit):
        return self.top_rank - len(str(unit)) + 1

    def get_rank(self, rank):
        rank = filter(lambda x: self.top_rank - len(str(x)) + 1 == rank, self.units)
        return rank

    def get_unit(self, soldier):
        for unit, who in self.data.iteritems():
            if who == soldier:
               return(unit)

    def find_subordinates(self, unit):
        subs_list = [unit]
        if len(str(unit)) >= self.top_rank:
            return subs_list
        else:
            children = [int(str(unit) + str((i % self.unit_size) + 1)) 
                        for i in range(self.unit_size)]
            for i in children:
                subs = self.find_subordinates(i)
                subs_list.append(subs)
        return subs_list

    def get_subordinates(self, unit):
        subs = self.find_subordinates(unit)
        fsubs = flatten(subs)
        fsubs.pop(0)
        return fsubs

    def get_superior(self, unit):
        if len(str(unit)) is 1:
            return 'Ruler'
        else:
            return unit/10
    
    def up_for_retirement(self):
        retirees = []
        for i in self.units:
            if self.data[i].will_retire(self.top_age) and self.unit_to_rank(i) is not 1:
                retirees.append(i)
        return retirees
    
    def up_for_promotion(self, openpos, ordered, byunit, slack):
        pool =[]
        openrank = self.unit_to_rank(openpos)
        for i in self.units:
            if self[i] and self[i].is_candidate(openrank, self.top_age, 
                                    ordered, byunit, slack):
                pool.append(i)
        return pool

    def picker(self, openpos, listpool, method):

        if method is 'seniority':
            refval = max([self.data[i].seniority for i in listpool])
            idx = [i for i in listpool if self.data[i].seniority is refval][0]

        if method is 'quality':
            refval = max([self.data[i].quality for i in listpool])
            idx = [i for i in listpool if self.data[i].quality is refval][0]

        if method is 'ideology':
            superior = self.get_superior(openpos)
            if superior is 'Ruler':
                s_ideology = self.data['Ruler']
            else:
                s_ideology = self.data[superior].ideology
            diff_ideo = [(self.data[i].seniority - s_ideology) for i in listpool]
            refval = min(diff_ideo)
            idx = [i for i in listpool if diff_ideo is refval][0]

        if method is 'random':
            idx = random.choice(listpool)

        return idx

    def promote(self, openpos, method, ordered, byunit):
        unavail = []

        openpos = filter(lambda x: self.unit_to_rank(x) is not 1, openpos)

        while openpos:
            toreplace = openpos[0]
            
            pool = self.up_for_promotion(toreplace, ordered, byunit, 1)
            pool = list(set(pool).difference(set(unavail)))
            idx = self.picker(toreplace, pool, method)

            unavail.append(self.data[idx])

            self.data[toreplace] = deepcopy(self.data[idx])
            self.data[toreplace].seniority = 0
            self.data[toreplace].rank = self.unit_to_rank(toreplace)
            self.data[toreplace].unit = toreplace

            self.data[idx] = None
            openpos.pop(0)
        
            if self.unit_to_rank(idx) > 1:
                openpos.append(idx)
                openpos = sorted(openpos, key = lambda x: self.unit_to_rank(idx),
                                 reverse = True)                

    def network(self, distance = 1/5.):
        tr = self.unit_size
        nw = np.zeros((tr, tr), int)
        gg = self.get_rank(self.top_rank)
        for i in range(len(gg)):
            for j in range(i):
                if i is j:
                    nw[i, j] = 0
                else:
                    if self.data[gg[i]].ideology - self.data[gg[j]].ideology < distance:
                        nw[i, j], nw[j, i] = 1, 1
                    else:
                        nw[i, j], nw[j, i] = 0, 0
        return Graph.Adjacency(nw.tolist()).as_undirected()

    def pass_time(self):
        for i in self.units:
            if self.data[i]:
                Soldier.pass_time(self.data[i], self.top_age)

    def recruit_soldiers(self):
        dead_soldiers = []
        dead_soldiers = filter(lambda x: self.data[x] is None, self.get_rank(1))

        for mia in dead_soldiers:
            rr = 1
            refbase = (self.top_rank + 1) - rr
            refscale = self.top_age - 1
            aa = int(round(np.random.beta(rr, refbase, 1) * refscale + 1))
            ss = 0
            qq = random.uniform(0, 1)
            ii = random.uniform(-1, 1)
            self.data[mia] = Soldier(rr, ss, aa, qq, ii, mia)        
            
    def run_promotion(self, method, ordered, byunit):
        openpos = self.up_for_retirement()
        self.promote(openpos, method, ordered, byunit)
        self.pass_time()
        self.recruit_soldiers()

    def test(self):
        ftest = True
        # No empy position
        novacancies = any(i is not None for i in self.data.values())
        # Position in agreement with rank
        consistent = [self.data[i].rank is self.unit_to_rank(i) for i in self.units]
        # Units in agreement
        check_units = [self.data[i].unit is i for i in self.units]
        # No duplicates
        nodupes = len(set(self.data.values())) is len(self.data.keys())
        if not novacancies or not consistent or not check_units or not nodupes:
            ftest = False
        return ftest
