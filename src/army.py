#! /usr/bin/python

from ruler import Ruler
from soldier import Soldier
from itertools import product
from np.random import beta, dirichlet
from np import mean
from copy import deepcopy
from random import choice

def generate_level_codes(units, depth, unitsize):
    tree = list([0]*units)
    for i in range(units):
        tree[i] = list(product(range(unitsize), repeat=depth))
        tree[i] = [(i, ) + j for j in tree[i]]
        i += 1
    tree = [reduce(lambda x, y: str(x) + str(y), l) for sublist in list(tree) for l in sublist]
    return tree

def generate_army_codes(units, depth, unitsize):
    level = []
    for i in range(depth):
        level.append(generate_level_codes(units, i, unitsize))
    level = [str(l) for sublist in level for l in sublist]
    return level

def all_indices(value, qlist):
    indices = []
    idx = -1
    while True:
        try:
            idx = qlist.index(value, idx+1)
            indices.append(idx)
        except ValueError:
            break
    return indices

class Army(Soldier):
    """ An ordered collection of soldiers with a ruler """
    def __init__(self, number_units, unit_size, top_rank, top_age, ruler):
        self.number_units = number_units
        self.unit_size = unit_size
        self.top_rank = top_rank
        self.top_age = top_age

        self.units = generate_army_codes(self.number_units,
                                         self.top_rank,
                                         self.unit_size)
        self.data = dict.fromkeys(self.units)
        self.data["Ruler"] = ruler

        self.populate()        

    def populate(self):
        """
        Fill positions in the army: Challenge is to fill with seniors 
        being older than juniors
        """
        for unit in self.units:
            rr = self.unit_to_rank(unit)            
            refbase = (self.top_rank + 1) - rr
            refscale = self.top_age - 1
            aa = int(round(beta(rr, refbase, 1) * refscale + 1))
            ss = choice(range(min(aa, rr), max(aa, rr) + 1))
            qq, ii = self.fill_quality_ideology()
            self.data[unit] = Soldier(rr, ss, aa, qq, ii, unit)

    def __getitem__(self, key):
        return self.data[key]

    @staticmethod
    def fill_quality_ideology():
        """ uniform """
        return dirichlet((2, 2), 1).tolist()[0]

    def get_rank(self, rank):
        rank = filter(lambda x: self.top_rank - len(str(x)) + 1 == rank, self.units)
        return rank

    def get_unit(self, soldier):
        for unit, who in self.data.iteritems():
            if who == soldier:
                return(unit)

    def unit_to_rank(self, unit):
        return self.top_rank - len(str(unit)) + 1         
            
    def get_subordinates(self, unit):
        cand = [unit == i[0:len(unit)] for i in self.units]
        subs = [j for i, j in zip(cand, self.units) if i is True and j != unit]
        return subs

    def get_superior(self, unit):
        if len(unit) is 1:
            return 'Ruler'
        else:
            return unit[0:(len(unit)-1)]

    def up_for_retirement(self):
        retirees = []
        for i in self.units:
            if self.data[i].will_retire(self.top_age) and self.unit_to_rank(i) is not 1:
                retirees.append(i)
        return retirees

    def up_for_promotion(self, openpos):
        pool = []
        openrank = self.unit_to_rank(openpos)
        for i in self.units:
            if self[i] and self[i].is_candidate(openrank,
                                                openpos,
                                                self.top_age):
                pool.append(i)
        return pool
    
    def promote(self, openpos):
        unavail = []
        openpos = filter(lambda x: self.unit_to_rank(x) is not 1, openpos)
        openpos = sorted(openpos, key=lambda x: self.unit_to_rank(x), reverse=True)
        
        while openpos:
            toreplace = openpos[0]
            pool = self.up_for_promotion(toreplace)
            pool = list(set(pool).difference(set(unavail)))

            if not pool:
                rr, aa, ss = self.unit_to_rank(toreplace), self.top_age - 1, 0
                qq, ii = self.fill_quality_ideology()
                self.data[toreplace] = Soldier(rr, ss, aa, qq, ii, toreplace)

                openpos.pop(0)
                unavail.append(toreplace)

            else:                        
                superior = self.get_superior(openpos)
                idx = PromotionSystem(self.parameters,
                                      self.data[toreplace],
                                      pool,
                                      self.data[superior]).pick()

                self.data[toreplace] = deepcopy(self.data[idx])
                self.data[toreplace].seniority = 0
                self.data[toreplace].rank = self.unit_to_rank(toreplace)
                self.data[toreplace].unit = toreplace
                self.data[idx] = None

                unavail.append(self.data[idx])
                openpos.pop(0)

                if self.unit_to_rank(idx) > 1:
                    openpos = [idx] + openpos
                    openpos = sorted(openpos, key=lambda x: self.unit_to_rank(idx),
                                     reverse=True)

    def recruit_soldiers(self):
        dead_soldiers = []
        dead_soldiers = filter(lambda x:
                               (self.data[x] is None) or (self.data[x].alive is False),
                               self.get_rank(1))

        for mia in dead_soldiers:
            refbase, refscale, ss = self.top_rank, self.top_age - 1, 1
            aa = int(round(beta(1, refbase, 1) * refscale + 1))
            qq, ii = self.fill_quality_ideology()
            self.data[mia] = Soldier(1, ss, aa, qq, ii, mia)

    def army_pass_time(self):
        for i in self.units:
            if self.data[i]:
                Soldier.update_time(self.data[i], self.top_age)
                
    def run_promotion(self):
        openpos = self.up_for_retirement()
        self.promote(openpos)
        self.army_pass_time()
        self.recruit_soldiers()


