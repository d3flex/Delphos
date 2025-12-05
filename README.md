# Delphos - ALM Testing Framework

Delphos is an open-source project that aims to explore the area of AI augmented
testing. The goal is to create a framework that can generate test scenarios,
provided a fresh eye in the testing process and help to find vulnerabilities
earlier and based on the experience of previous knownledge.

## Motivation

The idea is inspired from various resources and previous researches
in this field, such as [this paper](https://arxiv.org/pdf/2305.18323)
or [this video](https://www.youtube.com/watch?v=9Fr8KxeKvKI)

There are already some tools that can implementations in the field, such as 
[Google's OSS-Fuzz](https://github.com/google/oss-fuzz) which uses ML for
coverage-guided fuzzing. However, it supports specific languages at the
current state, and despite its open-source nature, a software is required to
be registered in order to run the tool.

## Design goals

Therefore, the idea here is to use common available tools such as [ollama](https://ollama.com/)
and known collection of datasets like commit history, documentation and CVE
databases to generate test scenarios.

For the approach, we will be using Rust and Python, for the following reasons.
Rust is a modern language which offers a lot of features such as type safety, memory safety,
and concurrency. It also has a lot of libraries that can help with testing, such libbpf-rs and
libc. This can be used as the test engine for the execution. Python in other hand, has strong
support for the LLM and Data analysis through many available libraries.

Python: AI Test Generator -> Rust: scheduling -> Rust: testing

The design should provide easy adaption and extensions, in order to be able to
run against many use case and a variety of software. The idea is to start with 
a simple kernel testing, but generalize the implementation for web applications,
and eventually other types of applications.

As part of the HackWeek, the goal is to have a basic eBPF tracing for one syscall.

A risk plan, at least for the first week, can be found in [docs/delphos_week1_plan.md](docs/delphos_week1_plan.md)

## How to use

Delphos has two main commands: `generate` and `run`.

### 1. Generate test scenarios

```bash
python main.py generate open --environment kernel-6.5
```

This will:
- Analyze the target (e.g., `open` syscall)
- Fetch documentation from available sources (man pages, CVE databases, etc.)
- Use LLM to generate test scenarios based on the environment
- Save scenarios to `test_scenarios.json`

**Options:**
- `--model`: LLM model to use (default: `llama3.2:3b`)
- `--scenarios`: Number of scenarios to generate (default: 5)
- `--test-type`: Test type (e.g., `syscall`, `procfs`, `sysfs`) (default: `syscall`)
- `--environment`: Target environment (e.g., `kernel-6.5`, `glibc-2.38`)

**Examples:**
```bash
# Generate 10 scenarios for 'read' syscall
python main.py generate read --scenarios 10

# Use a different model
python main.py generate open --model llama3.1:8b

# Specify environment
python main.py generate write --environment kernel-6.5

# Test procfs targets
python main.py generate /proc/meminfo --test-type procfs --scenarios 5
```

### 2. Run test scenarios

```bash
python main.py run
```

This will:
- Build the Rust test delph
- Execute all test scenarios from `test_scenarios.json`
- Save results to `test_results.json`
- Display summary

**Options:**
- `--scenarios-file`: Custom scenarios file (default: `test_scenarios.json`)
- `--release`: Build delph in release mode
- `--trace-log`: Path for trace log (default: `trace.log`)

**Example:**
```bash
# Run with custom scenarios file
python main.py run --scenarios-file my_tests.json

# Build in release mode for performance
python main.py run --release
```

### Configuration

Core settings in `config.py`:
- `llm_model`: LLM model name
- `num_scenarios`: Number of scenarios to generate
- `scenarios_file`: Path to scenarios JSON file
- `results_file`: Path to results JSON file
- `trace_log`: Path to eBPF trace log

### Quick Demo

```bash
# Full workflow
python main.py generate open --scenarios 5
python main.py run
```