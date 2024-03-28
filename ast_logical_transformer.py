import ast
from typing import Any
from collections import deque

class Parentage(ast.NodeTransformer):
    '''
    Adds and populates the 'parent' attribute for each node in the AST
    '''      
    parent = None

    def visit(self, node: ast.AST):
        node.parent = self.parent
        self.parent = node
        transformed_node = super().visit(node)
        if isinstance(transformed_node, ast.AST):
            self.parent = transformed_node.parent
        else:
            print (f'Transformed node: {type(transformed_node)}')    
        return transformed_node

class RemoveUnaccessed(ast.NodeTransformer):
    '''
    Removes unaccessed variables from the node's scope for which this class is invoked
    '''      
    def __init__(self, id) -> None:
        self.node_Name_id = id
        super().__init__()

    def visit_Assign(self, node: ast.Assign) -> Any:
        target = node.targets[0]
        if isinstance(target, ast.Name) and (target.id==self.node_Name_id):
            return None #Remove this node
        else:
            return node
        
class Transformer(Parentage):
    '''
    Transforms an AST using the specified option:
    E = EXPAND: Replace the keywords and/or/not/elif/else. This is essentially done using nested ifs
    e.g.

    if a and b:
        x()

    is transformed to-

    if a:
        if b:
            x()        

    C = COLLAPSE: Flatten a nested 'if' structure where possible
    e.g.

    if a:
        if b:
            x()       

    is transformed to-         

    if a and b:
        x()

    By default, 'if' statements tests having boolean ops will be "short-circuited" where possible 
    
    e.g.

    'if 1 or x' will become 'if 1'
    
    'if False and x' will result in this branch being pruned altogether    

    '''      
    EXPAND = 'E'
    COLLAPSE = 'C'
    tmp_bool_access = {} #Dictionary to track if the temp variable (for every 'if' block) has been accessed
    def __init__(self, mode = EXPAND, short_circuiting_flag = True) -> None:
        '''
        Constructor for this transformer takes 2 optional arguments
        mode: E(xpand)/C(ollapse) indicating nesting or flattening of if statements; Default = E
        short_circuiting_flag: Indicator for whether short-circuiting should be applied; Default = True
        '''
        self.mode = mode
        self.short_circuiting = short_circuiting_flag         
        self.dict_node_shortcct = {} #Dictionary to hold short-citcuit status of each if-test node    
        super().__init__()

    def generic_visit(self, node: ast.AST) -> ast.AST:
        '''
        Prints traversal info of nodes within the AST
        '''    
        try:        
            line_info =  f' at line: {node.lineno}, offset: {node.col_offset}'
        except Exception:
            line_info = ''
        print(f'entering {node.__class__.__name__}(parent: {node.parent.__class__.__name__}){line_info}')              
        super().generic_visit(node)
        print(f'leaving {node.__class__.__name__}(parent: {node.parent.__class__.__name__}){line_info}')      
        return node

    # def visit_Module(self, node: ast.Module) -> Any:        
    #     print(f'entering {node.__class__.__name__}')
    #     print(f'parent node {node.parent.__class__.__name__}')
    #     node.body = self.process_stmt_list((stmt for stmt in node.body))    
    #     return node    

    def visit_Call(self, node: ast.Call) -> ast.Call:
        '''
        Transforms a 'call' node encountered while traversing an AST
        It condenses the 'args' field by 'eval'ing it 

        e.g. 'print (True or False)' becomes 'print (True)'
        
        If eval fails, it returns the original node
        ''' 
        if self.mode == self.EXPAND and len(node.args): #Only do this if we're trying to replace and/or/not/in    
            try:            
                val = self.get_node_val(node.args[0])                   
                if Transformer.is_primitive(val):
                    node.args[0] = ast.Constant(value=val) 
                else:
                    super().generic_visit(node) #We need this for any nodes nested within the Call node   
            except Exception as e:
                print (f'Warn: {e}')  #Expression could not be evaluated at compile time (can only happen at run time)        
                
            return node
        else:
            super().generic_visit(node)
            return node
        

    def visit_If(self, node: ast.If) -> Any:
        '''
        Transforms an 'if' node (along with its children) encountered while traversing an AST
        ''' 
        processed_if = []
        line_info =  f' at line: {node.lineno}, offset: {node.col_offset}'        
        node_metadata = f'{node.__class__.__name__}(parent: {node.parent.__class__.__name__}){line_info}'        
        print(f'entering {node_metadata}')  
        
        p = node.parent #Get the parent of the current If node
        gp = p.parent #Get the grandparent of the current If node

        node_name = self.get_Name('print', ast.Load())
        node_call = self.get_Call(node_name, [ast.Constant(value = '<Node pruned>')])  # node_call = self.get_Call((self.get_Name('bool', ast.Load())), [last_if.test])              
        node_expr = self.get_Expr(node_call)
        node_expr.parent = p

        if self.mode == self.EXPAND:            
            processed_if = self.expand_if (node) #Break down this If node into its logical components
            if not processed_if:
                print (f'Entire sub-tree {node_metadata} pruned')
                processed_if.append(node_expr)
            return  processed_if    
        elif self.mode == self.COLLAPSE:
            processed_if = self.collapse_if(node) #Roll up nested Ifs into a single ast.BoolOp (op=ast.And)            
            if not processed_if:
                print (f'Entire sub-tree {node_metadata} pruned')
                processed_if.append(node_expr)
            return  processed_if    
        else:    
            super().generic_visit(node)
            return node
        

    def get_Assign(self, assign_targets: list, assign_value: ast.AST) -> ast.Assign:
        '''
        Returns an ast.Assign node constructed using the specified parameters
        '''         
        node_Assign = ast.Assign(
            targets=assign_targets,
            value= assign_value
        )
        return node_Assign

    def get_If(self, if_test, if_body: list, if_orelse: list = []) -> ast.If:
        '''
        Returns an ast.If node constructed using the specified parameters
        ''' 
        node_If = ast.If(
            test = if_test,
            body = if_body,
            orelse = if_orelse
        )
        return node_If

    def get_Compare(self, compare_left: ast.AST, compare_ops: list, compare_comparators: list) -> ast.Compare:
        '''
        Returns an ast.Compare node constructed using the specified parameters
        ''' 
        node_Compare = ast.Compare(
            left = compare_left,
            ops = compare_ops,
            comparators = compare_comparators
        )
        return node_Compare

    def get_Name(self, name_id: str, name_ctx: ast.AST) -> ast.Name:
        '''
        Returns an ast.Name node constructed using the specified parameters
        '''
        node_Name = ast.Name(
            id = name_id,
            ctx = name_ctx
        )
        return node_Name
    
    def get_Expr(self, value: ast.AST) -> ast.Expr:
        '''
        Returns an ast.Expr node constructed using the specified parameters
        '''
        node_Expr = ast.Expr(
            value=value
        )
        return node_Expr
    
    def get_Call(self, call_func: ast.AST, call_args: list) -> ast.Call:
        '''
        Returns an ast.Call node constructed using the specified parameters
        '''        
        node_Call = ast.Call(
            func=call_func,
            args=call_args,
            keywords=[]
        )
        return node_Call
    
    def get_BoolOp(self, boolop_op: ast.AST, boolop_values: list) -> ast.BoolOp:
        '''
        Returns an ast.BoolOp node constructed using the specified parameters
        '''
        node_BoolOp = ast.BoolOp(
            op=boolop_op,
            values=boolop_values
        )
        return node_BoolOp
    
    def get_UnaryOp(self, unaryop_op: ast.AST, unaryop_operand: ast.AST) -> ast.UnaryOp:
        '''
        Returns an ast.UnaryOp node constructed using the specified parameters
        '''
        node_UnaryOp = ast.UnaryOp(
            op=unaryop_op,
            operand=unaryop_operand
        )
        return node_UnaryOp
    
    def merge_Not(self, lroper: list, if_block_var_id: str) -> list:  
        '''
        Wrap an operand within the  NOT operator
        '''      
        processed_list = []
        last_if: ast.If = lroper.pop()
        last_if.body = ast.Pass() #If the condition is True, do nothing (pass)
        lroper.append(last_if)
        processed_list =  self.merge_Or(lroper, [], if_block_var_id) #Add provision to execute where condition is False
        return processed_list 


    def merge_And(self, loper: list, roper: list) -> list:
        '''
        Join/merge left and right operands with the AND operator    
        '''
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

    def merge_Or(self, loper: list, roper: list, if_block_var_id: str) -> list:
        '''
        Join/merge left and right operands with the OR operator    
        '''
        processed_list = []
        node_if: ast.If
        if loper:            
            node_temp_var_name = self.get_Name(if_block_var_id, ast.Load())
            node_if_test = self.get_Compare(node_temp_var_name, [ast.Is()], [ast.Constant(value = False)]) #Add a line that checks if the temp bool is False - we only do the 'OR' part if it is
            self.tmp_bool_access[if_block_var_id] = True
            node_if = self.get_If(node_if_test, roper)
            roper = [node_if]                
        processed_list = loper + roper   
        return processed_list 

    @staticmethod 
    def is_iftest_truthy_falsy(node_iftest):
        '''
        Skeleton method for checking if the test of an 'if' node is of a type that can be evaluated as True or False
        '''
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
    def is_primitive(val):
        '''
        Method for checking if a string value is of a primitive datatype - bool, int, float, str   
        '''
        return (
            isinstance(val, bool)
            or isinstance(val, int)
            or isinstance(val, float)
            or isinstance(val, str)
        ) 

    @staticmethod
    def get_node_val(node) -> Any:
        '''
        Takes in a node, changes it to an ast.Expression and 'eval's it to get its result 
        If an exception occurs because evaluation fails, it is to be handled by the caller of this method
        '''
        expr = ast.Expression(body=node)
        ast.fix_missing_locations(expr)
        val = eval(compile(expr, filename='', mode='eval'))
        return val
    
    
    def is_short_circuited(self, node_if_test: ast.AST) -> bool:
        '''
        -'eval's the input node (ast.If.test)
        - Adds node and eval result to the dict_node_shortcct attribute

        A True value will short-circuit an OR

        A False value will short-circuit an AND

        Prints a warning if Expression could not be evaluated at 'compile time'
        '''
        short_circuited = False        
        try:            
            val = self.get_node_val(node_if_test)
            short_circuited = True #Expression was evalauted successfully, so we should be able to do a truth test
            self.dict_node_shortcct[node_if_test] = val #Update the dict_node_shortcct attribute           
        except Exception as e:
            print (f'Warn: {e}')  #Expression could not be evaluated at compile time (can only happen at run time)
        return  short_circuited 

    def reduce_if_test(self, node_if_test: ast.AST) -> Any:        
        '''
        Takes in an ast.If.test node and recursively 'condenses' it to the bare minimum while keeping it logically consistent
        
        e.g.
        '0 or 1' becomes '1'
        '1 and 0' becomes '0'
        'not 0' becomes True
        'not 1' becomes None
        '''
        reduced_if_test:ast.AST = None
        if isinstance(node_if_test, ast.BoolOp):           
            reduced_if_test = self.get_BoolOp(node_if_test.op, [])            
            for test in node_if_test.values: 
                reduced_test = self.reduce_if_test(test)                                               
                if isinstance(node_if_test.op, ast.Or):                                                             
                    if reduced_test: 
                        if reduced_test in self.dict_node_shortcct and self.dict_node_shortcct[reduced_test]: 
                            #We have found the first True condition with an OR. No need to evaluate the rest of the expression                        
                            #reduced_if_test.values.append(reduced_test) #Return a BoolOp[op='Or'] with only 1 operand
                            reduced_if_test = reduced_test #Return the test on its own rather than as BoolOp.Or with only 1 operand
                            break
                        reduced_if_test.values.append(reduced_test)
                elif isinstance(node_if_test.op, ast.And):                    
                    if not reduced_test:                        
                        #We have found the first False condition with an AND. No need to evaluate the rest of the expression
                        reduced_if_test = None #None of the other 'and' conditions will get executed
                        break
                    reduced_if_test.values.append(reduced_test)
        elif isinstance(node_if_test, ast.UnaryOp): 
            if isinstance(node_if_test.op, ast.Not): #unary boolean 
                reduced_if_test = self.get_UnaryOp(node_if_test.op, None)     
                reduced_test = self.reduce_if_test(node_if_test.operand)  
                if reduced_test in self.dict_node_shortcct and self.dict_node_shortcct[reduced_test]:                         
                    #We have found a True condition with a NOT. !True == False, so this condition can go
                    reduced_if_test = None
                else:    
                    if reduced_test:
                        reduced_if_test.operand = reduced_test
                    else:
                        reduced_if_test = ast.Constant(value = True)  #!False == True, so replace 'not <cond>' with True
            else:
                reduced_if_test = node_if_test            
        else:
            if not self.is_short_circuited(node_if_test) or self.dict_node_shortcct[node_if_test]:                                
                reduced_if_test = node_if_test

        return reduced_if_test



    def get_Ifs_AndOr(self, node_if_test: ast.AST, if_block_var_id: str) -> list:
        '''
        Takes in an ast.If.test node and recursively 'expands' it using nested ifs while keeping it logically consistent
        '''
        node_If_list = []
        if isinstance(node_if_test, ast.BoolOp):           
            for node in node_if_test.values:                
                new_Ifs: list = self.get_Ifs_AndOr(node, if_block_var_id)
                last_if: ast.If = new_Ifs[-1] if new_Ifs else []
                if isinstance(node_if_test.op, ast.Or):                                                           
                    node_If_list = self.merge_Or(node_If_list, new_Ifs, if_block_var_id)                    
                elif isinstance(node_if_test.op, ast.And):                                        
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
                node_name = self.get_Name('bool', ast.Load())
                node_call = self.get_Call(node_name, [last_if.test])
                node_ifnot_test = self.get_Compare(ast.Constant(value = False), [ast.Eq()], [node_call])
                last_if.test = node_ifnot_test
                node_If_list.append(last_if)
        else:
            node_if = self.get_If(node_if_test, [])
            node_If_list.append(node_if)

        return node_If_list

    def process_stmt_list(self, gen) -> deque:
        '''
        Takes in a generator object yielding statements from a list
        Depending whether we're expanding or collapsing ifs, calls the appropriate method for each statement
        Returns the processed list of statements as a deque object
        '''
        processed_list = deque([])                
        while True:
            try:
                stmt= next(gen)
            except StopIteration:
                break
            #print(f'Generator yielded {stmt.__class__.__name__}')
            if  isinstance(stmt, ast.If):       
                if self.mode == self.EXPAND:            
                    processed_if = self.expand_if (stmt)  #Break down this If node into its logical components                    
                elif self.mode == self.COLLAPSE:
                    processed_if = self.collapse_if(stmt) #Roll up nested IFs into a single ast.BoolOp (op=ast.And)                         
                processed_list.extend(processed_if) 
            elif isinstance(stmt, ast.Expr):         
                if isinstance(stmt.value, ast.Call) and not (isinstance(stmt.value.args[0], ast.Constant)):
                    stmt.value = self.visit_Call (stmt.value) #Try to 'reduce' the call expression to its result
                processed_list.append(stmt)     
            else:
                processed_list.append(stmt) 
        return  processed_list 

    def field_generator(self, node: ast.AST, field: str) -> Any:
        '''
        Takes in a node with a list of statements (field)
        Yields a statement from the list at a time 
        '''
        for (fieldname, value) in ast.iter_fields(node):
            if fieldname == field:
                for stmt in value:
                    yield stmt        

    

    def expand_if(self, node: ast.If) -> list:
        '''
        Takes in an ast.If node and recursively replaces the keywords and/or/not/elif/else using nested ifs
        '''
        processed_if = []
        split = False 
        if_block_var_id = f'_boolIf{node.col_offset}'
        self.tmp_bool_access[if_block_var_id] = False  

        if self.short_circuiting:
            reduced_if_test = self.reduce_if_test(node.test)  
            node.test = reduced_if_test
        
        if node.test:
            if (isinstance(node.test, ast.BoolOp) or isinstance(node.test, ast.UnaryOp)) or node.orelse:        
                split = True #We will only split if the test has one of: and/or/not/elif/else
                

            #processed_body = self.process_stmt_list(node.body) #Process using list       
            #processed_body = self.process_stmt_list((stmt for stmt in node.body))  #Process using in-line generator
            processed_body = self.process_stmt_list(self.field_generator(node, 'body')) #Process using ast.iter_fields generator
            
            if processed_body:
                #Process test and merge body               
                new_ifs = self.get_Ifs_AndOr(node.test, if_block_var_id) #Break down the (boolean ops) from test into its individual logical ops
                if new_ifs: #If we have >=1 'if' statements merge the body with them, otherwise prune the entire branch
                    if split:
                        node_assign_if_pre = self.get_Assign([(self.get_Name(if_block_var_id, ast.Store()))], ast.Constant(value=False)) 
                        processed_if.append(node_assign_if_pre) #Initialise the bool variable for this IF node    
                        node_assign_if_post = self.get_Assign([(self.get_Name(if_block_var_id, ast.Store()))], ast.Constant(value=True)) 
                        #processed_body.insert(0, node_assign_if)  #Prepend to list     
                        processed_body.appendleft(node_assign_if_post)  #Prepend to deque                 
                    processed_if.extend(self.merge_And(new_ifs, list(processed_body))) #Add the body to the new Ifs we got from breaking down the test

        #Process orelse                       
        processed_orelse = self.process_stmt_list(self.field_generator(node, 'orelse'))            
        if processed_orelse:     
            processed_if = self.merge_Or(processed_if, list(processed_orelse), if_block_var_id)

        if processed_if and isinstance(processed_if[0], ast.Assign) and not self.tmp_bool_access[if_block_var_id]:
            processed_if.pop(0)
            unaccessedRemover = RemoveUnaccessed(if_block_var_id)
            clean_if = unaccessedRemover.visit(processed_if[0])
            processed_if = [clean_if]
        
        return processed_if
    
   
    def collapse_if(self, node: ast.If) -> list:
        '''
        Takes in an ast.If node and recursively flattens nested ifs where possible
        '''
        processed_if = []
        
        node = self.get_collapsed_if(node, []) #Roll up nested IFs into a single ast.BoolOp (op=ast.And)        

        if self.short_circuiting:
            reduced_if_test = self.reduce_if_test(node.test)
            if reduced_if_test:
               node.test = reduced_if_test 
            else:                                   
                if node.orelse:
                    processed_if = node.orelse
                node = None #Prune the 'if' part altogether           
                
        if node:
            #Process body      
            processed_body = self.process_stmt_list(self.field_generator(node, 'body')) #Process using ast.iter_fields generator
            if processed_body:
                node.body = list(processed_body)
                #Process orelse       
                processed_orelse = self.process_stmt_list(self.field_generator(node, 'orelse'))            
                node.orelse = list(processed_orelse)
            else: #The entire 'body' has been pruned 
                node = None #Can't have an if without a body, so prune the original if   
            processed_if.append(node)            
        
        return processed_if
    
    def get_collapsed_if(self, node: ast.If, operands: list = []) -> ast.If:
        '''
        Takes in an ast.If node and recursively flattens it to the max depth possible while remaining logically consistent
        '''
        ret_if:ast.If = None

        if len(node.body)==1 and isinstance(node.body[0], ast.If) and not node.orelse: #We have a nested 'and'
            nested_if = node.body[0]        
            operands.append(node.test)
            ret_if = self.get_collapsed_if(nested_if, operands)   
        elif operands:            
            operands.append(node.test)
            test = self.get_BoolOp(ast.And(), operands)
            ret_if = self.get_If(test, node.body, node.orelse)
        else:            
            ret_if = node
        return ret_if    

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

