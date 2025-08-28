import sys
import traceback

def function_c(value):
    # This will cause an error
    result = 100 / value
    return result

def function_b(value):
    # Add some context
    modified_value = value - 10
    return function_c(modified_value)

def function_a():
    # Initialize some variables
    starting_value = 10
    try:
        result = function_b(starting_value)
        print(f"Result: {result}")
    except Exception as e:
        print("\n=== ERROR OCCURRED ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        
        print("\n=== TRACEBACK ===")
        traceback.print_exc()
        
        print("\n=== STACK FRAMES ===")
        # Get the current exception info
        exc_type, exc_value, exc_traceback = sys.exc_info()
        
        # Print stack frames
        stack_frames = traceback.extract_tb(exc_traceback)
        for i, frame in enumerate(stack_frames):
            filename, line_number, func_name, text = frame
            print(f"Frame {i}: {func_name} in {filename}:{line_number}")
            print(f"  Code: {text}")
        
        # Print local variables if possible
        print("\n=== LOCAL VARIABLES ===")
        tb = exc_traceback
        while tb:
            frame = tb.tb_frame
            tb = tb.tb_next
            print(f"In function: {frame.f_code.co_name}")
            for key, value in frame.f_locals.items():
                print(f"  {key} = {value}")

# Run the code
function_a()

