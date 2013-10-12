#! /usr/bin/python

'''
Simulation of promotions in a military
PAPER: Promotions in ongoing hierarchical systems
Author: @griverorz

Started: 21Feb2012
'''

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
import helper_functions
import main_classes


def simulate(army, ruler, R, method, constraints):
    full_sim = dict.fromkeys(range(R))
    full_sim[0] = deepcopy(army)

    it = 1    
    while it < R:
        print("Iteration " + str(it))
        openpos = army.up_for_retirement()
        army.promote(method, constraints, openpos)
        army.pass_time()
        army.recruit()
        full_sim[it] = deepcopy(army)
        it += 1
    return full_sim

# write results into csv
def simulation_to_csv(ruler, simulation, method, constraints, filename):
    myfile = csv.writer(open(filename, 'wb'))

    R = len(simulation)

    for i in range(1, R):
        for j in simulation[i].soldiers:
            iteration = j.report()
            current_row = [i,
                           iteration['id'],
                           iteration['age'],
                           iteration['rank'],
                           iteration['seniority'],
                           iteration['unit'],
                           iteration['quality'],
                           iteration['ideology'],
                           method,
                           constraints,
                           ruler.ideology]
            myfile.writerow(current_row)

    print 'File successfully written!'

conn = psycopg2.connect("dbname=promotions")
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
METHOD varchar,
CONSTRAINTS varchar,
RULER_IDEOLOGY double precision);
"""
)
cur.close()
conn.close()

R = 100
leonidas = Ruler(0)
sparta = Army(leonidas, 20, 7, 4)

for method in ['ideology', 'random', 'seniority']:
    for constraint in ['none', 'ordered']:
        print('Simulation: ' + str(method) + ' ' + str(constraint))
        out = simulate(sparta, leonidas, R, method, constraint)
        fname = '/Users/gonzalorivero/Documents/wip/promotions/dta/sim' + \
                str(method) + '_' + str(constraint) + '.txt' 
     
        simulation_to_csv(leonidas, out, method, constraint, fname)
        
        conn = psycopg2.connect("dbname=promotions")
        cur = conn.cursor()
        cur.execute('COPY "simp" FROM %s CSV;', [str(fname)])
        conn.commit()
        cur.close()
        conn.close()



