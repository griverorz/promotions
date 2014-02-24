#! /usr/bin/python

""" MAIN CLASSES """

from helpers import *
import math
import sys
import random
import itertools
import numpy as np
from collections import defaultdict
from copy import deepcopy
from igraph import Graph
import operator

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
        chars = 'Rank: {}, \nSeniority: {}, \nAge: {}, \nQuality: {}, \nIdeology: {}, \nAlive: {}'.format(
            self.rank,
            self.seniority,
            self.age,
            self.quality,
            self.ideology,
            self.alive)
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

    def is_candidate(self, openrank, openunit, topage, ordered,
                     byunit = False, slack = 1):

        def _possible_superiors(code):
            out = []
            while len(str(code)) > 1:
                code = code/10
                out.append(code)
            return out

        is_sub = True
        if byunit:
            is_sub = openunit in _possible_superiors(self.unit)

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


class Ruler(object):
    """ The ruler """
    def __init__(self, ideology, params, utility):
        params = map(lambda x: truncate(x, 0, 10), params)
        self.ideology = ideology
        self.parameters = {"ideology": params[0],
                           "quality": params[1]}
        self.utility = {"internal": utility[0],
                        "external": utility[1]}

    def __str__(self):
        chars = "Ideology: {}, \nParameters: {}".format(
            self.ideology,
            self.parameters.values())
        return chars

    def update_parameters(self, newparams):
        newparams = map(lambda x: truncate(x, 0, 10), newparams)
        self.parameters = {"ideology": newparams[0],
                           "quality": newparams[1]}
                           # "seniority": newparams[2]}

class Army(Soldier):
    """ An ordered collection of soldiers """
    def __init__(self, unit_size, top_rank, top_age, ruler):
        self.unit_size = unit_size
        self.top_rank = top_rank
        self.top_age = top_age
        self.units = generate_army_codes(self.top_rank, self.unit_size)
        self.data = dict.fromkeys(self.units)
        self.data["Ruler"] = ruler
        self.uquality = dict.fromkeys(self.units)
        self.pquality = dict.fromkeys(self.units)
        self.factions = dict.fromkeys(self.get_rank(self.top_rank))
        self.urisk = 0

    def fill(self):
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
        return self.top_rank - len(str(unit)) + 1

    def get_rank(self, rank):
        rank = filter(lambda x: self.top_rank - len(str(x)) + 1 == rank, self.units)
        return rank

    def get_unit(self, soldier):
        for unit, who in self.data.iteritems():
            if who == soldier:
               return(unit)

    def fill_quality(self):
        return float(np.random.beta(2, 4, 1))

    def fill_ideology(self):
        return 2*float(np.random.beta(3, 3, 1)) - 1

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
            if self[i] and self[i].is_candidate(openrank, openpos, self.top_age,
                                                ordered, byunit, slack):
                pool.append(i)
        return pool

    def picker(self, openpos, listpool, byunit):
        superior = self.get_superior(openpos)
        if superior is 'Ruler' or byunit is False:
            s_ideo = self.data['Ruler'].ideology
        else:
            s_ideo = self.data[superior].ideology

        params = self["Ruler"].parameters

        qq = [self.data[i].quality for i in listpool]
        qq = map(lambda x: x/max(qq), qq)
        # ss = [params["seniority"]*self.data[i].seniority for i in listpool]
        ii = [abs(self.data[i].ideology - s_ideo) for i in listpool]
        ii = map(lambda x: x/max(ii), ii)

        score = [params["quality"]*qq[i] - params["ideology"]*ii[i] 
                 for i in range(len(listpool))]
        all_idx = all_indices(max(score), score)
        ## random choice only has grip when all_idx > 0
        ## and that only happens when there are ties
        ## If params = (0, 0, 0), then all Soldiers have the same value
        ## and this line promotes at random
        idx = listpool[random.choice(all_idx)]
        return idx

    def promote(self, openpos, ordered, byunit):
        unavail = []
        openpos = filter(lambda x: self.unit_to_rank(x) is not 1, openpos)
        openpos = sorted(openpos, key = lambda x: self.unit_to_rank(x),
                         reverse = True)

        while openpos:
            toreplace = openpos[0]
            # print "Replacing {}...".format(toreplace)
            slack = 1
            pool = self.up_for_promotion(toreplace, ordered, byunit, 1)

            while not pool and (self.unit_to_rank(toreplace) - slack) > 1:
                slack += 1
                pool = self.up_for_promotion(toreplace, ordered, byunit, slack)
                print "Looking one level deeper"

            pool = list(set(pool).difference(set(unavail)))

            if not pool:
                print "\tCreating {}'s holder".format(toreplace)
                rr = self.unit_to_rank(toreplace)
                aa = self.top_age - 1
                ss = 0
                qq = self.fill_quality()
                ii = self.fill_ideology()
                self.data[toreplace] = Soldier(rr, ss, aa, qq, ii, toreplace)

                openpos.pop(0)
                unavail.append(toreplace)

            else:
                idx = self.picker(toreplace, pool, byunit)
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
                    openpos = sorted(openpos, key = lambda x: self.unit_to_rank(idx),
                                     reverse = True)

    def network(self):
        def _make_link(i, j):
            diff = np.exp(-3.*(abs(i - j)))
            return np.random.binomial(1, diff)
        tr = self.unit_size
        nw = np.zeros((tr, tr), int)
        gg = self.get_rank(self.top_rank)
        for i in range(len(gg)):
            for j in range(i):
                if i is j:
                    nw[i, j] = 0
                else:
                    if _make_link(self[gg[i]].ideology, self[gg[j]].ideology) is 1:
                        nw[i, j], nw[j, i] = 1, 1
                    else:
                        nw[i, j], nw[j, i] = 0, 0
        g = Graph.Adjacency(nw.tolist()).as_undirected()
        g.vs["label"] = range(1, self.unit_size + 1)
        return g

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
        ftest = True
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
        def _iq(x):
            qq = self.data[x].quality * self.data[x].rank * self.data[x].seniority
            return qq
        for i in self.units:
            gq = map(_iq, self.get_subordinates(i))
            subterm = reduce(lambda x, y: x + y, gq, 1)
            self.uquality[i] = subterm * _iq(i)
            maxquality = subterm * _iq(i)/self.data[i].quality
            self.pquality[i] = self.uquality[i]/maxquality

    def get_factions(self):
        nn = self.network()
        nc = nn.clusters()
        tmp_factions = dict.fromkeys([i for i in range(len(nc))])
        for i in tmp_factions.keys():
            idx = [nn.vs["label"][sold] for sold in nc[i]]
            tmp_factions[i] = (idx, sum(self.uquality[uu] for uu in idx))
        ## Format for class
        for i in tmp_factions.keys():
            for j in tmp_factions[i][0]:
                self.factions[j] = (i, tmp_factions[i][1])


    def external_risk(self):
        extval = np.mean([self.pquality[i] for i in self.get_rank(self.top_rank)])
        return 1.0 - extval

    def above_coup(self):
        factions = {k: 0 for k in range(self.top_rank)}
        for i, j in self.factions.values():
            factions[i] += j
        return herfindahl(factions.values())

    def risk(self):
        uu = self["Ruler"].utility
        urisk = uu["internal"]*self.above_coup() + uu["external"]*self.external_risk()
        return urisk

    def run_promotion(self, ordered, byunit):
        openpos = self.up_for_retirement()
        self.promote(openpos, ordered, byunit)
        self.pass_time()
        self.recruit_soldiers()
        self.get_quality()
        self.get_factions()
        self.test()
