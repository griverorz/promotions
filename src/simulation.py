#! /usr/bin/python

'''
Simulation of promotions in a military
Author: @griverorz
'''

import pdb
import random
import numpy as np
import itertools
import time
import csv
import math
import psycopg2
from copy import deepcopy
import igraph 
import matplotlib.pyplot as plt

## auxiliary files
from classdef import Soldier, Army, Ruler

def external_risk(army):
    extval = np.mean([army.pquality[i] for i in army.get_rank(army.top_rank)])
    return 1 - extval        

def adapt(pp, varrisk, olddir):
    '''
    ruler self-explanatory
    drisk is a measure of risk differential associated with the current army
    d0 is the initial direction
    '''
    # pp = army["Ruler"].parameters.values()
    step = abs(varrisk)
    # creates random movement
    rdir = np.random.uniform(-1, 1, len(pp))
    rdir = map(lambda x: x*step, rdir/np.linalg.norm(rdir))
    if varrisk < 0:
        rdir = olddir
    nvector = [pp[i] + rdir[i] for i in range(len(pp))]
    return nvector, rdir

def f(x, y):
    return x**2 + y**2

oldpp = (2,-2)
olddir = (-1, 1)
evalf = -1
cumpp = []
for i in range(100):
    newpp, newdir = adapt(oldpp, evalf, olddir)
    evalf = (f(*newpp) - f(*oldpp))
    oldpp, oldir = newpp, newdir
    cumpp.append(newpp)

qq = [j[0] for i, j in enumerate(cumpp)]
ii = [j[1] for i, j in enumerate(cumpp)]
plot(qq, ii)

def simulate(army, R, ordered, byunit):
    full_sim = dict.fromkeys(range(R))
    full_sim[0] = deepcopy(army)
    it = 1

    risk_var = -1
    olddir = np.random.uniform(-10, 10, len(army["Ruler"].parameters))
    
    while it < R:
        if it % 10 is 0:
            print "Iteration {}".format(it)

        risk0 = external_risk(army)
        army.run_promotion(ordered, byunit)
    
        newpars, newdir = adapt(army, risk_var, olddir)
        army["Ruler"].update_parameters(newpars)
        
        risk1 = external_risk(army)
        risk_var = risk1 - risk0
        oldpars, olddir = newpars, newdir
        
        full_sim[it] = deepcopy(army)
        it += 1
    return full_sim

# write results into csv
def simulation_to_csv(simulation, ordered, byunit, filename):
    myfile = csv.writer(open(filename, 'wb'))

    R = len(simulation)

    for i in range(1, R):
        for j in simulation[i].units:
            iteration = simulation[i].data[j].report()
            ff = dict.fromkeys(simulation[i].get_rank(simulation[i].top_rank))
            ## Assign none to non-generals factions
            if len(str(j)) is 1:
                ff0, ff1 = simulation[i].factions[j][0], simulation[i].factions[j][1]
            else:
                ff0, ff1 = None, None

            current_row = [i,
                           iteration['age'],
                           iteration['rank'],
                           iteration['seniority'],
                           iteration['unit'],
                           iteration['quality'],
                           iteration['ideology'],
                           simulation[i].uquality[j],
                           ff0,
                           ff1,
                           simulation[i]["Ruler"].parameters["ideology"],
                           simulation[i]["Ruler"].parameters["quality"],
                           # simulation[i]["Ruler"].parameters["seniority"],
                           ordered,
                           byunit,
                           simulation[i]["Ruler"].ideology]
            myfile.writerow(current_row)
    print 'File successfully written!'

# def newtable():
#     conn = psycopg2.connect(database="promotions")
#     cur = conn.cursor()
    
#     cur.execute(
#         """
#         DROP TABLE IF EXISTS "simp";
#         CREATE TABLE "simp" (
#         ITERATION integer,
#         AGE integer,
#         RANK integer,
#         SENIORITY integer,
#         UNIT integer,
#         QUALITY double precision,
#         IDEOLOGY double precision,
#         UQUALITY double precision,
#         WHICH_FACTION integer,
#         FORCE_FACTION double precision,
#         PARAMS_IDEO double precision,
#         PARAMS_QUAL double precision,
#         PARAMS_SENR double precision,
#         CONSTRAINTS varchar,
#         FROM_WITHIN varchar,
#         RULER_IDEOLOGY double precision);
#         """
#     )
#     cur.close()
#     conn.close()


if __name__ == "__main__":
    # newtable()
    baseloc = '/Users/gonzalorivero/Documents/wip/promotions/dta/'
    R = 10000
    params = (0, 0)
    leonidas = Ruler(0.5, params)
    original_sparta = Army(3, 3, 15, leonidas)
    original_sparta.fill()
    original_sparta.get_quality()
    original_sparta.get_factions()
    for oo in [True]:
        for uu in [True]:
            sparta = deepcopy(original_sparta)
            print "Method {}, Ordered {}, Internal {}".format(params, oo, uu)
            simp = simulate(sparta, R, oo, uu)
            fname = baseloc+'sim_'+str(oo)+'_'+str(uu)+'.txt' 
            simulation_to_csv(simp, oo, uu, fname)
            
            conn = psycopg2.connect("dbname=promotions")
            cur = conn.cursor()
            cur.execute('COPY "simp" FROM %s CSV;', [str(fname)])
            conn.commit()
            cur.close()
            conn.close()

 
qq = [simp[i]["Ruler"].parameters["quality"] for i in range(len(simp))]
ii = [simp[i]["Ruler"].parameters["ideology"] for i in range(len(simp))]
plot(qq, ii)
