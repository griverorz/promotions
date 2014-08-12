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
    internal = 0.0
    external = 1.0

    try:
        opts, args = getopt.getopt(argv, 'r:i:e')
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-r':
            R = int(arg) 
        if opt == '-i':
            internal = float(arg) 
        if opt == '-e':
            external = float(arg)

    simp = Simulation()
    simp.newtable('promotions')
    baseloc = '/Users/gonzalorivero/Documents/wip/promotions/dta/'
    for s in [0.0, 10.0]:
        for r in [0.0, 10.0]:
            params = {'ideology': r, 'quality': s, 'seniority': 0}
            utility = {'internal': internal, 'external': external}
            leonidas = Ruler(0.75, params, utility)
            sparta = Army(10, 3, 3, 15, leonidas)
            sparta.populate()
            sparta.get_quality()
            sparta.get_factions()

            print 'Replication {}-{}'.format(r, s)
            for oo in [True, False]:
                print 'Inits: {}, Ordered: {}'.format(params, oo)
                fname = baseloc+'sim_'+str(oo)+'_'+str(s)+'.csv'
                sargs = {'R':100, 'ordered':True, 'fixed':'seniority'}
                simp.populate(sparta, fname, sargs)
                simp.run()
                simp.to_csv()
                simp.to_table()

if __name__ == '__main__':
    main(sys.argv[1:])
