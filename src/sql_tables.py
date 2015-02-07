'''
Description: SQL table
Author: Gonzalo Rivero
Date: 29-Jan-2015 22:00
'''

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import url
from sqlalchemy import create_engine
import json
import sys

DBase = declarative_base()

class DataTable(DBase):
    """ DB of simulations """
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True)
    replication = Column("replication", String)
    iteration = Column("iteration", Integer)
    age = Column("age", Integer)
    rank = Column("rank", Integer)
    seniority = Column("seniority", Integer)
    unit = Column("unit", String)
    quality = Column("quality", Float)
    ideology = Column("ideology", Float)
    uquality = Column("uquality", Float)
    params_ideo = Column("params_ideo", Float)
    params_qual = Column("params_qual", Float)
    params_sen = Column("params_sen", Float)
    utility = Column("utility", Float)
    risk = Column("risk", Float)
    constraints = Column("constraints", String)
    ruler_ideology = Column("ruler_ideology", Float);


def create_db(sqldata):
    sqldata = open(sqldata).read()
    dbdata = json.loads(sqldata)

    engine = create_engine(url.URL(**dbdata))
    DBase.metadata.create_all(engine)
    
if __name__ == "__main__":
    sqldata = sys.argv[1]
    create_db(sqldata)
