import pytest
from jitools import prime_list as pl


class TestInitPrimes:
    def test_first_six_primes(self):
        p = pl.PrimeList(20)
        assert p.primes[:6] == [2, 3, 5, 7, 11, 13]

    def test_primes_below_50(self):
        p = pl.PrimeList(50)
        assert p.primes == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

    def test_all_entries_are_prime(self):
        p = pl.PrimeList(100)
        for n in p.primes:
            assert p.is_prime(n), f"{n} should be prime"


class TestIsPrime:
    @pytest.mark.parametrize("n", [2, 3, 5, 7, 11, 13, 97])
    def test_known_primes(self, n):
        p = pl.PrimeList(100)
        assert p.is_prime(n)

    @pytest.mark.parametrize("n", [1, 4, 6, 8, 9, 10, 15, 25, 91])
    def test_known_composites(self, n):
        p = pl.PrimeList(100)
        assert not p.is_prime(n)


class TestFactors:
    @pytest.mark.parametrize("n,expected", [
        (1,          []),
        (2,          [(2, 1)]),
        (7,          [(7, 1)]),
        (12,         [(2, 2), (3, 1)]),
        (60,         [(2, 2), (3, 1), (5, 1)]),
        (2**3 * 3**2, [(2, 3), (3, 2)]),
        (2 * 3 * 5 * 7, [(2, 1), (3, 1), (5, 1), (7, 1)]),
    ])
    def test_factorization(self, n, expected):
        p = pl.PrimeList(100)
        assert p.factors(n) == expected

    def test_factors_large_prime(self):
        p = pl.PrimeList(100)
        assert p.factors(97) == [(97, 1)]

    def test_factors_roundtrip(self):
        p = pl.PrimeList(100)
        n = 2**4 * 3**2 * 5 * 7**3
        factors = p.factors(n)
        product = 1
        for prime, exp in factors:
            product *= prime ** exp
        assert product == n
