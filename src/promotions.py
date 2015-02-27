# data analysis from the simulation of promotion systems
# @griverorz
# 11Aug2014

import pandas as pd
from pylab import *
import itertools
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import url
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base
from sql_tables import SimData, SimParams
import json

dbdata = json.loads(open("sql_data.json").read())
engine = create_engine(url.URL(**dbdata))
DBase = declarative_base(engine)

    
def load_session(DBase):
    """"""
    metadata = DBase.metadata
    session = sessionmaker(bind=engine)
    dbsession = session()
    return dbsession

dbsession = load_session(DBase)

############################# ideology ####################
mtable = (dbsession.query(SimData.replication,
                          func.avg(SimData.ideology).label("ideology"),
                          SimData.iteration,
                          SimData.rank)
          .group_by(
              SimData.replication,
              SimData.iteration,
              SimData.rank))

colnames = [i['name'] for i in mtable.column_descriptions]
ideology = pd.DataFrame(mtable.all(), columns=colnames)

ideology = ideology.sort(["iteration", "replication"])
fig, axes = plt.subplots(4, 3, sharex=True, sharey=True) 

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
    plt.ylim(0, 1)

#################### quality ####################

mtable = (dbsession.query(SimData.replication,
                          func.avg(SimData.quality).label("quality"),
                          SimData.iteration,
                          SimData.rank)
          .group_by(
              SimData.replication,
              SimData.iteration,
              SimData.rank))

colnames = [i['name'] for i in mtable.column_descriptions]
quality = pd.DataFrame(mtable.all(), columns=colnames)

quality = quality.sort(["iteration", "replication"])
fig, axes = plt.subplots(4, 3, sharex=True, sharey=True)

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

mtable = dbsession.query(dtable.c.replication,
                       func.avg(dtable.c.params_ideo),
                       dtable.c.iteration,
                       dtable.c.constraints,
                       dtable.c.ruler_ideology).group_by(
                           dtable.c.replication,
                           dtable.c.iteration,
                           dtable.c.constraints,
                           dtable.c.ruler_ideology)


params = pd.DataFrame(mtable.all(),
                        columns=["replication", "params_ideo",
                                 "iteration",
                                 "constraints", "ruler_ideology"])
