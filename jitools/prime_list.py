from itertools import compress

#adapted from: https://stackoverflow.com/questions/31843844/how-to-calculate-the-exponents-of-prime-factors-for-a-given-number
#used to create list of primes, and to factor numbers into primes with exponents
class PrimeList():

    def __init__(self, max_val):
        self.primes = self._init_primes(max_val)
        self.extend(len(self.primes))

    def check(self,n):
        n = int(n)
        limit = int(math.sqrt(n))
        return all((n%p for p in self.primes if p<=limit))

    def extend(self,n):
        n = int(n)
        nextnum = self.primes[-1]
        while(self.primes[-1]<n):
            nextnum += 2
            if self.check(nextnum):
                self.primes.append(nextnum)

    def factors(self, n):
        n = int(n)
        x = n
        fact = dict()
        for p in self.primes:
            if p>x:
                break
            while x%p==0:
                x = x/p
                fact[p]=fact.get(p,0)+1
        if x>1:
            e = x if x!=n else int(math.sqrt(n))
            self.extend(e)
            return self.factors(n)
        return sorted(fact.items())

    def is_prime(self, n):
        n = int(n)
        self.extend(int(math.sqrt(n)))
        return self.check(n)

        #taken from https://stackoverflow.com/questions/2068372/fastest-way-to-list-all-primes-below-n/3035188#3035188
    def _init_primes(self, max_val):
        """ Returns a list of primes < n for n > 2 """
        sieve = bytearray([True]) * (max_val//2+1)
        for i in range(1,int(max_val**0.5)//2+1):
            if sieve[i]:
                sieve[2*i*(i+1)::2*i+1] = bytearray((max_val//2-2*i*(i+1))//(2*i+1)+1)
        return [2,*compress(range(3,max_val,2), sieve[1:])]