import time
import statistics
import matplotlib.pyplot as plt
from memory_profiler import memory_usage
import pprint

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

import oqs

ITERATIONS = 100


# -----------------------------
# STATISTICS FUNCTION
# -----------------------------
def compute_stats(data):
    return {
        "mean": statistics.mean(data),
        "std": statistics.stdev(data),
        "median": statistics.median(data),
        "min": min(data),
        "max": max(data)
    }


# -----------------------------
# MEMORY FUNCTION
# -----------------------------
def measure_memory(func):
    mem = memory_usage((func,), interval=0.01, timeout=1)
    return max(mem) - min(mem)


# -----------------------------
# RSA BENCHMARK
# -----------------------------
def benchmark_rsa():
    keygen_times, encrypt_times, decrypt_times = [], [], []
    pub_sizes, priv_sizes = [], []

    for _ in range(ITERATIONS):
        start = time.perf_counter()
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        keygen_times.append(time.perf_counter() - start)

        public_key = private_key.public_key()

        pub_sizes.append(public_key.key_size // 8)
        priv_sizes.append(private_key.key_size // 8)

        message = b"Hello PQC"

        # Encrypt
        start = time.perf_counter()
        ciphertext = public_key.encrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        encrypt_times.append(time.perf_counter() - start)

        # Decrypt
        start = time.perf_counter()
        private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        decrypt_times.append(time.perf_counter() - start)

    return {
        "keygen": compute_stats(keygen_times),
        "encrypt": compute_stats(encrypt_times),
        "decrypt": compute_stats(decrypt_times),
        "pub_size": statistics.mean(pub_sizes),
        "priv_size": statistics.mean(priv_sizes),
    }


# -----------------------------
# KYBER BENCHMARK
# -----------------------------
def benchmark_kyber():
    keygen_times, encap_times, decap_times = [], [], []
    pub_sizes, priv_sizes = [], []

    for _ in range(ITERATIONS):
        with oqs.KeyEncapsulation("Kyber512") as kem:

            start = time.perf_counter()
            public_key = kem.generate_keypair()
            secret_key = kem.export_secret_key()
            keygen_times.append(time.perf_counter() - start)

            pub_sizes.append(len(public_key))
            priv_sizes.append(len(secret_key))

            # Encapsulation
            start = time.perf_counter()
            ciphertext, ss_enc = kem.encap_secret(public_key)
            encap_times.append(time.perf_counter() - start)

            # Decapsulation
            start = time.perf_counter()
            ss_dec = kem.decap_secret(ciphertext)
            decap_times.append(time.perf_counter() - start)

            assert ss_enc == ss_dec

    return {
        "keygen": compute_stats(keygen_times),
        "encrypt": compute_stats(encap_times),
        "decrypt": compute_stats(decap_times),
        "pub_size": statistics.mean(pub_sizes),
        "priv_size": statistics.mean(priv_sizes),
    }


# -----------------------------
# DILITHIUM BENCHMARK
# -----------------------------
def benchmark_dilithium():
    keygen_times, sign_times, verify_times = [], [], []
    pub_sizes, priv_sizes, sig_sizes = [], [], []

    for _ in range(ITERATIONS):
        with oqs.Signature("Dilithium2") as sig:

            start = time.perf_counter()
            public_key = sig.generate_keypair()
            secret_key = sig.export_secret_key()
            keygen_times.append(time.perf_counter() - start)

            pub_sizes.append(len(public_key))
            priv_sizes.append(len(secret_key))

            message = b"Hello PQC"

            # Sign
            start = time.perf_counter()
            signature = sig.sign(message)
            sign_times.append(time.perf_counter() - start)

            sig_sizes.append(len(signature))

            # Verify
            start = time.perf_counter()
            sig.verify(message, signature, public_key)
            verify_times.append(time.perf_counter() - start)

    return {
        "keygen": compute_stats(keygen_times),
        "sign": compute_stats(sign_times),
        "verify": compute_stats(verify_times),
        "pub_size": statistics.mean(pub_sizes),
        "priv_size": statistics.mean(priv_sizes),
        "sig_size": statistics.mean(sig_sizes),
    }


# -----------------------------
# PERFORMANCE GRAPH
# -----------------------------
def plot_results(rsa, kyber, dilithium):
    labels = ["KeyGen", "Encrypt/Sign", "Decrypt/Verify"]
    x = range(len(labels))

    rsa_mean = [rsa["keygen"]["mean"], rsa["encrypt"]["mean"], rsa["decrypt"]["mean"]]
    kyber_mean = [kyber["keygen"]["mean"], kyber["encrypt"]["mean"], kyber["decrypt"]["mean"]]
    dilithium_mean = [dilithium["keygen"]["mean"], dilithium["sign"]["mean"], dilithium["verify"]["mean"]]

    rsa_std = [rsa["keygen"]["std"], rsa["encrypt"]["std"], rsa["decrypt"]["std"]]
    kyber_std = [kyber["keygen"]["std"], kyber["encrypt"]["std"], kyber["decrypt"]["std"]]
    dilithium_std = [dilithium["keygen"]["std"], dilithium["sign"]["std"], dilithium["verify"]["std"]]

    plt.figure(figsize=(9, 5))

    plt.errorbar(x, rsa_mean, yerr=rsa_std, marker='o', label="RSA", capsize=5)
    plt.errorbar(x, kyber_mean, yerr=kyber_std, marker='o', label="Kyber", capsize=5)
    plt.errorbar(x, dilithium_mean, yerr=dilithium_std, marker='o', label="Dilithium", capsize=5)

    plt.xticks(x, labels)
    plt.xlabel("Operations")
    plt.ylabel("Time (seconds)")
    plt.title("Performance Comparison (Mean ± Std Dev)")
    plt.legend()
    plt.grid()

    plt.savefig("comparison_detailed.png", dpi=300)
    print("📊 Saved: comparison_detailed.png")


# -----------------------------
# KEY SIZE GRAPH
# -----------------------------
def plot_key_sizes(rsa, kyber, dilithium):
    algorithms = ["RSA", "Kyber", "Dilithium"]

    pub_sizes = [rsa["pub_size"], kyber["pub_size"], dilithium["pub_size"]]
    priv_sizes = [rsa["priv_size"], kyber["priv_size"], dilithium["priv_size"]]

    x = range(len(algorithms))
    width = 0.35

    plt.figure(figsize=(8, 5))

    plt.bar([i - width/2 for i in x], pub_sizes, width=width, label="Public Key")
    plt.bar([i + width/2 for i in x], priv_sizes, width=width, label="Private Key")

    plt.xticks(x, algorithms)
    plt.xlabel("Algorithms")
    plt.ylabel("Size (bytes)")
    plt.title("Key Size Comparison")
    plt.legend()
    plt.grid(axis='y')

    plt.savefig("key_sizes.png", dpi=300)
    print("📊 Saved: key_sizes.png")


# -----------------------------
# MAIN
# -----------------------------
def main():
    print("Running benchmarks...\n")

    rsa_results = benchmark_rsa()
    kyber_results = benchmark_kyber()
    dilithium_results = benchmark_dilithium()

    pp = pprint.PrettyPrinter(indent=2)

    print("\n===== RESULTS =====\n")
    print("RSA:")
    pp.pprint(rsa_results)

    print("\nKyber:")
    pp.pprint(kyber_results)

    print("\nDilithium:")
    pp.pprint(dilithium_results)

    print("\n===== MEMORY USAGE (MB) =====")
    print("RSA:", measure_memory(benchmark_rsa))
    print("Kyber:", measure_memory(benchmark_kyber))
    print("Dilithium:", measure_memory(benchmark_dilithium))

    # Graphs
    plot_results(rsa_results, kyber_results, dilithium_results)
    plot_key_sizes(rsa_results, kyber_results, dilithium_results)


if __name__ == "__main__":
    main()