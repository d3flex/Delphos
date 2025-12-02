"""Test scenario generator using LLM for Delphos."""
import ollama
import json
from textwrap import dedent


def generate_test_scenarios(syscall_name: str, num_scenarios: int = 5) -> list:
    """Generate test scenarios for a given syscall using LLM.
    
    Args:
        syscall_name: Name of the syscall (e.g., "open", "read")
        num_scenarios: Number of test scenarios to generate
        
    Returns:
        List of test scenario dictionaries
    """
    prompt = dedent(f"""
        You are a Linux kernel testing expert. Generate {num_scenarios} test scenarios
        for the {syscall_name} syscall.

        For each scenario, provide:
        - id: A unique identifier (e.g., "t001")
        - description: What the test does
        - expected_result: "success" or "error"
        - expected_errno: The errno if error (e.g., "ENOENT"), or null if success

        Return ONLY a valid JSON array, no other text.
        Example format:
        [
          {{
            "id": "t001",
            "description": "Open existing file read-only",
            "expected_result": "success",
            "expected_errno": null
          }}
        ]
    """).strip()
    
    response = ollama.chat(
        model='llama3.2:3b',
        messages=[{'role': 'user', 'content': prompt}]
    )
    
    # Extract the response content
    content = response['message']['content']
    
    # Try to parse as JSON
    
    try:
        # Remove markdown code blocks if present
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0]
        elif '```' in content:
            content = content.split('```')[1].split('```')[0]
        
        scenarios = json.loads(content.strip())
        return scenarios
    except json.JSONDecodeError as e:
        print(f"Failed to parse LLM response as JSON: {e}")
        print(f"Response was: {content}")
        return []


if __name__ == "__main__":
    print("Generating test scenarios for 'open' syscall...")
    scenarios = generate_test_scenarios("open", 3)
    with open("test_scenario", "w") as test_scenarios:
        json.dump(scenarios, test_scenarios, indent=2)
    print(json.dumps(scenarios, indent=2))