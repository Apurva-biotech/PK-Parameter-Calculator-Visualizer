# PK Parameter Calculator & Visualizer

A production-quality Python portfolio project for pharmacokinetic analysis of plasma concentration-time data. The tool reads a CSV file, validates analytical data, calculates core pharmacokinetic parameters, fits a one-compartment IV bolus model, and exports a publication-ready PNG visualization.

## Project Overview

This project is designed for biotechnology and computational pharmacokinetics portfolios. It demonstrates:

- Robust CSV data ingestion and validation
- Noncompartmental pharmacokinetic calculations
- One-compartment IV bolus model fitting with `scipy.optimize.curve_fit`
- Modular Python code with type hints and docstrings
- Reproducible visualization with `matplotlib`
- Interactive web analysis with `streamlit` and `plotly`

## Project Structure

```text
pk_calculator/
├── data/
│   └── sample_data.csv
├── models/
│   └── one_compartment.py
├── calculator.py
├── visualizer.py
├── app.py
├── main.py
├── requirements.txt
└── README.md
```

## Pharmacokinetic Theory

The input data must contain plasma concentration measurements over time:

```csv
time,concentration
0.0,50.0
0.25,45.9
...
```

The calculator estimates:

- **Cmax**: maximum observed plasma concentration.
- **Tmax**: time at which Cmax occurs.
- **AUC0-last**: area under the observed concentration-time curve, calculated with the linear trapezoidal rule.
- **ke**: terminal elimination rate constant estimated from the slope of the log-linear terminal phase.
- **t1/2**: elimination half-life, calculated as `ln(2) / ke`.
- **Vd**: apparent volume of distribution for IV bolus dosing, calculated as `Dose / C0`.
- **CL**: clearance, calculated as `ke * Vd`.

The one-compartment IV bolus model is:

```text
C(t) = C0 * exp(-ke * t)
```

Key assumptions:

- The dose is administered as an IV bolus.
- Distribution is instantaneous and can be represented by a single well-mixed compartment.
- Elimination follows first-order kinetics.
- The terminal phase is log-linear.
- AUC is reported as observed AUC0-last and is not extrapolated to infinity.

## Installation

From the project directory:

```bash
cd pk_calculator
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Usage

Run the Streamlit web app:

```bash
streamlit run app.py
```

Run the sample analysis:

```bash
python main.py --input data/sample_data.csv --dose 1000 --output pk_profile.png
```

Use your own CSV file:

```bash
python main.py --input path/to/your_data.csv --dose 250 --output results/my_pk_plot.png
```

Your CSV must include:

```csv
time,concentration
0,50.0
1,35.8
2,26.4
4,14.9
8,4.9
```

## Example Output

Console output:

```text
PK Parameter Calculator & Visualizer
========================================
Cmax:       50.0000
Tmax:       0.0000
AUC0-last:  163.6375
ke:         0.2786
t1/2:       2.4884
Vd:         20.2727
CL:         5.6470

One-compartment model fit
C0:         49.3273
ke_fit:     0.3046

Saved plot: pk_profile.png
```

The generated PNG overlays observed concentration-time data with the fitted one-compartment curve.

## Streamlit Web App

The Streamlit interface provides:

- CSV upload for files containing `time` and `concentration` columns.
- Dose input from the sidebar.
- Calculated PK parameters displayed as metrics.
- Fitted one-compartment model parameters.
- Interactive Plotly concentration-time visualization.
- Downloadable `pk_results.csv` containing calculated parameters and model-fit results.

If no CSV is uploaded, the app analyzes `data/sample_data.csv` so the project is immediately demo-ready.

## Deployment

### Local macOS Deployment

From the project directory:

```bash
cd pk_calculator
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run app.py
```

Streamlit will print a local URL, usually:

```text
http://localhost:8501
```

### Streamlit Community Cloud

1. Push the `pk_calculator` project to a GitHub repository.
2. Confirm that `requirements.txt`, `app.py`, and the `data/` folder are committed.
3. Create a new app in Streamlit Community Cloud.
4. Set the app entry point to `app.py`.
5. Deploy the app.

For a repository where `pk_calculator` is a subfolder, set the app path to `pk_calculator/app.py`.

## Data Validation

The program checks that:

- Required columns `time` and `concentration` are present.
- There are no missing values.
- Time and concentration values are numeric.
- Time values are strictly increasing.
- Concentrations are non-negative.
- At least three observations are present.

## Notes on Units

The code is unit-consistent but unit-agnostic. For example, if dose is in mg and concentration is in mg/L, then:

- Vd is reported in L.
- CL is reported in L per time unit.
- ke is reported as inverse time.
- half-life uses the same time unit as the input time column.

## Future Improvements

- Add two-compartment IV bolus and oral absorption models.
- Estimate AUC extrapolated to infinity with terminal residual area.
- Support replicate observations and summary statistics.
- Add weighted regression options for heteroscedastic concentration data.
- Report confidence intervals and goodness-of-fit metrics.
- Add authentication and project persistence for the Streamlit interface.
- Export results to Excel and PDF reports.
