import sys
import traceback
import json
import pprint

class JupyterStyleDebugger:
    def __init__(self):
        self.history = []
        # Shared namespace for all cells
        self.shared_namespace = {}
        
    def execute_cell(self, code, cell_id):
        """Simulate executing a Jupyter cell"""
        print(f"\n[Cell {cell_id}]: {code}")
        
        # Store variables and their values
        local_vars = {}
        
        try:
            # Execute the code in the shared namespace
            exec(code, globals(), self.shared_namespace)
            
            # Store the variables
            for key, value in self.shared_namespace.items():
                if not key.startswith('__'):
                    local_vars[key] = self._format_value(value)
            
            print(f"✅ Cell executed successfully")
            if local_vars:
                print("Variables in namespace:")
                for key, value in local_vars.items():
                    print(f"  {key} = {value}")
            
            # Add to history
            self.history.append({
                'cell_id': cell_id,
                'code': code,
                'success': True,
                'variables': local_vars
            })
            
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            
            print(f"❌ Error in cell {cell_id}: {type(e).__name__}: {str(e)}")
            
            # Get traceback info
            tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            traceback_str = ''.join(tb_lines)
            
            print("Traceback:")
            print(traceback_str)
            
            # Add to history with error info
            self.history.append({
                'cell_id': cell_id,
                'code': code,
                'success': False,
                'error_type': type(e).__name__,
                'error_message': str(e),
                'traceback': traceback_str
            })
    
    def _format_value(self, value):
        """Format a value for display"""
        if isinstance(value, (int, float, bool, str)):
            return repr(value)
        elif isinstance(value, (list, tuple)) and len(value) <= 5:
            return repr(value)
        elif isinstance(value, dict) and len(value) <= 5:
            return repr(value)
        else:
            return f"{type(value).__name__} object"
    
    def get_history_json(self):
        """Get execution history as JSON"""
        return json.dumps(self.history, indent=2)
    
    def print_history(self):
        """Print execution history in a readable format"""
        print("\n=== JUPYTER NOTEBOOK EXECUTION HISTORY ===")
        for entry in self.history:
            print(f"\nCell {entry['cell_id']}:")
            print(f"Code: {entry['code']}")
            print(f"Success: {entry['success']}")
            
            if entry['success']:
                if entry.get('variables'):
                    print("Variables:")
                    # Only show a few variables for brevity
                    var_items = list(entry['variables'].items())[:5]
                    for key, value in var_items:
                        print(f"  {key} = {value}")
                    if len(entry['variables']) > 5:
                        print(f"  ... and {len(entry['variables']) - 5} more variables")
            else:
                print(f"Error: {entry.get('error_type')}: {entry.get('error_message')}")
                print("Traceback summary:")
                tb_lines = entry.get('traceback', '').split('\n')
                # Print just the last few lines of the traceback for brevity
                for line in tb_lines[-5:]:
                    print(f"  {line}")

# Create a debugger instance
debugger = JupyterStyleDebugger()

# Simulate some Jupyter cells
debugger.execute_cell("x = 10", 1)
debugger.execute_cell("y = 20", 2)
debugger.execute_cell("result = x + y", 3)
debugger.execute_cell("data = {'name': 'Test', 'values': [1, 2, 3]}", 4)
debugger.execute_cell("# This will cause an error\nz = x / (y - 20)", 5)
debugger.execute_cell("# This should work again\nfixed_result = x * 2", 6)

# Print the execution history
debugger.print_history()

# Print the history as JSON (similar to Jupyter notebook format)
print("\n=== JUPYTER NOTEBOOK JSON REPRESENTATION ===")
print(debugger.get_history_json())

