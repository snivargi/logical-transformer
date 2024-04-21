import collections
from operator import contains

def _isItemInIter(item, collection, check=True):
    found = False
    iterable = iter(collection)
    while True:
        try:
            iterator = next(iterable)
            if item == iterator:
                found = True
                break
        except StopIteration:
            break
    if found is False:
        try:
            iterable = iter(collection.split())
            while True:
                iterator = next(iterable)
                if item == iterator:
                    found = True
                    break
        except:
            pass
    return found if check else not found
a = b = c = ''
_boolIf0 = False
if a:
    if c:
        _boolIf0 = True
if _boolIf0 is False:
    if b:
        if c:
            _boolIf0 = True
if _boolIf0 is False:
    _boolIf0 = True
    print('Not test passed')
if _boolIf0 is False:
    print('Not test failed')
_boolIf0 = False
if 'False':
    _boolIf0 = True
    print(True)
    if isinstance(a, str):
        if 1:
            print('Inner if test executed')
if _boolIf0 is False:
    print(False)
print(True)
print('<Node pruned>')
print(-1073741824.0)
print(1)
print(bool(a))
print(iter('i love python'.split()))
if _isItemInIter(2, [1, 2, 3], True):
    if _isItemInIter('love', 'i love python', True):
        print('word test passed')
iterable0 = iter(range(2))
while True:
    try:
        i = next(iterable0)
    except StopIteration:
        break
    iterable4 = iter(range(2))
    while True:
        try:
            j = next(iterable4)
        except StopIteration:
            break
        if _isItemInIter('x', 'i love python', False):
            print(f'[{i},{j}]')
if False == bool(a):
    print('a is blank')
counter = 0
while False == bool(counter >= 3 and counter <= 7):
    print(counter)
    counter += 1
print(_isItemInIter(a, 'i love python', True))