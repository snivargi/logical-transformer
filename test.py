bool_IF_result0 = False
if  False == bool("False"):
    if False == bool(False == bool(True)):
        bool_IF_result0 = True
        print (True)  
if bool_IF_result0 is False:
    print (False) 
print (True)
print (0)
bool_IF_result0 = False
if 1:
    if 2:
        bool_IF_result0 = True
        print ('Hello, world!')
        bool_IF_result4 = False
        if 0:
            bool_IF_result4 = True
            print ('Bye, world!')
def comp_msg(x,y):
    bool_IF_result4 = False
    if x > 0:
        if y > 0:
            bool_IF_result4 = True
            print ('Both numbers are positive')
    if bool_IF_result4 is False:
        print ('At least one number is not positive')
comp_msg(3,7)
comp_msg(-1, 2)
a = 3
b = 2
c = 1
bool_IF_result0 = False
if a > b:
    if a > c:
        bool_IF_result0 = True
        print (f'{a} is the largest')
if bool_IF_result0 is False:
    if b > a:
        if b > c:
            bool_IF_result0 = True
            print (f'{b} is the largest')
print (True)
print (1)
bool_IF_result0 = False
if True:
    bool_IF_result0 = True
    print ('Hello, world!')
def temp_msg(temp):
    bool_IF_result4 = False
    if temp < 0:
        bool_IF_result4 = True
        print ('Temperature is extreme')
    if bool_IF_result4 is False:
        if temp > 30:
            bool_IF_result4 = True
            print ('Temperature is extreme')
    if bool_IF_result4 is False:
        print ('Temperature is moderate')
temp_msg(-1)		
temp_msg(10)
def marks_msg(marks):
    bool_IF_result4 = False
    if marks < 50:
        bool_IF_result4 = True
        print ('Fail or Invalid marks')
    if bool_IF_result4 is False:
        if marks > 100:
            bool_IF_result4 = True
            print ('Fail or Invalid marks')
    if bool_IF_result4 is False:
        print ('Pass')
marks_msg(110)		
marks_msg(70)
def even_odd(number):
    bool_IF_result4 = False
    if False == bool(number % 2 == 0):
        bool_IF_result4 = True
        print (f'{number} is odd')
    if bool_IF_result4 is False:
        print (f'{number} is even')
even_odd(3)
even_odd(4)
def str_msg(string):
    bool_IF_result4 = False
    if False == bool(string):
        bool_IF_result4 = True
        print ('String is empty')
    if bool_IF_result4 is False:
        print ('String is not empty')
str_msg('')
str_msg(' a ')
bool_IF_result0 = False
if False == bool(True==False):
    if False == bool(0 == 1):
        bool_IF_result0 = True
        print ('True is not False')
        bool_IF_result4 = False
        if 0:
            bool_IF_result4 = True
            print ("Something's wrong!")
bool_IF_result0 = False
if False == bool(True==False):
    bool_IF_result0 = True
    print ('True!=False')
counter = 0
while False == bool((counter >= 3 and counter <= 7)):
    print(counter)
    counter += 1
a = 3
print (a)
bool_IF_result0 = False
if 2:
    bool_IF_result0 = True
    print ('Operator precedence test passed')
if bool_IF_result0 is False:
    print ('Operator precedence test failed')
print (True)