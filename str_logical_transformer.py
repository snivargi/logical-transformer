import re
import textwrap as tw

OPERATORS = ('**',('*', '/', '//', '%'),('+', '-' ),('==', '!=', '>', '>=', '<', '<='),'not','and','or') #Tuples of Boolean and Arithmetic operators in order of precedence 
OPER_DICT = {} #Dictionary of operators and their precedence generated dynamically by set_oper_dict()

REGEX_OPER = r'''(\s*(\*+|\/+|%|\+|-|==|!=|>|>=|<|<=|not|and|or|$)\s*)'''#Regex to match a Boolean or Arithmetic operator in an expression
#REGEX_OPER ='''(\s*([^\w.()[]"', ]+|or|and|not|$)\s*)''' #Shorter? regex to match a Boolean or Arithmetic operator in an expression

REGEX_EXPR = r'''(.*(\b|[ \d)])(\*+|\/+|%|\+|-|==|!=|>|>=|<|<=|not|and|or)[(\d ].*)''' #Regex to match assignment target or expression. e.g. print (2 + 4) ; a = (2 +4)
#REGEX_EXPR = '''(.*([ \d)][^\w.()[]"', ]+|or|and|not)[(\d ].+?)''' #Shorter? Regex to match assignment target or expression. e.g. print (2 + 4) ; a = (2 +4)
BLOCKS = ('if','for') #Keywords indicating starting (sub)?blocks
CONDITIONS = ('if','elif','else')

REGEX_WORD = "\w+"
REGEX_IF = "^(\s*)if\s+"
REGEX_ELIF = "^(\s*)elif\s+(.+):"
REGEX_ELSE =  "^(\s*)else\s*:"
REGEX_IF_IN = "^(\s*)if\s+(.+)\sin\s(.+)\s*:"
REGEX_FOR_IN = "^(\s*)for\s+(.+)\s+in\s+(.+)\s*:"
REGEX_VAR_ASSIGNMENT = "(\w+)\s*=\s*(.)"
VAR_TYPES = ('(','[','{','"',"'") #Tuple, List, Dictionary, String
IF_RESULT_COUNTER = 'L' #Use L for (indentation)Level, B for Block(identifier)


ITERATION_CODE = """
iterable = iter(collection)
while True:
    try:
        iterator = next(iterable)
    except StopIteration:
        break    
"""

ITERATION_IF_CODE = """
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
    except:
        iterable = iter(collection)
    while True:
        try:
            iterator = next(iterable)
            if item == iterator:
                found = True
                break
        except StopIteration:
            break
if  found is True:           
"""

