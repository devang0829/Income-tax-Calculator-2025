import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Define tax slabs for old regime based on age
OLD_SLABS = {
    "<60": [
        (250000, 0.0),
        (500000, 0.05),
        (1000000, 0.2),
        (float('inf'), 0.3)
    ],
    "60-79": [
        (300000, 0.0),
        (500000, 0.05),
        (1000000, 0.2),
        (float('inf'), 0.3)
    ],
    "80+": [
        (500000, 0.0),
        (1000000, 0.2),
        (float('inf'), 0.3)
    ]
}

NEW_SLABS = [
    (300000, 0.0),
    (600000, 0.05),
    (900000, 0.1),
    (1200000, 0.15),
    (1500000, 0.2),
    (float('inf'), 0.3)
]

def calculate_tax(taxable_income, slabs):
    tax = 0
    prev_limit = 0
    breakdown = []
    for limit, rate in slabs:
        if taxable_income > limit:
            slab_income = limit - prev_limit
            tax_segment = slab_income * rate
            breakdown.append((f"₹{prev_limit + 1} - ₹{limit}", rate * 100, tax_segment))
            tax += tax_segment
            prev_limit = limit
        else:
            slab_income = taxable_income - prev_limit
            tax_segment = slab_income * rate
            breakdown.append((f"₹{prev_limit + 1} - ₹{taxable_income}", rate * 100, tax_segment))
            tax += tax_segment
            break
    return tax, breakdown

def rebate_under_87A(taxable_income, tax, regime):
    if regime == "old" and taxable_income <= 500000:
        return min(tax, 12500)
    elif regime == "new" and taxable_income <= 700000:
        return min(tax, 25000)
    return 0

def calculate_surcharge(taxable_income, base_tax):
    if 5000000 < taxable_income <= 10000000:
        return base_tax * 0.10
    elif 10000000 < taxable_income <= 20000000:
        return base_tax * 0.15
    elif 20000000 < taxable_income <= 50000000:
        return base_tax * 0.25
    elif taxable_income > 50000000:
        return base_tax * 0.37
    return 0

def apply_marginal_relief(taxable_income, base_tax, surcharge):
    thresholds = [
        (5000000, 0.10),
        (10000000, 0.15),
        (20000000, 0.25),
        (50000000, 0.37)
    ]
    for limit, rate in thresholds:
        if taxable_income > limit:
            excess = taxable_income - limit
            max_tax = base_tax + excess
            if base_tax + surcharge > max_tax:
                return max_tax
    return base_tax + surcharge

def display_breakdown(breakdown, surcharge, cess, title):
    labels = [x[0] for x in breakdown] + ["Surcharge", "Cess"]
    values = [x[2] for x in breakdown] + [surcharge, cess]
    df = pd.DataFrame({"Component": labels, "Amount": values})
    st.subheader(f"{title} Tax Breakdown")
    st.bar_chart(df.set_index("Component"))

def main():
    st.set_page_config(page_title="Income Tax Calculator AY 2025-26", layout="centered")
    st.title("Income Tax Calculator - AY 2025-26")

    with st.form("tax_form"):
        col1, col2 = st.columns(2)
        with col1:
            income = st.number_input("Enter Annual Income (in ₹):", value=800000, step=1000)
            age = st.selectbox("Select Age Category", ["<60", "60-79", "80+"])
        with col2:
            std_deduction = 50000
            sec_80C = st.number_input("Section 80C (Max ₹1.5L):", max_value=150000, value=150000)
            sec_80D = st.number_input("Section 80D (Max ₹25K or ₹50K):", max_value=50000, value=25000)
            nps = st.number_input("NPS (Max ₹50K under 80CCD(1B)):", max_value=50000, value=50000)
            hra = st.number_input("HRA Exemption:", value=0)

        submitted = st.form_submit_button("Calculate Tax")

    if submitted:
        total_deductions = std_deduction + sec_80C + sec_80D + nps + hra

        old_taxable = max(0, income - total_deductions)
        new_taxable = income

        old_tax, old_breakdown = calculate_tax(old_taxable, OLD_SLABS[age])
        new_tax, new_breakdown = calculate_tax(new_taxable, NEW_SLABS)

        rebate_old = rebate_under_87A(old_taxable, old_tax, "old")
        rebate_new = rebate_under_87A(new_taxable, new_tax, "new")

        old_after_rebate = old_tax - rebate_old
        new_after_rebate = new_tax - rebate_new

        surcharge_old = calculate_surcharge(old_taxable, old_after_rebate)
        surcharge_new = calculate_surcharge(new_taxable, new_after_rebate)

        old_with_surcharge = apply_marginal_relief(old_taxable, old_after_rebate, surcharge_old)
        new_with_surcharge = apply_marginal_relief(new_taxable, new_after_rebate, surcharge_new)

        final_old_tax = old_with_surcharge * 1.04
        final_new_tax = new_with_surcharge * 1.04

        st.header("Tax Comparison")
        st.metric("Old Regime (with deductions)", f"₹{final_old_tax:,.2f}")
        st.metric("New Regime", f"₹{final_new_tax:,.2f}")

        best = min(("Old Regime", final_old_tax), ("New Regime", final_new_tax), key=lambda x: x[1])
        st.success(f"Recommended Regime: {best[0]} with tax payable ₹{best[1]:,.2f}")

        # Visual breakdown
        display_breakdown(old_breakdown, surcharge_old, final_old_tax - old_with_surcharge, "Old Regime")
        display_breakdown(new_breakdown, surcharge_new, final_new_tax - new_with_surcharge, "New Regime")

if __name__ == "__main__":
    main()
