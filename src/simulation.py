#! /usr/bin/python

'''
Simulation of promotions in a military
PAPER: Promotions in ongoing hierarchical systems
Author: @griverorz

Started: 21Feb2012
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

## auxiliary files
from main_classes import Soldier, Army, Ruler

def simulate(army, ruler, R, method, ordered, byunit):
    full_sim = dict.fromkeys(range(R))
    full_sim[0] = deepcopy(army)

    it = 1    
    while it < R:
        if it % 10 is 0:
            print "Iteration {}".format(it)
        army.run_promotion(ordered, byunit)
        army.risk()
        full_sim[it] = deepcopy(army)
        it += 1
    return full_sim

# write results into csv
def simulation_to_csv(ruler, simulation, method, ordered, byunit, filename):
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
                           iteration['id'],
                           iteration['age'],
                           iteration['rank'],
                           iteration['seniority'],
                           iteration['unit'],
                           iteration['quality'],
                           iteration['ideology'],
                           simulation[i].uquality[j],
                           ff0,
                           ff1,
                           method,
                           ordered,
                           byunit,
                           ruler.ideology]
            myfile.writerow(current_row)

    print 'File successfully written!'

def newtable():
    conn = psycopg2.connect(database="promotions")
    cur = conn.cursor()
    
    cur.execute(
        """
        DROP TABLE IF EXISTS "simp";
        CREATE TABLE "simp" (
        ITERATION integer,
        ID integer,
        AGE integer,
        RANK integer,
        SENIORITY integer,
        UNIT integer,
        QUALITY double precision,
        IDEOLOGY double precision,
        UQUALITY double precision,
        WHICH_FACTION integer,
        FORCE_FACTION double precision,
        METHOD varchar,
        CONSTRAINTS varchar,
        FROM_WITHIN varchar,
        RULER_IDEOLOGY double precision);
        """
    )
    cur.close()
    conn.close()


if __name__ == "__main__":
    newtable()
    baseloc = '/Users/gonzalorivero/Documents/wip/promotions/dta/'
    R = 300
    leonidas = Ruler(0.5, (0, 1, 0))
    original_sparta = Army(3, 3, 15, leonidas)
    original_sparta.fill()
    for mm in ['ideology']:
        for oo in [True, False]:
            for uu in [True, False]:
                sparta = deepcopy(original_sparta)
                print "Method {}, Ordered {}, Internal {}".format(mm, oo, uu)
                simp = simulate(sparta, leonidas, R, mm, oo, uu)
                fname = baseloc+str(mm)+'_'+str(oo)+'_'+str(uu)+'.txt' 
                simulation_to_csv(leonidas, simp, mm, oo, uu, fname)
                
                conn = psycopg2.connect("dbname=promotions")
                cur = conn.cursor()
                cur.execute('COPY "simp" FROM %s CSV;', [str(fname)])
                conn.commit()
                cur.close()
                conn.close()
