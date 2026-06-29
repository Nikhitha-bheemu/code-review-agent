import ast
from groq import Groq

# Evaluates the score of a fix candidate compared to the original code.
def score_fix(original: str, fix: str) -> float:
    """
    Evaluates the quality of a fix candidate.
    
    Parameters:
    - original (str): The original Python code.
    - fix (str): The proposed Python fix.
    
    Returns:
    - float: Quality score (0.0 for syntax errors, >= 1.0 for valid code).
    """
    try:
        ast.parse(fix)
    except Exception:
        return 0.0
        
    score = 1.0
    
    original_lines = len(original.splitlines())
    fix_lines = len(fix.splitlines())
    if fix_lines < original_lines:
        score += 0.3
        
    if len(fix) < len(original):
        score += 0.2
        
    return score

# Performs line-level crossover between two fix candidates.
def crossover(fix1: str, fix2: str) -> str:
    """
    Combines the first half of fix1's lines with the second half of fix2's lines.
    
    Parameters:
    - fix1 (str): First parent fix.
    - fix2 (str): Second parent fix.
    
    Returns:
    - str: Combined fix code.
    """
    lines1 = fix1.splitlines()
    lines2 = fix2.splitlines()
    
    half1 = len(lines1) // 2
    half2 = len(lines2) // 2
    
    combined_lines = lines1[:half1] + lines2[half2:]
    return "\n".join(combined_lines)

# Mutates a fix candidate slightly using the Groq API.
def mutate(fix: str, api_key: str) -> str:
    """
    Slightly improves a Python fix candidate using Groq.
    
    Parameters:
    - fix (str): The code to mutate.
    - api_key (str): Groq API key.
    
    Returns:
    - str: Mutated/improved Python code.
    """
    try:
        client = Groq(api_key=api_key)
        user_message = f"Improve this Python fix slightly. Return only the improved code. No explanation.\n\n{fix}"
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        
        mutated_code = response.choices[0].message.content.strip()
        
        # Clean markdown code blocks if returned
        if "```python" in mutated_code:
            mutated_code = mutated_code.split("```python")[1].split("```")[0].strip()
        elif "```" in mutated_code:
            mutated_code = mutated_code.split("```")[1].split("```")[0].strip()
            
        return mutated_code
    except Exception as e:
        print(f"[DEBUG] Mutation failed: {e}. Returning original fix.")
        return fix

# Evolves a fix candidate over multiple generations using genetic algorithms.
def evolve_fix(code: str, bug: dict, api_key: str) -> str:
    """
    Finds the best bug fix candidate using a genetic algorithm over 3 generations.
    
    Parameters:
    - code (str): The original Python code.
    - bug (dict): Bug dictionary with line_number, bug_type, description, severity.
    - api_key (str): Groq API key.
    
    Returns:
    - str: The evolved bug fix code.
    """
    first_candidate = None
    try:
        client = Groq(api_key=api_key)
        candidates = []
        
        print("[DEBUG] Generating 4 initial fix candidates...")
        for i in range(4):
            user_prompt = (
                f"Please fix the bug in this Python code.\n\n"
                f"Code:\n{code}\n\n"
                f"Bug Details:\n"
                f"- Line: {bug.get('line_number')}\n"
                f"- Type: {bug.get('bug_type')}\n"
                f"- Description: {bug.get('description')}\n\n"
                f"Return ONLY the corrected Python code. No explanation. No markdown."
            )
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8
            )
            candidate = response.choices[0].message.content.strip()
            
            # Clean markdown code blocks if returned
            if "```python" in candidate:
                candidate = candidate.split("```python")[1].split("```")[0].strip()
            elif "```" in candidate:
                candidate = candidate.split("```")[1].split("```")[0].strip()
                
            candidates.append(candidate)
            if i == 0:
                first_candidate = candidate
                
        population = candidates
        
        for gen in range(3):
            scores = [score_fix(code, candidate) for candidate in population]
            # Print generation scores to console
            print(f"Generation {gen + 1} scores: {scores}")
            
            # Keep top 2
            scored_pop = sorted(zip(population, scores), key=lambda x: x[1], reverse=True)
            parent1 = scored_pop[0][0]
            parent2 = scored_pop[1][0]
            
            # Crossover
            child1 = crossover(parent1, parent2)
            child2 = crossover(parent2, parent1)
            
            # Mutate
            mutated_child1 = mutate(child1, api_key)
            mutated_child2 = mutate(child2, api_key)
            
            # New population
            population = [parent1, parent2, mutated_child1, mutated_child2]
            
        # Final scoring and selection
        final_scores = [score_fix(code, candidate) for candidate in population]
        print(f"Final generation scores: {final_scores}")
        best_idx = final_scores.index(max(final_scores))
        return population[best_idx]
        
    except Exception as e:
        print(f"[DEBUG] Error in evolve_fix: {e}")
        if first_candidate is not None:
            return first_candidate
        return code
