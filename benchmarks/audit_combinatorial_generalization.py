"""
Benchmark 04: Combinatorial Ising/QUBO Solver Generalization Audit
Evaluates solution stability and independent energy verification across synthetic graph topologies.
"""

import os
import sys
import time
from typing import Dict, Tuple
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from bridge import CombinatorialOptimizer


def build_synthetic_ising_dict(n_nodes: int, density: float, mode: str, seed: int = 42):
    rng = np.random.default_rng(seed)
    linear: Dict[int, float] = {i: 0.0 for i in range(n_nodes)}
    quadratic: Dict[Tuple[int, int], float] = {}
    k = max(1, int(n_nodes * density))

    for i in range(n_nodes):
        neighbors = rng.choice(n_nodes, size=k, replace=False)
        for j in neighbors:
            j_int = int(j)
            if j_int > i:
                w = 1.0 if mode == "unitary" else float(rng.choice([-1.0, 1.0]))
                quadratic[(i, j_int)] = w
    return linear, quadratic


def extract_spin_map(result, n_nodes: int) -> Dict[int, int]:
    if isinstance(result, dict):
        if all(isinstance(k, int) for k in result.keys()) and len(result) == n_nodes:
            return {int(k): int(v) for k, v in result.items()}
        for v in result.values():
            if isinstance(v, dict) and len(v) == n_nodes:
                return {int(k): int(val) for k, val in v.items()}
            arr = np.asarray(v)
            if arr.ndim == 1 and arr.size == n_nodes:
                return {i: int(arr[i]) for i in range(n_nodes)}
    elif isinstance(result, (tuple, list)):
        for item in result:
            if isinstance(item, dict) and len(item) == n_nodes:
                return {int(k): int(val) for k, val in item.items()}
            arr = np.asarray(item)
            if arr.ndim == 1 and arr.size == n_nodes:
                return {i: int(arr[i]) for i in range(n_nodes)}
    raise ValueError(f"Could not parse spin configuration from solver output: {type(result)}")


def compute_exact_ising_energy(
    linear: Dict[int, float],
    quadratic: Dict[Tuple[int, int], float],
    spins: Dict[int, int],
) -> float:
    assert set(spins.values()).issubset({-1, 1}), f"Invalid spin domain: {set(spins.values())}"
    energy = sum(h * spins[i] for i, h in linear.items())
    energy += sum(w * spins[i] * spins[j] for (i, j), w in quadratic.items())
    return float(energy)


def run_benchmark() -> None:
    print("=== COMBINATORIAL ISING/QUBO GENERALIZATION AUDIT ===")
    optimizer = CombinatorialOptimizer()

    scenarios = [
        ("Unitary Max-Cut (800 nodes, 3% density)", 800, 0.03, "unitary"),
        ("Frustrated Spin Glass (+/-1, 800 nodes)", 800, 0.03, "spin_glass"),
    ]

    for label, n_nodes, density, mode in scenarios:
        linear, quadratic = build_synthetic_ising_dict(n_nodes, density, mode)
        energies = []
        latencies = []

        for _ in range(3):
            t0 = time.perf_counter()
            result = optimizer.solve_ising(linear, quadratic)
            dt = (time.perf_counter() - t0) * 1000.0

            spin_map = extract_spin_map(result, n_nodes)
            verified_energy = compute_exact_ising_energy(linear, quadratic, spin_map)
            energies.append(verified_energy)
            latencies.append(dt)

        print(f"\n[SCENARIO] {label}")
        print(f"  -> Best Energy : {min(energies):.2f} | Mean: {np.mean(energies):.2f} | StdDev: {np.std(energies):.4f}")
        print(f"  -> Mean Latency: {np.mean(latencies):.2f} ms (Independent Hamiltonian energy verified)")


if __name__ == "__main__":
    run_benchmark()
