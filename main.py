#!/usr/bin/env python3
import sys
import json
import argparse
from pathlib import Path

from config import DelphosConfig
from generator.llm import generate_test_scenarios
from generator.scenarios import ScenarioManager
from orchestrator_runner import OrchestratorRunner


def cmd_generate(args, config):
    print("=" * 60)
    print("  Delphos - Test Scenario Generation")
    print("=" * 60)
    print()
    print(f"Target: {args.target}")
    print(f"Environment: {args.environment or 'auto-detect'}")
    print(f"Model: {config.llm_model}")
    print(f"Scenarios: {config.num_scenarios}")
    print()

    scenario_manager = ScenarioManager(config.scenarios_file)

    print(f"Generating {config.num_scenarios} test scenarios for '{args.target}'...")

    try:
        scenarios = generate_test_scenarios(
            args.target,
            config.num_scenarios,
            config.llm_model
        )

        if not scenarios:
            print("ERROR: Failed to generate scenarios")
            return 1

        valid_scenarios = [
            s for s in scenarios
            if scenario_manager.validate_scenario(s)
        ]

        if len(valid_scenarios) != len(scenarios):
            print(f"WARNING: {len(scenarios) - len(valid_scenarios)} "
                  f"invalid scenarios filtered out")

        scenario_manager.save_scenarios(valid_scenarios)

        print(f"✓ Generated {len(valid_scenarios)} valid scenarios")
        print(f"  Saved to: {config.scenarios_file}")
        print()
        print("Preview:")
        print(json.dumps(valid_scenarios[:2], indent=2))
        if len(valid_scenarios) > 2:
            print(f"  ... and {len(valid_scenarios) - 2} more scenarios")

        return 0

    except Exception as e:
        print(f"ERROR: Failed to generate scenarios: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_run(args, config):
    print("=" * 60)
    print("  Delphos - Test Execution")
    print("=" * 60)
    print()

    if not config.scenarios_file.exists():
        print(f"ERROR: Scenarios file not found: {config.scenarios_file}")
        print("Run 'python main.py generate' first to generate test scenarios")
        return 1

    orchestrator = OrchestratorRunner(
        config.orchestrator_dir,
        config.build_release
    )

    print("[1/2] Building Rust orchestrator...")
    if not orchestrator.build():
        print("ERROR: Failed to build orchestrator")
        return 1
    print("✓ Orchestrator built successfully")
    print()

    print("[2/2] Executing test scenarios...")
    result = orchestrator.run(
        config.scenarios_file,
        config.results_file,
        capture_output=False
    )

    if result is None:
        print("ERROR: Test execution failed")
        return 1

    print()
    print("=" * 60)
    print("  Results Summary")
    print("=" * 60)

    if not config.results_file.exists():
        print("WARNING: No results file generated")
        return 1

    with open(config.results_file) as f:
        results = json.load(f)

    print(json.dumps(results, indent=2))

    passed = sum(1 for r in results if r.get("passed", False))
    total = len(results)
    print()
    print(f"Tests passed: {passed}/{total}")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Delphos - AI-Augmented Testing Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate test scenarios"
    )
    generate_parser.add_argument(
        "target",
        help="Target to test (e.g., 'open', 'read', 'write')"
    )
    generate_parser.add_argument(
        "--environment",
        help="Environment info (e.g., 'kernel-6.5', 'glibc-2.38')"
    )
    generate_parser.add_argument(
        "--model",
        default="llama3.2:3b",
        help="LLM model to use (default: llama3.2:3b)"
    )
    generate_parser.add_argument(
        "--scenarios",
        type=int,
        default=5,
        help="Number of test scenarios to generate (default: 5)"
    )

    run_parser = subparsers.add_parser(
        "run",
        help="Execute test scenarios"
    )
    run_parser.add_argument(
        "--scenarios-file",
        default="test_scenarios.json",
        help="Path to scenarios file (default: test_scenarios.json)"
    )
    run_parser.add_argument(
        "--release",
        action="store_true",
        help="Build orchestrator in release mode"
    )
    run_parser.add_argument(
        "--trace-log",
        default="trace.log",
        help="Path to trace log file (default: trace.log)"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    config = DelphosConfig(
        llm_model=getattr(args, 'model', 'llama3.2:3b'),
        num_scenarios=getattr(args, 'scenarios', 5),
        scenarios_file=Path(getattr(args, 'scenarios_file', 'test_scenarios.json')),
        trace_log=Path(getattr(args, 'trace_log', 'trace.log')),
        build_release=getattr(args, 'release', False)
    )

    if args.command == "generate":
        return cmd_generate(args, config)
    elif args.command == "run":
        return cmd_run(args, config)


if __name__ == "__main__":
    sys.exit(main())
