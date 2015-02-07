#! /usr/bin/python

'''
Simulation of promotions in a military
Author: @griverorz
'''

import getopt
import sys
from classdef import *

def usage():
    print "python -r (# replications) -e (0-1 weight on external)\n"
    print 'Usage: '+sys.argv[0]+' -i <file1> [option]'

def main(argv):
    R = 500
    internal = .5
    external = .5

    try:
        opts, args = getopt.getopt(argv, 'h:r')
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(2)
        if opt in ('-r', '-replications'):
            R = int(arg)

    for s in [0.0, 10.0]:
        for r in [0.0, 10.0]:
            params = {'ideology': r, 'quality': s, 'seniority': 0}
            utility = {'internal': internal, 'external': external}
            leonidas = Ruler(0.75, params, utility)
            sparta = Army(3, 3, 3, 15, leonidas)
            sparta.populate()
            sparta.get_quality()

            print 'Replication with ideology {} and quality {}'.format(r, s)
            for oo in [True, False]:
                print 'Inits: {}, Ordered: {}'.format(params, oo)
                sargs = {'R':R, 'ordered':True, 'fixed':'seniority'}
                simp = Simulation()
                simp.populate(sparta, sargs)
                simp.run()
                simp.write()

if __name__ == '__main__':
    main(sys.argv[1:])
