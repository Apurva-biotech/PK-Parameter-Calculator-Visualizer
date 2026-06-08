"""Visualization utilities for concentration-time data and PK model fits."""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd

from models.one_compartment import OneCompartmentFit, concentration_time_model

os.environ.setdefault("MPLCONFIGDIR", str(Path.cwd() / ".matplotlib-cache"))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


def plot_concentration_time_profile(
    data: pd.DataFrame,
    model_fit: OneCompartmentFit,
    output_path: str | Path,
    points: int = 250,
) -> Path:
    """Plot observed concentration-time data and the fitted model curve.

    Args:
        data: DataFrame with `time` and `concentration` columns.
        model_fit: Fitted one-compartment model parameters.
        output_path: PNG path where the figure will be saved.
        points: Number of model-curve points.

    Returns:
        Path to the saved PNG file.
    """

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    time = data["time"].to_numpy(dtype=float)
    concentration = data["concentration"].to_numpy(dtype=float)
    model_time = np.linspace(float(time.min()), float(time.max()), points)
    model_concentration = concentration_time_model(model_time, model_fit.c0, model_fit.ke)

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)

    ax.scatter(time, concentration, color="#1f77b4", label="Observed data", zorder=3)
    ax.plot(
        model_time,
        model_concentration,
        color="#d62728",
        linewidth=2.2,
        label="One-compartment fit",
    )

    ax.set_title("Plasma Concentration-Time Profile")
    ax.set_xlabel("Time")
    ax.set_ylabel("Plasma concentration")
    ax.legend()
    ax.margins(x=0.02, y=0.08)

    fig.tight_layout()
    fig.savefig(output, format="png")
    plt.close(fig)

    return output
