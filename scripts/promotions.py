#! /usr/bin/python

'''
Simulation of promotions in a military
PAPER: Promotions in ongoing hierarchical systems
Author: @griverorz

Started: 21Feb2012
'''

import random
from numpy.random import binomial
import numpy
import itertools
import time
import csv
import matplotlib.pyplot as plt
import math
import copy

""" UTILITIES """
TOP_AGE = 15
TOP_RANK = 4
UNIT_SIZE = 3
R = 500

def toInt(numList):
    # Takes a list and returns it as integer
    if numList != []:
        s = ''.join(map(str, numList))
        return int(s)

def percentile(N, P):
    """
    mpounsett: http://stackoverflow.com/questions/2374640/how-do-i-calculate-percentiles-with-python-numpy
    Find the percentile of a list of values

    @parameter N - A list of values.  N must be sorted.
    @parameter P - A float value from 0.0 to 1.0

    @return - The percentile of the values.
    """
    N.sort()
    n = int(round(P * len(N) + 0.5))
    return N[n-1]
    
def baseconvert(number, todigits, fromdigits = "0123456789"):
    """ Copied from Drew Perttula: http://code.activestate.com/recipes/111286-numeric-base-converter-that-accepts-arbitrary-digi/ """

    """ converts a "number" between two bases of arbitrary digits

    The input number is assumed to be a string of digits from the
    fromdigits string (which is in order of smallest to largest
    digit). The return value is a string of elements from todigits
    (ordered in the same way). The input and output bases are
    determined from the lengths of the digit strings. Negative 
    signs are passed through.
    """
    if str(number)[0]=='-':
        number = str(number)[1:]
        neg = 1
    else:
        neg = 0

    # make an integer out of the number
    x = long(0)
    for digit in str(number):
       x = x*len(fromdigits) + fromdigits.index(digit)
    
    # create the result in base 'len(todigits)'
    res = ""
    while x > 0:
        digit = x % len(todigits)
        res = todigits[digit] + res
        x /= len(todigits)
    if neg:
        res = "-"+res
    if number is 0:
        res = "0"
    return res

""" MAIN CLASSES """

class Soldier(object):
    """ A soldier """

    id_generator = itertools.count(1)
    
    def __init__(self, rank, seniority, age, quality, wquality, ideology, unit, ruler_ideology):
        self.id = next(self.id_generator)
        self.rank = rank
        self.seniority = seniority
        self.age = age
        self.quality = quality
        self.wquality = self.quality
        self.ideology = ideology
        self.unit = unit
        self.ruler_ideology = ruler_ideology

    def __str__(self):
        characteristics = '\nID: '+ str(self.id) + '\nRank: ' + str(self.rank)  + '\nSeniority: ' + str(self.seniority) + \
            '\nAge: ' + str(self.age) + '\nQuality: ' + str(self.quality) + '\nWQuality: ' + str(self.wquality) + \
            '\nIdeology: ' + str(self.ideology) + '\nUnit: ' + str(self.unit) + '\n' 
        return characteristics
        
    # @staticmethod
    # def status():
    #     print('\nTotal army size is ', Soldier.total)
    def report(self):
        return({'id': self.id, 'rank': self.rank, 'age': self.age, 'quality': self.quality, 'wquality': self.wquality, \
                'ideology': self.ideology, 'unit': self.unit, 'seniority': self.seniority})
    
    def pass_time(self):
        self.age += 1
        self.seniority += 1
        if self.age > TOP_AGE:
            self.__kill()
        elif self.rank == 1:
            to_kill = int(numpy.random.binomial(1, float(self.age)/float(TOP_AGE + 1), 1))
            if to_kill is 1:
                self.__kill()

    # @property
    # def utility(self):
    #     happiness = self.rank/self.age - math.fabs(self.ruler_ideology - self.ideology)
    #     return happiness

    # def couprisk(self):
    #     risk = self.utility()
    #     return risk
        
    def promote(self, ranks = 0):
        if ranks == 0 or ranks == 1:
            self.rank += ranks
            # self.__pass_time()
        else:
            print('\nWrong number of steps')

    def __kill(self):
        self.age = 1
        self.rank = 1
        self.quality = random.uniform(0, 1)
        self.ideology = random.uniform(-1, 1)
        self.seniority = 1
        self.id = next(self.id_generator)

    """ Shallow copy """
    def __copy__(self):
        replicate = Soldier(copy.deepcopy(self.rank, self.seniority, self.age, self.quality, self.ideology, self.unit, self.ruler_ideology))
        return replicate


