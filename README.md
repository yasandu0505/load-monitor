# load-monitor

A Python program that logs system information including OS, CPU count, RAM, and active thread count.

## Features

- Logs current operating system information
- Displays number of CPUs
- Shows total and available RAM
- Displays current number of active threads

## Requirements

- Python 3.6+
- psutil library

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the program:
```bash
python main.py
```

The program will output system information to the console and exit.

## Output Example

```
==================================================
System Information
==================================================
Current OS: Darwin 24.6.0 (Darwin Kernel Version 24.6.0...)
Number of CPUs: 8
Total RAM: 16.00 GB
Available RAM: 4.50 GB
Number of active threads: 1
==================================================
```

## Deployment

This program can be deployed on any service that supports Python. Simply:
1. Upload the files to your service
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python main.py`