import sys
import io

def run_student_code(code: str):
    """Executes Python code and returns the printed output or the error."""
    # Create a fake "screen" to capture the print() statements
    fake_screen = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = fake_screen
    
    try:
        # DANGER: exec() runs whatever string you give it as real Python code!
        exec(code)
        
        # Grab whatever was printed to our fake screen
        output = fake_screen.getvalue()
        if not output:
            output = "Code ran successfully but didn't print anything."
            
    except Exception as e:
        # If the student's code crashes, catch the exact error!
        output = f"CRASH! Error: {type(e).__name__}: {str(e)}"
        
    finally:
        # Put the real screen back to normal
        sys.stdout = old_stdout
        
    return output

# --- TEST IT YOURSELF ---
# Uncomment these lines to test if your muscle works!
print(run_student_code("print('Hello World')"))
print(run_student_code("for i in range(3):\n    print(x)"))