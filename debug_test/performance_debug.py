import sys
import traceback
import json
import time
import random
import gc
from datetime import datetime

class PerformanceDebugger:
    def __init__(self):
        self.history = []
        self.shared_namespace = {}
        self.execution_times = {}
        self.memory_usage = {}
        
    def execute_cell(self, code, cell_id, track_memory=True):
        """Execute a cell of code and track its execution and memory usage"""
        print(f"\n[Cell {cell_id}] Executing: {code[:50]}{'...' if len(code) > 50 else ''}")
        
        # Track execution time
        start_time = time.time()
        
        # Track memory before execution
        if track_memory:
            gc.collect()  # Force garbage collection
            memory_before = self._get_memory_usage()
        
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
            
            # Track memory after execution
            if track_memory:
                gc.collect()  # Force garbage collection
                memory_after = self._get_memory_usage()
                memory_diff = memory_after - memory_before
                self.memory_usage[cell_id] = {
                    'before': memory_before,
                    'after': memory_after,
                    'diff': memory_diff
                }
                memory_info = f" (Memory: {memory_diff/1024/1024:.2f} MB)"
            else:
                memory_info = ""
            
            print(f"✅ Cell executed successfully in {execution_time:.4f} seconds{memory_info}")
            if output.strip():
                print(f"Output:\n{output}")
            
            # Add to history
            history_entry = {
                'cell_id': cell_id,
                'code': code,
                'success': True,
                'execution_time': execution_time,
                'output': output
            }
            
            if track_memory:
                history_entry['memory'] = {
                    'before_mb': memory_before / 1024 / 1024,
                    'after_mb': memory_after / 1024 / 1024,
                    'diff_mb': memory_diff / 1024 / 1024
                }
                
            self.history.append(history_entry)
            
        except Exception as e:
            # Restore stdout
            sys.stdout = original_stdout
            
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
            history_entry = {
                'cell_id': cell_id,
                'code': code,
                'success': False,
                'execution_time': execution_time,
                'error_type': type(e).__name__,
                'error_message': str(e),
                'traceback': traceback_str
            }
            
            if track_memory:
                # Track memory after error
                gc.collect()
                memory_after = self._get_memory_usage()
                memory_diff = memory_after - memory_before
                self.memory_usage[cell_id] = {
                    'before': memory_before,
                    'after': memory_after,
                    'diff': memory_diff
                }
                
                history_entry['memory'] = {
                    'before_mb': memory_before / 1024 / 1024,
                    'after_mb': memory_after / 1024 / 1024,
                    'diff_mb': memory_diff / 1024 / 1024
                }
                
            self.history.append(history_entry)
    
    def _get_memory_usage(self):
        """Get current memory usage in bytes"""
        # This is a simplified approach - in a real notebook you'd use more accurate methods
        # like psutil or memory_profiler
        gc.collect()
        return sys.getsizeof(self.shared_namespace)
    
    def print_performance_summary(self):
        """Print a summary of performance metrics"""
        print("\n=== PERFORMANCE SUMMARY ===")
        total_time = sum(self.execution_times.values())
        success_count = sum(1 for entry in self.history if entry['success'])
        error_count = len(self.history) - success_count
        
        print(f"Total cells executed: {len(self.history)}")
        print(f"Successful cells: {success_count}")
        print(f"Failed cells: {error_count}")
        print(f"Total execution time: {total_time:.4f} seconds")
        
        if self.memory_usage:
            print("\nMemory Usage by Cell:")
            for cell_id, memory in sorted(self.memory_usage.items()):
                status = "✅" if self.history[cell_id-1]['success'] else "❌"
                print(f"  {status} Cell {cell_id}: {memory['diff']/1024/1024:.2f} MB change")
        
        print("\nSlowest Cells:")
        sorted_times = sorted(self.execution_times.items(), key=lambda x: x[1], reverse=True)
        for cell_id, exec_time in sorted_times[:3]:
            status = "✅" if self.history[cell_id-1]['success'] else "❌"
            print(f"  {status} Cell {cell_id}: {exec_time:.4f} seconds")
    
    def get_history_json(self):
        """Get execution history as JSON"""
        return json.dumps(self.history, indent=2)

# Create a debugger instance
debugger = PerformanceDebugger()

# Simulate a performance-focused notebook
debugger.execute_cell("""
# Import necessary libraries
import random
import time
import sys

print("Libraries imported successfully")
""", 1)

debugger.execute_cell("""
# Define a function that's inefficient with memory
def create_large_list(size):
    return [random.random() for _ in range(size)]

# Create a medium-sized list
medium_list = create_large_list(100000)
print(f"Created list with {len(medium_list)} elements")
print(f"First 5 elements: {medium_list[:5]}")
""", 2)

debugger.execute_cell("""
# Define a slow function
def slow_function(iterations):
    start = time.time()
    result = 0
    for i in range(iterations):
        result += i * random.random()
        # Artificial delay
        if i % 10000 == 0:
            time.sleep(0.001)
    end = time.time()
    print(f"slow_function took {end - start:.4f} seconds")
    return result

# Run the slow function
result = slow_function(100000)
print(f"Result: {result:.2f}")
""", 3)

debugger.execute_cell("""
# Create a very large list (potential memory issue)
try:
    # This might cause memory pressure in limited environments
    large_list = create_large_list(1000000)
    print(f"Created large list with {len(large_list)} elements")
except Exception as e:
    print(f"Error creating large list: {e}")
""", 4)

debugger.execute_cell("""
# Optimize the slow function
def optimized_function(iterations):
    start = time.time()
    # Use more efficient approach
    result = sum(i * random.random() for i in range(iterations))
    end = time.time()
    print(f"optimized_function took {end - start:.4f} seconds")
    return result

# Run the optimized function
optimized_result = optimized_function(100000)
print(f"Optimized result: {optimized_result:.2f}")
""", 5)

debugger.execute_cell("""
# Memory cleanup
del medium_list
if 'large_list' in locals() or 'large_list' in globals():
    del large_list
    
# Force garbage collection
import gc
gc.collect()

print("Memory cleaned up")
""", 6)

debugger.execute_cell("""
# Compare performance
def benchmark(func, iterations, runs=3):
    times = []
    for i in range(runs):
        start = time.time()
        func(iterations)
        end = time.time()
        times.append(end - start)
    
    avg_time = sum(times) / len(times)
    print(f"Average time over {runs} runs: {avg_time:.4f} seconds")
    return avg_time

print("Benchmarking slow_function:")
slow_time = benchmark(slow_function, 10000)

print("\\nBenchmarking optimized_function:")
optimized_time = benchmark(optimized_function, 10000)

print(f"\\nSpeedup: {slow_time / optimized_time:.2f}x faster")
""", 7)

# Print performance summary
debugger.print_performance_summary()

# Print the history as JSON (partial)
print("\n=== PERFORMANCE DATA (PARTIAL) ===")
print(json.dumps(debugger.history[:2], indent=2))