block_num = 0
code1= """
if  not (1 or True) and not(False or 0):
    print (True)  
else:
    print (False) 
#===========AND========================================
print(True and True)
#True

print(1 and 2 and 0)
#0

if 1 and 2:
    print ('Hello, world!')
    if 0 and False:
        print ('Bye, world!')
#Hello, world!

def comp_msg(x,y):
    if x > 0 and y > 0:
        print ('Both numbers are positive')
    else:
        print ('At least one number is not positive')
comp_msg(3,7)
comp_msg(-1, 2)
#Both numbers are positive
#At least one number is not positive

a = 3
b = 2
c = 1
if a > b and a > c:
	print (f'{a} is the largest')
elif b > a and b > c:
	print (f'{b} is the largest')
#3 is the largest

#===========OR========================================
print(True or True)
#True

print(1 or 2 and not not 0)
#1

if True or False or False or True:
    print ('Hello, world!')
#Hello, world!

def temp_msg(temp):
    if temp < 0 or temp > 30:
        print ('Temperature is extreme')
    else:	
        print ('Temperature is moderate')
temp_msg(-1)		
temp_msg(10)

def marks_msg(marks):
    if marks < 50 or marks > 100:
        print ('Fail or Invalid marks')
    else:
        print ('Pass')
marks_msg(110)		
marks_msg(70)

#===========NOT========================================

def even_odd(number):
    if not number % 2 == 0:
        print (f'{number} is odd')
    else:
        print (f'{number} is even')
even_odd(3)
even_odd(4)
#3 is odd
#4 is even

def str_msg(string):
    if not string:
        print ('String is empty')
    else:
        print ('String is not empty')
str_msg('')
str_msg(' a ')
#String is empty
#String is not empty


#===========EXTRA NOT========================================
if not (True==False) and not (0 == 1):
    print ('True is not False')
    if 0 and False:
        print ("Something's wrong!")
#Hello, world!

if not  True==False :
    print ('True!=False')

counter = 0
while not(counter >= 3 and counter <= 7):
    print(counter)
    counter += 1
#2

a = (3 or 2 and 1)
print (a)
#3

if 2 or 1 and not True or (not 0):
    print ('Operator precedence test passed')
else:
    print ('Operator precedence test failed')
print (2 and not(0==1 ) )
"""
code2 = """
x=50
if (x > 100 or (x > 30 and (x > 70 or x < 60))):
    print ("if1")
elif x > 40:        
    print ("elif1")
elif (x < 40):
    if (x > 30 and x <40):  
        print ("elif2if2")    
else:    
    print ("else1")
list1 = ["a", "b" , "c"]
list2 = [1, 2, 3]

for x in list2:
    list1.append(x)

print(list1)  

for i in range(2,5):
    print(str(i))

likes = {"color": "blue", "fruit": "apple", "pet": "dog"}
for item in likes.items():
    print("Item: " + str(item))
    print("Item type: " + str(type(item)))

for key in likes.keys():
    print("Key: " + key)

for value in likes.values():
    print("Value: " + value)

fruits = {"apple": 0.40, "orange": 0.35, "banana": 0.25}

for fruit, price in fruits.items():
    fruits[fruit] = round(price * 0.9, 2)
print (fruits)

if 'love' in 'i love python':
    print ('word test passed')

if 'a' in list1:
    print ('a exists!')

if not 'x' in list1:
    print ('x does not exist!')    

if ('z' not in list1):
    print ('z does not exist!')
"""
code3="""
print (- (2 + 3 / .5) ** 10)
a= (not "False")
print (a)
print (not "False") 
print ( 3 or 2 and 1) 
print ( (not 0 ) + 1)
print ( not (0 + 1))
print ( not 0 + 1)
print (- 8 + 5 - 2*3)
print (- 8 + 5 - (2+3))
print ( 2 and (3 + 2 )* 6 or 20)
print ( 2 and (3 * 2 ) + (6 - 3) or 20)
print (- (2+3))
print (- (2 + 3 / .5) ** 10)
print ( 3 or 2 and 1) 
print (1 or 2 and not not 0) 
print (not (True==False) and not (0 == 1)) 
print (--1.2 * 10) 
print (++1.2 * 10)     
print (-(-4) ** 2)
print (-4 ** 2)
print (100 - (-6 + 4 ** 2))
print (100 - (-6 + 4) ** 2)
"""
def set_oper_dict():
    '''
    Populates a dictionary of operators where the key is the operator and value is the precedence order (0 is first/hightest).
    e.g.   {
            '**':0,
            '*':1, '/':1, '//':1, '%':1, 
            '+':2, '-':2, 
            '==':3, '!=':3, '>':3, '>=':3, '<':3, '<=':3,
            'not':4, 
            'and':5, 
            'or':6
            }
    '''
    global OPER_DICT #Use global variable because we only want to set this once - at the start
    for i in range (len(OPERATORS)):        
        ops = OPERATORS[i]
        if(isinstance(ops, str)):
            OPER_DICT[ops] = i
        else:    
            for j in range(len(ops)):
                oper = OPERATORS[i][j]
                OPER_DICT[oper] = i


def get_expr_within_brackets(s): 
    '''
    Takes in a string and returns the substring within the first pair () of brackets.
    e.g. '2 * (3 + (4 - 2))' -> '3 + (4 - 2)'
    '''
    bracket_cnt = 0    
    expr = ''
    opened = False
    
    for char in (s):
        if char == '(':
            opened = True
            bracket_cnt += 1
        elif char == ')':   
            bracket_cnt -= 1  
        if opened:               
            expr = f'{expr}{char}' 
            if bracket_cnt == 0: #We have the substring
                break
    expr = expr[1:-1]
    return expr                

def get_next_expr(prev_oper, expr):
    '''
    Takes in an expression and returns the next part of the expression to be evaluated respecting operator precedence. 
    This is with respect to a given operator.  
    e.g. ('1 and not True or (not 0)' , 'not') returns '1 and not True' as not > or
    ''' 
    oper = '' #operator(s) in this expression   
    prev_oper = prev_oper.strip() #Previous operator
    part = expr
    part_expr = ''
    next_expr = ''     
    while True: #Keep processing parts of the expression until none left        
        match_brackets = re.match('(\s*(not\s*)?)\(', part) #Bracketed expression                              
        match_expr = re.match(f'(\s*.+?){REGEX_OPER}', part)  #Non-bracketed expression      
        if match_brackets: #expression within brackets                                   
            part_expr = get_expr_within_brackets(part)
            next_expr += f'{match_brackets.group(1)}({part_expr})'
            part = part[part.find(part_expr)+len(part_expr)+1:] #Remaining part is anything after the first set of brackets in original part           
            match_oper  = re.match(REGEX_OPER.replace('|$',''), part) #Match operator after bracketed expression
            if match_oper:
                oper = match_oper.group(0)                
                if oper and (operator_precedence (oper) < operator_precedence (prev_oper)): #If operator has higher precedence to the previous one (<= has the same overall execution result but generated code doesn't match a generated AST)
                    next_expr += oper #Add operator to the next expression
                    part = part[match_oper.end(0):] #Remaining part is anything after the operator
                else:
                    part='' #We're done with the grouping   
            else:                
                part='' #We're done with the grouping           
        elif match_expr: #expression NOT within brackets                                   
            part_expr = match_expr.group(1)
            next_expr += part_expr
            oper = match_expr.group(2)                        
            if oper and (operator_precedence (oper) < operator_precedence (prev_oper)): #If operator has higher precedence to the previous one (<= has the same overall execution result but generated code doesn't match a generated AST)
                next_expr += oper
                part = part[match_expr.end(0):] #Remaining part is anything after the operator
            else:
                part='' #We're done with the grouping                 
              
        if (part.strip()==''):
            break         
    return next_expr   

