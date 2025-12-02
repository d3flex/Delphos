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
TBD