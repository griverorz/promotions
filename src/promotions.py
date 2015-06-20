# data analysis from the simulation of promotion systems
# @griverorz
# 11Aug2014

import pandas as pd
import matplotlib.pylab as plt
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import url
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base
from sql_tables import SimData, SimParams
import json
import itertools 

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

#################### divisions from the top ####################

mtable = (dbsession.query(SimData.replication,
                          SimData.quality,
                          SimData.iteration,
                          SimData.unit,
                          SimParams.params_ideo,
                          SimParams.ruler_ideology)
          .filter(SimData.rank == 3)
          .join(SimParams, SimParams.id==SimData.replication))

colnames = [i['name'] for i in mtable.column_descriptions]
factions = pd.DataFrame(mtable.all(), columns=colnames)


out = (factions.groupby(["iteration", "replication", "params_ideo", "ruler_ideology"]).
       apply(lambda x: np.var(x["quality"])))

prods = itertools.product(factions.ruler_ideology.unique(),
                          factions.params_ideo.unique())


for i in ["0", "1", "2", "3"]:
    plt.plot(factions["iteration"][factions["ruler_ideology"] == 0.7][factions["params_ideo"] == 0.1][factions["unit"] == i],
             factions["quality"][factions["ruler_ideology"] == 0.7][factions["params_ideo"] == 0.1][factions["unit"] == i], color="red")



for ideo in factions['ruler_ideology'].unique(): 
    tmpfactions = factions.loc[factions.ruler_ideology == ideo]
    it = tmpfactions["replication"].unique(); it.sort()
    f, axarr = plt.subplots(11)
    for k, i in enumerate(it):
        for j in ["0", "1", "2", "3"]:  
            x = tmpfactions["iteration"][
                tmpfactions["unit"] == j][
                tmpfactions["replication"] == it[k]]
            y = tmpfactions["quality"][
                tmpfactions["unit"] == j][
                tmpfactions["replication"] == it[k]]
            axarr[k].grid()
            axarr[k].set_ylim([0, 1])
            axarr[k].plot(x, y, color="red", alpha=0.5)
            axarr[k].axhline(y=0.5)
    axarr[0].set_title("Constant")
    idpar = tmpfactions['params_ideo'][tmpfactions['replication'] == it[k]].unique()
    f.suptitle("Quality={}, Ideology={}".format(float(1 - idpar), float(ideo)), size=16)    
    f.savefig('./../img/quality_ruler_{}_{}.png'.format(float(1 - idpar), float(ideo)))

############################# ideology ####################

mtable = (dbsession.query(SimData.replication,
                          SimData.ideology,
                          SimData.iteration,
                          SimData.unit,
                          SimParams.ruler_ideology, 
                          SimParams.utility, 
                          SimParams.adapt)
          .filter(SimData.rank == 3)
          .join(SimParams, SimParams.id==SimData.replication))

colnames = [i['name'] for i in mtable.column_descriptions]
factions = pd.DataFrame(mtable.all(), columns=colnames)

prods = itertools.product(factions.ruler_ideology.unique(),
                          factions.utility.unique())
namesprods = itertools.product(['low', 'midlow', 'midhigh', 'high'], 
                               ['high', 'midhigh', 'midlow', 'low'])
new_list = [item for item in namesprods]

for step, el in enumerate(prods): 
    tmpfactions = factions.loc[(factions.ruler_ideology == el[0]) & (factions.utility == el[1])]
    it = tmpfactions["replication"].unique(); it.sort()
    f, axarr = plt.subplots(4, 2)
    for k, i in enumerate(tmpfactions.replication.unique()):
        for j in ["0", "1", "2", "3"]:        
            x = tmpfactions["iteration"][tmpfactions["unit"] == j][tmpfactions["replication"] == it[k]]
            y = tmpfactions["ideology"][tmpfactions["unit"] == j][tmpfactions["replication"] == it[k]]
            axarr[k % 4., int(k < 4)].grid()
            axarr[k % 4., int(k < 4)].set_ylim([0, 1])
            axarr[k % 4., int(k < 4)].plot(x, y, color="red", alpha=0.5)
            axarr[k % 4., int(k < 4)].axhline(y=0.5)
    axarr[0, 1].set_title("Adaptive")
    axarr[0, 0].set_title("Constant")
    f.suptitle("Ideology={0:.1f}, Utility={1:.1f}".format(el[0], el[1]), size=16)    
    f.savefig('./../img/ideology_ruler_{}_{}.png'.format(new_list[step][0], new_list[step][1]))

#################### params ####################

mtable = (dbsession.query(SimData.replication,
                          func.avg(SimData.parquality).label("quality"),
                          func.avg(SimData.parideology).label("ideology"),
                          SimData.iteration)
          .group_by(
              SimData.replication,
              SimData.iteration))

colnames = [i['name'] for i in mtable.column_descriptions]
params = pd.DataFrame(mtable.all(), columns=colnames)

f, axarr = plt.subplots(4, 1)
it = params["replication"].unique(); it.sort()
params = params.sort(["replication", "iteration"])

for i in range(0, 4):
    axarr[i].plot(params["ideology"][params["replication"] == it[i]], 
                 params["quality"][params["replication"] == it[i]])
    axarr[i].set_xlim([-25, 25])
    axarr[i].set_ylim([-25, 25])
    axarr[i].axhline(y=0)
    axarr[i].axvline(x=0)
    # axarr[i].set_title("Rank {}, Replication {}".format(it[i]))
    
