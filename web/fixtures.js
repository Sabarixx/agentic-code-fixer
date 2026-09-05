/* ==========================================================================
   AGENTIC CODE FIXER - FIXTURES & SAMPLE TEST CASES
   ========================================================================== */

const FIXTURES = {
  typescript: {
    name: "untitled-failure.ts",
    source: `function getUserName(user: User) {
  return user.profile.name.toUpperCase();
}`,
    tests: `it("returns a user's display name", () => {
  expect(getUserName({ profile: { name: "Ada" } })).toBe("ADA");
  expect(getUserName({ profile: null })).toBe("");
});`,
    patchedCode: `function getUserName(user: User) {
  return user?.profile?.name?.toUpperCase() ?? "";
}`,
    analysis: {
      title: "Symbol Graph & AST Traversal",
      badge: "AST Parsed (3 symbols)",
      body: `→ Resolving member expression: user.profile.name
→ Inferred schema: User.profile can evaluate to null | undefined
→ Nullability hazard identified on property dereference [Line 2:10]`
    },
    diagnosis: {
      title: "Root Cause Diagnosis",
      badge: "TypeError: Cannot read properties of null",
      body: `The test fixture passes profile: null.
Dereferencing '.name' on null produces an unhandled runtime exception.
Required invariant: Safe navigation operator with empty string fallback.`
    },
    patch: {
      title: "Narrow Patch Synthesis",
      badge: "+1 -1 lines (99.4% confidence)",
      del: "-  return user.profile.name.toUpperCase();",
      add: "+  return user?.profile?.name?.toUpperCase() ?? \"\";"
    },
    rerun: {
      title: "Sandbox Test Execution",
      badge: "Jest Runner (2/2 Passed)",
      body: `✓ Test 1: returns a user's display name (profile present) [0.4ms]
✓ Test 2: returns a user's display name (profile null) [0.2ms]`
    },
    validation: {
      title: "Contract Verified & Sealed",
      badge: "Validated • Confidence 0.94",
      body: `Zero regressions detected across all assertions.
Generated patch adheres to narrow locality policy.`
    }
  },

  python: {
    name: "binary_search.py",
    source: `def binary_search(arr, target):
    left, right = 0, len(arr)
    while left < right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1`,
    tests: `def test_binary_search():
    assert binary_search([1, 3, 5, 7, 9], 9) == 4
    assert binary_search([1, 3, 5, 7, 9], 1) == 0
    assert binary_search([1, 3, 5, 7, 9], 6) == -1`,
    patchedCode: `def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1`,
    analysis: {
      title: "AST Control-Flow Graph",
      badge: "Control Flow Analysis",
      body: `→ Loop invariant check: while left < right
→ Initial bounds: right = len(arr)
→ Potential off-by-one boundary condition at rightmost element`
    },
    diagnosis: {
      title: "Boundary Condition Missed",
      badge: "AssertionError: 9 not found at index 4",
      body: `Target element at arr[len-1] was excluded when left == right.
Condition 'left <= right' with 'right = len(arr) - 1' is required.`
    },
    patch: {
      title: "Narrow Patch Synthesis",
      badge: "+2 -2 lines (100% confidence)",
      del: "-    left, right = 0, len(arr)\n-    while left < right:",
      add: "+    left, right = 0, len(arr) - 1\n+    while left <= right:"
    },
    rerun: {
      title: "Pytest Runner Execution",
      badge: "Pytest (3/3 Passed)",
      body: `✓ test_binary_search::case_rightmost_elem [PASSED]
✓ test_binary_search::case_leftmost_elem [PASSED]
✓ test_binary_search::case_missing_elem [PASSED]`
    },
    validation: {
      title: "Formal Invariants Verified",
      badge: "Validated • Confidence 0.98",
      body: `O(log N) complexity preserved. Termination proof satisfied.`
    }
  },

  javascript: {
    name: "async_queue.js",
    source: `async function processQueue(items, handler) {
  const results = [];
  items.forEach(async (item) => {
    const res = await handler(item);
    results.push(res);
  });
  return results;
}`,
    tests: `it("processes all items in order", async () => {
  const res = await processQueue([1, 2], async (x) => x * 2);
  expect(res).toEqual([2, 4]);
});`,
    patchedCode: `async function processQueue(items, handler) {
  const results = [];
  for (const item of items) {
    const res = await handler(item);
    results.push(res);
  }
  return results;
}`,
    analysis: {
      title: "Async Scope Analysis",
      badge: "Async Callback Escape",
      body: `→ forEach callback returns unawaited Promises
→ outer function returns empty results array synchronously before resolution`
    },
    diagnosis: {
      title: "Race Condition / Premature Return",
      badge: "AssertionError: Expected [2,4], received []",
      body: `Array.prototype.forEach does not await async iterations.
Fix with sequential 'for...of' or Promise.all concurrent dispatch.`
    },
    patch: {
      title: "Loop Structural Patch",
      badge: "+4 -4 lines (98.9% confidence)",
      del: "-  items.forEach(async (item) => {\n-    const res = await handler(item);\n-    results.push(res);\n-  });",
      add: "+  for (const item of items) {\n+    const res = await handler(item);\n+    results.push(res);\n+  }"
    },
    rerun: {
      title: "Mocha Runner Execution",
      badge: "Mocha (1/1 Passed)",
      body: `✓ processes all items in order [1.2ms]`
    },
    validation: {
      title: "Concurrency Contract Verified",
      badge: "Validated • Confidence 0.96",
      body: `Resolved async execution order. No unhandled promise rejections.`
    }
  },

  rust: {
    name: "safe_unwrap.rs",
    source: `pub fn parse_port(input: &str) -> u16 {
    input.parse::<u16>().unwrap()
}`,
    tests: `#[test]
fn test_port_parser() {
    assert_eq!(parse_port("8080"), 8080);
    assert_eq!(parse_port("invalid"), 80);
}`,
    patchedCode: `pub fn parse_port(input: &str) -> u16 {
    input.parse::<u16>().unwrap_or(80)
}`,
    analysis: {
      title: "Rust Borrow & Panic Check",
      badge: "Panic on invalid input",
      body: `→ Direct .unwrap() call on Result<u16, ParseIntError>
→ Vulnerable to thread panic on malformed strings`
    },
    diagnosis: {
      title: "Unhandled Err Variant",
      badge: "Panic: called Result::unwrap() on an Err",
      body: `Test contract specifies default fallback port 80 when parsing fails.`
    },
    patch: {
      title: "Safe Fallback Patch",
      badge: "+1 -1 lines (100% confidence)",
      del: "-    input.parse::<u16>().unwrap()",
      add: "+    input.parse::<u16>().unwrap_or(80)"
    },
    rerun: {
      title: "Cargo Test Runner",
      badge: "cargo test (1/1 Passed)",
      body: `test test_port_parser ... ok`
    },
    validation: {
      title: "Safety Contract Enforced",
      badge: "Validated • Confidence 1.0",
      body: `Zero unwrap panics. Fallback contract met.`
    }
  }
};
