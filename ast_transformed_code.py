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