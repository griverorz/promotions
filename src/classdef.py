#! /usr/bin/python

'''
Description: Main objects for the simulation
Author: Gonzalo Rivero
Date: 28-Jan-2015 22:03
'''

import itertools
import random
from copy import deepcopy
import numpy as np
from helpers import *
import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import url
from sql_tables import SimData, SimParams
from sqlalchemy import create_engine

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

    def __str__(self):
        chars = 'Rank: {}, \nSeniority: {}, \nAge: {}, \nQuality: {}, \nIdeology: {}'.\
                format(
                    self.rank,
                    self.seniority,
                    self.age,
                    self.quality,
                    self.ideology)
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
        """ Move time one period. If junior, kill with probability p """
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

    def is_candidate(self, openrank, openunit, topage, ordered, slack=1):
        """ Is a candidate for promotion given an open position? """
        def _possible_superiors(code):
            out = []
            while len(code) > 1:
                code = code[0:(len(code)-1)]
                out.append(code)
            return out

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

        is_sub = openunit in _possible_superiors(self.unit)
        isc = _candidate(openrank, topage, ordered, slack) and is_sub
        return isc

    def mutate(self):
        prob = np.random.binomial(1, 0.05, 1)
        if prob is 1:
            if self.ideology < 0.5:
                self.ideology = max(0, self.ideology - .2)
            else:
                self.ideology = min(self.ideology + .2, 1)
        
    def kill(self):
        self.alive = False


class Ruler(object):
    """ The ruler """

    def __init__(self, ideology, params, utility):
        self.ideology = ideology
        self.parameters = params
        self.utility = utility
        self.history = {"T": 0, "risk": [], "direction": []}

    def __str__(self):
        chars = "Ideology: {}, \nParameters: {}".format(
            self.ideology,
            self.parameters.values())
        return chars


    def adapt(self, old_dir, var_risk, fix="seniority"):

        pp = (self.parameters["ideology"],
              self.parameters["quality"],
              self.parameters["seniority"])

        # creates random movement
        if var_risk <= 0:
            rdir = old_dir
        else:
            rdir = np.random.uniform(-1, 1, len(pp))
            step = 0.5
            rdir = map(lambda x: x*step, rdir/np.linalg.norm(rdir))
            rdir = [abs(rdir[i])*-1*np.sign(old_dir[i]) for i in range(len(pp))]

        nvector = [pp[i] + rdir[i] for i in range(len(pp))]
        newvals = {"ideology": nvector[0],
                   "quality": nvector[1],
                   "seniority": nvector[2]}
        if fix:
            if isinstance(fix, basestring):
                newvals[fix] = 0
        else:
            for i in fix:
                newvals[i] = 0
        self.parameters = newvals
        return rdir
        
