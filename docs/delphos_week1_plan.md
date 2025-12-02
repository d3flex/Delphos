# Week 1 Planning: AI-Augmented Kernel Testing Framework MVP

**Project Name:** Delphos  
**Goal:** Build a minimal viable prototype that demonstrates AI-augmented testing for Linux kernel syscalls  
**Timeline:** 5 days  
**Developer:** Solo project, part-time effort (~3-4 hours/day)  
**Note:** Developer is learning Rust basics during this project

---

## Week 1 Objectives

By the end of week 1, we will have:

1. ✅ Development environment set up (Rust + Python)
2. ✅ Basic eBPF tracing capturing syscall activity
3. ✅ Local LLM generating test scenarios from syscall documentation
4. ✅ 5-10 executable test cases for a single syscall family
5. ✅ Simple pass/fail validation mechanism
6. ✅ End-to-end demo working on local machine

**Non-goals for Week 1:**
- Vector database integration (defer to Week 2)
- Complex ML models (defer to Week 2)
- Web UI or fancy reporting (defer to Week 3)
- Multiple syscall families (start with ONE)
- Performance optimization (focus on correctness first)

---

## Project Structure 
/Approxiammetely as per AI suggest/
mostly bootstrabbed by cargo and uv.

```
delphos/
├── rust/              # Rust workspace
│   ├── orchestrator/  # Main orchestration
│   │   ├── Cargo.toml
│   │   └── src/
│   └── ebpf-tracer/   # eBPF instrumentation (Week 2)
├── python/            # Python components
│   ├── ai_generator/  # LLM integration
│   │   ├── __init__.py
│   │   ├── generator.py
│   │   └── doc_parser.py
│   └── analyzer/      # Result analysis
│       └── __init__.py
├── pyproject.toml     # Python dependencies (uv managed)
├── uv.lock            # Locked dependencies
├── scripts/           # Helper scripts
│   ├── run_demo.sh
│   └── trace_fileops.bt
├── docs/              # Documentation
│   ├── daily_log.org  # Org-mode daily log
│   ├── architecture.md
│   └── week1_retrospective.md
├── tests/             # Integration tests
├── scenarios.json     # Generated test scenarios
├── results.json       # Test execution results
└── README.md
```

---

## Day-by-Day Breakdown

### Day 1: Environment Setup + Rust Basics
**Time: 3-4 hours**

**Tasks:**
1. Set up project structure (see above)

