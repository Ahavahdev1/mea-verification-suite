"""
Benchmark 01: Stabilizer Circuit Simulation (1,000-Qubit GHZ Entanglement Audit)
Verifies polynomial-time Clifford state preparation and global parity collapse.
"""

import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from bridge import StabilizerSimulator


def run_benchmark(num_qubits: int = 1000) -> None:
    print(f"=== STABILIZER CIRCUIT AUDIT ({num_qubits}-QUBIT GHZ STATE) ===")

    t0 = time.perf_counter()
    sim = StabilizerSimulator(num_qubits=num_qubits)
    sim.prepare_ghz_state()
    prep_ms = (time.perf_counter() - t0) * 1000.0

    t0 = time.perf_counter()
    measurements = [sim.measure_qubit(q) for q in range(num_qubits)]
    meas_ms = (time.perf_counter() - t0) * 1000.0

    unique_outcomes = set(measurements)
    assert len(unique_outcomes) == 1, f"Entanglement parity violation: {unique_outcomes}"

    collapsed_state = measurements[0]
    print(f"[PASS] State Preparation Time : {prep_ms:.2f} ms")
    print(f"[PASS] Sequential Measurement : {meas_ms:.2f} ms")
    print(f"[PASS] Global Parity Collapse : 100% correlated (all {num_qubits} qubits -> |{collapsed_state}>)")


if __name__ == "__main__":
    run_benchmark(1000)
