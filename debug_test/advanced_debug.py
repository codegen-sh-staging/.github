import sys
import traceback
import json
import time
import random
from datetime import datetime

class AdvancedDebugger:
    def __init__(self):
        self.history = []
        self.shared_namespace = {}
        self.execution_times = {}
        self.cell_outputs = {}
        
    def execute_cell(self, code, cell_id):
        """Execute a cell of code and track its execution"""
        print(f"\n[Cell {cell_id}] Executing: {code[:50]}{'...' if len(code) > 50 else ''}")
        
        # Store variables and their values
        local_vars_before = set(self.shared_namespace.keys())
        
        # Track execution time
        start_time = time.time()
        
        try:
            # Capture stdout
            original_stdout = sys.stdout
            from io import StringIO
            captured_output = StringIO()
            sys.stdout = captured_output
            
            # Execute the code in the shared namespace
            exec(code, globals(), self.shared_namespace)
            
            # Restore stdout
            sys.stdout = original_stdout
            output = captured_output.getvalue()
            
            # Calculate execution time
            end_time = time.time()
            execution_time = end_time - start_time
            self.execution_times[cell_id] = execution_time
            
            # Store the cell output
            self.cell_outputs[cell_id] = output
            
            # Find new or modified variables
            current_vars = set(self.shared_namespace.keys())
            new_vars = current_vars - local_vars_before
            modified_vars = {}
            
            for var in current_vars:
                if not var.startswith('__'):
                    if var in new_vars:
                        modified_vars[var] = self._format_value(self.shared_namespace[var])
            
            print(f"✅ Cell executed successfully in {execution_time:.4f} seconds")
            if output.strip():
                print(f"Output:\n{output}")
            
            if modified_vars:
                print("New/Modified Variables:")
                for key, value in modified_vars.items():
                    print(f"  {key} = {value}")
            
            # Add to history
            self.history.append({
                'cell_id': cell_id,
                'code': code,
                'success': True,
                'execution_time': execution_time,
                'output': output,
                'variables': modified_vars
            })
            
        except Exception as e:
            # Restore stdout
            sys.stdout = sys.__stdout__
            
            exc_type, exc_value, exc_traceback = sys.exc_info()
            
            print(f"❌ Error in cell {cell_id}: {type(e).__name__}: {str(e)}")
            
            # Get traceback info
            tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            traceback_str = ''.join(tb_lines)
            
            print("Traceback:")
            print(traceback_str)
            
            # Calculate execution time until error
            end_time = time.time()
            execution_time = end_time - start_time
            self.execution_times[cell_id] = execution_time
            
            # Add to history with error info
            self.history.append({
                'cell_id': cell_id,
                'code': code,
                'success': False,
                'execution_time': execution_time,
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
            return f"{type(value).__name__} object with {len(value) if hasattr(value, '__len__') else 'unknown'} items"
    
    def get_history_json(self):
        """Get execution history as JSON"""
        return json.dumps(self.history, indent=2)
    
    def print_execution_summary(self):
        """Print a summary of all cell executions"""
        print("\n=== EXECUTION SUMMARY ===")
        total_time = sum(self.execution_times.values())
        success_count = sum(1 for entry in self.history if entry['success'])
        error_count = len(self.history) - success_count
        
        print(f"Total cells executed: {len(self.history)}")
        print(f"Successful cells: {success_count}")
        print(f"Failed cells: {error_count}")
        print(f"Total execution time: {total_time:.4f} seconds")
        
        if error_count > 0:
            print("\nErrors encountered:")
            for entry in self.history:
                if not entry['success']:
                    print(f"  Cell {entry['cell_id']}: {entry.get('error_type')}: {entry.get('error_message')}")
        
        print("\nExecution time by cell:")
        for cell_id, exec_time in sorted(self.execution_times.items()):
            status = "✅" if self.history[cell_id-1]['success'] else "❌"
            print(f"  {status} Cell {cell_id}: {exec_time:.4f} seconds")

# Create a debugger instance
debugger = AdvancedDebugger()

# Simulate a data analysis notebook
debugger.execute_cell("""
# Import necessary libraries
import random
import math
from datetime import datetime

print("Libraries imported successfully")
""", 1)

debugger.execute_cell("""
# Generate some sample data
def generate_data(n=100):
    return [random.randint(1, 100) for _ in range(n)]

data = generate_data()
print(f"Generated {len(data)} data points")
print(f"First 5 elements: {data[:5]}")
""", 2)

debugger.execute_cell("""
# Calculate basic statistics
def calculate_stats(data):
    stats = {
        'min': min(data),
        'max': max(data),
        'mean': sum(data) / len(data),
        'median': sorted(data)[len(data) // 2],
        'sample_size': len(data)
    }
    return stats

stats = calculate_stats(data)
print("Statistics:")
for key, value in stats.items():
    print(f"  {key}: {value}")
""", 3)

debugger.execute_cell("""
# This cell will cause an error - trying to access non-existent data
missing_data = data[1000]
""", 4)

debugger.execute_cell("""
# Create a function with a bug
def process_data(data):
    processed = []
    for item in data:
        # Bug: division by zero when item = 0
        processed.append(100 / item)
    return processed

# Generate data that will trigger the bug
buggy_data = [random.randint(0, 10) for _ in range(20)]
processed = process_data(buggy_data)
""", 5)

debugger.execute_cell("""
# Fix the bug and try again
def process_data_fixed(data):
    processed = []
    for item in data:
        # Fixed: handle division by zero
        if item != 0:
            processed.append(100 / item)
        else:
            processed.append(float('inf'))  # or any other appropriate value
    return processed

processed_fixed = process_data_fixed(buggy_data)
print(f"Processed {len(processed_fixed)} items successfully")
""", 6)

debugger.execute_cell("""
# Create a visualization (simulated)
def create_visualization(data, stats):
    print("Creating visualization...")
    print(f"Data range: {stats['min']} to {stats['max']}")
    
    # Simulate a histogram with ASCII art
    buckets = 10
    bucket_size = (stats['max'] - stats['min']) / buckets
    histogram = [0] * buckets
    
    for value in data:
        bucket = min(int((value - stats['min']) / bucket_size), buckets - 1)
        histogram[bucket] += 1
    
    # Print ASCII histogram
    print("\\nHistogram:")
    max_count = max(histogram)
    for i, count in enumerate(histogram):
        bar_length = int(20 * count / max_count)
        lower = stats['min'] + i * bucket_size
        upper = lower + bucket_size
        print(f"{lower:3.0f}-{upper:3.0f} | {'#' * bar_length} ({count})")
    
    return "Visualization complete"

viz_result = create_visualization(data, stats)
""", 7)

# Print execution summary
debugger.print_execution_summary()

# Print the history as JSON
print("\n=== JUPYTER NOTEBOOK JSON REPRESENTATION (PARTIAL) ===")
print(json.dumps(debugger.history[:2], indent=2))