def prep_expr(expr, if_expr = False): 
    '''
    Pre-process an expression by removing unnecessary items.    
    '''
    mod_expr = expr
    if if_expr:
        mod_expr = mod_expr if('if' in mod_expr ) else f'if {mod_expr}' #Add an "if" at the start unless one exists    
    mod_expr = mod_expr.replace(' not not ', ' ') #'not not' is the same as ''
    mod_expr = mod_expr.replace('el','') #Change any elif to if
    mod_expr = (re.sub(':\s*$', '', mod_expr)) #Replace any trailing ':' as we'll add it in for individual expressions
    mod_expr = mod_expr.strip() #Get rid of the leading and trailing spaces as indentation will be handled during merge   
    return mod_expr     

def normalise_num_str(s): 
    '''
    Remove unnecessary characters from a string that represents a numeric value.
    '''
    s = s.replace(' ','')
    s= re.sub(r'([^\w.])\1', '', s) #Handle things like '--1.2', which should give 1.2    
    s= re.sub('\+\-|\-\+', '-', s) #Handle things like '+-1.2' or '-+1.2', which should give -1.2    
    return s

def get_number(s):  
    '''
    Returns the number within quotes as its primitive numeric datatype  (.e.g '1.5' -> 1.5)
    If there is no number in the string, returns the string itself
    '''
    s =  normalise_num_str(s)    
    try:
        return  int(s)        
    except ValueError:
        try:
            return float(s)
        except ValueError:            
            return s

    
def get_typed_val(s): 
    '''
    Returns a string value as its primitive datatype - bool, int, float, str   
    '''
    if isinstance(s, str):
        s = s.replace(' ','')
        val = None
        if s == 'True':
            val = True
        elif s == 'False':
            val = False   
        else:
            val = get_number(s)    
    else:
        val = s        
    return val

def eval_bin_bool_op (loper, oper, roper = []): 
    '''
    Evaluates a binary or boolean expression
    '''
    result = 0    
    left = get_typed_val(loper[0]) if loper else None
    right = get_typed_val(roper[0]) if roper else None  
    oper = oper.strip()
    if oper == '+':
        if(right is None):
            result = + left #Unary addition
        else:
            result = left + right #Binary addition            
    elif oper == '-':
        if(right is None):
            result = - left #Unary subtraction
        else:
            result = left - right #Binary subtraction
    elif oper == '*':
        result = left * right    
    elif oper == '/':
        result = left / right            
    elif oper == '//':
        result = left // right
    elif oper == '**':        
        result = (left) ** right    #Handles "negative" left operand. e.g. (-4) ** 2 = 8         
    elif oper == '%':
        result = left % right
    elif oper == 'and':
        result = left and right
    elif oper == 'or':
        result = left or right  
    elif oper == '==':
        result = left == right     
    elif oper == '!=':
        result = left != right     
    elif oper == '>':
        result = left > right     
    elif oper == '>=':
        result = left >= right     
    elif oper == '<':
        result = left < right     
    elif oper == '<=':
        result = left <= right                         
    elif oper == 'not':
        result = not left
    return result          

def operator_precedence (oper): 
    '''
    Returns a precedence number for an operator from the OPERATORS dictionary - 0 is highest
    e.g. '**' -> 0, 'or' -> 6
    '''
    prec_num = OPER_DICT[oper.strip()]
    return prec_num

