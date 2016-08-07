'''
Description: SQL table
Author: Gonzalo Rivero
Date: 29-Jan-2015 22:00
'''

from sqlalchemy import Column, Integer, String, ForeignKey
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
    iteration = Column(Integer, ForeignKey("simruler.id"))
    replication = Column(Integer, ForeignKey("simparams.id"))
    age = Column("age", JSON)
    rank = Column("rank", Integer)
    unit = Column("unit", String)
    quality = Column("quality", JSON)
    ideology = Column("ideology", JSON)


class SimRuler(DBase):
    __tablename__ = "simruler"
    
    id = Column(Integer, primary_key=True)
    children = relationship(SimData, backref="simruler")
    iteration = Column("iteration", Integer)
    ruler = Column("ruler", JSON)
    winner = Column("winner", Integer)
    

class SimParams(DBase):
    """ DB with simulation data """
    __tablename__ = "simparams"

    id = Column(Integer, primary_key=True)
    children = relationship(SimData, backref="simparams")


class SimPopulation(DBase):
    __tablename__ = "simpopulation"
    
    """ DB with population data """
    id = Column(Integer, primary_key=True)
    population = Column("population", JSON)
    
def create_db(sqldata):
    sqldata = open(sqldata).read()
    dbdata = json.loads(sqldata)

    engine = create_engine(url.URL(**dbdata))
    DBase.metadata.create_all(engine)
    
if __name__ == "__main__":
    sqldata = sys.argv[1]
    create_db(sqldata)
