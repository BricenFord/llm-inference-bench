# llm-inference-bench

A benchmarking suite for evaluating **LLM inference performance** across different models, client loads, and inference engines. This project tracks throughput and latency to identify optimal configurations for serving large language models efficiently.

## Features

- Benchmark multiple **server frameworks**:
  - Ollama
  - OllamaCPP
  - vLLM
  - Ray Serve
- Evaluate **client-side concurrency** and load
- Compare **different models** on inference performance
- Measure **throughput**, **latency**, and other key metrics
- Configurable experiments for both **server** and **client** parameters

## Prerequisites

- Python 3.10+
- Git

## Installation

```bash
git clone https://github.com/bricenford/llm-inference-bench.git
```

## Getting Started

This project is a configurable benchmarking framework for evaluating LLM inference performance across different engines, models, and client loads on Slurm-based clusters.

The workflow is now configuration-driven and template-based. Instead of manually editing scripts, you define experiments via config files and generate all required artifacts automatically.

---

### 1. Define Your Engine Configuration

Create or modify a configuration file for the inference engine you want to benchmark.

An example is provided at:
> config/ollama.json


This file defines:

- Models to benchmark
- Slurm resource parameters (partition, CPUs, memory, time, mail settings)
- Engine-specific settings (container image, model path, port, startup delay)
- Python environment configuration (modules, virtualenv directory, requirements file)
- Client behavior (timeout, input CSV, etc.)

Adjust this file to match your cluster environment and experiment goals.

---

### 2. Modify Templates (If Needed)

Job scripts and client files are generated from templates.

Example templates are located in:
> templates/ollama/


You can modify these templates to change:

- SBATCH directives
- Working directory behavior
- Logging paths
- Runtime environment setup
- Container execution logic

If the defaults match your needs, no changes are required.

---

### 3. Declare Python Dependencies

Add any required Python packages to:
> requirements.txt

These dependencies will be installed automatically inside a virtual environment during job execution.

---

### 4. Generate SBATCH and Client Files

Run the engine-specific build script to generate:

- `.sbatch` job files
- Corresponding `client.py` inference scripts

Example:
> scripts/ollama/build.py

After running the build step, generated artifacts will appear under:
> generated/<engine>/

Each model configuration results in a separate SBATCH job.

---

### 5. Submit Jobs to Slurm

Use the submission script to dispatch all generated jobs:

./run.sh

This submits each .sbatch file to the Slurm scheduler according to your configuration.

### 6. Collect Results

After completion, logs and benchmark outputs are written to:

results/
├── logs/   # stdout / stderr from Slurm jobs
└── runs/   # benchmark metrics

### 7. Analyze and Visualize Metrics (COMING SOON) !!!

Once runs complete, use plot_metrics.py to generate throughput and latency comparisons:

python plot_metrics.py results/