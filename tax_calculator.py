import streamlit as st

# Tax slab definitions for FY 2024-25
OLD_REGIME_SLABS = [
    (250000, 0.0),
    (500000, 0.05),
    (1000000, 0.2),
    (float('inf'), 0.3)
]

NEW_REGIME_SLABS = [
    (300000, 0.0),
    (600000, 0.05),
    (900000, 0.10),
    (1200000, 0.15),
    (1500000, 0.20),
    (float('inf'), 0.30)
]

def calculate_tax(taxable_income, slabs):
    tax = 0
    prev_limit = 0
    for limit, rate in slabs:
        if taxable_income > limit:
            tax += (limit - prev_limit) * rate
            prev_limit = limit
        else:
            tax += (taxable_income - prev_limit) * rate
            break
    return tax * 1.04  # 4% Health & Education Cess

def main():
    st.title("Income Tax Calculator - FY 2024-25")

    income = st.number_input("Enter Annual Income (in ₹):", value=800000)

    st.subheader("Optional Deductions (for Old Regime)")
    std_deduction = 50000
    sec_80C = st.number_input("Section 80C (Max ₹1.5L):", max_value=150000, value=150000)
    sec_80D = st.number_input("Section 80D (Medical Insurance, Max ₹25K):", max_value=25000, value=25000)
    nps = st.number_input("NPS (Max ₹50K under 80CCD(1B)):", max_value=50000, value=50000)
    hra = st.number_input("HRA Exemption (if applicable):", value=0)

    total_deductions = std_deduction + sec_80C + sec_80D + nps + hra

    # Calculate taxes
    old_tax_with_deductions = calculate_tax(max(0, income - total_deductions), OLD_REGIME_SLABS)
    old_tax_without_deductions = calculate_tax(income, OLD_REGIME_SLABS)
    new_tax = calculate_tax(income, NEW_REGIME_SLABS)

    # Display results
    st.subheader("Tax Comparison")
    st.write(f"Old Regime (with deductions): ₹{old_tax_with_deductions:,.2f}")
    st.write(f"Old Regime (without deductions): ₹{old_tax_without_deductions:,.2f}")
    st.write(f"New Regime: ₹{new_tax:,.2f}")

    best_option = min(
        ("Old Regime (with deductions)", old_tax_with_deductions),
        ("Old Regime (without deductions)", old_tax_without_deductions),
        ("New Regime", new_tax),
        key=lambda x: x[1]
    )
    st.success(f"Recommended Regime: {best_option[0]} with tax ₹{best_option[1]:,.2f}")

if __name__ == "__main__":
    main()