2. Install dependencies
   - Rust toolchain (rustup)
   - Python 3.10+
   - **uv** (modern Python package manager): `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Ollama + llama3.1:8b model
   - bpftrace or bpftrace development tools
   - Git

3. **Rust learning time** (1.5-2 hours)
   - Complete "Getting Started" from official Rust book (chapters 1-3)
   - Focus on: variables, functions, basic types, ownership basics
   - Run simple "Hello World" and basic examples
   - Goal: Understand enough to read and modify simple Rust code

4. Create basic project skeleton
   - Cargo workspace setup: `cargo new orchestrator --bin`
   - Python environment with uv: `uv venv` and `uv pip install ollama`
   - Create `pyproject.toml` for dependency management
   - Cargo.toml with dependencies

5. Document architecture decisions
   - Why Rust + Python hybrid
   - Communication protocol (JSON files for now - simpler than stdin/stdout)
   - Which syscall family to start with (recommendation: file operations)

**Deliverable:** 
- Working dev environment
- Project structure committed to git
- `docs/architecture.md` with design decisions
- Rust basics understood enough to proceed
- First entry in `docs/daily_log.org`

**Success Criteria:**
- `cargo build` works in rust/orchestrator
- `python --version` shows 3.10+
- `uv --version` shows uv is installed
- `ollama run llama3.1:8b` responds
- Can read and understand simple Rust examples
- `pyproject.toml` exists with ollama dependency

**Rust Learning Resources for Day 1:**
- https://doc.rust-lang.org/book/ch01-00-getting-started.html
- https://doc.rust-lang.org/book/ch03-00-common-programming-concepts.html
- Rustlings exercises (optional): https://github.com/rust-lang/rustlings

---

### Day 2: eBPF Tracing + Python LLM Integration
**Time: 3-4 hours**

**Tasks:**
1. Create basic eBPF probe using bpftrace (NOT Rust yet)
   - Trace: `sys_enter_openat`, `sys_enter_read`, `sys_enter_write`, `sys_exit_close`
   - Capture: PID, syscall arguments, return values

2. **Use bpftrace for Week 1** (defer Rust eBPF to Week 2)
   ```bash
   # trace_fileops.bt
   tracepoint:syscalls:sys_enter_openat {
       printf("%d: openat(%s, %d)\n", pid, str(args->filename), args->flags);
   }
   
   tracepoint:syscalls:sys_exit_openat {
       printf("%d: openat returned %d\n", pid, args->ret);
   }
   ```

3. Test with simple workload
   ```bash
   # Terminal 1: start tracing
   sudo bpftrace trace_fileops.bt > trace.log
   
   # Terminal 2: generate syscalls
   cat /etc/passwd
   echo "test" > /tmp/testfile
   rm /tmp/testfile
   ```

4. **Start Python LLM integration** (parallel task)
   - Create basic module to call Ollama
   - Parse man page for `open(2)` syscall
   - Generate ONE test scenario as proof of concept

**Deliverable:**
- Working eBPF trace script
- Sample trace output showing 10+ syscall events
- Python script that calls Ollama successfully
- One LLM-generated test scenario
- `docs/daily_log.org` updated

**Success Criteria:**
- Can see file operations from test workload in trace
- Trace includes filenames and return codes
- Python can communicate with Ollama
- LLM produces a reasonable test idea

**Why bpftrace instead of Rust eBPF?**
- Much faster to prototype
- No need to learn Rust eBPF yet
- Good enough for Week 1 validation
- Can migrate to Rust in Week 2 if needed

---

### Day 3: Complete Test Generator + Rust Learning
**Time: 3-4 hours**

**Tasks:**
1. **Rust learning time** (1 hour)
   - Rust book chapters 4-5: Ownership, structs
   - Focus on: How to read/write JSON in Rust
   - Learn `serde` crate basics
   - Practice: Write simple program that reads JSON file

2. Complete Python test generator
   ```python
   # python/ai_generator/generator.py
   import ollama
   import subprocess
   import json
   
   def get_syscall_docs(syscall_name):
       """Extract relevant sections from man page"""
       result = subprocess.run(['man', '2', syscall_name], 
                               capture_output=True, text=True)
       return parse_man_page(result.stdout)
   
   def generate_test_scenarios(syscall_name):
       """Use LLM to generate test scenarios"""
       docs = get_syscall_docs(syscall_name)
       
       prompt = f"""
       You are a Linux kernel testing expert.
       
       Syscall: {syscall_name}
       Documentation: {docs}
       
       Generate 5 test scenarios in JSON format:
       [
         {{
           "id": "test_001",
           "description": "Test normal file open",
           "syscall": "open",
           "args": {{"/tmp/test.txt", "O_RDONLY"}},
           "expected_result": "success",
           "expected_errno": null
         }},
         ...
       ]
       
       Focus on edge cases and potential bugs.
       """
       
       response = ollama.chat(
           model='llama3.1:8b',
           messages=[{'role': 'user', 'content': prompt}]
       )
       
       return parse_llm_response(response)
   ```

3. Generate 5-10 test scenarios for `open()` syscall
   - Save as `scenarios.json`
   - Validate JSON is well-formed
   - Review scenarios manually - are they good?

4. Create simple Python script runner
   ```bash
   python python/main.py --syscall open --output scenarios.json
   ```

**Deliverable:**
- Complete Python test generator
- `scenarios.json` with 5-10 test scenarios
- Understanding of Rust JSON handling (for tomorrow)
- `docs/daily_log.org` updated

**Success Criteria:**
- Can generate scenarios on demand
- Scenarios are specific and actionable
- JSON format is valid
- Comfortable reading Rust structs and JSON code

**Rust Learning Resources for Day 3:**
- https://doc.rust-lang.org/book/ch04-00-understanding-ownership.html
- https://serde.rs/ (Quick start guide)
- Example: https://github.com/serde-rs/json

---

### Day 4: Rust Test Executor
**Time: 3-4 hours**

**Tasks:**
1. **Rust learning/practice** (1 hour)
   - Review example Rust programs that call libc
   - Understand `unsafe` blocks (needed for syscalls)
   - Practice with simple file operations in Rust

2. Create minimal Rust test executor
   ```rust
   // rust/orchestrator/src/main.rs
   use serde::{Deserialize, Serialize};
   use std::fs;
   
   #[derive(Deserialize, Debug)]
   struct TestScenario {
       id: String,
       description: String,
       syscall: String,
   }
   
   #[derive(Serialize)]
   struct TestResult {
       id: String,
       passed: bool,
       message: String,
   }
   
   fn main() {
       // Read scenarios.json
       let data = fs::read_to_string("scenarios.json")
           .expect("Failed to read scenarios");
       
       let scenarios: Vec<TestScenario> = 
           serde_json::from_str(&data)
           .expect("Failed to parse JSON");
       
       // Execute each test (simplified for now)
       let mut results = Vec::new();
       for scenario in scenarios {
           let result = execute_test(&scenario);
           results.push(result);
       }
       
       // Write results
       let json = serde_json::to_string_pretty(&results).unwrap();
       fs::write("results.json", json).unwrap();
   }
   
   fn execute_test(scenario: &TestScenario) -> TestResult {
       // For Week 1: Just do basic open() test
       // We'll expand this in Week 2
       match scenario.syscall.as_str() {
           "open" => test_open(),
           _ => TestResult {
               id: scenario.id.clone(),
               passed: false,
               message: "Syscall not implemented".to_string(),
           }
       }
   }
   
   fn test_open() -> TestResult {
       use std::ffi::CString;
       
       let path = CString::new("/etc/passwd").unwrap();
       let fd = unsafe {
           libc::open(path.as_ptr(), libc::O_RDONLY)
       };
       
       let passed = fd >= 0;
       if fd >= 0 {
           unsafe { libc::close(fd) };
       }
       
       TestResult {
           id: "test_open".to_string(),
           passed,
           message: if passed { 
               "Successfully opened file".to_string() 
           } else { 
               "Failed to open file".to_string() 
           },
       }
   }
   ```

3. Add dependencies to Cargo.toml
   ```toml
   [dependencies]
   serde = { version = "1.0", features = ["derive"] }
   serde_json = "1.0"
   libc = "0.2"
   ```

4. Test the executor
   ```bash
   cd rust/orchestrator
   cargo build
   cargo run
   cat results.json
   ```

**Deliverable:**
- Working Rust executor that reads JSON and runs tests
- `results.json` with at least one successful test
- `docs/daily_log.org` updated

**Success Criteria:**
- Rust code compiles without errors
- Can execute at least 2-3 basic test scenarios
- Results are written to JSON correctly
- Understand the code well enough to modify it

**Note:** Keep it simple! We're not trying to implement all test types yet. Just prove that Rust can read JSON, call a syscall, and write results.

---

### Day 5: Integration, Demo & Documentation
**Time: 4-5 hours (slightly longer for demo prep)**

**Tasks:**
1. **Integration** (1.5 hours)
   - Create end-to-end script `run_demo.sh`
   ```bash
   #!/bin/bash
   set -e
   
   echo "=== Delphos Demo ==="
   echo
   
   echo "Step 1: Generating test scenarios..."
   python python/main.py --syscall open --output scenarios.json
   
   echo "Step 2: Executing tests..."
   cd rust/orchestrator && cargo run --quiet
   cd ../..
   
   echo "Step 3: Results:"
   cat results.json
   
   echo
   echo "Demo complete!"
   ```

   - Test full pipeline multiple times
   - Fix any integration issues
   - Add error handling

2. **Add eBPF validation** (1 hour)
   - Run tests under eBPF tracing
   - Compare expected vs actual syscalls
   - Save trace output alongside results
   ```bash
   # Enhanced demo with tracing
   sudo bpftrace trace_fileops.bt > trace.log &
   TRACE_PID=$!
   
   cargo run
   
   kill $TRACE_PID
   echo "Trace saved to trace.log"
   ```

3. **Create demo materials** (1 hour)
   - Write `README.md` with:
     - What is Delphos?
     - Installation instructions
     - How to run the demo
     - What to expect
   - Add example output
   - Include screenshots/terminal output

4. **Documentation** (1 hour)
   - Complete `docs/architecture.md`
   - Write `docs/week1_retrospective.md`
     - What worked well?
     - What was challenging?
     - What did we learn?
     - Surprises?
   - Update `docs/daily_log.org` with final entry

5. **Plan Week 2** (30 minutes)
   - Review Week 1 goals vs. actual achievements
   - List concrete next steps
   - Identify blockers or needed learning
   - Draft `docs/week2_plan.md` outline

**Deliverable:**
- Working end-to-end demo
- Complete documentation
- Demo video/recording (optional but recommended)
- Week 2 plan outline
- `docs/daily_log.org` complete for Week 1

**Success Criteria:**
- Can run `./run_demo.sh` from clean state
- Demo shows full workflow in < 5 minutes
- Someone else could follow README and run demo
- Have concrete data: X tests generated, Y passed, Z failed
- Clear understanding of what to do next

---

## Week 1 Definition of Done

We can confidently say Week 1 is complete when:

1. ✅ Code is committed to git with clear commit messages
2. ✅ `./run_demo.sh` executes successfully from fresh clone
3. ✅ README explains project and how to run demo
4. ✅ At least 3-5 test scenarios execute successfully
5. ✅ Results show pass/fail clearly
6. ✅ eBPF trace validates test execution
7. ✅ `docs/daily_log.org` documents the journey
8. ✅ Week 2 plan drafted based on learnings

---

## Key Decisions to Make

### Decision 1: Which Syscall Family?
**Recommendation:** Start with **file operations** (open, read, write, close)

**Why?**
- Well-documented (good man pages)
- Easy to test (don't need special hardware)
- Common source of bugs (many CVEs)
- Simple to validate (check files on disk)

**Alternative:** Network syscalls (socket, bind, connect)
- More complex, leave for Week 2

---

### Decision 2: eBPF Tooling
**Option A: bpftrace (Recommended for Week 1)**
- Pros: Fast to prototype, simple scripts
- Cons: Less control, harder to integrate

**Option B: Rust + aya/libbpf-rs**
- Pros: Type-safe, better integration
- Cons: Steeper learning curve

**Recommendation:** Start with bpftrace, migrate to Rust in Week 2 if needed

---

### Decision 3: LLM Model
**Recommendation:** llama3.1:8b via Ollama

**Why?**
- Runs locally (no API costs)
- Good enough for test generation
- Fast inference on modern CPU
- Easy to set up

**Fallback:** If local model struggles, use Claude API for complex reasoning

---

## Success Metrics for Week 1

At the end of Week 1, we should be able to answer YES to:

- [ ] Can we generate test scenarios using LLM from syscall documentation?
- [ ] Can we execute those scenarios and get results?
- [ ] Can we capture runtime behavior with eBPF?
- [ ] Does the end-to-end pipeline work?
- [ ] Did we find at least one interesting test case we wouldn't have thought of manually?

**Stretch Goals (if time permits):**
- [ ] Test 2 syscall families instead of 1
- [ ] Add ChromaDB integration (basic)
- [ ] Create simple web UI for viewing results

---

## Risk Mitigation

### Risk 1: Learning Rust while building
**Impact: High** - Could slow down development significantly  
**Mitigation:** 
- Allocate dedicated learning time each day (Days 1, 3)
- Keep Rust code simple - no advanced features in Week 1
- Use bpftrace instead of Rust eBPF to reduce complexity
- Have Python handle complex logic, Rust for simple execution
- Use lots of examples and copy-paste-modify approach
- Focus on reading/understanding code first, writing second

### Risk 2: eBPF is hard to debug
**Impact: Medium** - Kernel tracing can be finicky  
**Mitigation:** 
- Use bpftrace (simpler than writing eBPF in C/Rust)
- Start with existing examples
- Test on non-critical syscalls (file ops, not memory management)
- Keep probes simple - just capture, don't filter complex logic

### Risk 3: LLM generates nonsense
**Impact: Medium** - AI might produce useless tests  
**Mitigation:** 
- Manually review generated scenarios
- Have 2-3 hand-written fallback tests
- Iterate on prompts to improve quality
- Accept that some tests will be bad - that's okay for Week 1

### Risk 4: Running out of time (5 days is tight!)
**Impact: High** - Most likely risk  
**Mitigation:** 
- Cut scope aggressively if needed
- Demo with 3 tests is better than no demo
- Python-only version is acceptable if Rust is too hard
- Focus on showing the concept, not perfect implementation

### Risk 5: Integration issues between Python and Rust
**Impact: Medium** - JSON communication might have bugs  
**Mitigation:**
- Use simple file-based JSON exchange (not pipes/IPC)
- Validate JSON schemas explicitly
- Add lots of error messages
- Test each component independently first

---

## Resources Needed

### Hardware
- Development machine: Your current setup should be fine
- VM for testing (optional for Week 1): 2GB RAM, 20GB disk
- Note: Can test on host system with file operations (low risk)

### Software
- Ubuntu 24.04 or similar (for eBPF support)
- Rust toolchain: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
- Python 3.10+
- **uv** (modern Python package manager): `curl -LsSf https://astral.sh/uv/install.sh | sh`
  - Replaces pip/virtualenv with faster, more reliable tooling
  - Automatic lockfile management
  - See: https://github.com/astral-sh/uv
