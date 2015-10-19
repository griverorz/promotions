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

    for par in np.linspace(0, 1, 5):
        for rid in np.linspace(0, 1, 5):
            for put in np.linspace(0, 1, 5):

                params = {'ideology': par, 'quality': (1 - par), 'seniority': 0}
                utility = {'internal': put, 'external': (1 - put)}
                leonidas = Ruler(rid, params, utility)
                sparta = Army(4, 4, 3, 30, leonidas)

                print ('Replication: internal {}, ideology {}, ruler {}'.
                       format(utility["internal"], params["ideology"], rid))
                for oo in [True]:
                    # print 'Inits: {}, Ordered: {}'.format(params, oo)
                    sargs = {'R':R, 'method': 'satisfy'}
                    simp = Simulation(sparta, sargs)
                    simp.run()
                    simp.write()

if __name__ == '__main__':
    main(sys.argv[1:])
 