def merge_and(loper, roper, level, block): 
    '''
    Join/merge left and right operands with the AND operator    
    '''
    if(len(loper)==1): #Base case
        if(loper[0].strip()=='pass'):
            return loper
        else:    
            match = re.search('^\s*', loper[0])  #find the first "word" in the line         
            if match:
                spacing = match.group()            
                return  loper + indent_code(roper, f'{spacing}    ') #We merge the right operand for this block and return  
    
    
    main_block_processed_lines = [] #All processed lines at current level
    sub_block = -1
    sub_block_orig_lines =[]    
    new_sub_block = False #No new sub-blocks initially
    sub_block_level = None
    for line in loper:
        match = re.search(REGEX_WORD, line)  #find the first "word" in the line 
        indent_level = 0         
        if match:
            indent_level = match.start()
            if (indent_level > level): # and match.group() in ('if', 'elif')
                if (new_sub_block is False): #New sub block 
                    new_sub_block = True #We now have a new sub-block starting
                    sub_block_orig_lines = []
                    sub_block += 1 #Increment the sub-block number
                    sub_block_level = indent_level
                    sub_block_orig_lines.append(line) #Add current line to the new sub-block 
                else: #We have an existing sub-block that needs to be processed
                    sub_block_orig_lines.append(line) #Add current line to the new sub-block 
            else:
                if (new_sub_block is False and len(main_block_processed_lines)>0): #We have a leaf node
                    #We have an unprocessed sub-block, so let's process the sub-block here and merge with the main block
                    sub_block_orig_lines = [main_block_processed_lines.pop()]
                    sub_block_processed_lines = merge_and (sub_block_orig_lines, roper, sub_block_level, str(block) + str(sub_block))
                    main_block_processed_lines +=  sub_block_processed_lines                              
                elif (new_sub_block is True): #We have an existing sub-block to be processed
                    sub_block_processed_lines = merge_and (sub_block_orig_lines, roper, sub_block_level, str(block) + str(sub_block))
                    main_block_processed_lines +=  sub_block_processed_lines                  
                    new_sub_block = False                    
                main_block_processed_lines.append(line) #Add current line to the main block    
    
    if (new_sub_block is True): #Pending unprocessed sub-block
        #We have an unprocessed sub-block, so let's process the sub-block here and merge with the main block
        sub_block_processed_lines = merge_and (sub_block_orig_lines, roper, sub_block_level, str(block) + str(sub_block))
        main_block_processed_lines +=  sub_block_processed_lines 
    else:
        sub_block_orig_lines = [main_block_processed_lines.pop()]
        sub_block_processed_lines = merge_and (sub_block_orig_lines, roper, sub_block_level, str(block) + str(sub_block))
        main_block_processed_lines +=  sub_block_processed_lines     

    return   main_block_processed_lines
    

def merge_or(loper, roper, level, block):
    '''
    Join/merge left and right operands with the OR operator    
    '''
    boolif = f'bool_IF_result{block}' if IF_RESULT_COUNTER == 'B' else f'bool_IF_result{level}'
    boolifLine = [f'if {boolif} is False:']
    if len(roper)>0:
        roper = boolifLine + indent_code(roper, '    ')
    else:
        roper = boolifLine    
    return  loper + roper

def merge_not(lroper, level, block):
    '''
    Wrap an operand within the  NOT operator
    '''
    match = re.search('^\s*', lroper[-1])  #find the first "word" in the last line         
    if match:
        spacing = match.group()        
    lroper.append(f'{spacing}    pass') #If the condition is True, do nothing (pass)
    lroper = merge_or(lroper, [], level, block) #Add provision to execute where condition is False
    return lroper

def merge(loper, roper, oper, level, block):
    '''
    Merge 2 operands (lists) with optional Boolean operator (and, or)
    '''
    oper = oper.strip()
    merged_code = [] #This will be a list
    if 'and' in oper:
        merged_code = merge_and(loper, roper, 0, 0)
    elif 'or' in oper:
        merged_code = merge_or(loper, roper, level, block)
    else:    
        merged_code = loper + roper
    return merged_code

def indent_code(lines, spacing): 
    '''
    Applies uniform indent to all lines equal to 'spacing'
    '''
    processed_lines = []    
    linestr = '\n'.join(lines)
    processed_lines = tw.indent(linestr, spacing).split('\n')  
    return processed_lines

def dedent_code(lines): #Applies uniform dedent to all lines
    '''
    Applies uniform dedent (remove common spacing) to all lines
    '''
    processed_lines = []
    linestr = '\n'.join(lines)
    processed_lines = tw.dedent(linestr).split('\n')  
    return processed_lines

def is_valid_expr(expr): 
    '''
    Checks if an expression is 'valid' for solving by our parse_expr function
    If there is a "bare" word, i.e. a non-bool-keyword without quotes, the expression is invalid for our purposes
    '''
    tokens = expr.split()
    valid = True
    found_or_and = False
    for token in tokens:
        #if not token[0] in ("'", '"') and not re.match('''(and|or|not|True|False|None|==|[\d()]+)''', token): #(token in ('and', 'or', 'not', 'True', 'False', 'None', '==') or token.isdigit()):
        if not token[0] in ("'", '"') and (not re.match('''(and|or|not|True|False|None|==|\d+\.?|[^\w]+)''', token) or ',' in token):     
            valid = False
            break
        else:
            if (not found_or_and and re.match('(or|and)\(?', token)):
                found_or_and = True #We need to have an or/and in the expression
    return valid

def replace_not(expr):
    '''
    Replaces the 'not' keyword without changing the meaning of the expression
    '''
    expr = str(expr).strip()    
    #Replace not
    newexpr = (re.sub(r'\bnot\b', 'False == ', expr)) #'not' is the same as 'False =='    
    return newexpr

