#!/usr/bin/env python3
"""
Delphos - AI-Augmented Kernel Testing Framework
Main orchestrator script
"""
import sys
import json
import argparse

from config import DelphosConfig
from generator.llm import generate_test_scenarios
from generator.scenarios import ScenarioManager
from orchestrator_runner import OrchestratorRunner


class Delphos:
    """Main orchestrator for the Delphos testing framework."""

    def __init__(self, config: DelphosConfig):
        """Initialize Delphos with configuration.

        Args:
            config: Configuration object
        """
        self.config = config
        self.scenario_manager = ScenarioManager(config.scenarios_file)
        self.orchestrator = OrchestratorRunner(
            config.orchestrator_dir,
            config.build_release
        )

    def generate_scenarios(self) -> bool:
        """Generate test scenarios using LLM.

        Returns:
            True if successful, False otherwise
        """
        print(f"[1/3] Generating {self.config.num_scenarios} test scenarios "
              f"for '{self.config.syscall_name}'...")

        try:
            scenarios = generate_test_scenarios(
                self.config.syscall_name,
                self.config.num_scenarios
            )

            if not scenarios:
                print("ERROR: Failed to generate scenarios")
                return False

            # Validate scenarios
            valid_scenarios = [
                s for s in scenarios
                if self.scenario_manager.validate_scenario(s)
            ]

            if len(valid_scenarios) != len(scenarios):
                print(f"WARNING: {len(scenarios) - len(valid_scenarios)} "
                      f"invalid scenarios filtered out")

            self.scenario_manager.save_scenarios(valid_scenarios)

            print(f"✓ Generated {len(valid_scenarios)} valid scenarios")
            print(f"  Saved to: {self.config.scenarios_file}")
            return True

        except Exception as e:
            print(f"ERROR: Failed to generate scenarios: {e}")
            return False

    def build_orchestrator(self) -> bool:
        """Build the Rust orchestrator.

        Returns:
            True if successful, False otherwise
        """
        print("[2/3] Building Rust orchestrator...")

        if not self.orchestrator.build():
            print("ERROR: Failed to build orchestrator")
            return False

        print("✓ Orchestrator built successfully")
        return True

    def run_tests(self) -> bool:
        """Execute test scenarios.

        Returns:
            True if successful, False otherwise
        """
        print("[3/3] Executing test scenarios...")

        result = self.orchestrator.run(
            self.config.scenarios_file,
            self.config.results_file,
            capture_output=False
        )

        if result is None:
            print("ERROR: Test execution failed")
            return False

        return True

    def display_results(self) -> None:
        """Display test results."""
        print()
        print("=" * 60)
        print("  Results Summary")
        print("=" * 60)

        if not self.config.results_file.exists():
            print("WARNING: No results file generated")
            return

        with open(self.config.results_file) as f:
            results = json.load(f)

        print(json.dumps(results, indent=2))

        # Summary statistics
        passed = sum(1 for r in results if r.get("passed", False))
        total = len(results)
        print()
        print(f"Tests passed: {passed}/{total}")

    def run(self) -> int:
        """Run the complete Delphos pipeline.

        Returns:
            Exit code (0 for success, 1 for failure)
        """
        print("=" * 60)
        print("  Delphos - AI-Augmented Kernel Testing Framework")
        print("=" * 60)
        print()

        # Step 1: Generate scenarios
        if not self.generate_scenarios():
            return 1
        print()

        # Step 2: Build orchestrator
        if not self.build_orchestrator():
            return 1
        print()

        # Step 3: Run tests
        if not self.run_tests():
            return 1

        # Step 4: Display results
        self.display_results()

        print()
        print("=" * 60)
        print("  Demo Complete!")
        print("=" * 60)

        return 0


def parse_args():
    """Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Delphos - AI-Augmented Kernel Testing Framework"
    )
    parser.add_argument(
        "--syscall",
        default="open",
        help="Syscall to test (default: open)"
    )
    parser.add_argument(
        "--scenarios",
        type=int,
        default=3,
        help="Number of scenarios to generate (default: 3)"
    )
    parser.add_argument(
        "--release",
        action="store_true",
        help="Build orchestrator in release mode"
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    # Create configuration from args
    config = DelphosConfig(
        syscall_name=args.syscall,
        num_scenarios=args.scenarios,
        build_release=args.release
    )

    # Run Delphos
    delphos = Delphos(config)
    exit_code = delphos.run()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
