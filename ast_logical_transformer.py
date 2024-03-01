import ast
from typing import Any
from collections import deque

class Parentage(ast.NodeTransformer):
    parent = None

    def visit(self, node):
        node.parent = self.parent
        self.parent = node
        node = super().visit(node)
        if isinstance(node, ast.AST):
            self.parent = node.parent
        return node


class Transformer(Parentage):
    
    dict_node_shortcct = {} #Dictionary to hold short-citcuit status of each if-test node    

    def __init__(self, short_circuiting_flag = True) -> None:
        self.short_circuiting = short_circuiting_flag 
        super().__init__()

    # def visit_Module(self, node: ast.Module) -> Any:        
    #     print(f'entering {node.__class__.__name__}')
    #     print(f'parent node {node.parent.__class__.__name__}')
    #     node.body = self.process_stmt_list((stmt for stmt in node.body))    
    #     return node    

    def visit_If(self, node: ast.If) -> Any:
        return_list = []
        print(f'entering {node.__class__.__name__} at line: {node.lineno} and offset: {node.col_offset}')
        print(f'parent node {node.parent.__class__.__name__}')
        #super().generic_visit(node)

        p = node.parent #Get the parent of the current If node
        gp = p.parent #Get the grandparent of the current If node

        if not (isinstance(node.test, ast.BoolOp) or isinstance(node.test, ast.UnaryOp)):
            return node

        if_block_var_id = f'_boolIf{node.col_offset}'
        node_assign_if = self.get_Assign(if_block_var_id, ast.Store(), False) 
        return_list.append(node_assign_if) #Initialise the bool variable for this IF node

        processed_if_list = self.process_If (node, if_block_var_id) #Break down this If node into its logical components

        #Merge the 2 lists
        #return_list.append(processed_if_list) #Doesn't work as intended - adds if_list as a nested list
        #return_list= [node_assign_if] + self.process_If (node) #Works
        return_list.extend(processed_if_list) #Works
        
        return  return_list

    def get_Assign(self, node_Name_id, node_Name_ctx, bool_val = False):

        node_Name = self.get_Name(node_Name_id, node_Name_ctx)                                
        node_Assign = ast.Assign(
            targets=[node_Name],
            value=ast.Constant(value=bool_val)
        )
        return node_Assign

    def get_If(self, if_test, if_body, if_orelse = []):

        node_If = ast.If(
            test = if_test,
            body = if_body,
            orelse = if_orelse
        )
        return node_If

    def get_Compare(self, compare_left, compare_ops, compare_comparators):

        node_Compare = ast.Compare(
            left = compare_left,
            ops = [compare_ops],
            comparators = [compare_comparators]
        )
        return node_Compare

    def get_Name(self, name_id, name_ctx):

        node_Name = ast.Name(
            id = name_id,
            ctx = name_ctx
        )
        return node_Name
    
    def get_Call(self, node_Name_id, node_Name_ctx, node_Call_arg):

        node_Name = self.get_Name(node_Name_id, node_Name_ctx)                                
        node_Call = ast.Call(
            func=node_Name,
            args=[node_Call_arg],
            keywords=[]
        )
        return node_Call
    
    def merge_Not(self, lroper: list, if_block_var_id):        
        processed_list = []
        last_if: ast.If = lroper.pop()
        last_if.body = ast.Pass() #If the condition is True, do nothing (pass)
        lroper.append(last_if)
        processed_list =  self.merge_Or(lroper, [], if_block_var_id) #Add provision to execute where condition is False
        return processed_list 


    def merge_And(self, loper: list, roper: list):

        processed_list = []
        if loper:
            for item in loper:
                if isinstance(item, ast.If): #Potential replacement here
                    if len(item.body)==0: #Merge here
                        item.body = roper             
                    else:
                        item.body = self.merge_And(item.body, roper)
                processed_list.append(item)
        else:            
            processed_list = roper
        return processed_list

    def merge_Or(self, loper: list, roper: list, if_block_var_id):

        node_if: ast.If
        if loper:            
            node_temp_var_name = self.get_Name(if_block_var_id, ast.Load())
            node_if_test = self.get_Compare(node_temp_var_name, ast.Is(), ast.Constant(value = False))
            node_if = self.get_If(node_if_test, roper)
            roper = [node_if]                
        return  loper + roper

    @staticmethod 
    def is_iftest_truthy_falsy(node_iftest):
        return (
            isinstance(node_iftest, ast.Constant)
            or isinstance(node_iftest, ast.FormattedValue)
            or isinstance(node_iftest, ast.JoinedStr)
            or isinstance(node_iftest, ast.List)
            or isinstance(node_iftest, ast.Tuple)
            or isinstance(node_iftest, ast.Set)
            or isinstance(node_iftest, ast.Dict)
        ) 

    @staticmethod
    def get_node_val(node):
        expr = ast.Expression(body=node)
        ast.fix_missing_locations(expr)
        val = eval(compile(expr, filename='', mode='eval'))
        return val
    
    
    def is_short_circuited(self, node_if_test: ast):
        short_circuited = False        
        try:            
            val = self.get_node_val(node_if_test)
            short_circuited = True #Expression was evalauted successfully, so we should be able to do a truth test
            if (val): #We have a value that's evaluated to True                    
                self.dict_node_shortcct[node_if_test] = 'or' #A True value will short-circuit an OR
            elif (not val):  #We have a value that's evaluated to False                    
                self.dict_node_shortcct[node_if_test] = 'and'#A False value will short-circuit an AND
        except Exception as e:
            print (e)    #Expression could not be evaluated at compile time (can only happen at run time)
        return  short_circuited 


    def get_Ifs_AndOr(self, node_if_test: ast, if_block_var_id):

        node_If_list = []
        if isinstance(node_if_test, ast.BoolOp):           
            for node in node_if_test.values:                
                new_Ifs: list = self.get_Ifs_AndOr(node, if_block_var_id)
                last_if: ast.If = new_Ifs[-1] if new_Ifs else []
                if isinstance(node_if_test.op, ast.Or):                                        
                    if self.short_circuiting and last_if and last_if.test in self.dict_node_shortcct and self.dict_node_shortcct[last_if.test] == 'or': 
                        #We have found the first True condition with an OR. No need to evaluate the rest of the expression
                        if not node_If_list: 
                            node_If_list = self.merge_Or(node_If_list, new_Ifs, if_block_var_id) #If the return list is empty, add this condition first
                        break
                    node_If_list = self.merge_Or(node_If_list, new_Ifs, if_block_var_id)                    
                elif isinstance(node_if_test.op, ast.And):                    
                    if self.short_circuiting and not last_if:                        
                        #We have found the first False condition with an AND. No need to evaluate the rest of the expression
                        node_If_list = [] #None of the other 'and' conditions will get executed
                        break
                    node_If_list = self.merge_And(node_If_list, new_Ifs)                    
        elif isinstance(node_if_test, ast.UnaryOp) and isinstance(node_if_test.op, ast.Not): #unary boolean                                    
            if isinstance(node_if_test.operand, ast.BoolOp): #Negation of bracketed boolean expressions more complex than initially anticipated   
                #ToDo: 
                #Break down the BoolOps and then merge with additional 'not' statements
                ...#node_If_list = self.merge_Not(new_Ifs, if_block_var_id) 
                
                #Keep the expression as-is for now        
                node_if = self.get_If(node_if_test, [])  
                node_If_list.append(node_if)        
            else:
                new_Ifs: list = self.get_Ifs_AndOr(node_if_test.operand, if_block_var_id)        
                last_if: ast.If = new_Ifs[-1] 
                node_ifnot_test = self.get_Compare(ast.Constant(value = False), ast.Eq(), self.get_Call('bool', ast.Load(), last_if.test))
                last_if.test = node_ifnot_test
                node_If_list.append(last_if)
        else:
            if not self.short_circuiting or not self.is_short_circuited(node_if_test) or self.dict_node_shortcct[node_if_test] == 'or':                
                node_if = self.get_If(node_if_test, [])
                node_If_list.append(node_if)

        return node_If_list

    def process_stmt_list(self, gen):
        processed_list = deque([])                
        while True:
            try:
                stmt= next(gen)
            except StopIteration:
                break
            print(f'Generator yielded {stmt.__class__.__name__}')
            if  isinstance(stmt, ast.If):
                if_block_var_id = f'_boolIf{stmt.col_offset}'
                node_assign_if = self.get_Assign(if_block_var_id, ast.Store(), False) 
                processed_list.append(node_assign_if) #Initialise the bool variable for this IF node
                processed_if = self.process_If (stmt, if_block_var_id)
                if not processed_if:
                    processed_list.pop() #Remove the bool variable for this IF node if the entire sub-tree was pruned
                processed_list.extend(processed_if)    
            else:
                processed_list.append(stmt) 
        return  processed_list 

    def field_generator(self, node, field):

        for (fieldname, value) in ast.iter_fields(node):
            if fieldname == field:
                for stmt in value:
                    yield stmt        

    def process_If(self, node: ast.If, if_block_var_id):
        processed_if = []
               
        #processed_body = self.process_stmt_list(node.body) #Process using list       
        #processed_body = self.process_stmt_list((stmt for stmt in node.body))  #Process using in-line generator
        processed_body = self.process_stmt_list(self.field_generator(node, 'body')) #Process using ast.iter_fields generator
        
        #Process test and merge body               
        new_ifs = self.get_Ifs_AndOr(node.test, if_block_var_id) #Break down the (boolean ops) from test into its individual logical ops
        if new_ifs: #If we have >=1 'if' statements merge the body with them, otherwise prune the entire branch
            node_assign_if = self.get_Assign(if_block_var_id, ast.Store(), True) 
            #processed_body.insert(0, node_assign_if)  #Prepend to list     
            processed_body.appendleft(node_assign_if)  #Prepend to deque     
            processed_if = self.merge_And(new_ifs, list(processed_body)) #Add the body to the new Ifs we got from breaking down the test

        #Process orelse       
        #processed_orelse = self.process_stmt_list(node.orelse)       
        #processed_orelse = self.process_stmt_list((stmt for stmt in node.orelse))            
        processed_orelse = self.process_stmt_list(self.field_generator(node, 'orelse'))            
        if processed_orelse:     
            processed_if = self.merge_Or(processed_if, list(processed_orelse), if_block_var_id)


        return processed_if

code = '''
if  not ("False") and not (not True):
    print (True)
else:    
    print (False)      
'''
code1 = '''
a = ''
if  "False" or 1 and True:
    print (True)
    if 0 or isinstance(a, str) and 1:
        print ('Inner if test executed')
else:    
    print (False)
'''

tree = ast.parse(code1)
print(ast.dump(tree, indent='   '))

#We don't want to "short-circuit" 'if' statement tests having boolean ops
#new_tree = Transformer(short_circuiting = False).visit(tree) 

#By default, 'if' statements tests having boolean ops will be "short-circuited" where possible 
#
# Examples:
# 'if 1 or x' will become 'if 1:'
#
#'if False and x' will prune this branch altogether
#
new_tree = Transformer().visit(tree) 
new_tree = ast.fix_missing_locations(new_tree)
print(ast.dump(new_tree, indent='   '))

#View new code
new_code = ast.unparse(new_tree)
print(new_code)

#Write new code to file
with open('ast_transformed_code.py', 'w') as f:
        f.write(new_code)  

#Compile and Execute new code        
# code_object = compile(new_tree, '', 'exec')
# exec(code_object)
