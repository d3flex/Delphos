import ollama
import json
from textwrap import dedent
from .context_builder import ContextBuilder


def generate_test_scenarios(
    target: str,
    num_scenarios: int = 5,
    model: str = "llama3.2:3b",
    test_type: str = "syscall",
) -> list:
    builder = ContextBuilder()
    context = builder.build_context(target)

    context_text = ""
    for source_name, data in context.items():
        context_text += f"\n=== {source_name.upper()} ===\n{data}\n"

    if not context_text:
        context_text = f"No documentation available for {target}"

    context_description = "syscall" if test_type == "syscall" else f"{test_type} target"

    prompt = dedent(f"""
        You are a Linux kernel testing expert. Generate {num_scenarios} test scenarios
        for the {target} {context_description}.

        Available Context:
        {context_text}

        IMPORTANT CONSTRAINTS - Tests will run as a non-root user:
        - Use /tmp/ for writable paths (e.g., /tmp/test_file)
        - /etc/ files are READ-ONLY (use O_RDONLY)
        - Parent directories must exist (can't create /nonexistent/file)
        - Don't mix contradictory flags (O_RDONLY | O_WRONLY is invalid)
        - Only use the exact target syscall name provided: "{target}"

        For each scenario, provide:
        - id: A unique identifier (e.g., "t001", "t002")
        - description: What the test does
        - test_type: Type of test - use "{test_type}"
        - target: The target name - MUST BE EXACTLY "{target}"
        - params: JSON object with test parameters (path, flags, fd, count, etc.)
        - expected_result: "success" or "error"
        - expected_errno: The errno if error (e.g., "ENOENT"), or null if success

        Focus on realistic edge cases that can actually be tested as a non-root user.

        Return ONLY a valid JSON array, no other text.
        Example format:
        [
          {{
            "id": "t001",
            "description": "Open existing file read-only",
            "test_type": "{test_type}",
            "target": "{target}",
            "params": {{
              "path": "/etc/passwd",
              "flags": "O_RDONLY"
            }},
            "expected_result": "success",
            "expected_errno": null
          }},
          {{
            "id": "t002",
            "description": "Open non-existent file",
            "test_type": "{test_type}",
            "target": "{target}",
            "params": {{
              "path": "/nonexistent/file",
              "flags": "O_RDONLY"
            }},
            "expected_result": "error",
            "expected_errno": "ENOENT"
          }}
        ]
    """).strip()

    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])

    content = response["message"]["content"]

    try:
        # The ollama adds extra text sometimes.
        # We need to extract just the JSON array.
        start_index = content.find('[')
        end_index = content.rfind(']')

        json_str = content[start_index : end_index + 1]
        scenarios = json.loads(json_str)
        return scenarios
    except json.JSONDecodeError as e:
        print(f"Failed to parse LLM response as JSON: {e}")
        print(f"Response was: {content}")
        return []


if __name__ == "__main__":
    print("Generating test scenarios for 'open' syscall...")
    scenarios = generate_test_scenarios(
        target="open", num_scenarios=3, test_type="syscall"
    )
    with open("test_scenarios.json", "w") as test_scenarios:
        json.dump(scenarios, test_scenarios, indent=2)
    print(json.dumps(scenarios, indent=2))
