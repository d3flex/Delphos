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
    test_type: String,
    target: String,
    params: serde_json::Value,
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

fn run_open_syscall(scenario: &TestScenario) -> (String, Option<String>) {
    use std::ffi::CString;

    // Step 3: Extract params from JSON
    let path = match scenario.params.get("path").and_then(|v| v.as_str()) {
        Some(p) => p,
        None => return ("error".to_string(), Some("MISSING_PATH_PARAM".to_string())),
    };

    let flags_str = scenario
        .params
        .get("flags")
        .and_then(|v| v.as_str())
        .unwrap_or("O_RDONLY");

    // Step 4: Parse flags (supports combined flags like "O_WRONLY|O_CREAT")
    let flags = flags_str.split('|').map(|f| f.trim()).fold(0, |acc, flag| {
        acc | match flag {
            "O_RDONLY" => libc::O_RDONLY,
            "O_WRONLY" => libc::O_WRONLY,
            "O_RDWR" => libc::O_RDWR,
            "O_CREAT" => libc::O_CREAT,
            "O_EXCL" => libc::O_EXCL,
            "O_TRUNC" => libc::O_TRUNC,
            "O_APPEND" => libc::O_APPEND,
            "O_DIRECTORY" => libc::O_DIRECTORY,
            "O_CLOEXEC" => libc::O_CLOEXEC,
            "O_NOCTTY" => libc::O_NOCTTY,
            "O_NONBLOCK" => libc::O_NONBLOCK,
            "O_ASYNC" => libc::O_ASYNC,
            "O_DIRECT" => libc::O_DIRECT,
            "O_LARGEFILE" => libc::O_LARGEFILE,
            _ => 0,
        }
    });

    // Step 5: Execute the syscall
    let c_path = match CString::new(path) {
        Ok(p) => p,
        Err(_) => return ("error".to_string(), Some("INVALID_PATH".to_string())),
    };

    // If O_CREAT is used, we need to provide mode (default to 0o644)
    let fd = if flags & libc::O_CREAT != 0 {
        let mode = scenario
            .params
            .get("mode")
            .and_then(|v| v.as_u64())
            .unwrap_or(0o644) as libc::mode_t;
        unsafe { libc::open(c_path.as_ptr(), flags, mode) }
    } else {
        unsafe { libc::open(c_path.as_ptr(), flags) }
    };

    // Step 6: Check result and return
    if fd >= 0 {
        unsafe { libc::close(fd) };
        ("success".to_string(), None)
    } else {
        let errno = unsafe { *libc::__errno_location() };
        let errno_name = match errno {
            libc::ENOENT => "ENOENT",             // File not found
            libc::EACCES => "EACCES",             // Permissions denied
            libc::EPERM => "EPERM",               // operation not allowed
            libc::EAI_BADFLAGS => "EAI_BADFLAGS", // Invalid flags
            _ => "UNKNOWN",
        };
        ("error".to_string(), Some(errno_name.to_string()))
    }
}

fn run_syscall(scenario: &TestScenario) -> (String, Option<String>) {
    // Step 2: Dispatch based on syscall target
    match scenario.target.as_str() {
        "open" => run_open_syscall(scenario),
        _ => ("error".to_string(), Some("UNSUPPORTED_SYSCALL".to_string())),
    }
}

fn run_scenario(scenario: &TestScenario) -> TestResults {
    // Step 1: Dispatch based on test_type and target
    let (actual_result, actual_errno) = match scenario.test_type.as_str() {
        "syscall" => run_syscall(scenario),
        _ => (
            "error".to_string(),
            Some("UNSUPPORTED_TEST_TYPE".to_string()),
        ),
    };

    let passed = actual_result == scenario.expected_result;

    // Build failure message with details
    let message = if passed {
        "PASS".to_string()
    } else {
        match &actual_errno {
            Some(errno) => format!(
                "FAIL: expected {}, got {} ({})",
                scenario.expected_result, actual_result, errno
            ),
            None => format!(
                "FAIL: expected {}, got {}",
                scenario.expected_result, actual_result
            ),
        }
    };

    TestResults {
        id: scenario.id.clone(),
        description: scenario.description.clone(),
        passed,
        actual_result,
        actual_errno,
        message,
    }
}
// fn run_scenario(scenario: &TestScenario) -> TestResults {
//     use std::ffi::CString;
//     let test_file = CString::new("/etc/passwd").unwrap();
//     let fd = unsafe { libc::open(test_file.as_ptr(), libc::O_RDONLY) };
//     let (actual_result, actual_errno) = if fd >= 0 {
//         unsafe { libc::close(fd) };
//         ("success".to_string(), None)
//     } else {
//         let errno = unsafe { *libc::__errno_location() };
//         ("error".to_string(), Some(format!("ERRNO_{}", errno)))
//     };
//     let passed = actual_result == scenario.expected_result;
//     TestResults {
//         id: scenario.id.clone(),
//         description: scenario.description.clone(),
//         passed,
//         actual_result,
//         actual_errno,
//         message: if passed {
//             "PASS".to_string()
//         } else {
//             "FAIL".to_string()
//         },
//     }
// }
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
