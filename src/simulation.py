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
from helpers import herfindahl

def external_risk(army):
    extval = np.mean([army.pquality[i] for i in army.get_rank(army.top_rank)])
    return 1 - extval        

def above_coup(army):
    total_value = [i[1] for i in army.factions.values()]
    return herfindahl(total_value)
    
# def below_coup()

def adapt(army, varrisk, olddir):
    '''
    ruler self-explanatory
    drisk is a measure of risk differential associated with the current army
    d0 is the initial direction
    '''
    pp = army["Ruler"].parameters.values()
    step = abs(varrisk)
    # creates random movement
    rdir = np.random.uniform(-1, 1, len(pp))
    rdir = map(lambda x: x*step, rdir/np.linalg.norm(rdir))
    if varrisk <= 0:
        rdir = olddir
    else:
        rdir = [abs(rdir[i])*-1*np.sign(olddir[i]) for i in range(len(pp))]
    nvector = [pp[i] + rdir[i] for i in range(len(pp))]
    return nvector, rdir

def simulate(army, R, ordered, byunit):
    full_sim = dict.fromkeys(range(R))
    full_sim[0] = deepcopy(army)
    it = 1

    risk_var = -1
    olddir = np.random.uniform(-1, 1, len(army["Ruler"].parameters))
    
    while it < R:
        if it % 50 is 0:
            print "Iteration {}".format(it)

        risk0 = 0.0*above_coup(army) + 1.*external_risk(army)
        army.run_promotion(ordered, byunit)
    
        newpars, newdir = adapt(army, risk_var, olddir)
        army["Ruler"].update_parameters(newpars)
        
        risk1 = 0.*above_coup(army) + 1.*external_risk(army)
        risk_var = float(risk1 - risk0)
        oldpars, olddir = newpars, newdir
        
        full_sim[it] = deepcopy(army)
        it += 1
    return full_sim

# write results into csv
def simulation_to_csv(simulation, ordered, byunit, filename, replication):
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

            current_row = [replication,
                           i,
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

def newtable():
    conn = psycopg2.connect(database="promotions")
    cur = conn.cursor()
    
    cur.execute(
        """
        DROP TABLE IF EXISTS "simp";
        CREATE TABLE "simp" (
        REPLICATION integer,
        ITERATION integer,
        AGE integer,
        RANK integer,
        SENIORITY integer,
        UNIT integer,
        QUALITY double precision,
        IDEOLOGY double precision,
        UQUALITY double precision,
        WHICH_FACTION integer,
        FORCE_FACTION double precision,
        PARAMS_IDEO double precision,
        PARAMS_QUAL double precision,
        CONSTRAINTS varchar,
        FROM_WITHIN varchar,
        RULER_IDEOLOGY double precision);
        """
    )
    cur.close()
    conn.close()


if __name__ == "__main__":
    # newtable()
    baseloc = '/Users/gonzalorivero/Documents/wip/promotions/dta/'
    R = 1000
    S = 10
    for s in range(S):
        params = (0, 0)
        leonidas = Ruler(0.5, params)
        original_sparta = Army(3, 3, 15, leonidas)
        original_sparta.fill()
        original_sparta.get_quality()
        original_sparta.get_factions()

        print "Replication {}".format(s)
        for oo in [True, False]:
            for uu in [True, False]:
                sparta = deepcopy(original_sparta)
                print "Method {}, Ordered {}, Internal {}".format(params, oo, uu)
                simp = simulate(sparta, R, oo, uu)
                fname = baseloc+'sim_'+str(oo)+'_'+str(uu)+'_'+str(s)+'.txt' 
                simulation_to_csv(simp, oo, uu, fname, s)

                conn = psycopg2.connect("dbname=promotions")
                cur = conn.cursor()
                cur.execute('COPY "simp" FROM %s CSV;', [str(fname)])
                conn.commit()
                cur.close()
                conn.close()

# qq = [simp[i]["Ruler"].parameters["quality"] for i in range(len(simp))]
# ii = [simp[i]["Ruler"].parameters["ideology"] for i in range(len(simp))]
# plot(qq, ii)
