# data analysis from the simulation of promotion systems
# @griverorz
# 11Aug2014

import pandas as pd
import matplotlib.pyplot as plt
import itertools
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import url
from sql_tables import DataTable
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.orm import mapper
from sqlalchemy.ext.declarative import declarative_base
import json

dbdata = json.loads(open("sql_data.json").read())
engine = create_engine(url.URL(**dbdata))
DBase = declarative_base(engine)

class Promotions(DBase):
    __tablename__ = 'promotions'
    __table_args__ = {'autoload':True}

    
def load_session(DBase):
    """"""
    metadata = DBase.metadata
    session = sessionmaker(bind=engine)
    dbsession = session()
    return dbsession

dbsession = load_session(DBase)

############################# ideology ####################
mtable = (dbsession.query(Promotions.replication,
                          func.avg(Promotions.ideology),
                          Promotions.iteration,
                          Promotions.rank,
                          Promotions.constraints,
                          Promotions.ruler_ideology)
          .group_by(
              Promotions.replication,
              Promotions.iteration,
              Promotions.rank,
              Promotions.constraints,
              Promotions.ruler_ideology))

ideology = pd.DataFrame(mtable.all(),
                        columns=["replication", "ideology",
                                 "iteration", "rank",
                                 "constraints", "ruler_ideology"])


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
mtable = dbsession.query(dtable.c.replication,
                       func.avg(dtable.c.quality),
                       dtable.c.iteration,
                       dtable.c.rank,
                       dtable.c.constraints,
                       dtable.c.ruler_ideology).group_by(
                           dtable.c.replication,
                           dtable.c.iteration,
                           dtable.c.rank,
                           dtable.c.constraints,
                           dtable.c.ruler_ideology)


quality = pd.DataFrame(mtable.all(),
                        columns=["replication", "quality",
                                 "iteration", "rank",
                                 "constraints", "ruler_ideology"])

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
