use serde::{Deserialize, Serialize};
use std::fs;

//const SCENARIOS: &str = "../test_scenarios.json";
// Reads test_scenario
// Calls open(), read(), etc. DIRECTLY from Rust
// Writes results to results.json

#[derive(Deserialize)]
struct TestScenario {
    id: String,
    description: String,
    expected_result: String,
    expected_errno: Option<String>,
}

#[derive(Deserialize, Serialize)]
struct TestResults {
    id: String,
    description: String,
    passed: bool,
    actual_result: String,
    actual_errno: Option<String>,
    message: String,
}
fn run_scenario(scenario: &TestScenario) -> TestResults {
    use std::ffi::CString;
    let test_file = CString::new("/etc/passwd").unwrap();
    let fd = unsafe { libc::open(test_file.as_ptr(), libc::O_RDONLY) };
    let (actual_result, actual_errno) = if fd >= 0 {
        unsafe { libc::close(fd) };
        ("success".to_string(), None)
    } else {
        let errno = unsafe { *libc::__errno_location() };
        ("error".to_string(), Some(format!("ERRNO_{}", errno)))
    };
    let passed = actual_result == scenario.expected_result;
    TestResults {
        id: scenario.id.clone(),
        description: scenario.description.clone(),
        passed,
        actual_result,
        actual_errno,
        message: if passed {
            "PASS".to_string()
        } else {
            "FAIL".to_string()
        },
    }
}
fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 3 {
        eprintln!("Usage: {} <scenarios.json> <results.json>", args[0]);
        std::process::exit(1);
    }
    let scenarios_path = &args[1];
    let results_path = &args[2];
    let scenarios = fs::read_to_string(scenarios_path)
        .expect("Failed to read the scenarion file from {scenarios_path}");
    //println!("File contents:\n{}", scenarios);
    let scenarios: Vec<TestScenario> =
        serde_json::from_str(&scenarios).expect("Failed to parse JSON");
    let mut all_results = Vec::new();
    for scenario in scenarios {
        println!("  * {}: {}", scenario.id, scenario.description);
        //println!("    Expected: result: {} errno: {:?}", scenario.expected_result, scenario.expected_errno);
        let test_result = run_scenario(&scenario);
        println!(
            "    Result: {} (expected: {})",
            test_result.actual_result, scenario.expected_result
        );
        println!(
            "    Status: {}",
            if test_result.passed {
                "✓ PASS"
            } else {
                "✗ FAIL"
            }
        );
        all_results.push(test_result);
    }

    let results_json =
        serde_json::to_string_pretty(&all_results).expect("Failed to serialize results");
    fs::write(results_path, results_json).expect("Failed to write results file");

    println!("\nResults written to {}", results_path);
}
