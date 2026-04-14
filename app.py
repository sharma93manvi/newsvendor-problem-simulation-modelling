import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Newsvendor Simulation", page_icon="📰", layout="wide")

st.title("📰 Newsvendor Problem — Monte Carlo Simulation")
st.markdown(
    "Simulate the classic newsvendor problem: how many newspapers should you order "
    "to maximize profit when demand is uncertain?"
)

with st.expander("ℹ️ How to Use — with Sample Values"):
    st.markdown("""\
Set the parameters in the sidebar, then click **Run Simulation**. Here's an example to get started:

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

The app will sweep every order quantity in your search range, find the one that maximizes
average profit, and display the results with interactive charts.
""")

# ── Sidebar: Parameters ──────────────────────────────────────────────
st.sidebar.header("⚙️ Parameters")

st.sidebar.subheader("Cost & Revenue")
cost = st.sidebar.number_input(
    "Unit cost (buy from supplier) $", min_value=0.01, value=0.25, step=0.05, format="%.2f"
)
price = st.sidebar.number_input(
    "Resale price (sell at newsstand) $", min_value=0.01, value=1.00, step=0.05, format="%.2f"
)
salvage = st.sidebar.number_input(
    "Salvage value (unsold) $", min_value=0.00, value=0.00, step=0.05, format="%.2f",
    help="Revenue recovered per unsold unit (e.g. recycling value)."
)

st.sidebar.subheader("Demand Distribution (Uniform)")
demand_mean = st.sidebar.number_input(
    "Mean demand", min_value=1, value=150, step=5
)
demand_half_range = st.sidebar.number_input(
    "± range around mean", min_value=1, value=50, step=5,
    help="Demand is drawn uniformly from [mean − range, mean + range]."
)
demand_low = demand_mean - demand_half_range
demand_high = demand_mean + demand_half_range
st.sidebar.caption(f"Demand ~ Uniform({demand_low}, {demand_high})")

st.sidebar.subheader("Order Quantity Search Range")
q_lower = st.sidebar.number_input(
    "Lower limit (Q min)", min_value=1, value=max(1, demand_low), step=5,
    help="Smallest order quantity to evaluate."
)
q_upper = st.sidebar.number_input(
    "Upper limit (Q max)", min_value=1, value=demand_high, step=5,
    help="Largest order quantity to evaluate."
)
q_step = st.sidebar.number_input(
    "Step size", min_value=1, value=5, step=1,
    help="Increment between order quantities in the search."
)
st.sidebar.caption(f"Searching Q ∈ [{q_lower}, {q_upper}] with step {q_step}")

st.sidebar.subheader("Simulation Settings")
n_reps = st.sidebar.number_input(
    "Number of replications", min_value=10, max_value=100_000, value=1000, step=100
)
seed = st.sidebar.number_input("Random seed (0 = random)", min_value=0, value=5, step=1)

run = st.sidebar.button("🚀 Run Simulation", use_container_width=True, type="primary")

# ── Validation ────────────────────────────────────────────────────────
if price <= cost:
    st.warning("Resale price should be greater than unit cost to make a profit.")
if salvage > cost:
    st.warning("Salvage value exceeding cost means there's no risk — check your inputs.")
if demand_low < 0:
    st.error("Demand lower bound is negative. Increase the mean or decrease the range.")
    st.stop()
if q_lower > q_upper:
    st.error("Q lower limit must be ≤ Q upper limit.")
    st.stop()

