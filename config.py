from pathlib import Path
from dataclasses import dataclass


@dataclass
class DelphosConfig:
    llm_model: str = "llama3.2:3b"
    num_scenarios: int = 5
    scenarios_file: Path = Path("test_scenarios.json")
    results_file: Path = Path("test_results.json")
    trace_log: Path = Path("trace.log")
    orchestrator_dir: Path = Path("orchestrator")
    build_release: bool = False

    def __post_init__(self):
        if isinstance(self.scenarios_file, str):
            self.scenarios_file = Path(self.scenarios_file)
        if isinstance(self.results_file, str):
            self.results_file = Path(self.results_file)
        if isinstance(self.trace_log, str):
            self.trace_log = Path(self.trace_log)
        if isinstance(self.orchestrator_dir, str):
            self.orchestrator_dir = Path(self.orchestrator_dir)