def match_bool_output (line, useEvalResult = True): 
    '''
    Returns lines that ensure that the result of boolean expressions is unchanged while replacing and/or/not
    '''
    line = str(line)
    lines = []  
    line = line.replace(' not not ', ' ') #'not not' is the same as ''
    
    #match = re.match('''(\s*)(\w+)\s*\(([^'"]+ (or|and|not) .+)\)$''', line)  #Non-assignment expression with and|or|not within brackets e.g.print(1 and 2 and 0)    
    #match = re.match('''(\s*)(\w+)\s*\(([^'"]+)\)\s*$''', line)  #Non-assignment boolean and/or arithmetic expression  e.g.print(1 and 2 and 0)    
    match = re.match(f'''(\s*)(\w+)\s*\({REGEX_EXPR}\)\s*$''', line) #Non-assignment expression

    #match_assign = re.match('''(\s*)(\w+)\s?=\s?([^'"]+ (or|and|not) .+)''', line) #Assignment lines with or/and/not
    #match_assign = re.match('''(\s*)(\w+)\s?=\s?([^'"]+)\s*$''', line) #Assignment line with boolean and/or arithmetic expression 
    match_assign = re.match(f'''(\s*)(\w+)\s*=\s*\(?{REGEX_EXPR}\)?\s*$''', line) #Assignment line

    match_while = re.match('(\s*while\s+not\s*)(.+):\s*', line) #While not line
    try:
        if match:                    
            spacing = match.group(1)
            func = match.group(2)
            expr = match.group(3).strip()             
            ##Evaluate the expression at run-time and make that the argument to the function. e.g. print(True and True) becomes print (True)
            if not useEvalResult:
                    evalline = f"""{spacing}eval ('''{line}''')"""   #Wrap this line in eval if we can't use the result of an eval or a boolean operator "directly"                  
            else:                        
                if (re.match('''['"][^'"]+['"]$''', expr)):    
                    evalline = line
                else:    
                    if is_valid_expr(expr):
                        result = (parse_expr(expr))[0]     #Use our own eval function       
                        evalline = f'{spacing}{func} ({result})'                
                    else:
                        result = (eval(expr))            
                        if (isinstance(result, (str))):     
                            evalline = f'{spacing}{func} ("{result}")' #Use the built-in Python eval function                        
                        elif (isinstance(result, (float, int))):     
                            evalline = f'{spacing}{func} ({result})' #Use the built-in Python eval function                        
                        elif (isinstance(result, (list, dict, tuple))):     
                            evalline = f'{spacing}{func} {result}' #Use the built-in Python eval function                            
                        else:
                            evalline = line       
            lines.append(evalline)       
        elif match_assign: #Assignment lines with or/and/not
            spacing = match_assign.group(1)
            var = match_assign.group(2)
            expr = match_assign.group(3).strip()          
            ## Evaluate the expression at run-time and make that the assignment target, etc. e.g. 'a = 3 or 2 and 1' becomes 'a = 3'
            if not useEvalResult: #Wrap this line in eval if we can't use the result of an eval or a boolean operator "directly" 
                    evalline = f"""eval ('''{expr}''')"""   
                    evalline = f'{spacing}{var} = {evalline}'                    
            else:                 
                if (re.match('''['"][^'"]+['"]$''', expr)):    #Check if this is simply a quoted string
                    evalline = line
                else:       
                    if is_valid_expr(expr):
                        result = (parse_expr(expr))[0] #Use our own eval function       
                        evalline = f'{spacing}{var} = {result}'                
                    else: 
                        result = (eval(expr))     #Use the built-in Python eval function 
                        if (isinstance(result, (str))):     
                            evalline = f'{spacing}{var} = "{result}"' 
                        elif (isinstance(result, (float, int))):     
                            evalline = f'{spacing}{var} = ({result})'     
                        elif (isinstance(result, (list, dict, tuple))):     
                            evalline = f'{spacing}{var} = {result}'    
                        else:
                            evalline = line    
            lines.append(evalline)          
        elif match_while:            
            while_not = match_while.group(1)
            while_not = replace_not(while_not)
            cond =  match_while.group(2)
            line = f'{while_not}bool({cond}):'
            lines.append(line)
        else:
            lines.append(line)
    except Exception as e:        
        print (f'WARN: Unable to "eval({line})" : {e}')
        lines.append(line)   #Leave the line unchanged if an exception occurs    
    return lines    

def process_single_line_bools(lines):
    '''
    Processes boolean expressions line by line
    '''
    lines = list(lines)
    processed_lines = []
    for line in lines:
        processed_lines += match_bool_output (line, True)
    return processed_lines 