- Ollama: `curl -fsSL https://ollama.com/install.sh | sh`
- bpftrace: `sudo apt install bpftrace`
- Git

### Time Allocation
- **Rust learning:** ~3-4 hours total across Week 1
  - Day 1: 1.5-2 hours (basics)
  - Day 3: 1 hour (ownership, JSON)
  - Day 4: 1 hour (unsafe, libc)
- **Building:** ~12-15 hours across 5 days
- **Total:** ~3-4 hours per day

### Learning Resources

**Rust (Essential for Week 1):**
- Official Rust Book: https://doc.rust-lang.org/book/
  - Focus on chapters 1-5, 8, 10.1
- Rust by Example: https://doc.rust-lang.org/rust-by-example/
- Rustlings exercises: https://github.com/rust-lang/rustlings
- Serde documentation: https://serde.rs/
- "Too Many Lists" (for ownership): https://rust-unofficial.github.io/too-many-lists/

**eBPF:**
- eBPF.io tutorial: https://ebpf.io/what-is-ebpf/
- bpftrace guide: https://github.com/iovisor/bpftrace/blob/master/docs/tutorial_one_liners.md
- Brendan Gregg's eBPF page: https://www.brendangregg.com/ebpf.html

**Ollama:**
- Official docs: https://github.com/ollama/ollama
- Python library: https://github.com/ollama/ollama-python
- Model library: https://ollama.com/library

