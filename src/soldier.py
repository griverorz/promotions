from itertools import count
from np.random import binomial

class Soldier(object):
    """ A soldier """

    id_generator = count(1)

    def __init__(self, rank, seniority, age, quality, ideology, unit):
        self.id = next(self.id_generator)
        self.rank = rank
        self.seniority = seniority
        self.age = age
        self.quality = quality
        self.ideology = ideology
        self.unit = unit
        self.alive = True

    def report(self):
        return({'id': self.id,
                'rank': self.rank,
                'age': self.age,
                'quality': self.quality,
                'ideology': self.ideology,
                'unit': self.unit,
                'seniority': self.seniority})

    def update_time(self, topage):
        """ Move time one period. If junior, kill with probability p """
        self.age += 1
        self.seniority += 1
        if self.age > topage:
            self.kill()
        elif self.rank is 1:
            prob = float(self.age)/float(topage + 1)
            to_kill = int(binomial(1, prob, 1))
            if to_kill is 1:
                self.kill()

    def will_retire(self, topage):
        if self.age == (topage - 1):
            return(True)
        else:
            return(False)

    def is_candidate(self, openrank, openunit, topage):
        """ Is a candidate for promotion given an open position? """
        def _possible_superiors(code):
            out = []
            while len(str(code)) > 1:
                code = code[0:(len(str(code))-1)]
                out.append(code)
            return(out)
 
        def _candidate(openrank, topage):
            isc = False
            condalive = self.age < topage and self.alive
            if self.rank == (openrank - 1) and condalive:
                isc = True
            return(isc)

        is_sub = openunit in _possible_superiors(self.unit)
        isc = _candidate(openrank, topage) and is_sub
        return(isc)
        
    def kill(self):
        self.alive = False