# ── Simulation ────────────────────────────────────────────────────────
if run:
    rng = np.random.default_rng(seed if seed > 0 else None)
    demands = rng.integers(demand_low, demand_high + 1, size=int(n_reps))

    # ── Sweep over order quantities ───────────────────────────────────
    q_range = np.arange(int(q_lower), int(q_upper) + 1, int(q_step))
    mean_profits = np.empty(len(q_range))
    std_profits = np.empty(len(q_range))

    progress = st.progress(0, text="Simulating…")
    for i, q in enumerate(q_range):
        s = np.minimum(demands, q)
        u = np.maximum(q - demands, 0)
        p = s * price + u * salvage - q * cost
        mean_profits[i] = p.mean()
        std_profits[i] = p.std()
        progress.progress((i + 1) / len(q_range), text=f"Evaluating Q = {q}")
    progress.empty()

    best_idx = int(np.argmax(mean_profits))
    best_q = int(q_range[best_idx])
    best_profit = mean_profits[best_idx]

    # ── Optimal Q highlight ───────────────────────────────────────────
    st.success(
        f"🏆 Optimal order quantity: **Q = {best_q}** → "
        f"Average profit = **${best_profit:,.2f}** "
        f"(over {int(n_reps):,} replications)"
    )

    # ── Average Profit Curve ──────────────────────────────────────────
    st.subheader("📈 Average Profit by Order Quantity")
    sens_df = pd.DataFrame({
        "Order Quantity": q_range,
        "Avg Profit ($)": np.round(mean_profits, 2),
        "Std Dev ($)": np.round(std_profits, 2),
    })

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=q_range, y=mean_profits,
        mode="lines", name="Avg Profit",
        line=dict(color="#636EFA", width=2),
    ))
    # ± 1 std dev band
    fig.add_trace(go.Scatter(
        x=np.concatenate([q_range, q_range[::-1]]),
        y=np.concatenate([mean_profits + std_profits, (mean_profits - std_profits)[::-1]]),
        fill="toself", fillcolor="rgba(99,110,250,0.15)",
        line=dict(color="rgba(255,255,255,0)"),
        name="± 1 Std Dev",
    ))
    # Mark optimal Q
    fig.add_trace(go.Scatter(
        x=[best_q], y=[best_profit],
        mode="markers+text",
        marker=dict(color="green", size=14, symbol="star"),
        text=[f"Q*={best_q}  ${best_profit:,.2f}"],
        textposition="top center",
        name="Optimal Q",
    ))
    fig.update_layout(
        xaxis_title="Order Quantity (Q)",
        yaxis_title="Average Profit ($)",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Detailed stats for optimal Q ──────────────────────────────────
    sold = np.minimum(demands, best_q)
    unsold = np.maximum(best_q - demands, 0)
    lost_sales = np.maximum(demands - best_q, 0)
    profit = sold * price + unsold * salvage - best_q * cost

    st.subheader(f"📊 Detailed Stats at Optimal Q = {best_q}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Mean Profit", f"${profit.mean():,.2f}")
    c2.metric("Std Dev Profit", f"${profit.std():,.2f}")
    c3.metric("Min Profit", f"${profit.min():,.2f}")
    c4.metric("Max Profit", f"${profit.max():,.2f}")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Mean Demand", f"{demands.mean():,.1f}")
    c6.metric("Avg Units Sold", f"{sold.mean():,.1f}")
    c7.metric("Avg Unsold", f"{unsold.mean():,.1f}")
    c8.metric("Avg Lost Sales", f"{lost_sales.mean():,.1f}")

    st.markdown(f"**Service level (% demand met):** {100 * sold.sum() / demands.sum():.1f}%")

    # ── Profit distribution at optimal Q ──────────────────────────────
    st.subheader("📉 Profit Distribution at Optimal Q")
    fig_hist = px.histogram(
        x=profit, nbins=40, color_discrete_sequence=["#636EFA"],
        labels={"x": "Profit ($)"},
    )
    fig_hist.add_vline(x=profit.mean(), line_dash="dash", line_color="red",
                       annotation_text=f"Mean = ${profit.mean():,.2f}")
    fig_hist.update_layout(bargap=0.05, xaxis_title="Profit ($)", yaxis_title="Count")
    st.plotly_chart(fig_hist, use_container_width=True)

    # ── Demand histogram ──────────────────────────────────────────────
    st.subheader("📊 Demand Distribution (sampled)")
    fig_demand = px.histogram(
        x=demands, nbins=40, color_discrete_sequence=["#00CC96"],
        labels={"x": "Demand"},
    )
    fig_demand.add_vline(x=best_q, line_dash="dash", line_color="red",
                         annotation_text=f"Optimal Q = {best_q}")
    fig_demand.update_layout(xaxis_title="Demand", yaxis_title="Count")
    st.plotly_chart(fig_demand, use_container_width=True)

    # ── Search results table ──────────────────────────────────────────
    with st.expander("🗂️ View Full Search Results"):
        st.dataframe(sens_df, use_container_width=True, height=400)
        csv = sens_df.to_csv(index=False)
        st.download_button("⬇️ Download CSV", csv, "newsvendor_search.csv", "text/csv")
else:
    st.info("👈 Set your parameters in the sidebar and click **Run Simulation** to begin.")