**Python Tooling:**
- uv package manager: https://github.com/astral-sh/uv
  - Modern, fast pip/venv replacement by Astral (makers of Ruff)
  - Excellent lockfile support
  - Much faster than pip

---

## Daily Log Format (Org-mode)

Keep a daily log in `docs/daily_log.org`:

```org
* Week 1: Delphos MVP Development

** Day 1 [2024-12-02 Mon]
*** Goals
- [ ] Set up development environment
- [ ] Learn Rust basics (chapters 1-3)
- [ ] Create project structure

*** Accomplished
- [X] Installed Rust toolchain
- [X] Set up Python venv
- [X] Read Rust book chapters 1-2
- [ ] Chapter 3 pending

*** Challenges
- Understanding ownership took longer than expected
- bpftrace installation had dependency issues

*** Learning Notes
- Rust's ownership model is different from anything I've used
- Cargo is very pleasant compared to make
- Need to spend more time with borrowing concepts

*** Tomorrow
- Complete Rust basics
- Start eBPF tracing script
- Begin Python LLM integration

*** Time Spent
3.5 hours

** Day 2 [2024-12-03 Tue]
*** Goals
...
```

This format allows:
- Clear tracking of progress
- Honest assessment of challenges
- Learning capture
- Time tracking
- Easy review at end of week