class Army(Soldier):
    """ An ordered collection of soldiers with a ruler """
    def __init__(self, number_units, unit_size, top_rank, top_age, ruler):
        self.number_units = number_units
        self.unit_size = unit_size
        self.top_rank = top_rank
        self.top_age = top_age
        self.units = generate_army_codes(self.number_units,
                                         self.top_rank, self.unit_size)
        self.data = dict.fromkeys(self.units)
        self.data["Ruler"] = ruler
        self.uquality = dict.fromkeys(self.units)
        self.pquality = dict.fromkeys(self.units)
        self.factions = dict.fromkeys(self.get_rank(self.top_rank))
        self.urisk = 0
        
    def populate(self):
        """
        Fill positions in the army: Challenge is to fill with seniors 
        being older than juniors
        """
        for unit in self.units:
            rr = self.unit_to_rank(unit)
            refbase = (self.top_rank + 1) - rr
            refscale = self.top_age - 1
            aa = int(round(np.random.beta(rr, refbase, 1) * refscale + 1))
            ss = random.choice(range(min(aa, rr), max(aa, rr) + 1))
            qq, ii = self.fill_quality_ideology()
            self.data[unit] = Soldier(rr, ss, aa, qq, ii, unit)

    def __str__(self):
        chars = "Soldiers: {}, \nUnit size: {}, \nTop rank: {}".format(
            len(self.units),
            self.unit_size,
            self.top_rank)
        return chars

    def __getitem__(self, key):
        return self.data[key]

    def unit_to_rank(self, unit):
        return self.top_rank - len(unit) + 1

    def get_rank(self, rank):
        rank = filter(lambda x: self.top_rank - len(x) + 1 == rank, self.units)
        return rank

    def get_unit(self, soldier):
        for unit, who in self.data.iteritems():
            if who == soldier:
                return(unit)

    def fill_quality_ideology(self):
        """ Uniform """
        return np.random.dirichlet((2, 2), 1).tolist()[0]

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

    def up_for_promotion(self, openpos, ordered, slack):
        pool = []
        openrank = self.unit_to_rank(openpos)
        for i in self.units:
            if self[i] and self[i].is_candidate(openrank, openpos,
                                                self.top_age, ordered, slack):
                pool.append(i)
        return pool

    def picker(self, openpos, listpool):
        """
        If the unit is to be a general, use the position of the Ruler;
        otherwise, that of the superior
        """
        superior = self.get_superior(openpos)
        if superior is 'Ruler':
            s_ideo = self.data['Ruler'].ideology
        else:
            s_ideo = self.data[superior].ideology

        params = self["Ruler"].parameters

        ii = [abs(self.data[i].ideology - s_ideo) for i in listpool]
        ii = map(lambda x: x/max(ii), ii)

        if superior is 'Ruler':
            qq = [self.data[i].quality for i in listpool]
            qq = map(lambda x: x/max(qq), qq)
            ss = [self.data[i].seniority for i in listpool]
            ss = map(lambda x: x/max(ss), ss)

            score = [params["quality"]*qq[i] +
                     params["seniority"]*ss[i] -
                     params["ideology"]*ii[i]
                     for i in range(len(listpool))]
        else:
            score = [-ii[i] for i in range(len(listpool))]
        all_idx = all_indices(max(score), score)
        ## random choice only has grip when all_idx > 0
        ## and that only happens when there are ties
        ## If params = (0, 0, 0), then all Soldiers have the same value
        ## and this line promotes at random
        idx = listpool[random.choice(all_idx)]
        return idx

    def promote(self, openpos, ordered):
        unavail = []
        openpos = filter(lambda x: self.unit_to_rank(x) is not 1, openpos)
        openpos = sorted(openpos, key=lambda x: self.unit_to_rank(x), reverse=True)

        while openpos:
            toreplace = openpos[0]
            # print "Replacing {}...".format(toreplace)
            slack = 1
            pool = self.up_for_promotion(toreplace, ordered, 1)

            while not pool and (self.unit_to_rank(toreplace) - slack) > 1:
                slack += 1
                pool = self.up_for_promotion(toreplace, ordered, slack)
                print "Looking one level deeper"

            pool = list(set(pool).difference(set(unavail)))

            if not pool:
                print "\tCreating {} holder".format(toreplace)
                rr = self.unit_to_rank(toreplace)
                aa = self.top_age - 1
                ss = 0
                qq, ii = self.fill_quality_ideology()
                self.data[toreplace] = Soldier(rr, ss, aa, qq, ii, toreplace)

                openpos.pop(0)
                unavail.append(toreplace)

            else:
                idx = self.picker(toreplace, pool)
                # print "\tPromoting {}...".format(idx)
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

    def army_pass_time(self):
        for i in self.units:
            if self.data[i]:
                Soldier.pass_time(self.data[i], self.top_age)
                
    # def mutate(self):
    #     for i in self.units:
    #         if self.data[i]:
    #             Soldier.mutate()

    def recruit_soldiers(self):
        dead_soldiers = []
        dead_soldiers = filter(lambda x:
                               (self.data[x] is None) or (self.data[x].alive is False),
                               self.get_rank(1))

        for mia in dead_soldiers:
            refbase = self.top_rank
            refscale = self.top_age - 1
            aa = int(round(np.random.beta(1, refbase, 1) * refscale + 1))
            ss = 1
            qq, ii = self.fill_quality_ideology()
            self.data[mia] = Soldier(1, ss, aa, qq, ii, mia)

    def test(self):
        """ Check the structure of the military """
        # No empty position
        tests = dict.fromkeys(["novacancies", "allalive",
                               "rconsistent", "uconsistent", "nodupes"])
        tests["novacancies"] = any(i is not None for i in self.data.values())
        # Position in agreement with rank
        tests["rconsistent"] = all([self.data[i].rank is self.unit_to_rank(i)
                                    for i in self.units])
        tests["allalive"] = all([self.data[i].alive for i in self.units])
        # Units in agreement
        tests["uconsistent"] = all([self.data[i].unit is i for i in self.units])
        # No duplicates
        tests["nodupes"] = len(set(self.data.values())) == len(self.data.keys())
        # return tests
        if not all(tests.values()):
            fails = [tests.keys()[i] for i in all_indices(False, tests.values())]
            print "Fails tests: " + ', '.join(fails)

    def get_quality(self):
        def _individual_quality(x):
            qq = self.data[x].quality*self.data[x].rank*self.data[x].seniority
            return qq
        for i in self.units:
            self.uquality[i] = _individual_quality(i)
            self.pquality[i] = self.uquality[i]/ \
                               (self.data[i].rank*self.data[i].seniority)

    def external_risk(self):
        extval = np.mean([self.pquality[i] for i in self.get_rank(self.top_rank)])
        return 1.0 - extval

    def risk(self):
        uu = self["Ruler"].utility
        urisk = uu["external"]*self.external_risk()
        return urisk

    def run_promotion(self, ordered):
        openpos = self.up_for_retirement()
        self.promote(openpos, ordered)
        # self.mutate()
        self.army_pass_time()
        self.recruit_soldiers()
        self.get_quality()