class Ruler(object):
    """ The ruler """
    def __init__(self, ideology):
        self.ideology = ideology

    def __str__(self):
        characteristics = "\nIdeology: " + str(self.ideology)
        return characteristics

def generate_starting(level):
    ll = (TOP_RANK - level) + 1
    out = []
    for i in range(ll):
        out.append(10**i)
    return sum(out)


""" 1 is lowest rank """

def generate_army(N = UNIT_SIZE**TOP_RANK, K = TOP_AGE, U = UNIT_SIZE, ruler_ideology = 0):
    """ Generates army of size N (at the base level) with K levels. Each unit being of size U"""
    army = []
    if N % U is not 0:
        print('Wrong dimensions')
    else:
        fill_rank = 1
        while fill_rank <= TOP_RANK:
            start = generate_starting(fill_rank)
            population_rank = UNIT_SIZE**(TOP_RANK - fill_rank + 1)
            for i in range(population_rank):
                id = baseconvert(i, [str(j) for j in range(U)])
                """ Senior officers tend to be older"""
                # def __init__(self, rank, age, quality, ideology, unit, ruler_ideology):
                age = int(round(numpy.random.beta(fill_rank, (TOP_RANK + 1) - fill_rank, 1) * (TOP_AGE - 1) + 1))
                seniority = random.choice(range(min(age, fill_rank), max(age, fill_rank) + 1)) # Double check
                quality = random.uniform(0, 1)
                captain = Soldier(fill_rank, seniority, age,
                                  quality, quality, random.uniform(-1, 1), start + int(id), ruler_ideology)
                army.append(captain)
            population_rank = population_rank/U
            fill_rank += 1
    return army


""" DECISION RULES """

""" Highest number, highest rank """

def order(x):
    ''' Equivalent to the order() function in R.
    Always returns reverse order'''
    out = numpy.array(x).ravel().argsort()
    return(out.tolist())

# def promote_seniority(army, ruler, to_replace, to_exclude = []):
#     ''' Given army and list of vacants, promote individual with highest experience in the positionl'''
#     vacants = []
#     officers_to_be_replaced = [army[i] for i in to_replace]
#     seniority = [x.seniority for i,x in enumerate(army)]

#     for officer in officers_to_be_replaced:
#         candidates = []
#         ll = 1
#         while len(candidates) is 0 and ll < (TOP_RANK -1):
#             candidates = [i for i,j in enumerate(army) if (j.rank == (officer.rank - 1) and j.age < TOP_AGE) and (i not in (vacants + to_replace + to_exclude))]
#             if ll > 1:
#                 print "Empty pool!"
#             ll += 1

#         restricted_seniority = [j for i,j in enumerate(seniority) if i in candidates]

#         if len(restricted_seniority) > 0:
#             max_seniority = numpy.array(restricted_seniority).max()
#             vacants.append(candidates[restricted_seniority.index(max_seniority)])
#     return(vacants)

def generate_children_codes(unit):
    final_codes = []
    missing_levels = TOP_RANK - len(str(unit).strip())
    for lvl in range(1, missing_levels + 1):
        additional_codes = itertools.repeat(range(1, UNIT_SIZE + 1), lvl)
        codes_to_add = list(itertools.product(*list(additional_codes)))
        pasted_codes_to_add = [reduce(lambda x, y: str(x)+str(y), i) for i in codes_to_add]
        final_codes.append(pasted_codes_to_add)
    children = [int(str(unit)+str(i)) for i in list(itertools.chain(*final_codes))]
    return(children)    