---

## Week 1 Definition of Done

We can confidently say Week 1 is complete when:

1. ✅ Code is committed to git with clear commit messages
2. ✅ README explains how to run the demo
3. ✅ Demo shows end-to-end workflow working
4. ✅ At least 5 test scenarios execute successfully
5. ✅ We have data on test effectiveness (which found issues?)
6. ✅ Week 2 plan is drafted based on Week 1 learnings

---

## Next Steps (After Week 1)

**Week 2 Preview:**
- Add vector database (ChromaDB) with CVE data
- Expand to 2-3 more syscall families
- Improve test generation quality
- Add ML-based test prioritization

**Week 3 Preview:**
- Generalize framework beyond syscalls
- Add web application testing target
- Performance optimization
- CI/CD integration

---

## Questions to Answer During Week 1

1. How good are LLM-generated test scenarios compared to manual ones?
2. What's the signal-to-noise ratio (useful tests vs. useless tests)?
3. How fast can we generate and execute tests?
4. What kinds of bugs can this approach realistically find?
5. What's the developer experience like? Is it painful or pleasant?
6. How much Rust is really needed for this project?

---

## References & Related Work

### Academic Papers & Research

**AI-Augmented Testing:**
- "Learning to Fuzz from Symbolic Execution" (Böhme et al., 2017)
  - https://dl.acm.org/doi/10.1145/3133956.3138820
  - Uses ML to guide fuzzing based on symbolic execution

