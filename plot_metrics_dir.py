# HOW TO USE:
# python3 plot_metrics_dir.py results/logs/

#!/usr/bin/env python3
"""
plot_metrics_dir.py

Plots ALL *_stdout.txt files in a directory on the same figure.
- Latency lines (solid) on top plot
- Throughput lines (solid) on bottom plot
- Same color per file (paired)
- Right-side panel shows mean latency (top) + mean throughput (bottom) as colored boxes
"""

import argparse
import matplotlib.pyplot as plt
import re
import colorsys
from pathlib import Path


METRIC_PATTERN = re.compile(
    r"(\d+),\s*([0-9]*\.?[0-9]+(?:[eE][-+]?\d+)?)\s*s,\s*([0-9]*\.?[0-9]+(?:[eE][-+]?\d+)?)\s*q/s,"
)

LABEL_RE = re.compile(r"^(?P<prefix>.+?)_(?P<params>[^_]+)_(?:\d+)_stdout$", re.IGNORECASE)


# Parse a stdout metrics file into aligned index/latency/throughput arrays.
def parse_metrics(file_path: Path):
    indices, latencies, throughputs = [], [], []
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            m = METRIC_PATTERN.search(line)
            if m:
                indices.append(int(m.group(1)))
                latencies.append(float(m.group(2)))
                throughputs.append(float(m.group(3)))
    return indices, latencies, throughputs


# Derive a run label from a filename by dropping the job id and _stdout suffix when present.
def label_from_file(file_path: Path) -> str:
    stem = file_path.stem
    m = LABEL_RE.match(stem)
    if m:
        return f"{m.group('prefix')}_{m.group('params')}"
    return re.sub(r"_(?:\d+)_stdout$", "", stem, flags=re.IGNORECASE)


# Generate a list of visually separated colors using golden-ratio hue stepping in HLS space.
def color_cycle(n: int):
    golden_ratio = 0.618033988749895
    hue = 0.0
    colors = []
    for _ in range(n):
        hue = (hue + golden_ratio) % 1.0
        r, g, b = colorsys.hls_to_rgb(hue, 0.55, 0.65)
        colors.append((r, g, b))
    return colors


# Render a right-side panel of color-matched metric summary boxes for each run.
def add_box_panel(ax, title: str, items, max_items: int):
    ax.set_axis_off()
    ax.set_title(title, loc="left", fontsize=10, pad=6)

    items = items[:max_items]
    if not items:
        return

    y = 0.98
    dy = 0.92 / len(items)

    for label, value, color in items:
        ax.text(
            0.02,
            y,
            f"{value}  {label}",
            transform=ax.transAxes,
            va="top",
            ha="left",
            fontsize=8,
            color="black",
            bbox=dict(boxstyle="round,pad=0.25", facecolor=color, alpha=0.35, edgecolor=color),
        )
        y -= dy


# Load all matching stdout files, plot per-run latency/throughput, and show/save with mean summary panels.
def plot_directory(dir_path: Path, pattern: str, out_path: Path | None, top_n: int, panel_limit: int):
    files = sorted(dir_path.glob(pattern))
    if not files:
        raise SystemExit(f"No files matched in {dir_path} with pattern: {pattern}")

    series = []
    for fp in files:
        idx, lat, thr = parse_metrics(fp)
        if idx:
            series.append((fp, idx, lat, thr))

    if not series:
        raise SystemExit(f"Matched {len(files)} file(s) but found no metrics lines in any of them.")

    series.sort(key=lambda t: (label_from_file(t[0]).lower(), t[0].name.lower()))

    if top_n > 0 and len(series) > top_n:
        series = series[:top_n]

    colors = color_cycle(len(series))

    fig = plt.figure(figsize=(16, 9), constrained_layout=True)
    gs = fig.add_gridspec(2, 2, width_ratios=[5.6, 1.4], height_ratios=[1, 1])

    ax_lat = fig.add_subplot(gs[0, 0])
    ax_thr = fig.add_subplot(gs[1, 0], sharex=ax_lat)
    ax_lat_box = fig.add_subplot(gs[0, 1])
    ax_thr_box = fig.add_subplot(gs[1, 1])

    ax_lat.set_ylabel("Latency (s)")
    ax_thr.set_ylabel("Throughput (q/s)")
    ax_thr.set_xlabel("Question Index")

    ax_lat.grid(True, alpha=0.25)
    ax_thr.grid(True, alpha=0.25)

    handles, labels = [], []
    lat_items = []
    thr_items = []

    for color, (fp, idx, lat, thr) in zip(colors, series):
        label = label_from_file(fp)

        (h_lat,) = ax_lat.plot(idx, lat, color=color, linewidth=1.4, alpha=0.9)
        ax_thr.plot(idx, thr, color=color, linewidth=1.4, alpha=0.9)

        handles.append(h_lat)
        labels.append(label)

        mean_lat = sum(lat) / len(lat)
        mean_thr = sum(thr) / len(thr)

        lat_items.append((label, f"{mean_lat:.3f}s", color))
        thr_items.append((label, f"{mean_thr:.3f} q/s", color))

    ax_lat.set_title("Latency")
    ax_thr.set_title("Throughput")

    ncols = 2 if len(labels) > 12 else 1
    ax_lat.legend(handles, labels, loc="upper right", fontsize=8, framealpha=0.9, ncol=ncols)

    add_box_panel(ax_lat_box, "Mean Latency", lat_items, max_items=panel_limit)
    add_box_panel(ax_thr_box, "Mean Throughput", thr_items, max_items=panel_limit)

    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=200)
        print(f"Saved: {out_path}")
    else:
        plt.show()


# Parse CLI args, resolve paths, and invoke directory plotting.
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("directory", type=str, help="Directory containing *_stdout.txt files")
    ap.add_argument("--pattern", type=str, default="*_stdout.txt")
    ap.add_argument("--out", type=str, default="")
    ap.add_argument("--top", type=int, default=0)
    ap.add_argument("--panel-limit", type=int, default=60)
    args = ap.parse_args()

    dir_path = Path(args.directory).expanduser().resolve()
    if not dir_path.exists() or not dir_path.is_dir():
        raise SystemExit(f"Not a directory: {dir_path}")

    out_path = Path(args.out).expanduser().resolve() if args.out else None
    plot_directory(dir_path, args.pattern, out_path, top_n=args.top, panel_limit=args.panel_limit)


if __name__ == "__main__":
    main()