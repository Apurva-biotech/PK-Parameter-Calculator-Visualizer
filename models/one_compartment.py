"""One-compartment IV bolus pharmacokinetic model."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import curve_fit


@dataclass(frozen=True)
class OneCompartmentFit:
    """Estimated parameters for a one-compartment IV bolus model.

    Attributes:
        c0: Concentration at time zero, in the same units as the input data.
        ke: First-order elimination rate constant, in inverse time units.
        covariance: Covariance matrix returned by scipy.optimize.curve_fit.
    """

    c0: float
    ke: float
    covariance: np.ndarray


def concentration_time_model(
    time: np.ndarray | float,
    c0: float,
    ke: float,
) -> np.ndarray | float:
    """Return concentration for a one-compartment IV bolus model.

    The model assumes instantaneous distribution and first-order elimination:
    C(t) = C0 * exp(-ke * t).
    """

    return c0 * np.exp(-ke * time)


def fit_one_compartment_model(
    time: np.ndarray,
    concentration: np.ndarray,
) -> OneCompartmentFit:
    """Fit C(t) = C0 * exp(-ke * t) to concentration-time data.

    Args:
        time: Increasing sampling times.
        concentration: Non-negative plasma concentrations.

    Returns:
        Estimated C0, ke, and covariance matrix.

    Raises:
        ValueError: If the data are insufficient for nonlinear fitting.
        RuntimeError: If scipy cannot estimate model parameters.
    """

    if time.size < 3:
        raise ValueError("At least three concentration-time points are required for model fitting.")

    positive = concentration > 0
    if positive.sum() < 3:
        raise ValueError("At least three positive concentrations are required for model fitting.")

    initial_c0 = float(max(concentration[0], concentration.max()))
    terminal_time = time[positive]
    terminal_concentration = concentration[positive]

    # Estimate an initial ke from a log-linear slope to help nonlinear fitting converge.
    slope, _intercept = np.polyfit(terminal_time, np.log(terminal_concentration), 1)
    initial_ke = float(max(-slope, 1e-6))

    bounds = ([0.0, 0.0], [np.inf, np.inf])
    popt, pcov = curve_fit(
        concentration_time_model,
        time,
        concentration,
        p0=[initial_c0, initial_ke],
        bounds=bounds,
        maxfev=10_000,
    )

    return OneCompartmentFit(c0=float(popt[0]), ke=float(popt[1]), covariance=pcov)
