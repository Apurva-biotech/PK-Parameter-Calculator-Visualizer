"""Command-line entry point for the PK Parameter Calculator & Visualizer."""

from __future__ import annotations

import argparse
from pathlib import Path

from calculator import PKParameters, calculate_pk_parameters, load_concentration_data
from models.one_compartment import OneCompartmentFit, fit_one_compartment_model
from visualizer import plot_concentration_time_profile


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""

    parser = argparse.ArgumentParser(
        description="Calculate PK parameters and fit a one-compartment IV bolus model."
    )
    parser.add_argument(
        "--input",
        default="data/sample_data.csv",
        help="CSV file containing time and concentration columns.",
    )
    parser.add_argument(
        "--dose",
        type=float,
        default=1000.0,
        help="IV bolus dose. Units determine Vd and CL units.",
    )
    parser.add_argument(
        "--output",
        default="pk_profile.png",
        help="Output PNG path for the concentration-time plot.",
    )
    parser.add_argument(
        "--terminal-points",
        type=int,
        default=3,
        help="Number of final positive points used for noncompartmental ke estimation.",
    )
    return parser


def print_results(parameters: PKParameters, model_fit: OneCompartmentFit, figure_path: Path) -> None:
    """Print formatted analysis results."""

    print("\nPK Parameter Calculator & Visualizer")
    print("=" * 40)
    print(f"Cmax:       {parameters.cmax:.4f}")
    print(f"Tmax:       {parameters.tmax:.4f}")
    print(f"AUC0-last:  {parameters.auc:.4f}")
    print(f"ke:         {parameters.ke:.4f}")
    print(f"t1/2:       {parameters.half_life:.4f}")
    print(f"Vd:         {parameters.vd:.4f}")
    print(f"CL:         {parameters.clearance:.4f}")
    print("\nOne-compartment model fit")
    print(f"C0:         {model_fit.c0:.4f}")
    print(f"ke_fit:     {model_fit.ke:.4f}")
    print(f"\nSaved plot: {figure_path}")


def main() -> None:
    """Run the full PK analysis workflow."""

    parser = build_parser()
    args = parser.parse_args()

    data = load_concentration_data(args.input)
    model_fit = fit_one_compartment_model(
        data["time"].to_numpy(dtype=float),
        data["concentration"].to_numpy(dtype=float),
    )
    parameters = calculate_pk_parameters(
        data,
        dose=args.dose,
        c0=model_fit.c0,
        terminal_points=args.terminal_points,
    )
    figure_path = plot_concentration_time_profile(data, model_fit, args.output)

    print_results(parameters, model_fit, figure_path)


if __name__ == "__main__":
    main()
