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

This project currently includes scripts designed for **Slurm-based clusters**. The general workflow is as follows:

1. **Build Experiment Scripts**

   Run `build.sh` to generate all the `model.py` files.

   - Currently, these scripts only run **Ollama**, but more inference engines will be added in the future.
   - `build.sh` also generates `.sbatch` files for each experiment configuration.

   ```bash
   ./build.sh
   ```

2. **Run Experiments on the Server**

   Copy the generated files to a server that has the target inference engine installed.

   Use `run.sh` to submit all the `.sbatch` jobs to the Slurm scheduler according to your configuration:

   ```bash
   ./run.sh
   ```

3. **Collect Logs**

   Once all experiments complete, the log files from each inference engine will be stored in the `results/` directory.

   This directory will contain separate subdirectories for each engine, model, and client load configuration.

4. **Analyze and Visualize Results**

   Use `plot_metrics.py` to generate comparison plots for throughput, latency, and other key metrics:

   ```bash
   python plot_metrics.py results/
   ```