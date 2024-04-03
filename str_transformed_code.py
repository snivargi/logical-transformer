x=50
bool_IF_result0 = False
if x > 100:
    bool_IF_result0 = True
    print ("if1")
if bool_IF_result0 is False:
    if x > 30:
        if x > 70:
            bool_IF_result0 = True
            print ("if1")
        if bool_IF_result0 is False:
            if x < 60:
                bool_IF_result0 = True
                print ("if1")
if bool_IF_result0 is False:
    if x > 40:
        bool_IF_result0 = True
        print ("elif1")
if bool_IF_result0 is False:
    if (x < 40):
        bool_IF_result0 = True
        bool_IF_result4 = False
        if x > 30:
            if x <40:
                bool_IF_result4 = True
                print ("elif2if2")    
if bool_IF_result0 is False:
    print ("else1")
list1 = ["a", "b" , "c"]
list2 = [1, 2, 3]
iterable0 = iter(list2)
while True:
    try:
        x = next(iterable0)
    except StopIteration:
        break    
    list1.append(x)
print(list1)  
iterable1 = iter(range(2,5))
while True:
    try:
        i = next(iterable1)
    except StopIteration:
        break    
    print(str(i))
likes = {"color": "blue", "fruit": "apple", "pet": "dog"}
iterable2 = iter(likes.items())
while True:
    try:
        item = next(iterable2)
    except StopIteration:
        break    
    print("Item: " + str(item))
    print("Item type: " + str(type(item)))
iterable3 = iter(likes.keys())
while True:
    try:
        key = next(iterable3)
    except StopIteration:
        break    
    print("Key: " + key)
iterable4 = iter(likes.values())
while True:
    try:
        value = next(iterable4)
    except StopIteration:
        break    
    print("Value: " + value)
fruits = {"apple": 0.40, "orange": 0.35, "banana": 0.25}
iterable5 = iter(fruits.items())
while True:
    try:
        fruit, price = next(iterable5)
    except StopIteration:
        break    
    fruits[fruit] = round(price * 0.9, 2)
print (fruits)
found = False
iterable = iter('i love python')
while True:
    try:
        iterator = next(iterable)
        bool_IF_result8 = False
        if 'love' == iterator:
            bool_IF_result8 = True
            found = True
            break
    except StopIteration:
        break
bool_IF_result0 = False
if found is False:
    bool_IF_result0 = True
    try:
        iterable = iter('i love python'.split())    
        while True:    
            iterator = next(iterable)
            bool_IF_result12 = False
            if 'love' == iterator:
                bool_IF_result12 = True
                found = True
                break
    except:
        pass
bool_IF_result0 = False
if  found is True:            
    bool_IF_result0 = True
    print ('word test passed')
found = False
iterable = iter(list1)
while True:
    try:
        iterator = next(iterable)
        bool_IF_result8 = False
        if 'a' == iterator:
            bool_IF_result8 = True
            found = True
            break
    except StopIteration:
        break
bool_IF_result0 = False
if found is False:
    bool_IF_result0 = True
    try:
        iterable = iter(list1.split())    
        while True:    
            iterator = next(iterable)
            bool_IF_result12 = False
            if 'a' == iterator:
                bool_IF_result12 = True
                found = True
                break
    except:
        pass
bool_IF_result0 = False
if  found is True:            
    bool_IF_result0 = True
    print ('a exists!')
found = False
iterable = iter(list1)
while True:
    try:
        iterator = next(iterable)
        bool_IF_result8 = False
        if'x' == iterator:
            bool_IF_result8 = True
            found = True
            break
    except StopIteration:
        break
bool_IF_result0 = False
if found is False:
    bool_IF_result0 = True
    try:
        iterable = iter(list1.split())    
        while True:    
            iterator = next(iterable)
            bool_IF_result12 = False
            if'x' == iterator:
                bool_IF_result12 = True
                found = True
                break
    except:
        pass
bool_IF_result0 = False
if  found is False:            
    bool_IF_result0 = True
    print ('x does not exist!')    
found = False
iterable = iter(list1)
while True:
    try:
        iterator = next(iterable)
        bool_IF_result8 = False
        if 'z'== iterator:
            bool_IF_result8 = True
            found = True
            break
    except StopIteration:
        break
bool_IF_result0 = False
if found is False:
    bool_IF_result0 = True
    try:
        iterable = iter(list1.split())    
        while True:    
            iterator = next(iterable)
            bool_IF_result12 = False
            if 'z'== iterator:
                bool_IF_result12 = True
                found = True
                break
    except:
        pass
bool_IF_result0 = False
if  found is False:            
    bool_IF_result0 = True
    print ('z does not exist!')