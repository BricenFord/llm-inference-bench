# HOW TO USE:
# python3 plot_metrics.py results/logs/(file)

#!/usr/bin/env python3

import matplotlib.pyplot as plt
import re
import sys
from pathlib import Path

JOB_DIR = ""

def parse_metrics(file_path):
    indices, latencies, throughputs = [], [], []
    pattern = re.compile(r"(\d+),\s*([0-9]*\.?[0-9]+(?:[eE][-+]?\d+)?)\s*s,\s*([0-9]*\.?[0-9]+(?:[eE][-+]?\d+)?)\s*q/s,")

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            match = pattern.search(line)
            if match:
                indices.append(int(match.group(1)))
                latencies.append(float(match.group(2)))
                throughputs.append(float(match.group(3)))

    return indices, latencies, throughputs

def plot_metrics(indices, latencies, throughputs, title_suffix=""):
    fig, ax1 = plt.subplots(figsize=(12, 6))

    color = "tab:blue"
    ax1.set_xlabel("Question Index")
    ax1.set_ylabel("Latency (s)", color=color)
    ax1.plot(indices, latencies, color=color, linestyle="-", label="Latency")
    mean_latency = sum(latencies) / len(latencies)
    ax1.axhline(mean_latency, color=color, linestyle="--", alpha=0.5, label=f"Mean Latency ({mean_latency:.3f}s)")

    mid_index = indices[len(indices) // 2]
    ax1.text(
        mid_index,
        mean_latency * 1.02,
        f"{mean_latency:.3f}s",
        color=color,
        va="bottom",
        ha="center",
        fontsize=9,
        backgroundcolor="white",
        alpha=0.8,
    )

    ax1.tick_params(axis="y", labelcolor=color)
    ax1.grid(True)

    ax2 = ax1.twinx()
    color = "tab:red"
    ax2.set_ylabel("Throughput (q/s)", color=color)
    ax2.plot(indices, throughputs, color=color, linestyle="-", label="Throughput")
    mean_throughput = sum(throughputs) / len(throughputs)
    ax2.axhline(mean_throughput, color=color, linestyle="--", alpha=0.5, label=f"Mean Throughput ({mean_throughput:.3f} q/s)")

    ax2.text(
        mid_index,
        mean_throughput * 1.02,
        f"{mean_throughput:.3f}",
        color=color,
        va="bottom",
        ha="center",
        fontsize=9,
        backgroundcolor="white",
        alpha=0.8,
    )

    ax2.tick_params(axis="y", labelcolor=color)

    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc="upper right")

    fig.tight_layout()
    plt.title(f"Ollama Latency and Throughput {title_suffix}".strip())
    plt.show()

def main():
    if len(sys.argv) < 2:
        print("Usage: python plot_metrics.py <stdout_file_name_or_path>")
        return

    arg_path = Path(sys.argv[1]).expanduser()
    file_path = arg_path if arg_path.is_absolute() or arg_path.exists() else (Path(JOB_DIR) / arg_path)

    if not file_path.exists():
        print(f"File not found: {file_path}")
        return

    indices, latencies, throughputs = parse_metrics(file_path)
    if not indices:
        print(f"No metrics found in {file_path}.")
        return

    title_suffix = file_path.stem
    plot_metrics(indices, latencies, throughputs, title_suffix=title_suffix)

if __name__ == "__main__":
    main()