- "Neuro-Symbolic Program Search" (Shi et al., 2019)
  - Shows neural networks can learn to generate programs
  - Relevant for test generation approach

- "Learning to Test" (Pei et al., 2019)
  - Uses deep learning to learn test generation strategies
  - Similar goal but different approach

**Fuzzing & Testing Research:**
- "AFL: American Fuzzy Lop" (Zalewski, 2014)
  - https://lcamtuf.coredump.cx/afl/
  - Coverage-guided fuzzing - inspiration for our approach

- "LibFuzzer: Coverage-guided fuzzing" (LLVM project)
  - https://llvm.org/docs/LibFuzzer.html
  - Modern fuzzing engine, potential integration point

- "OSS-Fuzz: Google's continuous fuzzing service"
  - https://github.com/google/oss-fuzz
  - Large-scale fuzzing infrastructure, shows ML potential

**Kernel Testing:**
- "Syzkaller: Kernel fuzzer" (Google)
  - https://github.com/google/syzkaller
  - State-of-the-art kernel fuzzer
  - Delphos could complement this with AI-guided scenarios

- "Trinity: Linux system call fuzzer"
  - https://github.com/kernelslacker/trinity
  - Random syscall fuzzing
  - We aim to be more intelligent

### Tools & Projects

**Similar Efforts:**
- **Kani Rust Verifier** (AWS)
  - https://github.com/model-checking/kani
  - Formal verification for Rust
  - Different approach but similar goal (finding bugs)

- **Hypothesis** (Python property-based testing)
  - https://hypothesis.readthedocs.io/
  - Generates test cases from properties
  - Could integrate with our LLM generation

- **QuickCheck** (Haskell/Rust)
  - https://github.com/BurntSushi/quickcheck
  - Property-based testing
  - Inspiration for our contract-based approach

**AI Code Tools:**
- **Gemini** / **Maybe try others too**
  - AI-assisted code generation
  - Shows LLMs can reason about code

- **Amazon CodeWhisperer**
  - Similar space, security-focused

