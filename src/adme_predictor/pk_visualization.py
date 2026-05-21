"""Visualization helpers for educational PK/NCA outputs."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd


def plot_concentration_time(profile: pd.DataFrame):
    """Create a linear concentration-time plot."""
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(profile["time"], profile["concentration"], marker="o", linewidth=1.8)
    ax.set_xlabel("Time")
    ax.set_ylabel("Concentration")
    ax.set_title("Concentration-Time Profile")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    return fig


def plot_semilog_concentration_time(profile: pd.DataFrame):
    """Create a semi-log concentration-time plot."""
    fig, ax = plt.subplots(figsize=(7, 4))
    positive = profile[profile["concentration"] > 0]
    ax.semilogy(positive["time"], positive["concentration"], marker="o", linewidth=1.8)
    ax.set_xlabel("Time")
    ax.set_ylabel("Concentration, log scale")
    ax.set_title("Semi-Log Concentration-Time Profile")
    ax.grid(alpha=0.25, which="both")
    fig.tight_layout()
    return fig
