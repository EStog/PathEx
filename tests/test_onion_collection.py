import random
from pathex.adts.containers.onion_collection import EmptyOnionCollection, NonemptyOnionCollection, from_iterable

def test_adition():
    random.seed()
    c = EmptyOnionCollection()
    l = []
    numbers = list(range(100))
    for _ in range(100):
        r = random.choice(numbers)
        c = NonemptyOnionCollection(c, r)
        l.append(r)
    assert list(c) == l
    c1 = from_iterable(l)
    assert c == c1
    assert hash(c) == hash(c1)

if __name__ == '__main__':
    test_adition()
