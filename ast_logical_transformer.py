import ast
from typing import Any
from collections import deque

class Parentage(ast.NodeTransformer):
    '''
    Adds and populates the 'parent' attribute for each node in the AST
    This is so that the parent can be referenced from within a child if required
    '''      
    parent = None #New attribute to add to each node to reference the parent
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

class TransformerIn(ast.NodeTransformer):
    '''
    Transforms an AST by replacing the keyword 'in' while keeping the code logically consistent (original output unchanged)
    '''      
    is_iter_func_reqd = False  #Flag to check if a FunctionDef is required for an if-in construct
    #Code snippet to insert for if-in, for-in constructs
    ITERATION_CODE = '''  
iterable = iter(collection)
while True:
    try:
        iterator = next(iterable)    
''' 
    #Code snippet to insert for a for-in construct   
    ITERATION_FOR_CODE = f'''
{ITERATION_CODE}
    except StopIteration:
        break    
'''
    ITERATION_DEF_CODE = ITERATION_CODE.replace('\n','\n    ') #Add extra indent to the code since it will be embedded in a func    
    #Code snippet to insert for an if-in construct   
    ITERATION_IF_CODE = f'''
def _isItemInIter(item, collection, check = True):    
    found = False
    {ITERATION_DEF_CODE}
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
'''
    def visit_Module(self, node: ast.Module) -> Any:   
        '''
        Traverse the AST and insert an ast.FunctionDef if called for
        '''      
        super().generic_visit(node)
        if self.is_iter_func_reqd:            
            iter_func: list = ast.parse(self.ITERATION_IF_CODE).body #Add function def           
            node.body.insert(self.get_loc_iter(node.body), iter_func)
        return node    
    
    def visit_If(self, node: ast.If) -> list:
        '''
        Visits an 'if' node and its children to try to replace keyword 'in' in them
        '''   
        super().generic_visit(node)
        if_w_replaced_in = self.replace_in_if(node)
        return if_w_replaced_in
    
    def visit_For(self, node: ast.For) -> list:
        '''
        Visits a 'for' node and its children to try to replace keyword 'in' in them
        The 'for' loop is replaced with a 'while' loop to achieve this
        It uses an iter(<list>) object which allows the same functionality without the keyword 'in'
        '''   
        super().generic_visit(node)
        for_w_replaced_in = self.replace_in_for(node)
        return for_w_replaced_in
    
    def get_loc_iter(self, stmt_list: list) -> int:
        '''
        Returns the first line where a new FunctionDef can be inserted (i.e., after any imports)
        ''' 
        for i in range(len(stmt_list)):
            stmt = stmt_list[i]
            if not isinstance(stmt, (ast.Import, ast.ImportFrom)):            
                return i

    def replace_in_for(self, node_for: ast.For) -> list:  
        '''
        Replaces the keyword 'in' where it appears with a 'for'
        '''  
        processed_for: list = []          
        iterator = ast.unparse(node_for.target)
        collection = ast.unparse(node_for.iter)
        iter_lines = self.ITERATION_FOR_CODE
        replace_dict = {
            'iterator': iterator, 
            'collection': collection, 
            'iterable': f'iterable{node_for.col_offset}'
        }            
        iter_lines = TransformerIn.str_multi_replace(iter_lines, replace_dict) #Get the new code as a string     
        iter_lines = ast.parse(iter_lines).body #Turn the new code back into an AST (the module body is a list)
        node_while:ast.While = iter_lines.pop()
        node_while.body.append(node_for.body)
        processed_for = iter_lines + [node_while] 
        return processed_for
    
    @staticmethod
    def str_multi_replace(old: str, replace_dict: dict) -> str:                
        '''
        Performs multiple replacements (specified as a dict) in target string
        '''  
        for k, v in replace_dict.items():
            old = old.replace(k, v)
        return old

    def get_comparators(self, node_compare: ast.Compare) -> tuple:
        '''
        Gets comparators from a compare node as a tuple
        We're specifically calling this for those nodes that have ast.(Not)?In as ast.Compare.ops[0] 
        e.g. '1 in [1, 2, 3]'  returns '1' as the item and '[1, 2, 3]' as the collection (list)
        ''' 
        item = ast.unparse(node_compare.left) 
        collection = ast.unparse(node_compare.comparators[0])
        return (item, collection)
    
    def get_iter_code_from_compare(self, node_compare: ast.Compare, negated: bool = False) -> list:
        '''
        Creates a new AST code object after replacing the keyword 'in' from a compare node
        ''' 
        item, collection = self.get_comparators(node_compare)   
        iter_lines = TransformerIn.ITERATION_IF_CODE
        if (
                isinstance(node_compare.ops[0], ast.In) and negated) \
                or (isinstance(node_compare.ops[0], ast.NotIn) and not negated): #e.g. 'not 1 in [1, 2, 3]' or '1 not in [1, 2, 3]'                      
            iter_lines = f'_isItemInIter({item}, {collection}, False)'
        else:  #e.g. '1 in [1, 2, 3]' ; 'not 1 not in [1, 2, 3]'                           
            iter_lines = f'_isItemInIter({item}, {collection}, True)'
        iter_lines = ast.parse(iter_lines).body #Turn the new code back into an AST (the module body is a list)
        return iter_lines


    def get_iter_code_from_test(self, test: ast.AST) -> list:
        '''
        Checks if the ast.If.test node is an ast.Compare with ast.(Not)?In as ast.Compare.ops[0]
        If so, replaces the keyword 'in' and returns a new AST code object
        ''' 
        iter_lines: list = []
        if isinstance (test, ast.UnaryOp) and isinstance(test.op, ast.Not):
            if isinstance(test.operand, ast.Compare) and isinstance(test.operand.ops[0], (ast.In, ast.NotIn)):                                
                iter_lines = self.get_iter_code_from_compare(test.operand, True)
        elif isinstance (test, ast.Compare) and isinstance(test.ops[0], (ast.In, ast.NotIn)):
                iter_lines = self.get_iter_code_from_compare(test)            
        return iter_lines        
    

    def replace_in_if(self, node_if: ast.If) -> list:
        '''
        Replaces the keyword 'in' where it appears with an 'if'
        e.g. 'if x in <list>' is replaced with a 'while' loop that uses an iter(<list>) object for the check
        '''          
        processed_if: list = []     
        iter_lines = self.get_iter_code_from_test(node_if.test)
        if iter_lines:                    
            node_if.test = iter_lines[0].value                                 
            self.is_iter_func_reqd = True #We need to insert a function that does the if-in check without using in
        processed_if.append(node_if)        
        return processed_if

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
        node_metadata = self.get_node_metadata(node)   
        print(f'entering {node_metadata}')              
        super().generic_visit(node)
        print(f'leaving {node_metadata}')      
        return node

    def visit_Module(self, node: ast.Module) -> Any: 
        '''
        Traverses a 'Module' node (along with its children)
        Checks post-traversal if ast.Module.body has been pruned completely during traversal
        If so, returns an Expr node since an empty module is NOT a valid AST
        '''        
        super().generic_visit(node)
        if not (self.is_valid_body(node.body)):           
            print (f'Entire Module pruned')
            node.body.append(self.get_expr_node_pruned(None)) 
        return node    

    def visit_Call(self, node: ast.Call) -> ast.Call:
        '''
        Transforms a 'call' node encountered while traversing an AST
        It condenses the 'args' field by 'eval'ing it 

        e.g. 'print (True or False)' becomes 'print (True)'
        
        If eval fails, it returns the original node
        ''' 
        if self.mode in (self.EXPAND, self.COLLAPSE) and len(node.args): #Only do this if we're trying to replace and/or/not/in    
            try:            
                val = self.get_node_val(node.args[0])                   
                if Transformer.isprimitive(val):
                    node.args[0] = ast.Constant(value=val) 
                else:
                    super().generic_visit(node) #We need this for any nodes nested within the Call node   
            except Exception as e:
                print (f'Warn: {e}')  #Expression could not be evaluated at compile time (can only happen at run time)        
                super().generic_visit(node) #We need this for any nodes nested within the Call node                   
            return node
        else:
            super().generic_visit(node)
            return node
        
    def get_expr_node_pruned(self, parent: ast.AST) -> ast.Expr:
        '''
        Returns an ast.Expr node to replace a pruned node
        ''' 
        node_name = self.get_Name('print', ast.Load())
        node_call = self.get_Call(node_name, [ast.Constant(value = '<Node pruned>')])
        node_expr = self.get_Expr(node_call)
        node_expr.parent = parent
        return node_expr

    def visit_If(self, node: ast.If) -> Any:
        '''
        Transforms an 'if' node (along with its children) encountered while traversing an AST
        ''' 
        processed_if = []
        node_metadata = self.get_node_metadata(node)   
        print(f'entering {node_metadata}')  
        
        p = node.parent #Get the parent of the current If node
        gp = p.parent #Get the grandparent of the current If node
        
        super().generic_visit(node)
        if self.mode == self.EXPAND:            
            processed_if = self.expand_if (node) #Break down this If node into its logical components
            if not processed_if:
                print (f'Entire sub-tree {node_metadata} pruned')
                processed_if.append(self.get_expr_node_pruned(p))
            return  processed_if    
        elif self.mode == self.COLLAPSE:
            processed_if = self.collapse_if(node) #Roll up nested Ifs into a single ast.BoolOp (op=ast.And)            
            if not processed_if:
                print (f'Entire sub-tree {node_metadata} pruned')
                processed_if.append(self.get_expr_node_pruned(p))
            return  processed_if    
        else:               
            return node
        
    def get_node_metadata(self, node: ast.AST) -> str:
        '''
        Returns info about a node such as lineno, col_offset, parent node
        ''' 
        try:        
            line_info =  f' at line: {node.lineno}, offset: {node.col_offset}'
        except Exception:
            line_info = ''        
        node_metadata = f'{node.__class__.__name__}(parent: {node.parent.__class__.__name__}){line_info}'        
        return node_metadata
    
    def visit_While(self, node: ast.While) -> list:
        '''
        Transforms a 'while' node (along with its children) encountered while traversing an AST         
        ''' 
        processed_while = []
        node_metadata = self.get_node_metadata(node)
        print(f'entering {node_metadata}')  
        super().generic_visit(node)
        if not (self.is_valid_body(node.body)):           
            print (f'Entire sub-tree {node_metadata} pruned')
            node.body = self.get_expr_node_pruned(node.parent)
            processed_while.append(self.get_expr_node_pruned(node.parent))            
        else:
            if (isinstance(node.test, ast.UnaryOp) and isinstance(node.test.op, ast.Not)): #unary boolean                
                node.test = self.get_not_test(node.test.operand)
        processed_while.append(node)        
        
        if node.orelse: #Remove the keyword 'else' if it exists (in a while-else construct)
            processed_while.append(node.orelse)        
            node.orelse = []            
        return processed_while    
        
    def get_not_test(self, test: ast.AST) -> ast.Compare:
        '''
        Returns an ast.Compare node replacing the keyword 'not' in an if/while test
        e.g.  'not (a)' becomes 'False==bool(a)'
        '''  
        node_name = self.get_Name('bool', ast.Load())
        node_call = self.get_Call(node_name, [test])
        node_compare = self.get_Compare(ast.Constant(value = False), [ast.Eq()], [node_call])
        return node_compare

    def get_Assign(self, assign_targets: list, assign_value: ast.AST) -> ast.Assign:
        '''
        Returns an ast.Assign node constructed using the specified parameters
        '''         
        node_Assign = ast.Assign(
            targets=assign_targets,
            value= assign_value
        )
        return node_Assign

    def get_If(self, if_test: ast.AST, if_body: list, if_orelse: list = []) -> ast.If:
        '''
        Returns an ast.If node constructed using the specified parameters
        ''' 
        node_If = ast.If(
            test = if_test,
            body = if_body,
            orelse = if_orelse
        )        
        return node_If
    
    def get_control_node(self, node_control_type: ast.AST, 
                        test: ast.AST = None,  body: list = [], orelse: list = [],
                        handlers: list = [], finalbody: list = [], 
                        exceptType: ast.AST = None, exceptName: str = '',
                        target: ast.AST = None, iter: ast.AST = None,
                        ) -> Any:
        '''
        Returns a control node (ast.(If|Try|While|For|ExceptHandler)) constructed using the specified parameters        
        ''' 
        node_control: ast.AST = None
        match node_control_type:
            case ast.If | ast.While:
                node_control = node_control_type(
                    test = test,
                    body = body,
                    orelse = orelse
                )                
            case ast.Try:
                node_control = node_control_type(                    
                    body = body,
                    handlers = handlers,
                    orelse = orelse,
                    finalbody = finalbody
                )                
            case ast.ExceptHandler:
                node_control = node_control_type(                    
                    type = exceptType,
                    name = exceptName,
                    body = body                    
                )   
            case _:
                raise SyntaxError(f'Unsupported node type {node_control_type}')            
        return  node_control 


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

        e.g.
         
        'not (a and b)' is wrapped logically into: 
        if a:
            if b:
                <a & b> = True
        if <a & b> is False:
            ...

        'not (a or b)' is wrapped logically into: 
        if a:
            <a> = True
        if <a> is False:
            if b:
                <b> = True
        if <a | b> is True:
            ...
        '''     
        node_assign = self.get_Assign([(self.get_Name(if_block_var_id, ast.Store()))], ast.Constant(value=True))  
        processed_list =self.merge_And(lroper, [node_assign])  
        processed_list = self.merge_Or(processed_list, [], if_block_var_id) #Add provision to execute where condition is False (i.e. not True)                                    
        return processed_list 


    def merge_And(self, loper: list, roper: list) -> list:
        '''
        Join/merge left and right operands with the AND operator  
        
        e.g. 'if a' and 'if b' are merged as: 
        if a:
            if b:
                ...
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

        e.g. 'if a' or 'if b' are merged as: 
        if a:
            ...
        if <a> is False:
            if b:
                ...
        '''
        processed_list = []
        node_if: ast.If
        if loper:            
            node_temp_var_name = self.get_Name(if_block_var_id, ast.Load())
            node_if_test = self.get_Compare(node_temp_var_name, [ast.Is()], [ast.Constant(value = False)]) #Add a line that checks if the temp bool is False - we only do the 'OR' part if it is
            self.tmp_bool_access[if_block_var_id] = True           
            node_if = self.get_control_node(ast.If, node_if_test, body=roper)
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
    def isprimitive(val):
        '''
        Checks if a value is of a primitive datatype - bool, int, float, str   
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
            if isinstance(node_if_test.operand, ast.BoolOp): #Negation of boolean expressions
                #Break down the BoolOps
                new_Ifs: list = self.get_Ifs_AndOr(node_if_test.operand, if_block_var_id)
                #Then merge with additional 'not' statements
                node_If_list = self.merge_Not(new_Ifs, if_block_var_id) 

                #To keep the expression as-is:                        
                # node_if = self.get_control_node(ast.If, test=node_if_test)
                # node_If_list.append(node_if)        
            else:
                new_Ifs: list = self.get_Ifs_AndOr(node_if_test.operand, if_block_var_id)        
                last_if: ast.If = new_Ifs[-1]                
                last_if.test = self.get_not_test(last_if.test)
                node_If_list.append(last_if)
        else:            
            node_if = self.get_control_node(ast.If, test=node_if_test)
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

    def is_valid_body(self, body: list) -> bool:
        '''
        Checks if the body of a node is empty
        '''
        is_valid = True
        try:
            if not len(body) or (body[0].value.args[0].value=='<Node pruned>'):
                is_valid = False 
        except Exception as e:                          
            #print (e)
            pass
        return is_valid    

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
                
            
            if self.is_valid_body(node.body):
                #Process if.test and merge if.body               
                new_ifs = self.get_Ifs_AndOr(node.test, if_block_var_id) #Break down the (boolean ops) from test into its individual logical ops
                if new_ifs: #If we have >=1 'if' statements, merge the body with them, otherwise prune the entire branch
                    if split:
                        node_assign_if_pre = self.get_Assign([(self.get_Name(if_block_var_id, ast.Store()))], ast.Constant(value=False)) 
                        processed_if.append(node_assign_if_pre) #Initialise the bool variable for this IF node    
                        node_assign_if_post = self.get_Assign([(self.get_Name(if_block_var_id, ast.Store()))], ast.Constant(value=True)) 
                        node.body.insert(0, node_assign_if_post)  #Prepend to list
                    processed_if.extend(self.merge_And(new_ifs, node.body)) #Add the body to the new Ifs we got from breaking down the test

        #Process if.orelse                               
        if  node.orelse:     
            processed_if = self.merge_Or(processed_if,  node.orelse, if_block_var_id)

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
            if self.is_valid_body(node.body):               
                processed_if.append(node)            
            else: #Not needed, but keeping it here to help clarify logic    
                node = None #Can't have an if without a body, so prune the original if              
            
        
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
            ret_if = self.get_control_node(ast.If, test, node.body, node.orelse)
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
import collections
from operator import contains
a = b= c= ''
if not ((a or b) and c):
    print ('Not test passed')
