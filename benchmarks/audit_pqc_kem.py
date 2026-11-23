"""
Benchmark 02: Post-Quantum Lattice Cryptography (ML-KEM / Kyber Parameters)
Verifies key encapsulation/decapsulation parity and authenticated payload integrity.
"""

import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from bridge import PostQuantumKEM


def run_benchmark() -> None:
    print("=== POST-QUANTUM LATTICE KEM AUDIT (n=256, q=3329, eta=2) ===")

    kem = PostQuantumKEM(n=256, q=3329, eta=2)

    t0 = time.perf_counter()
    pk, sk = kem.keygen()
    keygen_ms = (time.perf_counter() - t0) * 1000.0

    t0 = time.perf_counter()
    ciphertext, shared_secret_sender = kem.encapsulate(pk)
    shared_secret_receiver = kem.decapsulate(ciphertext, sk)
    kem_ms = (time.perf_counter() - t0) * 1000.0

    assert shared_secret_sender == shared_secret_receiver, "KEM shared secret mismatch!"

    payload = b"AUDIT_RECORD_ID_8841: SETTLEMENT_CONFIRMED_1000000_USD"
    t0 = time.perf_counter()
    encrypted = kem.encrypt_payload(payload, pk)
    decrypted = kem.decrypt_payload(encrypted, sk)
    payload_ms = (time.perf_counter() - t0) * 1000.0

    assert payload == decrypted, "Decrypted payload integrity failure!"

    print(f"[PASS] Keypair Generation     : {keygen_ms:.2f} ms")
    print(f"[PASS] Encapsulate+Decapsulate: {kem_ms:.2f} ms (Shared Secret Match: True)")
    print(f"[PASS] Payload Encrypt+Decrypt: {payload_ms:.2f} ms (Bit-Exact Match: True)")


if __name__ == "__main__":
    run_benchmark()
