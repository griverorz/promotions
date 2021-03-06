#! /usr/bin/python

'''
Main call. Initiate with given parameters and run simulation model
Author: @griverorz
'''

import getopt
import sys
import numpy as np
from army import Army
from simulation import Simulation
from ruler import Ruler
from population import Population


def usage():
    print('Usage: python '+sys.argv[0]+' -r replications')


def main(argv):
    R = 500

    try:
        opts, args = getopt.getopt(argv, "hr:", ["help", "reps="])
    except getopt.GetoptError:
                sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(2)
        if opt in ('-r', '-replications'):
            R = int(arg)

    # Instantiate ruler ideology parameters
    rid0 = float(np.random.beta(2, 2, 1))
    rid1 = float(np.random.beta(2, 2, 1))
    params0 = {'ideology': 1, 'quality': 0, 'seniority': 0}
    params1 = {'ideology': 1, 'quality': 0, 'seniority': 0}
    leonidasr = Ruler(rid0, params0)
    spartar = Army(3, 3, 4, 30, [2, 4], leonidasr)
    leonidasl = Ruler(rid1, params1)
    spartal = Army(3, 3, 4, 30, [4, 2], leonidasl)

    print('Replication: ruler0-params {}, \
                        ruler1-params {}'.
          format(rid0,
                 rid1))
    for oo in [True]:
        # print 'Inits: {}, Ordered: {}'.format(params, oo)
        population = Population().population
        sargs = {'R': R, 'method': 'none'}
        simp = Simulation(spartar, spartal, population, sargs)
        simp.run()
        simp.write()

if __name__ == '__main__':
    main(sys.argv[1:])
