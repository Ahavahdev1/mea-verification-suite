"""
Benchmark 03: Deterministic AI Output Verification (Numeric Hallucination Guard)
Verifies strict cross-referencing of generated numerical claims against ground-truth records.
"""

import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from bridge import GroundedMemoryGuard


def run_benchmark() -> None:
    print("=== DETERMINISTIC NUMERIC GROUNDING AUDIT ===")
    temp_store = "temp_grounding_audit.json"
    if os.path.exists(temp_store):
        os.remove(temp_store)

    try:
        guard = GroundedMemoryGuard(storage_path=temp_store)
        ground_truth = "The combinatorial solver achieved a max-cut score of 13359 on Stanford G22."
        query = "What was the max-cut score achieved on Stanford G22?"

        guard.ingest("g22_record", ground_truth)

        # Case 1: Factual output matching ground truth
        t0 = time.perf_counter()
        res_valid = guard.verify_output(
            query=query,
            ground_truth=ground_truth,
            candidate_output="The solver reached a score of 13359 on G22."
        )
        dt_valid = (time.perf_counter() - t0) * 1000.0

        # Case 2: Hallucinated numeric claim
        t0 = time.perf_counter()
        res_hallucinated = guard.verify_output(
            query=query,
            ground_truth=ground_truth,
            candidate_output="The solver reached a score of 99999 on G22."
        )
        dt_veto = (time.perf_counter() - t0) * 1000.0

        assert res_valid.get("status") == "SUCESSO_AUDITADO_TOTAL", f"Unexpected valid status: {res_valid}"
        assert res_hallucinated.get("status") == "VETO_NUMERICO_ALUCINACAO", f"Failed to veto hallucination: {res_hallucinated}"

        print(f"[PASS] Factual Claim Verified : {dt_valid:.2f} ms -> Status: {res_valid['status']}")
        print(f"[PASS] Hallucination Vetoed   : {dt_veto:.2f} ms -> Status: {res_hallucinated['status']}")
        print(f"[PASS] Safe Fallback Enforced : '{res_hallucinated['resposta_segura']}'")
    finally:
        if os.path.exists(temp_store):
            os.remove(temp_store)


if __name__ == "__main__":
    run_benchmark()
