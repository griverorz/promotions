from itertools import count
from copy import deepcopy
import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import url
from sql_tables import SimData, SimParams, SimRuler
from sqlalchemy import create_engine
from compete import Compete

class Simulation(Compete):
    id_generator = count(1)
    
    def __init__(self, army0, army1, population, args):
        self.id = next(self.id_generator)
        self.army0 = army0
        self.army1 = army1
        self.population = population
        self.R = args["R"]
        self.method = args["method"]
        self.history = {"army0": dict.fromkeys(range(self.R)),
                        "army1": dict.fromkeys(range(self.R)),
                        "winner": dict.fromkeys(range(self.R))}

        self.history["army0"][0] = deepcopy(self.army0)
        self.history["army1"][0] = deepcopy(self.army1)
        self.history["winner"][0] = None
        
    def run(self):
        it = 1

        while it < self.R:
            if it % 500 is 0:
                print "Iteration {}".format(it)

            competition = Compete(self.population, self.army0, self.army1)
            winner = competition.compete()
            mover = [True, True]
            mover[winner] = False

            replace0, replace1 = mover
            self.army0.run_promotion(replace0)
            self.army1.run_promotion(replace1)

            self.history["army0"][it] = deepcopy(self.army0)
            self.history["army1"][it] = deepcopy(self.army1)
            self.history["winner"][it] = winner

            it += 1

    def parse_simulation(self):
        simparams = {"id": self.id}
        self.simparams = simparams

    def parse_history(self): 
        self.parsed_data = []
        self.ruler_row = []
        R = self.R

        for i in range(1, R):
            sim0 = self.history["army0"][i]
            sim1 = self.history["army1"][i]
            winner = self.history["winner"][i]
            for j in sim0.units:
                iteration0 = sim0.data[j].report()
                iteration1 = sim1.data[j].report()

                current_row = {"iteration": i,
                               "replication": self.id,
                               "rank": iteration0['rank'],
                               "unit": iteration0['unit'],

                               "age": {"army0": iteration0['age'],
                                       "army1": iteration1["age"]},
                               "ideology": {"army0": iteration0['ideology'].tolist(),
                                            "army1": iteration1["ideology"].tolist()},
                               "quality": {"army0": iteration0['quality'],
                                           "army1": iteration1["quality"]}
                }
                self.parsed_data.append(current_row)
                
            ruler_row = {"iteration": i,
                         "ruler": {"army0": sim0["Ruler"].ideology.tolist(),
                                   "army1": sim1["Ruler"].ideology.tolist()},
                         "winner": winner}
            self.ruler_row.append(ruler_row)

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
        """ Write ruler data """
        newruler = [SimRuler(**i) for i in self.ruler_row]
        self.dbsession.add_all(newruler)
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