def parse_expr (expr, level = 0, block =0, if_expr = False): 
    '''
    For an arithmetic/boolean expression, parses and solves it recursively.
    Returns the result as a single item in a list.
    e.g. '2 + 4 * 6' -> 26
    
    For an if/elif expression into its individual logical parts - supports chaining with and without brackets.
    Returns the result as a list of if statements with the proper indentation maintained.
    e.g. 'if a and b or c:' ->
    if a:
        if b:
    if c:    
    '''
    part = prep_expr(expr, if_expr) #Prepare the expression for processing    
    loper = [] #Left operand    
    oper = '' #operator - and, or
    while True: #Keep processing parts of the expression until none left        
        if len(loper)>0: #We have the left operand already and are now integrating the right operands                        
            roper = [] #Right operand
            match = re.match('\s*(and|or) ', part)                        
            match_expr = re.match(REGEX_OPER, part)
            if if_expr and match: #Get the right operand and process an 'if/elif' expression
                oper = match.group(1).strip() #operator
                
                #Check if we have a result already so we can short-circuit the expression                                
                # left = (re.sub('^(el)?if', '', loper[0])) #Replace the 'if/elif' keywords
                # left = left.replace(':','')  #Replace any trailing ':'
                match_expr = re.match('if(.+):', loper[0])
                left = match_expr.group(1) #operator
                left = get_typed_val(left) #Get the left operand in its primitive datatype               
                #Short-circuiting logic
                if oper == 'and' and not left:
                    part='' ##We have found the first False condition with an AND. This is the result.  No need to evaluate the rest of the expression
                elif oper == 'or' and ((left and not isinstance(left,str)) or (isinstance(left,str) and re.match(r'''(['"])[^\1]+\1$''', left))):
                    part = '' #We have found the first True condition with an OR. This is the result.  No need to evaluate the rest of the expression
                else:
                    part = part[match.end(0):] #Entire expression after the first operator
                    part_expr = get_next_expr(oper, part) #Get the next (sub)expression to be evaluated
                    part = part[part.find(part_expr)+len(part_expr):] #Remaining part is anything after the next expression
                    roper = parse_expr (f'if {part_expr}', level, block, if_expr=True) #Call parse_expr recursively on the next expression
                    loper = merge(loper, roper, oper, level, block)            
            elif match_expr:  #Get the right operand and process an arithmetic/boolean expression   
                oper = match_expr.group(1) #operator
                part = part[match_expr.end(0):] #Entire expression after the first operator
                part_expr = get_next_expr(oper, part) #Get the next (sub)expression to be evaluated
                part = part[part.find(part_expr)+len(part_expr):] #Remaining part is anything after the next expression
                roper = parse_expr (part_expr) #Call parse_expr recursively on the next expression                
                if 'not' in str(loper[0]):                
                    loper[0] = loper[0].replace('not','')                    
                    uloper = eval_bin_bool_op (loper , oper , roper) #Solve the binary part first (without the unary 'not')
                    result = eval_bin_bool_op ([str(uloper)] , uoper) #Then solve the unary part (with the 'not')                   
                    loper = [result]
                else:
                    result = eval_bin_bool_op (loper , oper , roper)    
                    loper = [result]
        else: #We need to get the left operand going            
            match = re.match('((\s*((el)?if)?(\s+not)?)\s*(\()?)?(((.+?)(?= and | or ))|(.+$))', part)  #find the condition as if/elif + optional not        
            match_expr = re.match(f'((not|-+|\++)?\s*(\()?(\s*.+?)){REGEX_OPER}', part)  #match expression that has a binary operator with an optional unary operator (repeating allowed e.g. --1.2) at the start          
            if if_expr and match: #Process an if statement
                cond = match.group(2)#condition - if/elif
                if match.group(6) == '(': #Expression/operand is in brackets
                    part_expr = get_expr_within_brackets(part)
                    part = part[part.find(part_expr)+len(part_expr)+1:] #Remaining part should be anything after the closing bracket of the first bracketed expression
                    if (re.search(r'\b(and|or|not)\b', part_expr)): #Check if expression needs to be broken down further 
                        loper = parse_expr (cond.replace('not','').strip() + ' ' + part_expr, level, block, if_expr=True)#Recursive call to get left operand from the expression within brackets; if this is a 'not' expr, it'll be handled below
                        #----Handle NOT-----------
                        if 'not' in cond:
                            loper = merge_not(loper, level, block)      
                    else:
                        if 'not' in cond:
                            cond = replace_not(cond)
                            loper.append (f'{cond}bool({part_expr}):')
                        else:
                            loper.append (f'{cond} {part_expr}:')                       
                else: #Expression not within brackets, needs to become code                                 
                    part_expr = match.group(7).strip() #This is the first expression and will become the left operand                
                    part = part[part.find(part_expr)+len(part_expr):] #Remaining part is the part after the first expression
                    if 'not' in cond:
                        cond = replace_not(cond)
                        loper.append (f'{cond}bool({part_expr}):')
                    else:
                        loper.append (f'{cond} {part_expr}:')           
            elif match_expr: #Process an arithmetic/boolean expression 
                uoper = match_expr.group(2) #Unary operator                   
                if uoper and normalise_num_str(uoper) == '-':
                        loper = ['-1']   
                        part = part.replace('-', '*', 1)
                else:
                    if match_expr.group(3) == '(': #Expression is in brackets
                        part_expr = get_expr_within_brackets(part)
                        part = part[part.find(part_expr)+len(part_expr)+1:] #Remaining part should be anything after the closing bracket of the first bracketed expression
                        loper = parse_expr (part_expr)#Recursive call to get left operand from the expression within brackets; if this is a 'not' expr, it'll be handled below                        
                        if uoper: #Expression is negated or signed. e.g. not (1 + 2) -> False. group(2) =~ 'not'                        
                            result = eval_bin_bool_op (loper , uoper)
                            loper = [result]                          
                    else:
                        part_expr = (match_expr.group(1))
                        part = part[part.find(part_expr)+len(part_expr):] #Remaining part is the part after the first expression
                        if uoper and part == '': #Expression is negated or signed. e.g. not 0 -> 1. group(2) =~ 'not'                                                
                            uloper = match_expr.group(4) #Unary operand string
                            result = eval_bin_bool_op ([uloper] , uoper) #Pass in the unary operand as a list
                            loper = [result]                          
                        else:
                            loper.append (part_expr)
        if (part.strip()==''):#If there is nothing remaining of the expression, break out of the loop
            break        
    return  loper             

