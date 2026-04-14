# 📰 Newsvendor Problem — Monte Carlo Simulation

A Streamlit app for simulating the classic **Newsvendor (single-period inventory) problem**. It helps you find the order quantity that maximizes average profit when demand is uncertain and uniformly distributed.

## How It Works

1. You set cost, revenue, and demand parameters in the sidebar.
2. The app generates random demand samples from a uniform distribution.
3. It sweeps through a range of order quantities you define and calculates the average profit for each.
4. The optimal order quantity (Q*) is identified and highlighted on an interactive chart.

## Getting Started

### Install dependencies

```bash
pip install streamlit numpy pandas plotly
```

### Run the app

```bash
streamlit run app.py
```

## Sample Parameter Values

Below is an example configuration you can enter in the sidebar:

| Section | Parameter | Example Value |
|---|---|---|
| **Cost & Revenue** | Unit cost (buy from supplier) | $0.25 |
| | Resale price (sell at newsstand) | $1.00 |
| | Salvage value (unsold) | $0.00 |
| **Demand Distribution** | Mean demand | 150 |
| | ± range around mean | 50 |
| | *(resulting distribution)* | Uniform(100, 200) |
| **Order Quantity Search** | Lower limit (Q min) | 100 |
| | Upper limit (Q max) | 200 |
| | Step size | 5 |
| | *(search space)* | Q ∈ [100, 200] with step 5 |
| **Simulation Settings** | Number of replications | 1000 |
| | Random seed (0 = random) | 5 |

## Features

- Interactive profit curve with ±1 std dev band and optimal Q marked
- KPI cards: mean / std / min / max profit, service level, lost sales
- Profit distribution histogram at the optimal order quantity
- Demand distribution chart overlaid with optimal Q
- Downloadable CSV of all search results
