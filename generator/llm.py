import ollama
import json
from textwrap import dedent
from .context_builder import ContextBuilder


def generate_test_scenarios(syscall_name: str, num_scenarios: int = 5, model: str = "llama3.2:3b") -> list:
    builder = ContextBuilder()
    context = builder.build_context(syscall_name)

    context_text = ""
    for source_name, data in context.items():
        context_text += f"\n=== {source_name.upper()} ===\n{data}\n"

    if not context_text:
        context_text = f"No documentation available for {syscall_name}"

    prompt = dedent(f"""
        You are a Linux kernel testing expert. Generate {num_scenarios} test scenarios
        for the {syscall_name} syscall.

        Available Context:
        {context_text}

        For each scenario, provide:
        - id: A unique identifier (e.g., "t001")
        - description: What the test does
        - expected_result: "success" or "error"
        - expected_errno: The errno if error (e.g., "ENOENT"), or null if success

        Focus on edge cases and potential bugs based on the documentation.

        Return ONLY a valid JSON array, no other text.
        Example format:
        [
          {{
            "id": "t001",
            "description": "Test for {syscall_name} syscall",
            "expected_result": "success",
            "expected_errno": null
          }}
        ]
    """).strip()

    response = ollama.chat(
        model=model,
        messages=[{'role': 'user', 'content': prompt}]
    )

    content = response['message']['content']

    try:
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
    with open("test_scenarios.json", "w") as test_scenarios:
        json.dump(scenarios, test_scenarios, indent=2)
    print(json.dumps(scenarios, indent=2))