**Testing Frameworks:**
- **Linux Test Project (LTP)**
  - https://github.com/linux-test-project/ltp
  - Comprehensive kernel test suite
  - We're trying to augment, not replace this

- **KUnit** (Linux kernel unit testing)
  - https://docs.kernel.org/dev-tools/kunit/
  - In-kernel testing framework

### Technical Documentation

**eBPF:**
- BPF Performance Tools book (Brendan Gregg)
  - http://www.brendangregg.com/bpf-performance-tools-book.html
  - Comprehensive eBPF guide

- Linux kernel eBPF documentation
  - https://docs.kernel.org/bpf/
  - Official kernel docs

- Cilium eBPF library for Go
  - https://github.com/cilium/ebpf
  - Good alternative if we want to try Go

**Rust for Systems Programming:**
- "Writing an OS in Rust" (Philipp Oppermann)
  - https://os.phil-opp.com/
  - Shows Rust's systems programming capabilities

- "The Rustonomicon" (unsafe Rust)
  - https://doc.rust-lang.org/nomicon/
  - Essential for syscall interfacing

**LLM Prompting:**
- Gemini Prompting Strategies
  - https://ai.google.dev/gemini-api/docs/prompting-strategies
  - Prompt design is the process of creating prompts

- Anthropic Prompt Engineering Guide
  - https://docs.anthropic.com/claude/docs/prompt-engineering
  - Best practices for Claude

- OpenAI Prompt Engineering Guide
  - https://platform.openai.com/docs/guides/prompt-engineering
  - General LLM prompting techniques

### Blog Posts & Articles

**Relevant Techniques:**
- "Fuzzing with AFL" (Michael Macnair)
  - http://moyix.blogspot.com/2016/07/fuzzing-with-afl-is-an-art.html
  - Practical fuzzing insights

- "eBPF - The Future of Networking & Security"
  - https://cilium.io/blog/2020/11/10/ebpf-future-of-networking/
  - Why eBPF matters

- "Using Machine Learning to Improve Fuzzing"
  - Various blog posts from security researchers
  - Shows ML+fuzzing is active research area

**AI + Testing:**
- "ChatGPT for Testing" (Various 2023-2024 posts)
  - Mixed results, shows promise and limitations
  - We're trying to be more systematic

### Datasets & Benchmarks

**CVE Databases:**
- National Vulnerability Database (NVD)
  - https://nvd.nist.gov/
  - Source for kernel CVEs

- Linux Kernel CVE list
  - https://www.linuxkernelcves.com/
  - Kernel-specific CVE tracking

- MITRE CVE database
  - https://cve.mitre.org/
  - Comprehensive vulnerability data

**Benchmark Suites:**
- Google's FuzzBench
  - https://github.com/google/fuzzbench
  - Fuzzer evaluation framework
  - We could use this to benchmark Delphos

### Related Projects to Watch

**AI-Assisted Security:**
- **ZioSec** - AI security testing
- **Mayhem** - Automated security testing
- **ForAllSecure** - Continuous security testing

**Research Groups:**
- **UC Berkeley RISE Lab** - AI systems
- **MIT CSAIL** - Program synthesis
- **Stanford Security Lab** - Security testing

### Key Insights from Related Work

1. **Coverage-guided fuzzing works** - AFL showed this in 2014
2. **ML can improve fuzzing** - Multiple papers show 10-30% improvement
3. **Kernel fuzzing is valuable** - Syzkaller found 1000+ bugs
4. **LLMs understand code** - Copilot/Claude demonstrate this
5. **No one has combined these effectively yet** - Opportunity for Delphos!

### Gaps Delphos Addresses

- **Existing fuzzers are mostly random** - We use AI for intelligence
- **LLM tools are general purpose** - We're domain-specific (kernel testing)
- **Manual testing is slow** - We automate scenario generation
- **Fuzzing lacks context** - We use documentation and historical CVEs
- **Testing and AI are separate** - We integrate them deeply

---

**Remember the name:** Delphos - like the Oracle at Delphos, we're building something that can predict where bugs might be hiding. 🔮

