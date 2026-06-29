import ast
import difflib

# Validates a code fix and evaluates its difference and score.
def validate_fix(original: str, fix: str) -> dict:
    """
    Validates the syntax and structure of a proposed fix against the original code.
    
    Parameters:
    - original (str): The original Python code.
    - fix (str): The proposed Python fix.
    
    Returns:
    - dict: A dictionary containing validation details (is_valid, diff, lines_changed, score).
    """
    try:
        # Check syntax validity
        try:
            ast.parse(fix)
            is_valid = True
        except Exception:
            is_valid = False
            
        # Count lines
        original_lines = original.splitlines()
        fix_lines = fix.splitlines()
        orig_count = len(original_lines)
        fix_count = len(fix_lines)
        
        # Generate unified diff
        diff_generator = difflib.unified_diff(
            original_lines,
            fix_lines,
            fromfile='original',
            tofile='fix',
            lineterm=''
        )
        diff_str = "\n".join(diff_generator)
        
        # Calculate lines changed as absolute difference in line count
        lines_changed = abs(orig_count - fix_count)
        
        # Calculate score
        if not is_valid:
            score = 0.0
        else:
            # 1.0 = valid + shorter (fewer lines or fewer characters) + no parse warnings
            # 0.8 = valid + fewer or equal lines
            # 0.5 = valid syntax
            is_shorter = (fix_count < orig_count) or (len(fix) < len(original))
            if is_shorter:
                score = 1.0
            elif fix_count <= orig_count:
                score = 0.8
            else:
                score = 0.5
                
        return {
            "is_valid": is_valid,
            "diff": diff_str,
            "lines_changed": lines_changed,
            "score": score
        }
    except Exception:
        return {
            "is_valid": False,
            "diff": "",
            "lines_changed": 0,
            "score": 0.0
        }
