'''
Description: SQL table
Author: Gonzalo Rivero
Date: 29-Jan-2015 22:00
'''

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import url
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship
import json
import sys

DBase = declarative_base()

class SimData(DBase):
    """ DB of simulations """
    __tablename__ = "simdata"

    id = Column(Integer, primary_key=True)
    iteration = Column("iteration", Integer)
    replication = Column(Integer, ForeignKey("simparams.id"))
    age = Column("age", Integer)
    rank = Column("rank", Integer)
    seniority = Column("seniority", Integer)
    unit = Column("unit", String)
    quality = Column("quality", Float)
    ideology = Column("ideology", Float)
    params = Column("params", JSON)
    g_utility = Column("g_utility", Float)
    g_quality = Column("g_quality", Float)


class SimParams(DBase):
    """ DB with simulation data """
    __tablename__ = "simparams"

    id = Column(Integer, primary_key=True)
    children = relationship(SimData, backref="simparams")
    method = Column("method", String)
    ideology = Column("ideology", Float);
    utility = Column("utility", JSON)
    
def create_db(sqldata):
    sqldata = open(sqldata).read()
    dbdata = json.loads(sqldata)

    engine = create_engine(url.URL(**dbdata))
    DBase.metadata.create_all(engine)
    
if __name__ == "__main__":
    sqldata = sys.argv[1]
    create_db(sqldata)
