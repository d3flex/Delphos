"""Runner for the Rust orchestrator."""

import subprocess
from pathlib import Path
from typing import Optional


class OrchestratorRunner:
    """Manages building and running the Rust test orchestrator."""

    def __init__(self, orchestrator_dir: Path, release: bool = False):
        """Initialize orchestrator runner.

        Args:
            orchestrator_dir: Path to orchestrator directory
            release: Build in release mode
        """
        self.orchestrator_dir = orchestrator_dir
        self.release = release

    def build(self) -> bool:
        """Build the Rust orchestrator.

        Returns:
            True if build succeeded, False otherwise
        """
        cmd = ["cargo", "build"]
        if self.release:
            cmd.append("--release")

        result = subprocess.run(
            cmd, cwd=self.orchestrator_dir, capture_output=True, text=True
        )

        if result.returncode != 0:
            print(f"Build failed:\n{result.stderr}")
            return False

        return True

    def run(
        self, scenarios_file: Path, results_file: Path, capture_output: bool = False
    ) -> Optional[subprocess.CompletedProcess]:
        cmd = [
            "cargo",
            "run",
            "--",
            str(scenarios_file.absolute()),
            str(results_file.absolute()),
        ]

        if self.release:
            cmd.insert(2, "--release")

        result = subprocess.run(
            cmd, cwd=self.orchestrator_dir, capture_output=capture_output, text=True
        )

        if result.returncode != 0:
            if capture_output:
                print(f"Execution failed:\n{result.stderr}")
            return None

        return result
