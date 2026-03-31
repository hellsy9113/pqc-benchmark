#  Post-Quantum Cryptography Benchmark (Kyber & Dilithium vs RSA)

##  Overview

This project benchmarks classical cryptography using RSA against post-quantum cryptographic algorithms:

* **Kyber** (Key Encapsulation Mechanism)
* **Dilithium** (Digital Signature Scheme)

The objective is to evaluate **performance, key sizes, and computational trade-offs** to understand the transition toward **quantum-resistant cryptographic systems**.

---

##  Features

* Benchmarking over **100 iterations**
* Statistical analysis:

  * Mean
  * Median
  * Standard Deviation
* Memory usage tracking
* Graphical visualization:

  * Performance comparison (with error bars)
  * Key size comparison

---

##  Key Findings

* Kyber achieves **significantly faster key generation and encapsulation** compared to RSA
* Dilithium offers **efficient verification**, though signature sizes are larger
* Post-quantum algorithms introduce **increased key and signature sizes**, highlighting a trade-off between performance and storage

---

##  Graphs

### Performance Comparison

![Performance](comparison_detailed.png)

### Key Size Comparison

![Key Sizes](key_sizes.png)

---

##  Real-World Relevance

Modern secure systems (e.g., HTTPS, messaging platforms) rely on public-key cryptography. However, advances in quantum computing threaten classical algorithms like RSA.

This project demonstrates how **post-quantum cryptographic schemes** such as Kyber and Dilithium can replace traditional methods to ensure **future-proof security**.

---

##  How to Run

```bash
python3 -m venv pqc-env
source pqc-env/bin/activate
pip install -r requirements.txt
python script.py
```

---

##  Key Insights

* Post-quantum cryptography can outperform RSA in **computational efficiency**
* Larger key and signature sizes introduce **storage and transmission overhead**
* Hybrid cryptographic systems (PQC + symmetric encryption) are essential for real-world deployment

---

##  Tech Stack

* Python
* liboqs (Open Quantum Safe)
* cryptography
* matplotlib
* memory-profiler

---

##  Future Work

* Integrate **AES with Kyber** for hybrid encryption systems
* Develop a **secure messaging prototype using PQC**
* Benchmark additional NIST-standardized PQC algorithms
* Export results to CSV for extended analysis

---