def remove_empty_lines(lines): 
    '''
    Remove all blank and commented lines from a list
    '''
    return [x for x in lines if (str(x).strip() and not re.match('\s*#', str(x))) ]

def replace_in (lines):        
    '''
    Replaces the 'in' keyword in a list of code line while ensuring the code output remains unchanged
    '''
    if not isinstance(lines, list):
            return lines
    for_counter = -1
    processed_lines = [] #All processed lines at current level
    for line in lines:        
        iter_lines = ''
        #if ('for ' in line and ' in ' in line): #for loop with in
        if re.search(REGEX_FOR_IN, line):
            for_counter += 1
            match = re.search(REGEX_FOR_IN, line)  #iterable loop
            indentation = match.group(1)
            iterator = match.group(2)
            collection = match.group(3)            
            iter_lines = ITERATION_CODE.replace('iterator', iterator).replace('collection', collection).replace('iterable', f'iterable{for_counter}').split('\n')            
            indented_iter_lines = indent_code(iter_lines, indentation)
            processed_lines = processed_lines + indented_iter_lines            
        #elif ('if ' in line and ' in ' in line): #if condition with in
        elif re.search(REGEX_IF_IN, line):
            line = ''.join(char for char in line if char not in ['(', ')'])
            match = re.search(REGEX_IF_IN, line)  #check existence of an item in iterable             
            indentation = match.group(1)
            item = match.group(2)
            collection = match.group(3)
            #METHOD1 : USE CONTAINS OPERATOR
            # processed_lines.append(indentation + 'from operator import contains') 
            # if (' not ' in line):
            #     processed_lines.append(indentation + 'if not contains( ' + collection + ' , ' + item.replace('not','') + ' ):' )             
            # else:
            #     processed_lines.append(indentation + 'if contains( ' + collection + ' , ' + item + ' ):' )         

            #METHOD2: USE ITERATOR
            if (' not ' in line):
                iter_lines =  ITERATION_IF_CODE.replace('item', item).replace('collection',collection).replace(' not ','').replace('is True','is False').split('\n')                
            else:
                iter_lines =  ITERATION_IF_CODE.replace('item', item).replace('collection',collection).split('\n')
            indented_iter_lines = indent_code(iter_lines, indentation)
            processed_lines = processed_lines + indented_iter_lines    
        else:
            processed_lines.append(line)  
    return  processed_lines  

