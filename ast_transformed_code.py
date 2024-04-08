a = ''
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
_found = False
iterable = iter([1, 2, 3])
while True:
    try:
        iterator = next(iterable)
        if 2 == iterator:
            _found = True
            break
    except StopIteration:
        break
if _found is False:
    try:
        iterable = iter([1, 2, 3].split())
        while True:
            iterator = next(iterable)
            if 2 == iterator:
                _found = True
                break
    except:
        pass
if _found is True:
    _found = False
    iterable = iter('i love python')
    while True:
        try:
            iterator = next(iterable)
            if 'love' == iterator:
                _found = True
                break
        except StopIteration:
            break
    if _found is False:
        try:
            iterable = iter('i love python'.split())
            while True:
                iterator = next(iterable)
                if 'love' == iterator:
                    _found = True
                    break
        except:
            pass
    if _found is True:
        print('word test passed')