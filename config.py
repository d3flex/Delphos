from pathlib import Path
from dataclasses import dataclass


@dataclass
class DelphosConfig:
    """Configuration for Delphos test framework."""

    # Generator settings
    syscall_name: str = "open"
    num_scenarios: int = 3
    llm_model: str = "llama3.2:3b"

    # File paths
    scenarios_file: Path = Path("test_scenario.json")
    results_file: Path = Path("results.json")
    trace_log: Path = Path("trace.log")

    # Orchestrator settings
    orchestrator_dir: Path = Path("orchestrator")
    build_release: bool = False

    # Tracer settings
    enable_tracing: bool = False
    tracer_script: Path = Path("tracer/fileops.bt")

    def __post_init__(self):
        """Convert string paths to Path objects."""
        if isinstance(self.scenarios_file, str):
            self.scenarios_file = Path(self.scenarios_file)
        if isinstance(self.results_file, str):
            self.results_file = Path(self.results_file)
        if isinstance(self.trace_log, str):
            self.trace_log = Path(self.trace_log)
        if isinstance(self.orchestrator_dir, str):
            self.orchestrator_dir = Path(self.orchestrator_dir)
        if isinstance(self.tracer_script, str):
            self.tracer_script = Path(self.tracer_script)
