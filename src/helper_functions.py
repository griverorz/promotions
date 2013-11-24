#! /usr/bin/python

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
