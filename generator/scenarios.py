"""Scenario management and storage."""
import json
from pathlib import Path
from typing import List, Dict, Any


class ScenarioManager:
    """Manages test scenario generation and storage."""

    def __init__(self, output_path: Path = Path("test_scenario")):
        self.output_path = output_path

    def save_scenarios(self, scenarios: List[Dict[str, Any]]) -> None:
        """Save scenarios to JSON file.

        Args:
            scenarios: List of test scenario dictionaries
        """
        with open(self.output_path, "w") as f:
            json.dump(scenarios, f, indent=2)

    def load_scenarios(self) -> List[Dict[str, Any]]:
        """Load scenarios from JSON file.

        Returns:
            List of test scenario dictionaries
        """
        if not self.output_path.exists():
            return []

        with open(self.output_path) as f:
            return json.load(f)

    def validate_scenario(self, scenario: Dict[str, Any]) -> bool:
        """Validate a scenario has required fields.

        Args:
            scenario: Scenario dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["id", "description", "expected_result"]
        return all(field in scenario for field in required_fields)
