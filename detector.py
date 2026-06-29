import json
from groq import Groq

# Function to detect bugs in Python code using Groq.
def detect_bugs(code: str, api_key: str) -> list:
    """
    Analyzes Python code for potential bugs using Groq (llama-3.3-70b-versatile).
    
    Parameters:
    - code (str): The Python code content to analyze.
    - api_key (str): Groq API key.
    
    Returns:
    - list: A parsed list of dictionaries representing detected bugs.
    """
    try:
        print("[DEBUG] Initializing Groq client...")
        client = Groq(api_key=api_key)
        print("[DEBUG] Groq client initialized successfully.")
        
        system_prompt = "You are a senior Python code reviewer."
        user_message = (
            "You are a strict Python bug detector. "
            "You MUST find bugs. NEVER return an empty array.\n\n"
            "Find ALL of these bug types:\n"
            "1. Division by zero risk\n"
            "2. Index out of range\n"
            "3. TypeError (string + int)\n"
            "4. Missing return statement\n"
            "5. Unclosed file handles\n"
            "6. Empty list operations\n"
            "7. Any other issues\n\n"
            "Code to review:\n"
            f"{code}\n\n"
            "Return ONLY a valid JSON array.\n"
            "No explanation. No markdown. JSON only.\n"
            "Format:\n"
            "[\n"
            "  {\n"
            '    "line_number": 5,\n'
            '    "bug_type": "ZeroDivision",\n'
            '    "description": "Division by zero risk",\n'
            '    "severity": "high"\n'
            "  }\n"
            "]"
        )
        
        print("[DEBUG] Sending request to Groq (llama-3.3-70b-versatile)...")
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.0  # Set low temperature for structured output stability
        )
        print("[DEBUG] Response received from Groq.")
        
        raw_text = chat_completion.choices[0].message.content
        print(f"[DEBUG] Raw response content (length: {len(raw_text)} chars).")
        
        print("[DEBUG] Stripping markdown and cleaning response text...")
        cleaned_text = raw_text.strip()
        if "```json" in cleaned_text:
            cleaned_text = cleaned_text.split("```json")[1]
        elif "```" in cleaned_text:
            cleaned_text = cleaned_text.split("```")[1]
        if "```" in cleaned_text:
            cleaned_text = cleaned_text.split("```")[0]
        cleaned_text = cleaned_text.strip()
        
        print("[DEBUG] Parsing cleaned text with json.loads()...")
        parsed_bugs = json.loads(cleaned_text)
        print(f"[DEBUG] Successfully parsed {len(parsed_bugs)} bug(s).")
        
        if not isinstance(parsed_bugs, list):
            raise ValueError("Parsed JSON is not a list/array.")
            
        return parsed_bugs
        
    except Exception as e:
        print(f"[DEBUG] Error occurred during bug detection: {e}")
        return []
