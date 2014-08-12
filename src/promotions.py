# data analysis from the simulation of promotion systems
# @griverorz
# 11Aug2014

import psycopg2
import pandas as pd
import matplotlib.pylab as plt

database='promotions'
conn = psycopg2.connect(database=database)

############################# ideology ####################
cur = conn.cursor()
cur.execute(
    "select replication, avg(ideology) as ideology, iteration, rank, \
    	    constraints, ruler_ideology, params_ideo, params_qual \
    from simp \
    group by replication, iteration, rank, constraints, ruler_ideology, \
    	  ruler_ideology, params_ideo, params_qual;")
ideology = cur.fetchall()
ideology = pd.DataFrame(ideology)

#################### quality ####################
cur = conn.cursor()
cur.execute(
"select avg(quality) as quality, iteration, rank, \
        constraints, ruler_ideology, \
        params_ideo, params_qual \
from simp \
group by iteration, rank, constraints, ruler_ideology,  \
        params_ideo, params_qual;")
quality = cur.fetchall()
quality = pd.DataFrame(quality)

#################### params ####################
cur = conn.cursor()
cur.execute(
"select replication, avg(params_ideo) as pideo, \
        avg(params_qual) as pqual, \
        iteration, \
        constraints, ruler_ideology \
from simp \
group by replication, iteration, constraints, ruler_ideology \
order by iteration;")
params = cur.fetchall()
params = pd.DataFrame(params)

conn.close()
