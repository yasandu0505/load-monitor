#!/usr/bin/env python3

"""

System Information Logger

Logs system information including OS, CPU count, RAM, and active thread count.

"""

import time
import os
import platform
import threading
import subprocess
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import psutil


def get_lscpu_output():
    """Run lscpu command and return its output."""
    try:
        # Run lscpu command and capture output
        result = subprocess.run(
            ['lscpu'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except FileNotFoundError:
        return "lscpu command not found (Linux only)"
    except subprocess.CalledProcessError as e:
        return f"Error running lscpu: {e.stderr}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


def get_cpu_usage():
    """Get CPU usage information."""
    # Get overall CPU usage percentage (1 second interval for accuracy)
    overall_cpu_percent = psutil.cpu_percent(interval=1)
    
    # Get per-CPU usage percentages
    per_cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
    
    # Count CPUs that are actively being used (threshold: > 5% usage)
    active_cpus = sum(1 for cpu in per_cpu_percent if cpu > 5.0)
    
    # Count CPUs with high usage (threshold: > 50% usage)
    high_usage_cpus = sum(1 for cpu in per_cpu_percent if cpu > 50.0)
    
    return {
        'overall_percent': overall_cpu_percent,
        'per_cpu_percent': per_cpu_percent,
        'active_cpus': active_cpus,
        'high_usage_cpus': high_usage_cpus
    }


def get_system_info():
    """Collect and return system information."""
    # Get OS information
    os_name = platform.system()
    os_release = platform.release()
    os_version = platform.version()
    current_os = f"{os_name} {os_release} ({os_version})"
    
    # Get CPU count
    cpu_count = os.cpu_count()
    
    # Get CPU usage information
    cpu_usage = get_cpu_usage()
    
    # Get RAM information
    memory = psutil.virtual_memory()
    total_ram_gb = memory.total / (1024 ** 3)  # Convert bytes to GB
    available_ram_gb = memory.available / (1024 ** 3)
    
    # Get current active thread count
    active_threads = threading.active_count()
    
    # Get lscpu output (Linux only)
    lscpu_output = get_lscpu_output()
    
    return {
        'os': current_os,
        'cpu_count': cpu_count,
        'cpu_usage': cpu_usage,
        'total_ram_gb': total_ram_gb,
        'available_ram_gb': available_ram_gb,
        'active_threads': active_threads,
        'lscpu_output': lscpu_output
    }


def log_system_info():
    """Log system information."""
    info = get_system_info()
    cpu_usage = info['cpu_usage']
    
    print("=" * 50)
    print("System Information")
    print("=" * 50)
    print(f"Current OS: {info['os']}")
    print(f"Number of CPUs: {info['cpu_count']}")
    print(f"Overall CPU Usage: {cpu_usage['overall_percent']:.2f}%")
    print(f"CPUs Currently in Use (>5%): {cpu_usage['active_cpus']} / {info['cpu_count']}")
    print(f"CPUs with High Usage (>50%): {cpu_usage['high_usage_cpus']} / {info['cpu_count']}")
    print(f"Total RAM: {info['total_ram_gb']:.2f} GB")
    print(f"Available RAM: {info['available_ram_gb']:.2f} GB")
    print(f"Number of active threads: {info['active_threads']}")
    print("=" * 50)
    
    # Display per-CPU usage
    print("\nPer-CPU Usage:")
    print("-" * 50)
    for i, cpu_percent in enumerate(cpu_usage['per_cpu_percent']):
        status = "IN USE" if cpu_percent > 5.0 else "idle"
        print(f"CPU {i}: {cpu_percent:6.2f}% [{status}]")
    print("=" * 50)
    
    print("\nlscpu output:")
    print("-" * 50)
    print(info['lscpu_output'])
    print("=" * 50)


def get_memory_mb() -> float:
    """Return current process memory usage (RSS) in MB."""
    process = psutil.Process(os.getpid())
    rss_bytes = process.memory_info().rss
    return rss_bytes / (1024 * 1024)


def work_chunk(n_samples: int, seed: int) -> int:
    """
    Generate n_samples random points and count how many are inside the unit circle.
    """
    rng = np.random.default_rng(seed)
    x = rng.random(n_samples)
    y = rng.random(n_samples)
    inside = (x * x + y * y) <= 1.0
    return int(inside.sum())


def run_pi_estimate(total_samples: int, num_threads: int):
    samples_per_thread = total_samples // num_threads
    remainder = total_samples % num_threads

    t0 = time.perf_counter()

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []

        for i in range(num_threads):
            n = samples_per_thread + (1 if i < remainder else 0)
            seed = 1234 + i
            futures.append(executor.submit(work_chunk, n, seed))

        hits = sum(f.result() for f in futures)

    elapsed = time.perf_counter() - t0
    pi_estimate = 4.0 * hits / total_samples

    return pi_estimate, elapsed


def benchmark():
    sample_sizes = [5_000_000, 10_000_000, 20_000_000, 40_000_000, 50_000_000, 100_000_000]
    thread_counts = [1, 2, 4, 8, 16]

    print("\n=== Performance Benchmark: Monte Carlo π Estimation ===\n")
    print("samples\tthreads\tpi_estimate\telapsed_s\tmem_before_MB\tmem_after_MB\tmem_delta_MB")
    print("-" * 110)

    for total_samples in sample_sizes:
        for n_threads in thread_counts:

            mem_before = get_memory_mb()
            pi_est, elapsed = run_pi_estimate(total_samples, n_threads)
            mem_after = get_memory_mb()
            mem_delta = mem_after - mem_before

            print(
                f"{total_samples:,}\t"
                f"{n_threads}\t"
                f"{pi_est:.6f}\t"
                f"{elapsed:.4f}\t\t"
                f"{mem_before:8.2f}\t"
                f"{mem_after:8.2f}\t"
                f"{mem_delta:8.2f}"
            )

        print()  # blank line between sample groups


if __name__ == "__main__":
    # Log system information first
    log_system_info()
    
    # Then run the benchmark
    benchmark()