def calculate_wquality(army):
    wquality = []
    for soldier in army:
        wquality_own = soldier.quality * soldier.rank * soldier.seniority
        children = generate_children_codes(soldier.unit)
        wquality_children = [i.quality * i.rank * i.seniority for i in army if i.unit in children]
        wquality_soldier = sum(wquality_children) + wquality_own
        soldier.wquality = wquality_soldier
    return(army)

def promote_random(army, ruler, to_replace, ordered, seniority, to_exclude = []):
    ''' Given army and list of vacants, promote individual at random'''
    vacants = []
    officers_to_be_replaced = [army[i] for i in to_replace]

    for officer in officers_to_be_replaced:
        
        if ordered is True:
            if seniority is True:
                candidates = []
                ll = 0
                rr = 1
                while len(candidates) is 0 and (rr <= (officer.rank - 1) and ll <= 3):
                    qq = [.75, .5, .25, 0]
                    avseniority = percentile([h.seniority for h in army if h.rank is (officer.rank - rr)], qq[ll])
                    candidates = [i for i,j in enumerate(army) if (j.rank == (officer.rank - rr) \
                                                                   and j.age < TOP_AGE \
                                                                   and j.seniority >= float(avseniority)) \
                                                                   and (i not in (vacants + to_replace + to_exclude))]
                    if ll < 3:
                        ll += 1
                    else:
                        print "Empty pool!"
                        rr += 1
                        ll = 0
                    
            else:
                candidates = []
                rr = 1
                while len(candidates) is 0 and rr <= (officer.rank - 1): # second condition is too wide
                    candidates = [i for i,j in enumerate(army) if (j.rank == (officer.rank - rr) \
                                                                   and j.age < TOP_AGE) \
                                                                   and (i not in (vacants + to_replace + to_exclude))]
                    if len(candidates) is 0:
                        print "Empty pool!"
                        rr += 1

        else:
            candidates = [i for i,j in enumerate(army) if (j.rank < officer.rank and j.age < TOP_AGE) and (i not in (vacants + to_replace + to_exclude))]

        vacants.append(random.choice(candidates))
    return(vacants)

# def promote_minrisk(army, ruler, to_replace, ordered, seniority, to_exclude = []):
#     ''' Given army and list of vacants, promote individual that is closest to the ruler'''
#     vacants = []
#     highest_rank = max([i.rank for i in army])
#     # oo = order([army[i].rank for i in to_replace])
#     # oo.reverse()
#     # to_replace = [to_replace[i] for i in oo]
#     officers_to_be_replaced = [army[i] for i in to_replace]
#     distances = [math.fabs(x.ideology - ruler.ideology) for i,x in enumerate(army)]
#     for officer in officers_to_be_replaced:

#         if ordered is True:
#             if seniority is True:
#                 candidates = []
#                 ll = 0
#                 rr = 1
#                 while len(candidates) is 0 and (rr <= (officer.rank - 1) and ll <= 3):
#                     qq = [.75, .5, .25, 0]
#                     avseniority = percentile([h.seniority for h in army if h.rank is (officer.rank - rr)], qq[ll])
#                     candidates = [i for i,j in enumerate(army) if (j.rank == (officer.rank - rr) \
#                                                                    and j.age < TOP_AGE \
#                                                                    and j.seniority >= float(avseniority)) \
#                                                                    and (i not in (vacants + to_replace + to_exclude))]
#                     # print(str(ll)+"\n"+"officer: "+str(officer.id)+"\n"+"to_replace: "+str(to_replace)+"\n"+"to_exclude: "+str(to_exclude)+"\n"+"vacants: "+str(vacants)+"\n")
#                     if ll < 3:
#                         ll += 1
#                     else:
#                         print "Empty pool!"
#                         rr += 1
#                         ll = 0
                    
#             else:
#                 candidates = []
#                 rr = 1
#                 while len(candidates) is 0 and rr <= (officer.rank - 1): # second condition is too wide
#                     candidates = [i for i,j in enumerate(army) if (j.rank == (officer.rank - rr) \
#                                                                    and j.age < TOP_AGE) \
#                                                                    and (i not in (vacants + to_replace + to_exclude))]
#                     if len(candidates) is 0:
#                         print "Empty pool!"
#                         rr += 1


