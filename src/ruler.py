from numpy import array, pi, sin, cos
from numpy.random import uniform, binomial


def toarray(x):
    '''
    Utility function to ensure that parameters of the Ruler
    are pulled and pushed in order
    '''
    return(array([x["ideology"],
                  x["quality"],
                  x["seniority"]]))


def truncate(x, xmin=0, xmax=1):
    '''
    Winsorize a vector between min and max
    '''
    if x < xmin:
        x = xmin
    if x > xmax:
        x = xmax
    return(x)


def random_two_vector(center, stepsize):
    '''
    Create a random vector centered at `center` with length `stepsize`
    '''
    phi = uniform(0, pi*2)
    x = center[0] + stepsize * cos(phi)
    y = center[1] + stepsize * sin(phi)
    return (x, y)


def normalize(x):
    '''
    Normalize a vector to unit length
    '''
    return(toarray(x)/sum(toarray(x)))


class Adapt(object):
    '''
    Adapt the location of the ruler.

    Given an initial point, create a new location based on a adaptation method.
    '''
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
        state = toarray(self.state)
        rdir = random_two_vector(state, stepsize)
        newvals = {"ideology": rdir[0],
                   "quality": rdir[1],
                   "seniority": 0}
        return(newvals)


class Ruler(object):
    """
    The ruler.
    
    A dictionary with parameters and a decision to adapt.
    """

    def __init__(self, ideology, params):
        self.ideology = ideology
        self.parameters = params
        self.alive = True

    def __str__(self):
        chars = "Ideology: {}, \nParameters: {}".format(
            self.ideology,
            toarray(self.parameters))
        return chars

    def update_time(self):
        prob = 0.05
        to_kill = int(binomial(1, prob, 1))

        if to_kill is 1:
            self.kill()

    def kill(self):
        self.alive = False
        
    def utilityfunction():
        pass
    
    def adapt(self, should_adapt, method):
        adaptive = Adapt(method,
                         self.parameters,
                         should_adapt)
        self.parameters = adaptive.new_state()
