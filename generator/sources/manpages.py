import subprocess
from .base import DocumentSource


class ManPageSource(DocumentSource):
    def fetch(self, syscall_name: str) -> str:
        result = subprocess.run(
            ["man", "2", syscall_name], capture_output=True, text=True, timeout=10
        )

        if result.returncode != 0:
            return f"Error: Could not find man page for syscall '{syscall_name}'"

        return self._parse_man_page(result.stdout)

    def is_available(self) -> bool:
        try:
            result = subprocess.run(
                ["man", "--version"], capture_output=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def _parse_man_page(self, man_output: str) -> str:
        if not man_output:
            return ""

        sections_to_extract = [
            "NAME",
            "SYNOPSIS",
            "DESCRIPTION",
            "RETURN VALUE",
            "ERRORS",
        ]
        extracted = []

        lines = man_output.split("\n")
        current_section = None
        section_content = []

        for line in lines:
            if line.strip() and line.strip().isupper() and not line.startswith(" "):
                if current_section in sections_to_extract and section_content:
                    extracted.append(f"{current_section}:\n{''.join(section_content)}")

                current_section = line.strip()
                section_content = []
            elif current_section in sections_to_extract:
                section_content.append(line + "\n")

        if current_section in sections_to_extract and section_content:
            extracted.append(f"{current_section}:\n{''.join(section_content)}")

        result = "\n\n".join(extracted)

        if len(result) > 2000:
            result = result[:2000] + "\n... (truncated)"

        return result


if __name__ == "__main__":
    source = ManPageSource()
    print(f"Man pages available: {source.is_available()}")
    print("\nFetching 'open' syscall documentation...")
    docs = source.fetch("open")
    print(docs)
    print(f"\nDocument length: {len(docs)} characters")