#         else:
#             candidates = [i for i,j in enumerate(army) if (j.rank < officer.rank and j.age < TOP_AGE) and (i not in (vacants + to_replace + to_exclude))]

#         restricted_distances = [j for i,j in enumerate(distances) if i in candidates]

#         if len(restricted_distances) > 0:
#             restricted_distances = numpy.array(restricted_distances)
#             min_distance = restricted_distances.min()
#             vacants.append((distances == min_distance).nonzero()[0][0]) # this indexing is odd, isn't it?
#     return(vacants)

def promote_closest(army, ruler, to_replace, ordered, seniority, to_exclude = []):
    ''' Given army and list of vacants, promote individual that is closest to the ruler'''
    vacants = []
    highest_rank = max([i.rank for i in army])
    # oo = order([army[i].rank for i in to_replace])
    # oo.reverse()
    # to_replace = [to_replace[i] for i in oo]
    officers_to_be_replaced = [army[i] for i in to_replace]
    distances = [math.fabs(x.ideology - ruler.ideology) for i,x in enumerate(army)]
    for officer in officers_to_be_replaced:

        if ordered is True:
            if seniority is True:
                candidates = []
                ll = 0
                rr = 1
                while len(candidates) is 0 and (rr <= (officer.rank - 1) and ll <= 3):
                    qq = [.75, .5, .25, 0]
                    avseniority = percentile([h.seniority for h in army if h.rank is (officer.rank - rr)], qq[ll])
                    candidates = [i for i,j in enumerate(army) if (j.rank == (officer.rank - rr) \
                                                                   and j.age < TOP_AGE \
                                                                   and j.seniority >= float(avseniority)) \
                                                                   and (i not in (vacants + to_replace + to_exclude))]
                    # print(str(ll)+"\n"+"officer: "+str(officer.id)+"\n"+"to_replace: "+str(to_replace)+"\n"+"to_exclude: "+str(to_exclude)+"\n"+"vacants: "+str(vacants)+"\n")
                    if ll < 3:
                        ll += 1
                    else:
                        print "Empty pool!"
                        rr += 1
                        ll = 0
                    
            else:
                candidates = []
                rr = 1
                while len(candidates) is 0 and rr <= (officer.rank - 1): # second condition is too wide
                    candidates = [i for i,j in enumerate(army) if (j.rank == (officer.rank - rr) \
                                                                   and j.age < TOP_AGE) \
                                                                   and (i not in (vacants + to_replace + to_exclude))]
                    if len(candidates) is 0:
                        print "Empty pool!"
                        rr += 1


        else:
            candidates = [i for i,j in enumerate(army) if (j.rank < officer.rank and j.age < TOP_AGE) and (i not in (vacants + to_replace + to_exclude))]

        restricted_distances = [j for i,j in enumerate(distances) if i in candidates]

        if len(restricted_distances) > 0:
            restricted_distances = numpy.array(restricted_distances)
            min_distance = restricted_distances.min()
            vacants.append((distances == min_distance).nonzero()[0][0]) # this indexing is odd, isn't it?
    return(vacants)


