# data analysis from the simulation of promotion systems
# @griverorz
# 11Aug2014

import psycopg2
import pandas as pd
import matplotlib.pylab as plt
import itertools

database='promotions'
conn = psycopg2.connect(database=database)

############################# ideology ####################
cur = conn.cursor()

cur.execute(
    "select replication, avg(ideology) as ideology, iteration, rank, \
        constraints, ruler_ideology \
    from simp \
    group by replication, iteration, rank, constraints, ruler_ideology, \
    	  ruler_ideology;")

ideology = cur.fetchall()
ideology = pd.DataFrame(ideology)
ideology.columns = [i[0] for i in cur.description]

ideology = ideology.sort(["iteration", "replication"])
fig, axes = plt.subplots(4, 3, sharex='col')

loc = itertools.product(*[range(len(set(ideology['replication']))), 
                          range(3)])

reps = list(set(ideology['replication']))
ranks = range(1, 4)

for i, j in loc:
    axes[i, j].plot(ideology["iteration"][ideology["rank"] == ranks[j]]
                    [ideology["replication"] == reps[i]], 
                    ideology["ideology"][ideology["rank"] == ranks[j]]
                    [ideology["replication"] == reps[i]])
    axes[i, j].set_title("Rank {}, Replication {}".format(ranks[j], reps[i]))

#################### quality ####################
cur.execute(
    "select replication, avg(quality) as quality, iteration, rank, \
        constraints, ruler_ideology \
    from simp \
    group by replication, iteration, rank, constraints, ruler_ideology;")
quality = cur.fetchall()
quality = pd.DataFrame(quality)
quality.columns = [i[0] for i in cur.description]

quality = quality.sort(["iteration", "replication"])
fig, axes = plt.subplots(4, 3, sharex='col')

loc = itertools.product(*[range(len(set(quality['replication']))), 
                          range(3)])

reps = list(set(quality['replication']))
ranks = range(1, 4)

for i, j in loc:
    axes[i, j].plot(quality["iteration"][quality["rank"] == ranks[j]]
                    [quality["replication"] == reps[i]], 
                    quality["quality"][quality["rank"] == ranks[j]]
                    [quality["replication"] == reps[i]])
    axes[i, j].set_title("Rank {}, Replication {}".format(ranks[j], reps[i]))

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
params.columns = [i[0] for i in cur.description]

conn.close()
