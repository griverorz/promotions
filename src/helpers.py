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

def flatten(x):
    ## stackoverflow.com/questions/2158395/flatten-an-irregular-list-of-lists-in-python
    if isinstance(x, collections.Iterable):
        return [a for i in x for a in flatten(i)]
    else:
        return [x]

def generate_army_codes(toprank, unitsize):
    basic_level = reference = generate_base_codes(toprank, unitsize)
    for rank in range(1, toprank):
        reference = set([i/10 for i in reference])
        basic_level.append(list(reference))
    return flatten(basic_level)

def all_indices(value, qlist):
    indices = []
    idx = -1
    while True:
        try:
            idx = qlist.index(value, idx+1)
            indices.append(idx)
        except ValueError:
            break
    return indices

def herfindahl(value):
    shares = sum([(float(j)/sum(value))**2 for i,j in enumerate(value)])
    norm_shares = (shares - 1./len(value))/(1 - 1./len(value))
    return norm_shares
