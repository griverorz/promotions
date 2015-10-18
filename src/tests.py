def test(self):
    """ Check the structure of the military """
    # No empty position
    tests = dict.fromkeys(["novacancies", "allalive",
                           "rconsistent", "uconsistent", "nodupes"])
    tests["novacancies"] = any(i is not None for i in self.data.values())
    # Position in agreement with rank
    tests["rconsistent"] = all([self.data[i].rank is self.unit_to_rank(i)
                                for i in self.units])
    tests["allalive"] = all([self.data[i].alive for i in self.units])
    # Units in agreement
    tests["uconsistent"] = all([self.data[i].unit is i for i in self.units])
    # No duplicates
    tests["nodupes"] = len(set(self.data.values())) == len(self.data.keys())
    # return tests
    if not all(tests.values()):
        fails = [tests.keys()[i] for i in all_indices(False, tests.values())]
        print "Fails tests: " + ', '.join(fails)
