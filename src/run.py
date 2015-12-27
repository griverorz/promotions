#! /usr/bin/python

'''
Simulation of promotions in a military
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
    print 'Usage: python '+sys.argv[0]+' -r replications'

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


    par, rid, put = np.random.uniform(0, 1, 3)
    params = {'ideology': 1, 'quality': 0, 'seniority': 0}
    utility = {'internal': put, 'external': (1 - put)}
    leonidas0 = Ruler(rid, params, utility)
    sparta0 = Army(3, 3, 3, 30, leonidas0, [2, 2])
    leonidas1 = Ruler(rid, params, utility)
    sparta1 = Army(3, 3, 3, 30, leonidas1, [2, 2])
    population = Population().population

    print ('Replication: internal {}, ideology {}, ruler {}'.
           format(utility["internal"], params["ideology"], rid))
    for oo in [True]:
        # print 'Inits: {}, Ordered: {}'.format(params, oo)
        sargs = {'R':R, 'method': 'none'}
        simp = Simulation(sparta0, sparta1, population, sargs)
        simp.run()
        simp.write()

if __name__ == '__main__':
    main(sys.argv[1:])
