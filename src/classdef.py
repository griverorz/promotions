#! /usr/bin/python

'''
Description: Main objects for the simulation
Author: Gonzalo Rivero
Date: 28-Jan-2015 22:03
'''

import itertools
import random
from copy import deepcopy
import psycopg2
import numpy as np
import csv
from helpers import *


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
        self.utility = (self.age - self.rank)**2*self.quality*self.seniority

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

    def kill(self):
        self.alive = False


class Ruler(object):
    """ The ruler """

    def __init__(self, ideology, params, utility):
        for k in params.keys():
            params[k] = truncate(params[k], 0, 10)
        self.ideology = ideology
        self.parameters = params
        self.utility = utility
        self.history = {"T": 0, "risk": [], "direction": []}

    def __str__(self):
        chars = "Ideology: {}, \nParameters: {}".format(
            self.ideology,
            self.parameters.values())
        return chars

    def update(self, newparams):
        self.parameters = newparams

    def adapt(self):
        """ Do not adapt """
        self.update(self.parameters) 


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
            qq = self.fill_quality()
            ii = self.fill_ideology()
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

    def fill_quality(self):
        return float(np.random.beta(1, 1, 1))

    def fill_ideology(self):
        return 2*float(np.random.beta(3, 3, 1)) - 1

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
                qq = self.fill_quality()
                ii = self.fill_ideology()
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

    def pass_time(self):
        for i in self.units:
            if self.data[i]:
                Soldier.pass_time(self.data[i], self.top_age)

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
            qq = self.fill_quality()
            ii = self.fill_ideology()
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
        self.pass_time()
        self.recruit_soldiers()
        self.get_quality()


class Simulation(object):
    def __init__(self):
        pass

    def populate(self, army, filename, args):
        self.army = army
        self.R = args["R"]
        self.ordered = args["ordered"]
        self.fixed = args["fixed"]
        self.history = dict.fromkeys(range(self.R))
        self.history[0] = deepcopy(self.army)
        self.filename = filename

    def run(self):
        it = 1
        risk_var = 0

        while it < self.R:
            if it % 500 is 0:
                print "Iteration {}".format(it)

            risk0 = self.army.risk()

            self.army.run_promotion(self.ordered)
            self.army["Ruler"].adapt(risk_var, fix=self.fixed)

            risk_var = float(self.army.risk() - risk0)

            self.history[it] = deepcopy(self.army)
            it += 1

    def to_csv(self, replication):
        myfile = csv.writer(open(self.filename, 'wb'))

        R = self.R

        for i in range(1, R):
            sim = self.history[i]
            risk = sim.risk()
            for j in sim.units:
                iteration = sim.data[j].report()

                current_row = [replication,
                               i,
                               iteration['age'],
                               iteration['rank'],
                               iteration['seniority'],
                               "".join(str(x) for x in iteration['unit']),
                               iteration['quality'],
                               iteration['ideology'],
                               sim.uquality[j],
                               sim["Ruler"].parameters["ideology"],
                               sim["Ruler"].parameters["quality"],
                               sim["Ruler"].parameters["seniority"],
                               sim["Ruler"].utility["internal"],
                               sim["Ruler"].utility["external"],
                               risk,
                               self.ordered,
                               sim["Ruler"].ideology]
                myfile.writerow(current_row)
        print 'File successfully written!'


    def newtable(self, database):
        conn = psycopg2.connect(database=database)
        cur = conn.cursor()

        cur.execute(
            """
            DROP TABLE IF EXISTS "simp";
            CREATE TABLE "simp" (
            REPLICATION varchar,
            ITERATION integer,
            AGE integer,
            RANK integer,
            SENIORITY integer,
            UNIT varchar,
            QUALITY double precision,
            IDEOLOGY double precision,
            UQUALITY double precision,
            WHICH_FACTION integer,
            FORCE_FACTION double precision,
            PARAMS_IDEO double precision,
            PARAMS_QUAL double precision,
            PARAMS_SEN double precision,
            UTILITY_INT double precision,
            UTILITY_EXT double precision,
            RISK double precision,
            CONSTRAINTS varchar,
            RULER_IDEOLOGY double precision);
            """
        )
        conn.commit()
        cur.close()
        conn.close()

    def to_table(self):
        conn = psycopg2.connect(database="promotions")
        cur = conn.cursor()
        cur.execute('COPY "simp" FROM %s CSV;', [str(self.filename)])
        conn.commit()
        cur.close()
        conn.close()
