#!/usr/bin/env python3
"""
System Information Logger
Logs system information including OS, CPU count, RAM, and active thread count.
"""

import platform
import os
import threading
import subprocess
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


def main():
    """Main function to log system information."""
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


if __name__ == "__main__":
    main()

