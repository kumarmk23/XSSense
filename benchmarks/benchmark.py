import time
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from mock_targets import start_mock_server
from contextxss.core.requester import send_request
from contextxss.core.reflector import detect_reflection
from contextxss.core.analyzer import analyze_context
from contextxss.core.payload_engine import get_payloads
from contextxss.core.evaluator import evaluate_payloads

TARGETS = {
    "html_vuln": ("http://localhost:8099/html_vuln?q=test", True),
    "html_safe": ("http://localhost:8099/html_safe?q=test", False),
    "attr_vuln": ("http://localhost:8099/attr_vuln?q=test", True),
    "attr_safe": ("http://localhost:8099/attr_safe?q=test", False),
    "js_vuln":   ("http://localhost:8099/js_vuln?q=test", True),
    "js_safe":   ("http://localhost:8099/js_safe?q=test", False)
}

def run_benchmark(mode="quick"):
    results = {"total_time": 0, "tp": 0, "fp": 0, "tn": 0, "fn": 0}
    
    start_time = time.time()
    
    for name, (url, expected_vuln) in TARGETS.items():
        status, headers, response_text, req_url, req_data = send_request(url, payload="XSSCTX12345", timeout=3)
        if status is None:
            continue
            
        is_reflected, positions = detect_reflection(response_text, "XSSCTX12345")
        if not is_reflected:
            if not expected_vuln:
                results["tn"] += 1
            else:
                results["fn"] += 1
            continue
            
        context_type = analyze_context(response_text, "XSSCTX12345", positions)
        payloads = get_payloads(context_type, mode)
        
        eval_results = evaluate_payloads(url, "GET", None, payloads, context_type, 3)
        
        found_vuln = any(r["success"] for r in eval_results)
        
        if found_vuln and expected_vuln:
            results["tp"] += 1
        elif found_vuln and not expected_vuln:
            results["fp"] += 1
        elif not found_vuln and not expected_vuln:
            results["tn"] += 1
        elif not found_vuln and expected_vuln:
            results["fn"] += 1
            
    results["total_time"] = time.time() - start_time
    return results

if __name__ == "__main__":
    print("Starting mock server on port 8099...")
    server = start_mock_server(8099)
    time.sleep(1)
    
    print("\nRunning QUICK mode benchmark...")
    quick_res = run_benchmark("quick")
    
    print("Running DEEP mode benchmark...")
    deep_res = run_benchmark("deep")
    
    server.shutdown()
    
    print("\n" + "="*50)
    print("BENCHMARK RESULTS")
    print("="*50)
    print(f"{'Mode':<10} | {'True Pos':<10} | {'False Pos':<10} | {'Time (s)':<10}")
    print("-" * 50)
    print(f"{'QUICK':<10} | {quick_res['tp']:<10} | {quick_res['fp']:<10} | {quick_res['total_time']:.2f}")
    print(f"{'DEEP':<10} | {deep_res['tp']:<10} | {deep_res['fp']:<10} | {deep_res['total_time']:.2f}")
    print("="*50)
    
    results_out = {
        "quick": quick_res,
        "deep": deep_res
    }
    
    results_path = os.path.join(os.path.dirname(__file__), "results.json")
    with open(results_path, "w") as f:
        json.dump(results_out, f, indent=4)
        
    print(f"\nResults saved to {results_path}")