else:
    print ('Not test failed')

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

if 2 in [1,2,3]:
    if 'love' in 'i love python':
        print ('word test passed')

#2D Matrix (nested 'for') test        
for i in range(2):
    for j in range(2):
        if 'x' not in 'i love python':
            print (f'[{i},{j}]') 

if not (a):
    print ('a is blank')  

counter = 0
while not(counter >= 3 and counter <= 7):
    print(counter)
    counter += 1
else:    
    print('while-else test executed')
'''
def main():   
    '''
    Tests our code
    '''    
    #READ and PARSE the code, generate an AST
    try:
        tree = ast.parse(code1)
        new_tree = None #variable to store transformed AST
        print(ast.dump(tree, indent='   '))


        #VISIT and TRANSFORM the AST    
        
        #Replace keywords 'else/elif/not/and/or in the code
        #new_tree = Transformer().visit(tree) 
        new_tree = Transformer(mode='E', short_circuiting_flag = True).visit(tree) 
        #new_tree = Transformer(mode='C', short_circuiting_flag = True).visit(tree) 
    
        #Replace keyword 'in' in the new AST
        new_tree = TransformerIn().visit(new_tree) if new_tree else TransformerIn().visit(tree)
    
        #Add missing location info to the new nodes and display the new AST
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
    except Exception as e:
        print (f'{type(e).__name__} occurred during AST transformation: {e}')
    
            
if __name__ == '__main__':    
    main()            
