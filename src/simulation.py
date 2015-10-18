from itertools import count
from copy import deepcopy
from np.random import uniform
import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import url
from sql_tables import SimData, SimParams
from sqlalchemy import create_engine

class Simulation(object):
    id_generator = count(1)
    
    def __init__(self):
        self.id = next(self.id_generator)

    def populate(self, army, args):
        self.army = army
        self.R = args["R"]
        self.ordered = args["ordered"]
        self.fixed = args["fixed"]
        self.adapt = args["adapt"]
        self.history = dict.fromkeys(range(self.R))
        self.history[0] = deepcopy(self.army)

    def run(self):
        it = 1
        var_risk = 0
        new_dir = list(uniform(-1, 1, 3))

        while it < self.R:
            if it % 500 is 0:
                print "Iteration {}".format(it)

            risk0 = self.army.risk()

            self.army.run_promotion(self.ordered)
            new_dir = self.army["Ruler"].adapt(new_dir,
                                               var_risk, 
                                               fix="seniority",
                                               adapt=self.adapt)
            var_risk = float(self.army.risk() - risk0)

            self.history[it] = deepcopy(self.army)
            it += 1

    def parse_simulation(self):
        simparams = {"id": self.id,
                     "params_ideo": self.army["Ruler"].parameters["ideology"],
                     "params_qual": self.army["Ruler"].parameters["quality"],
                     "params_sen": self.army["Ruler"].parameters["seniority"],
                     "utility": self.army["Ruler"].utility["external"],
                     "constraints": self.ordered,
                     "adapt": self.adapt,
                     "ruler_ideology": self.army["Ruler"].ideology}
        self.simparams = simparams
        
    def parse_history(self): 
        self.parsed_data = []
        R = self.R
        
        for i in range(1, R):
            sim = self.history[i]
            risk = sim.risk()
            for j in sim.units:
                iteration = sim.data[j].report()

                current_row = {"iteration": i,
                               "replication": self.id,
                               "age": iteration['age'],
                               "rank": iteration['rank'],
                               "seniority": iteration['seniority'],
                               "unit": "".join(str(x) for x in iteration['unit']),
                               "quality": iteration['quality'],
                               "ideology": iteration['ideology'],
                               "uquality": sim.uquality[j],
                               "parideology": sim.data["Ruler"].parameters["ideology"],
                               "parseniority": sim.data["Ruler"].parameters["seniority"],
                               "parquality": sim.data["Ruler"].parameters["quality"],
                               "risk": risk}
                                                              
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
