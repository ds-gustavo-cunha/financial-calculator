
# --- Logic Function ---
from typing import List
from typing import Dict
from typing import Union
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
plt.style.use("fivethirtyeight")

# --- Logic Function ---
def calculate_projection(
    monthly_savings: int,
    yearly_return: Union[int, float],
    yearly_inflation: Union[int, float],
    max_years: int = 10
) -> Dict[str, pd.DataFrame]:
    # Create a dataframe with months
    df_finance: pd.DataFrame = pd.DataFrame(data={
        "months": np.arange(0, max_years * 12 + 1)
    })

    # Get years column
    df_finance["years"] = df_finance["months"] / 12

    # Create a column with invested money
    df_finance["total_invested"] = df_finance["months"] * monthly_savings

    # Get month return as percentage
    monthly_return_percent = (1 + yearly_return / 100) ** (1 / 12) - 1

    # Convert yearly inflation to monthly and get as percentage
    #   1 + r_{annual} = (1 + r_{monthly})^12
    monthly_inflation_percent = (1 + yearly_inflation / 100) ** (1 / 12) - 1
    
    # Calculate Nominal Value
    # Handle month 0 to avoid division by zero
    nominal_vals: List[float] = [0.0]
    # Iterate over all possible months
    for _ in range(len(df_finance) - 1):
        # new momth value = last month value * monthly return + monthly savings
        nominal_vals.append(
            nominal_vals[-1] * (1 + monthly_return_percent) + monthly_savings
        )
    
    # Add nominal vals to dataframe
    df_finance["gross_value"] = nominal_vals

    # Create net value
    df_finance["net_value"] = df_finance["gross_value"] / (1 + monthly_inflation_percent) ** df_finance["months"]

    # Create return columns
    df_finance["gross_return"] = df_finance["gross_value"] - df_finance["total_invested"]
    df_finance["net_return"] = df_finance["net_value"] - df_finance["total_invested"]

    return dict(
        df_finance_months=df_finance,
        df_finance_years=df_finance[
            df_finance["months"] % 12 == 0
        ]
    )


# --- Streamlit UI ---
st.set_page_config(page_title="Investment & Inflation Calculator", layout="wide")
st.title("📈 Financial Freedom Calculator")
st.markdown("Visualize how compound interest grows your wealth and how inflation impacts your purchasing power.")

# --- Sidebar Inputs ---
st.sidebar.header("User Inputs")
monthly_savings = st.sidebar.number_input(
    label="Monthly Savings ($)",
    min_value=0, value=20_000, step=100
)
yearly_return = st.sidebar.slider(
    label="Yearly Return Rate (%)",
    min_value=0.0, max_value=100.0, value=10.0, step=0.1
)
yearly_inflation = st.sidebar.slider(
    label="Yearly Inflation Rate (%)",
    min_value=0.0, max_value=100.0, value=10.0, step=0.01
)
max_years = int(
    st.sidebar.number_input(
        label="Investment Horizon (Years)",
        min_value=1, max_value=50, value=10
    )
)

# --- Calculations ---
df_finance_months = calculate_projection(
    monthly_savings=monthly_savings,
    yearly_return=yearly_return,
    yearly_inflation=yearly_inflation,
    max_years=max_years
)["df_finance_months"]


# --- Summary Metrics ---
# Get metrics
invested_final = monthly_savings * max_years * 12
gross_final = df_finance_months["gross_value"].iloc[-1]
net_final = df_finance_months["net_value"].iloc[-1]
# Display
col1, col2, col3 = st.columns(3)
col1.metric(
    label="Total Cash Invested", value=f"$ {invested_final:,.0f}"
)
col2.metric(
    label="Final Bank Balance (Nominal)",
    value=f"$ {gross_final:,.0f}", 
    delta=f"${gross_final - invested_final:,.0f} interest",
    delta_color="normal"
)
col3.metric(
    label="Purchasing Power (Real)",
    value=f"$ {net_final:,.0f}", 
    delta=f"-${gross_final - net_final:,.0f} lost to inflation",
    delta_color="normal"
)

# --- Plotting ---
st.subheader("Wealth Projection Over Time")
fig, ax = plt.subplots(figsize=(10, 5))
sns.lineplot(
    data=df_finance_months,
    x="years",
    y="gross_value",
    label="Nominal Value (Bank Balance)",
    ax=ax
)
sns.lineplot(
    data=df_finance_months,
    x="years",
    y="net_value",
    label="Real Value (Purchasing Power)",
    ax=ax    
)
# ax.set_title("Projection over time")
ax.set_xticks(range(0, max_years + 1, max(1, max_years // 10)))
ax.set_xlabel("Years")
ax.set_ylabel("Amount ($)")
ax.legend()
# # Format y-axis as currency
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'$ {x:,.0f}'))
st.pyplot(fig)

# --- Data Table ---
if st.checkbox("Show Raw Data Table"):
    st.dataframe(
        df_finance_months.style.format({
            "total_invested": "${:,.2f}",
            "gross_value": "${:,.2f}",
            "net_value": "${:,.2f}",
            "gross_return": "{:,.2f}",
            "net_return": "{:,.2f}",
        })
    )
