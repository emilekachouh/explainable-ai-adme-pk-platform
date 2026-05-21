"""Visualization helpers for educational PK/NCA outputs."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


LINE_COLOR = "#2563eb"
POINT_COLOR = "#0f172a"
GRID_COLOR = "#cbd5e1"


def _style_axis(ax, title: str) -> None:
    ax.set_title(title, fontsize=12, pad=12, weight="bold")
    ax.set_xlabel("Time")
    ax.set_ylabel("Concentration")
    ax.grid(alpha=0.35, color=GRID_COLOR)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def plot_concentration_time(profile: pd.DataFrame):
    """Create a linear concentration-time plot."""
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.plot(
        profile["time"],
        profile["concentration"],
        color=LINE_COLOR,
        linewidth=2.2,
    )
    ax.scatter(profile["time"], profile["concentration"], color=POINT_COLOR, s=22, zorder=3)
    _style_axis(ax, "Concentration-Time Profile")
    fig.tight_layout()
    return fig


def plot_semilog_concentration_time(profile: pd.DataFrame):
    """Create a semi-log concentration-time plot."""
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    positive = profile[profile["concentration"] > 0]
    ax.semilogy(
        positive["time"],
        positive["concentration"],
        color=LINE_COLOR,
        linewidth=2.2,
    )
    ax.scatter(positive["time"], positive["concentration"], color=POINT_COLOR, s=22, zorder=3)
    _style_axis(ax, "Semi-Log Concentration-Time Profile")
    ax.set_ylabel("Concentration, log scale")
    ax.grid(alpha=0.35, which="both", color=GRID_COLOR)
    fig.tight_layout()
    return fig