class Simulation(object):
    id_generator = itertools.count(1)
    
    def __init__(self):
        self.id = next(self.id_generator)

    def populate(self, army, args):
        self.army = army
        self.R = args["R"]
        self.ordered = args["ordered"]
        self.fixed = args["fixed"]
        self.history = dict.fromkeys(range(self.R))
        self.history[0] = deepcopy(self.army)

    def run(self):
        it = 1
        var_risk = 0

        while it < self.R:
            if it % 500 is 0:
                print "Iteration {}".format(it)

            if it is 1:
                new_dir = list(np.random.uniform(-1, 1, 3))
                
            risk0 = self.army.risk()

            self.army.run_promotion(self.ordered)
            new_dir = self.army["Ruler"].adapt(new_dir, var_risk, fix="seniority")
            var_risk = float(self.army.risk() - risk0)

            self.history[it] = deepcopy(self.army)
            it += 1

    def parse_simulation(self):
        simparams = {"id": self.id,
                     "params_ideo": self.army["Ruler"].parameters["ideology"],
                     "params_qual": self.army["Ruler"].parameters["quality"],
                     "params_sen": self.army["Ruler"].parameters["seniority"],
                     "utility": self.army["Ruler"].utility["external"],
                     "constraints": self.ordered,
                     "ruler_ideology": self.army["Ruler"].ideology}
        self.simparams = simparams
        
    def parse_history(self): 
        self.parsed_data = []
        R = self.R
        
        for i in range(1, R):
            sim = self.history[i]
            risk = sim.risk()
            for j in sim.units:
                iteration = sim.data[j].report()

                current_row = {"iteration": i,
                               "replication": self.id,
                               "age": iteration['age'],
                               "rank": iteration['rank'],
                               "seniority": iteration['seniority'],
                               "unit": "".join(str(x) for x in iteration['unit']),
                               "quality": iteration['quality'],
                               "ideology": iteration['ideology'],
                               "uquality": sim.uquality[j],
                               "parideology": sim.data["Ruler"].parameters["ideology"],
                               "parseniority": sim.data["Ruler"].parameters["seniority"],
                               "parquality": sim.data["Ruler"].parameters["quality"],
                               "risk": risk}
                                                              
                self.parsed_data.append(current_row)


    def connect_db(self):
        dbdata = json.loads(open("sql_data.json").read())
        engine = create_engine(url.URL(**dbdata))
        DBSession = sessionmaker()
        self.dbsession = DBSession(bind=engine)

    def write_to_table(self):
        self.connect_db()
        """ Write simulation parameters """
        newparams = SimParams(**self.simparams)
        self.dbsession.add(newparams)
        self.dbsession.commit()
        """ Write simulation data """
        newcases = [SimData(**i) for i in self.parsed_data]
        self.dbsession.add_all(newcases) 
        self.dbsession.commit()
        self.dbsession.flush()
        
    def write(self):
        self.parse_simulation()
        self.parse_history()
        self.write_to_table()
