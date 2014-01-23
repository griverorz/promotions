#! /usr/bin/python

import collections

def argmax(lst):
     return lst.index(max(lst))    

def argmin(lst):
     return lst.index(min(lst))    
    
def toInt(numList):
    # Takes a list and returns it as integer
    if numList != []:
        s = ''.join(map(str, numList))
        return int(s)
        
def percentile(N, P):
    """
    Find the percentile of a list of values

    @parameter N - A list of values.  N must be sorted.
    @parameter P - A float value from 0.0 to 1.0

    @return - The percentile of the values.
    """
    N.sort()
    n = int(round(P * len(N) + 0.5))
    return N[n-1]
    
def baseconvert(number, todigits, fromdigits = "0123456789"):
    """ converts a "number" between two bases of arbitrary digits

    The input number is assumed to be a string of digits from the
    fromdigits string (which is in order of smallest to largest
    digit). The return value is a string of elements from todigits
    (ordered in the same way). The input and output bases are
    determined from the lengths of the digit strings. Negative 
    signs are passed through.
    """
    if str(number)[0]=='-':
        number = str(number)[1:]
        neg = 1
    else:
        neg = 0

    # make an integer out of the number
    x = long(0)
    for digit in str(number):
        x = x*len(fromdigits) + fromdigits.index(digit)
    
    # create the result in base 'len(todigits)'
    res = ""
    while x > 0:
        digit = x % len(todigits)
        res = todigits[digit] + res
        x /= len(todigits)
    if neg:
        res = "-"+res
    if number is 0:
        res = "0"
    return res

def product(vv):
   return(reduce(lambda x, y: x*y, vv))

def generate_first_code(toprank, level):
    """ 1 is lowest rank """
    ll = (toprank - level) + 1
    out = []
    for i in range(ll):
        out.append(10**i)
    return sum(out)

def generate_base_codes(toprank, unitsize):
    list_codes = []
    start = generate_first_code(toprank, 1)
    pop_rank = unitsize**toprank
        
    for i in range(pop_rank):
        id = baseconvert(i, [str(j) for j in range(unitsize)])
        list_codes.append(start + int(id))
    return(list_codes)

def populate_army(topage, toprank, unitsize):
    """ Generates army of size N (at the base level) with K levels. 
        Each unit being of size U
    """
    army = []
    fill_rank = 1
    while fill_rank <= toprank:
        
        start = generate_first_code(toprank, fill_rank)
        pop_rank = unitsize**(toprank - fill_rank + 1)
        
        for i in range(pop_rank):
            id = baseconvert(i, [str(j) for j in range(unitsize)])
            ## Senior officers tend to be older
            refbase = (toprank + 1) - fill_rank
            refscale = topage - 1
            age = int(round(np.random.beta(fill_rank, refbase, 1) * refscale + 1))
            seniority = random.choice(range(min(age, fill_rank), 
                                            max(age, fill_rank) + 1))
            quality = random.uniform(0, 1)
            ## Put everything together
            captain = Soldier(fill_rank, 
                              seniority,
                              age,
                              quality, 
                              random.uniform(-1, 1),
                              start + int(id))
            army.append(captain)
        pop_rank = pop_rank/unitsize
        fill_rank += 1
    return army

def flatten(x):
    ## http://stackoverflow.com/questions/2158395/flatten-an-irregular-list-of-lists-in-python
    if isinstance(x, collections.Iterable):
        return [a for i in x for a in flatten(i)]
    else:
        return [x]

def reverse_lookup(mydict, value):
    tmp = dict((v,k) for k, v in mydict.iteritems())
    return tmp[value]

def find_subordinates(rank):
    subs_list = [rank]
    if rank is 1:
        return subs_list
    else:
        unit = str(soldier.unit)
        children = [str(unit) + str((i % self.unit_size) + 1) \
                    for i in range(self.unit_size)]
        ids = [i.unit for i in self.soldiers]
        for i in children:
            idx = ids.index(int(i))
            subs = self.find_subordinates(self.soldiers[idx])
            subs_list.append(subs)
            return subs_list
            
def get_subordinate(self, soldier):
    subs = self.find_subordinates(soldier)
    fsubs = flatten(subs)
    fsubs.pop(0)
    return fsubs

def generate_army_codes(toprank, unitsize):
    basic_level = reference = generate_base_codes(toprank, unitsize)
    for rank in range(1, toprank):
        reference = set([i/10 for i in reference])
        basic_level.append(list(reference))
    return flatten(basic_level)
