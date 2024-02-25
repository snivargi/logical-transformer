import ast
from typing import Any

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
    
    # def visit_Module(self, node: ast.Module) -> Any:        
    #     print(f'entering {node.__class__.__name__}')
    #     print(f'parent node {node.parent.__class__.__name__}')
    #     node.body = self.process_stmt_list(node.body)    
    #     return node    

    def visit_If(self, node: ast.If) -> Any:
        return_list = []
        print(f'entering {node.__class__.__name__} at line: {node.lineno} and offset: {node.col_offset}')
        print(f'parent node {node.parent.__class__.__name__}')
        #super().generic_visit(node)

        p = node.parent #Get the parent of the current If node
        gp = p.parent #Get the grandparent of the current If node

        if_block_var_id = f'_boolIf{node.col_offset}'
        node_assign_if = self.get_Assign(if_block_var_id, ast.Store(), False) #self.get_Assign(node_name_if, False)
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
        last_if.body = ast.Pass()
        lroper.append(last_if)
        processed_list =  self.merge_Or(lroper, [], if_block_var_id)
        # lroper.append(f'{spacing}    pass') #If the condition is True, do nothing (pass)
        # lroper = merge_or(lroper, [], level, block) #Add provision to execute where condition is False
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
            #temp_var_id = f'_boolIf{col_offset}'
            node_temp_var_name = self.get_Name(if_block_var_id, ast.Load())
            node_if_test = self.get_Compare(node_temp_var_name, ast.Is(), ast.Constant(value = False))
            node_if = self.get_If(node_if_test, roper)
            roper = [node_if]                
        return  loper + roper

    def get_Ifs_AndOr(self, node_if_test: ast, if_block_var_id):

        node_If_list = []
        if isinstance(node_if_test, ast.BoolOp):           
            for node in node_if_test.values:
                new_Ifs: list = self.get_Ifs_AndOr(node, if_block_var_id)
                if isinstance(node_if_test.op, ast.Or):
                    node_If_list = self.merge_Or(node_If_list, new_Ifs, if_block_var_id)
                elif isinstance(node_if_test.op, ast.And):
                    node_If_list = self.merge_And(node_If_list, new_Ifs)
        elif isinstance(node_if_test, ast.UnaryOp) and isinstance(node_if_test.op, ast.Not): #unary boolean                                    
            if isinstance(node_if_test.operand, ast.BoolOp): #Negation of bracketed boolean expressions more complex than initially anticipated   
                #ToDo: Break down the BoolOps and then merge with additional 'not' statements
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
            node_if = self.get_If(node_if_test, [])
            node_If_list.append(node_if)

        return node_If_list

    def process_stmt_list(self, stmt_list):
        processed_list = []        
        gen = iter(stmt_list) #Use a generator in case the tree is large
        while True:
            try:
                stmt= next(gen)
            except StopIteration:
                break
            print(f'Iterator yielded {stmt.__class__.__name__}')
            if  isinstance(stmt, ast.If):
                if_block_var_id = f'_boolIf{stmt.col_offset}'
                node_assign_if = self.get_Assign(if_block_var_id, ast.Store(), False) #self.get_Assign(node_name_if, False)
                processed_list.append(node_assign_if) #Initialise the bool variable for this IF node
                processed_if = self.process_If (stmt, if_block_var_id)
                processed_list.extend(processed_if)    
            else:
                processed_list.append(stmt) 
        return  processed_list         

    def process_If(self, node: ast.If, if_block_var_id):
        processed_if = []
        
        #Process body
        body = node.body        
        for body_node in body:
            print(f'body has node: {body_node.__class__.__name__}')
            if isinstance(body_node, ast.If): #We need to start breaking up the 'body' into individual IFs
                pass
        processed_body = self.process_stmt_list(body)        
        node_assign_if = self.get_Assign(if_block_var_id, ast.Store(), True) 
        processed_body.insert(0, node_assign_if)

        #Process test
        test = node.test
        new_ifs = self.get_Ifs_AndOr(test, if_block_var_id) #Break down the (boolean ops) from test into its individual logical ops
        processed_if = self.merge_And(new_ifs, processed_body) #Add the body to the new Ifs we got from breaking down the test

        #Process orelse
        orelse = node.orelse
        for orelse_node in orelse:
            print(f'orelse has node: {orelse_node.__class__.__name__}')
            if isinstance(orelse_node, ast.If): #We need to start breaking up the 'orelse' into individual IFs
                pass
        processed_orelse = self.process_stmt_list(orelse)       
        if processed_orelse:     
            processed_if = self.merge_Or(processed_if, processed_orelse, if_block_var_id)


        return processed_if

code = '''
if  not ("False") and not (not True):
    print (True)  
'''
code1 = '''
if  1 or "False" and True:
    print (True)
    if isinstance('T', str):
        print ('Inner if test')
else:    
    print (False)
'''

tree = ast.parse(code)
print(ast.dump(tree, indent='   '))

new_tree = Transformer().visit(tree)
new_tree = ast.fix_missing_locations(new_tree)
print(ast.dump(new_tree, indent='   '))
print(ast.unparse(new_tree))