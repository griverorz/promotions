from numpy import array, pi, sin, cos
from numpy.random import uniform

def toarray(x):
    return(array([x["ideology"],
                  x["quality"],
                  x["seniority"]]))

def truncate(x, xmin=0, xmax=1):
    if x < xmin:
        x = xmin
    if x > xmax:
        x = xmax
    return(x)

def random_two_vector(stepsize):
    phi = uniform(0, pi*2)
    x = stepsize * cos(phi)
    y = stepsize * sin(phi)
    return (x, y)

def normalize(x):
    return(toarray(x)/sum(toarray(x)))

class Adapt(object):
    def __init__(self, method, state, adapt=True):
        self.method = method
        self.state = state
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
            newdir = self.new_direction()
        else:
            newdir = self.noadapt()
        return(newdir)

    def new_direction(self, stepsize=0.05):
        state = toarray(self.state).tolist()
        ll = len(state) - 1
        rdir = random_two_vector(stepsize)
        nvector = [state[i] + rdir[i] for i in range(ll)]
        newvals = {"ideology": nvector[0],
                   "quality": nvector[1],
                   "seniority": 0}
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
    
    def adapt(self, adapt, method):
        adaptive = Adapt(method,
                         self.parameters,
                         adapt)
        self.parameters = adaptive.new_state()
