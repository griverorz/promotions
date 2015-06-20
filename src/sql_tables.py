'''
Description: SQL table
Author: Gonzalo Rivero
Date: 29-Jan-2015 22:00
'''

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import url
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref
import json
import sys

DBase = declarative_base()

class SimData(DBase):
    """ DB of simulations """
    __tablename__ = "simdata"

    id = Column(Integer, primary_key=True)
    replication = Column(Integer, ForeignKey("simparams.id"))
    iteration = Column("iteration", Integer)
    age = Column("age", Integer)
    rank = Column("rank", Integer)
    seniority = Column("seniority", Integer)
    unit = Column("unit", String)
    quality = Column("quality", Float)
    ideology = Column("ideology", Float)
    uquality = Column("uquality", Float)
    parideology = Column("parideology", Float)
    parseniority = Column("parseniority", Float)
    parquality = Column("parquality", Float)
    risk = Column("risk", Float)


class SimParams(DBase):
    """ DB with simulation data """
    __tablename__ = "simparams"

    id = Column(Integer, primary_key=True)
    children = relationship(SimData, backref="simparams")
    params_ideo = Column("params_ideo", Float)
    params_qual = Column("params_qual", Float)
    params_sen = Column("params_sen", Float)
    constraints = Column("constraints", String)
    adapt = Column("adapt", String)
    ruler_ideology = Column("ruler_ideology", Float);
    utility = Column("utility", Float)
    
def create_db(sqldata):
    sqldata = open(sqldata).read()
    dbdata = json.loads(sqldata)

    engine = create_engine(url.URL(**dbdata))
    DBase.metadata.create_all(engine)
    
if __name__ == "__main__":
    sqldata = sys.argv[1]
    create_db(sqldata)