def promote_ablest(army, ruler, to_replace, ordered, seniority, to_exclude = []):
    ''' Given army and list of vacants, promote individual that has the highest quality'''
    vacants = []
    highest_rank = max([i.rank for i in army])
    # oo = order([army[i].rank for i in to_replace])
    # oo.reverse()
    # to_replace = [to_replace[i] for i in oo]
    officers_to_be_replaced = [army[i] for i in to_replace]
    qualities = [i.quality for i in army]
    for officer in officers_to_be_replaced:

        if ordered is True:
            if seniority is True:
                candidates = []
                ll = 0
                rr = 1
                while len(candidates) is 0 and (rr <= (officer.rank - 1) and ll <= 3):
                    qq = [.75, .5, .25, 0]
                    avseniority = percentile([h.seniority for h in army if h.rank is (officer.rank - rr)], qq[ll])
                    candidates = [i for i,j in enumerate(army) if (j.rank == (officer.rank - rr) \
                                                                   and j.age < TOP_AGE \
                                                                   and j.seniority >= float(avseniority)) \
                                                                   and (i not in (vacants + to_replace + to_exclude))]
                    if ll < 3:
                        ll += 1
                    else:
                        print "Empty pool!"
                        rr += 1
                        ll = 0
                    
            else:
                candidates = []
                rr = 1
                while len(candidates) is 0 and rr <= (officer.rank - 1): # second condition is too wide
                    candidates = [i for i,j in enumerate(army) if (j.rank == (officer.rank - rr) and j.age < TOP_AGE) and (i not in (vacants + to_replace + to_exclude))]
                    if rr > 1:
                        print "Empty pool!"
                        rr += 1

        else:
            candidates = [i for i,j in enumerate(army) if (j.rank < officer.rank \
                                                           and j.age < TOP_AGE) \
                                                           and (i not in (vacants + to_replace + to_exclude))]

        restricted_qualities = [j for i,j in enumerate(qualities) if i in candidates]

        if len(restricted_qualities) > 0:
            restricted_qualities = numpy.array(restricted_qualities)
            max_quality = restricted_qualities.max()
            vacants.append((qualities == max_quality).nonzero()[0][0]) # this indexing is odd, isn't it?
    return(vacants)


def promote(army, ruler, method, ordered, seniority):
    ''' Apply promotion rule recursively. '''
    # is_dead = []
    to_replace = [i for i,x in enumerate(army) if x.age >= TOP_AGE and x.rank is not 1]
    # soldiers to die
    # for i in range(len(army)):
    #     if army[i].rank is not 1:
    #         to_kill = int(numpy.random.binomial(1, float(army[i].age)/float(army[i].rank)/TOP_AGE/TOP_RANK, 1))
    #         if to_kill is 1:
    #             is_dead.append(i)
    # to_replace = list(set(to_replace + is_dead))

    oo = order([army[i].rank for i in to_replace])
    oo.reverse()
    to_replace = [to_replace[i] for i in oo]

    army_full = False    
    if len(to_replace) is 0:
        army_full = True
        
    acc_to_promote = []
    new_ranks = []
    new_units = []
    
    """ The army is full when the only vacants are in the base rank.
     The loop accumulates all the changes before applying them in order to avoid double-promotions """
    
    while army_full is False:
        if method is 'closest':
            to_promote = promote_closest(army, ruler, to_replace, ordered, seniority, acc_to_promote)

        if method is 'ablest':
            to_promote = promote_ablest(army, ruler, to_replace, ordered, seniority, acc_to_promote)

        if method is 'random':
            to_promote = promote_random(army, ruler, to_replace, ordered, seniority, acc_to_promote)
            
        to_adjust = [i for i in to_promote if army[i].rank is not 1]
        acc_to_promote.extend(to_promote)
        ranks_to_replace = [army[i].rank for i in to_replace]
        units_to_replace = [army[i].unit for i in to_replace]

        new_ranks.extend(ranks_to_replace)
        new_units.extend(units_to_replace)
        
        to_replace = to_adjust
        army_full = len(to_replace) is 0
    
    if len(acc_to_promote) > 0:
        """ Applies promotions system """
        p = 0
        for i in range(len(acc_to_promote)):
            army[acc_to_promote[i]].rank = new_ranks[p]
            army[acc_to_promote[i]].unit = new_units[p]
            army[acc_to_promote[i]].seniority = 0
            p += 1

    for man in army:
        man.pass_time()

    # print numpy.histogram([i.rank for i in army])
    # print "\nSeniority: "+str(army[0].seniority)+"\nAge: "+str(army[0].age)+"\nRank: "+str(army[0].rank)
    return(army)


def quality_army(army):
    """ Calculates average quality of the army, weighted by rank """
    N = len(army)
    maxE = sum([i.rank for i in army])/N
    E = sum([i.quality*i.rank for i in army])/N
    return(E/maxE)