if 0:
    print (False)
else:
    print (True or False)    

if 1:
    if 2:
        if 0:
            print ('And test executed')  


print (- (2 + 3 / .5) ** 10)

print(1 or 2 and not not 0)

print(bool(a))

print (iter('i love python'.split()))
'''
def main():   
    '''
    Tests our code
    '''    
    #READ and PARSE the code, generate an AST
    tree = ast.parse(code1)
    print(ast.dump(tree, indent='   '))

    #VISIT and TRANSFORM the AST    
    #new_tree = Transformer().visit(tree) 
    new_tree = Transformer(mode='E', short_circuiting_flag = True).visit(tree) 
    #new_tree = Transformer(mode='C', short_circuiting_flag = True).visit(tree) 
    new_tree = ast.fix_missing_locations(new_tree)
    print(ast.dump(new_tree, indent='   '))

    #UNPARSE the transformed AST and VIEW new code 
    new_code = ast.unparse(new_tree)
    print(new_code)

    #WRITE new code to file
    with open('ast_transformed_code.py', 'w') as f:
            f.write(new_code)  

    #COMPILE the new AST into a binary object        
    # code_object = compile(new_tree, '', 'exec')

    #EXECUTE the code in the binary object        
    # exec(code_object)
            
if __name__ == '__main__':    
    main()            