class Utility(Army):
    def __init__(self, army):
        self.army = army
        self.quality = self.get_quality()
        self.risk = self.get_risk()
        
    def individual_quality(self, x):
        qq = self.army.data[x].quality*\
             (self.army.data[x].rank/float(self.army.top_rank))*\
             (self.army.data[x].seniority/float(self.army.top_age))
        return qq
    
    def get_quality(self):
        quality = mean([self.individual_quality(i)
                        for i in self.army.get_rank(self.army.top_rank)])
        return quality

    def internal_risk(self):
        intval = mean([self.army.data[i].ideology
                       for i in self.army.get_rank(self.army.top_rank)])
        return abs(self.army.data['Ruler'].ideology - intval)

    def external_risk(self):
        extval = mean([self.individual_quality(i)
                       for i in self.army.get_rank(self.army.top_rank)])
        return 1.0 - extval

    def get_risk(self):
        uu = self.army.data["Ruler"].utility
        urisk = uu["external"]*self.external_risk() + uu["internal"]*self.internal_risk()
        return urisk

class TestArmy(Army):
    def __init__(self, army):
        self.army = army
        self.data = army.data
        self.units = army.units
    
    def novacancies(self):
        # No empty position
        return(any(i is not None for i in self.data.values()))

    def rconsistent(self):
        return(all([self.data[i].rank is self.army.unit_to_rank(i) for i in self.units]))
        
    def allalive(self):
        return(all([self.data[i].alive for i in self.units]))

    def uconsistent(self):
        return(all([self.data[i].unit is i for i in self.units]))

    def nodupes(self):
        return(len(set(self.data.values())) == len(self.data.keys()))


class PromotionSystem(Army):
    """
    Takes candidates and an open position and a parametrized method to produce the picked
    """
    
    def __init__(self, parameters, slot, candidates, picker):
        self.parameters = parameters
        self.slot = slot
        self.candidates = candidates
        self.picker = picker
        
        
    def pick(self):
        """
        If the unit is to be a general, use the position of the Ruler;
        otherwise, that of the superior
        """
        
        params = self.parameters
        
        ii = [abs(i.ideology - self.picker.ideology) for i in self.candidates]
        ii = map(lambda x: x/max(ii), ii)

        if isinstance(self.picker, Ruler):
            qq = [i.quality for i in self.candidates]
            qq = map(lambda x: x/max(qq), qq)
            ss = [i.seniority for i in self.candidates]
            ss = map(lambda x: x/max(ss), ss)

            score = [params["quality"]*qq[i] +
                     params["seniority"]*ss[i] -
                     params["ideology"]*ii[i]
                     for i in range(len(self.candidates))]
        else:
            score = [-ii[i] for i in range(len(self.candidates))]
        all_idx = all_indices(max(score), score)
        ## random choice only has grip when all_idx > 0
        ## and that only happens when there are ties
        ## If params = (0, 0, 0), then all Soldiers have the same value
        ## and this line promotes at random
        idx = self.candidates[choice(all_idx)]
        return idx.unit


