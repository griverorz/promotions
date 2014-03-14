#! /usr/bin/python

'''
Simulation of promotions in a military
Author: @griverorz
'''

import numpy as np
import csv
import psycopg2
from copy import deepcopy
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
def simulate(army, R, ordered):
    full_sim = dict.fromkeys(range(R))
    full_sim[0] = deepcopy(army)
    it = 1

    risk_var = 0

    while it < R:
        if it % 500 is 0:
            print "Iteration {}".format(it)

        risk0 = army.risk()

        army.run_promotion(ordered)
        army["Ruler"].adapt(risk_var, fix="seniority")

        risk_var = float(army.risk() - risk0)

        full_sim[it] = deepcopy(army)
        it += 1
    return full_sim


# write results into csv
def simulation_to_csv(simulation, ordered, filename, replication):
    myfile = csv.writer(open(filename, 'wb'))

    R = len(simulation)

    for i in range(1, R):
        risk = simulation[i].risk()
        for j in simulation[i].units:
            iteration = simulation[i].data[j].report()
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
                           simulation[i]["Ruler"].parameters["seniority"],
                           simulation[i]["Ruler"].utility["internal"],
                           simulation[i]["Ruler"].utility["external"],
                           risk,
                           ordered,
                           simulation[i]["Ruler"].ideology]
            myfile.writerow(current_row)
    print 'File successfully written!'


def newtable():
    conn = psycopg2.connect(database="promotions", host="/tmp/.s.PGSQL.5432")
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
        UNIT integer,
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
    cur.close()
    conn.close()


if __name__ == "__main__":
    # newtable()
    baseloc = '/Users/gonzalorivero/Documents/wip/promotions/dta/'
    R = 5000
    # S = -10
    for s in [0.0, 10.0]:
        for r in [0.0, 10.0]:
            params = {'ideology': r, 'quality': s, 'seniority': 0}
            utility = {'internal': 0.0, 'external': 1.0}
            leonidas = Ruler(0.75, params, utility)
            original_sparta = Army(3, 3, 15, leonidas)
            original_sparta.fill()
            original_sparta.get_quality()
            original_sparta.get_factions()

            print "Replication {}-{}".format(r, s)
            for oo in [True, False]:
                sparta = deepcopy(original_sparta)
                print "Inits: {}, Ordered: {}".format(params, oo)
                simp = simulate(sparta, R, oo)
                fname = baseloc+'sim_'+str(oo)+'_'+str(s)+'.txt'
                simulation_to_csv(simp, oo, fname, str(r)+str(s))
                conn = psycopg2.connect(database="promotions")
                cur = conn.cursor()
                cur.execute('COPY "simp" FROM %s CSV;', [str(fname)])
                conn.commit()
                cur.close()
                conn.close()