def generate_all_codes_ranks(rank):
    codes = []
    rank_size = UNIT_SIZE**(TOP_RANK - rank + 1)
    start = generate_starting(rank)
    for p in range(rank_size):
        id = baseconvert(p, [str(j) for j in range(UNIT_SIZE)])
        codes.append(start + int(id))
    return(codes)

def locate_missing_codes(army):
    missing_code = []
    for rank in range(1, TOP_RANK + 1):
        army_codes = [i.unit for i in army if i.rank is rank]
        coderank = generate_all_codes_ranks(rank)
        for code in coderank:
            if code not in army_codes:
                missing_code.append(code)
    return(missing_code)

def locate_wrong_units(army):
    wrong = []
    rankunit = [(i.rank, i.unit) for i in army]
    for uu in range(len(rankunit)):
        expected = len(str(generate_starting(rankunit[uu][0])).strip())
        actual = len(str(rankunit[uu][1]).strip())
        if expected is not actual:
            wrong.append(uu)
    return(wrong)

def reassign_units(army):
    # no need to verify that rank of the new unit matches unit number (if the function works well, it should complete only rank == 1)
    missings = locate_missing_codes(army)
    wrongs = locate_wrong_units(army)
    for p in range(len(missings)):
        # if army[wrongs[p]].rank 
        army[wrongs[p]].unit = missings[p]
    return(army)

# def reassign_units(army):
#     """ Reallocates units in the army """
#     U = UNIT_SIZE
#     r = 1
#     while r <= TOP_RANK:
#         p = 0
#         start = generate_starting(r)
#         for i in range(len(army)):
#             if army[i].rank is r:
#                 id = baseconvert(p, [str(j) for j in range(U)])
#                 army[i].unit = start + int(id)
#                 p += 1
#         r += 1
#     return(army)

def simulation_to_csv(sim, file, method, ordered, seniority):
    """ Writes a simulation file to a csv """
    myfile = open(file, 'wb')
    mywriter = csv.writer(myfile)
    fieldnames = ['it', 'id', 'age', 'rank', 'order', 'unit', 'quality',
                  'wquality', 'ideology', 'method', 'ordered', 'seniority']
    mywriter.writerow(fieldnames)
    R = len(sim)
    for i in range(1, R):
        iteration = [j.report() for j in sim[i]]
        for k in range(len(iteration)):
            current_row = [i, iteration[k]['id'], iteration[k]['age'], iteration[k]['rank'], iteration[k]['seniority'], iteration[k]['unit'],
                           iteration[k]['quality'], iteration[k]['wquality'], iteration[k]['ideology'], method, ordered, seniority]
            mywriter.writerow(current_row)
    myfile.close()
    print 'File successfully written to '+str(file)


''' DYNAMICS '''
leonidas = Ruler(random.uniform(-1, 1))
sparta = generate_army(ruler_ideology = leonidas.ideology)

def simulate(army, ruler, R, method, ordered, seniority):
    simarmy = copy.deepcopy(army)
    it = 1
    outcome = dict.fromkeys(range(1, R + 1))
    outcome[it] = copy.deepcopy(simarmy)
    it += 1
    
    while it <= R:
        print 'Iteration '+str(it)
        simarmy = promote(simarmy, ruler, method, ordered, seniority)
        simarmy = reassign_units(simarmy)
        simarmy = calculate_wquality(simarmy)
        outcome[it] = copy.deepcopy(simarmy)
        it += 1
    return outcome

for meth in ['random', 'closest', 'ablest']:
    for ord in [False, True]:
        for sen in [False, True]:
            Result = simulate(sparta, leonidas, R, method = meth, ordered = ord, seniority = sen)
            simulation_to_csv(Result, '/Users/gonzalorivero/Dropbox/tese/promotions/data/sim_'+meth+'_'+str(sen)+'_'+str(ord)+'.csv', meth, ord, sen)

myfile = open("/Users/gonzalorivero/Dropbox/tese/promotions/data/ruler.csv", 'w')
mywriter = csv.writer(myfile)
fieldnames = [leonidas.ideology]
mywriter.writerow(fieldnames)
myfile.close()
