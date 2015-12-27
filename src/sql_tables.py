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
    age0 = Column("age0", Integer)
    age1 = Column("age1", Integer)
    rank = Column("rank", Integer)
    unit = Column("unit", String)

    quality0 = Column("quality0", Float)
    ideology0 = Column("ideology0", Float)
    quality1 = Column("quality1", Float)
    ideology1 = Column("ideology1", Float)
    ruler0 = Column("ruler0", Float)
    ruler1 = Column("ruler1", Float)

    winner = Column("winner", Integer)
    
class SimParams(DBase):
    """ DB with simulation data """
    __tablename__ = "simparams"

    id = Column(Integer, primary_key=True)
    children = relationship(SimData, backref="simparams")
    
def create_db(sqldata):
    sqldata = open(sqldata).read()
    dbdata = json.loads(sqldata)

    engine = create_engine(url.URL(**dbdata))
    DBase.metadata.create_all(engine)
    
if __name__ == "__main__":
    sqldata = sys.argv[1]
    create_db(sqldata)
