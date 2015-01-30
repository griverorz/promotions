#! /usr/bin/python

'''
Simulation of promotions in a military
Author: @griverorz
'''

import getopt
import sys
from classdef import *


def main(argv):
    R = 500
    internal = .5
    external = .5

    try:
        opts, args = getopt.getopt(argv, 'r:i:e')
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-r':
            R = int(arg)
        if opt == '-e':
            external = float(arg)

    simp = Simulation()
    simp.connect_db()
    for s in [0.0, 10.0]:
        for r in [0.0, 10.0]:
            params = {'ideology': r, 'quality': s, 'seniority': 0}
            utility = {'internal': internal, 'external': external}
            leonidas = Ruler(0.75, params, utility)
            sparta = Army(3, 3, 3, 15, leonidas)
            sparta.populate()
            sparta.get_quality()

            print 'Replication {}-{}'.format(r, s)
            for oo in [True, False]:
                print 'Inits: {}, Ordered: {}'.format(params, oo)
                sargs = {'R':R, 'ordered':True, 'fixed':'seniority'}
                simp.populate(sparta, sargs)
                simp.run()
                simp.parse(str(s)+str(r))
                simp.write_to_table()

if __name__ == '__main__':
    main(sys.argv[1:])
