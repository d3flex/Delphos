from .sources.manpages import ManPageSource
from .sources.cve_db import CVEDatabaseSource
from .sources.kernel_docs import KernelDocsSource
from .sources.bug_commits import BugCommitSource
from .sources.vector_store import VectorStoreSource


class ContextBuilder:

    def __init__(self):
        self.sources = {
            'manpages': ManPageSource(),
            'cve_db': CVEDatabaseSource(),
            'kernel_docs': KernelDocsSource(),
            'bug_commits': BugCommitSource(),
            'vector_store': VectorStoreSource(),
        }

    def build_context(self, syscall_name: str) -> dict:
        context = {}

        for name, source in self.sources.items():
            if source.is_available():
                try:
                    data = source.fetch(syscall_name)
                    if data:
                        context[name] = data
                except Exception as e:
                    print(f"Warning: Failed to fetch from {name}: {e}")

        return context

    def get_available_sources(self) -> list:
        return [name for name, source in self.sources.items() if source.is_available()]


if __name__ == "__main__":
    builder = ContextBuilder()
    print(f"Available sources: {builder.get_available_sources()}")
    print("\nBuilding context for 'open' syscall...")
    context = builder.build_context("open")
    for source_name, data in context.items():
        print(f"\n=== {source_name} ===")
        print(data[:200] + "..." if len(data) > 200 else data)
