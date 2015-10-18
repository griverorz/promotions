from numpy import sign
from numpy.random import uniform
from numpy.linalg import norm
from random import choice

class Adapt(object):

    def __init__(self, method, state, delta, adapt=True):
        self.method = method
        self.state = (state["ideology"],
                      state["quality"],
                      state["seniority"])
        self.delta = delta
        self.adapt = adapt

    def new_state(self):
        if self.method is "none":
            newvals = self.noadapt()
        elif self.method is "satisfy":
            newvals = self.satisficing()
        else:
            raise Exception("Method not implemented")
        return(newvals)
    
    def noadapt(self):
        return(self.state)

    def satisficing(self):
        if self.adapt:
            newdir = self.other_direction()
        else:
            newdir = self.noadapt()
        return(newdir)

    def other_direction(self, step=0.1):
        ll = 3 # Number of parameters
        rdir = uniform(0, 1, ll)
        switcher = choice(range(ll))
        switcher = [-1 if i == switcher else 1 for i in range(ll)]
        rdir = [rdir[i]*switcher[i]*sign(self.delta[i]) for i in range(ll)]
        rdir = [(rdir[i]/norm(rdir))*step for i in range(ll)]
        nvector = [self.state[i] + rdir[i] for i in range(ll)]
        newvals = {"ideology": nvector[0],
                   "quality": nvector[1],
                   "seniority": nvector[2]}
        return(newvals)
    
class Ruler(object):
    """ The ruler """

    def __init__(self, ideology, params, utility):
        self.ideology = ideology
        self.parameters = params
        self.utility = utility

    def __str__(self):
        chars = "Ideology: {}, \nParameters: {}".format(
            self.ideology,
            self.parameters.values())
        return chars

    def utilityfunction():        
        pass
    
    def adapt(self, delta, adapt, method="satisficing"):
        adaptive = Adapt(method,
                         self.parameters,
                         delta,
                         adapt)
        self.parameters = adaptive.new_state()