def process_blocks_and_or(lines, level, block):
    '''
    Processes 'if' blocks
    For each block, calls function that replaces the keywords and/or/elif/else while ensuring the code output remains unchanged
    '''
    main_block_processed_lines = [] #All processed lines at current level    
    sub_block = -1
    sub_block_orig_lines =[]
    
    new_sub_block = False #No new sub-blocks initially
    sub_block_level = None
    for line in lines:
        match = re.search(REGEX_WORD, line)  #find the first "word" in the line 
        indent_level = 0         
        if match:
            indent_level = match.start()        
        if (indent_level > level ):
            if (new_sub_block is False): #Anything indented is a sub-block;  and match.group() in CONDITIONS
                new_sub_block = True #We now have a new sub-block starting
                sub_block_orig_lines = []
                sub_block += 1 #Increment the sub-block number
                sub_block_level = indent_level
            if (new_sub_block is True):    
                sub_block_orig_lines.append(line) #Add current line to the new sub-block
            else:
                main_block_processed_lines.append(line) #Add current line to the main block   
        else:
            if (new_sub_block is True):
                #We have just returned to the main block from a sub-block, so let's process the sub-block here and merge with the main block
                sub_block_processed_lines = process_blocks_and_or(sub_block_orig_lines, sub_block_level, str(block) + str(sub_block))
                expr_line = main_block_processed_lines.pop()
                sub_block_processed_lines = replace_and_or(expr_line, sub_block_processed_lines, level, str(block))
                main_block_processed_lines = main_block_processed_lines + sub_block_processed_lines
                new_sub_block = False #Reset sub-block as any sub-blocks we find after this will be new
            main_block_processed_lines.append(line)
    
    if (new_sub_block is True): #Pending unprocessd sub-block
        #We have an unprocessed sub-block, so let's process the sub-block here and merge with the main block
        sub_block_processed_lines = process_blocks_and_or(sub_block_orig_lines, sub_block_level, str(block) + str(sub_block))
        expr_line = main_block_processed_lines.pop()
        sub_block_processed_lines = replace_and_or(expr_line, sub_block_processed_lines, level, str(block))
        main_block_processed_lines = main_block_processed_lines + sub_block_processed_lines
    
    
    #We're done looping through the main block at this level        
    lines= [] #Free up some memory as we now have all the required lines in main_block_orig_lines       
    return   main_block_processed_lines

def replace_and_or(expr_line, lines, level, block):  
    '''
    For given 'if' block, replaces the keywords: and, or
    These are replaced with individual 'if' blocks while ensuring the code output remains unchanged
    '''  
    boolif = f'bool_IF_result{block}' if IF_RESULT_COUNTER == 'B' else f'bool_IF_result{level}'
    expr_lines = []    
    parsed_expr_lines= []
    merged_code = []
    spacing = '' 
    match = re.search('^(\s*)(\w+)', expr_line)  #find the first "word" in the line 
    if match:
        spacing = match.group(1)
        cond = match.group(2)
        if (cond == 'if'):
            expr_lines.append(f'{spacing}{boolif} = False')
        elif (cond in ('elif','else')):
            expr_lines.append(f'{spacing}if {boolif} is False:')
            spacing += '    ' #Extra indent        
        #if (cond in ('if','elif') and (' and ' in expr_line or ' or ' in expr_line or ' not ' in expr_line)):
        if (cond in ('if','elif') and ( re.search(r'\b(and|or|not)\b', expr_line))):    
            parsed_expr_lines = parse_expr (expr_line, level,block, if_expr = True)                
            parsed_expr_lines = indent_code(parsed_expr_lines, spacing)                        
            lines  = [f'{boolif} = True'] + dedent_code(lines)           
            merged_code = merge_and(parsed_expr_lines, lines, 0, 0)   
            merged_code = expr_lines + merged_code  
        else:
            if (cond == 'if'):
                expr_lines.append(expr_line)
                expr_lines.append(f'{spacing}    {boolif} = True')
                merged_code = expr_lines + lines
            elif (cond == 'elif'):                
                expr_lines.append(spacing + (expr_line).replace('elif','if').strip())                  
                expr_lines.append(f'{spacing}    {boolif} = True')                 
                merged_code = expr_lines + indent_code(lines, spacing) #lines                
            elif (cond == 'else'):
                merged_code = expr_lines + lines
            else:    
                expr_lines.append(expr_line)
                merged_code = expr_lines + lines
    return merged_code   

def main():   
    '''
    Tests our code
    '''    
    code = code1
    print (code) 
    code_lines =  code.split('\n')    
    code_lines = remove_empty_lines(code_lines)
    
    processed_lines = []
    if len(processed_lines)==0:
        processed_lines = remove_empty_lines(replace_in(code_lines)) #Replace the 'in' keyword and remove empty lines from the output
        processed_lines = process_single_line_bools (processed_lines) #Process single line boolean expressions e.g. print (True or True)
        processed_lines = remove_empty_lines(process_blocks_and_or(processed_lines,0,0))  #Replace the 'and' and 'or' keywords and remove empty lines from the output
    else:
        processed_lines = remove_empty_lines(replace_in(processed_lines)) #Replace the 'in' keyword and remove empty lines from the output
        processed_lines = process_single_line_bools (processed_lines) #Process single line boolean expressions e.g. print (True or True)
        processed_lines = remove_empty_lines(process_blocks_and_or(processed_lines,0,0))  #Replace the 'and' and 'or' keywords and remove empty lines from the output      

    # for line in processed_lines:
    #     print (line)
    
    new_code = '\n'.join(processed_lines)
    print (new_code)
    
    #Execute new code
    #exec (new_code)

    #Write new code to file
    with open('test.py', 'w') as f:
         f.write(new_code)  
    
if __name__ == '__main__':
    set_oper_dict() #Create the dictionary of operators and their precedence dynamically from a tuple of operators
    main()    