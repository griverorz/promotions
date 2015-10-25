from itertools import count
from copy import deepcopy
import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import url
from sql_tables import SimData, SimParams
from sqlalchemy import create_engine
from army import Utility
from ruler import toarray
from numpy import array

class Simulation(object):
    id_generator = count(1)
    
    def __init__(self, army, args):
        self.id = next(self.id_generator)
        self.army = army
        self.R = args["R"]
        self.method = args["method"]
        self.history = dict.fromkeys(range(self.R))
        self.history[0] = deepcopy(self.army)
        self.utility = Utility(self.army)
        
    def run(self):
        it = 1
        udelta = 0.
        
        while it < self.R:
            if it % 500 is 0:
                print "Iteration {}".format(it)

            u0 = Utility(self.army).utility
            self.army.run_promotion()
            udelta = float(Utility(self.army).utility - u0)

            move = False
            if udelta < 0:
                move = True

            self.army["Ruler"].adapt(move, self.method)

            self.history[it] = deepcopy(self.army)
            it += 1

    def parse_simulation(self):
        simparams = {"id": self.id,
                     "utility": self.army["Ruler"].utility,
                     "method": self.method,
                     "ideology": self.army["Ruler"].ideology}
        self.simparams = simparams
        
    def parse_history(self): 
        self.parsed_data = []
        R = self.R
        
        for i in range(1, R):
            sim = self.history[i]
            for j in sim.units:
                iteration = sim.data[j].report()

                current_row = {"iteration": i,
                               "replication": self.id,
                               "age": iteration['age'],
                               "rank": iteration['rank'],
                               "seniority": iteration['seniority'],
                               "unit": iteration['unit'],
                               "quality": iteration['quality'],
                               "ideology": iteration['ideology'],
                               "params":sim["Ruler"].parameters,
                               "g_utility":Utility(sim).utility,
                               "g_quality":Utility(sim).quality
                }
                                                              
                self.parsed_data.append(current_row)


    def connect_db(self):
        dbdata = json.loads(open("sql_data.json").read())
        engine = create_engine(url.URL(**dbdata))
        DBSession = sessionmaker()
        self.dbsession = DBSession(bind=engine)

    def write_to_table(self):
        self.connect_db()
        """ Write simulation parameters """
        newparams = SimParams(**self.simparams)
        self.dbsession.add(newparams)
        self.dbsession.commit()
        """ Write simulation data """
        newcases = [SimData(**i) for i in self.parsed_data]
        self.dbsession.add_all(newcases) 
        self.dbsession.commit()

        self.dbsession.flush()
        
    def write(self):
        self.parse_simulation()
        self.parse_history()
        self.write_to_table()
