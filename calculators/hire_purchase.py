import streamlit as st
import pandas as pd

def get_waiver_percentage_hp(settlement_type, repayment_period, ageing_classification, principal_outstanding):
    """Returns: dict: {'principalWaiverPercent': %, 'bankFeeWaiverPercent': %, 'interestWaiverPercent': %, 'lateChargesWaiverPercent': %}"""
    
    has_principal = principal_outstanding > 0
    
    if settlement_type == "Lump Sum":
        # With Principal > 0
        if has_principal:
            if ageing_classification == "3 years or less":
                return {
                    'principalWaiverPercent': 0,
                    'bankFeeWaiverPercent': 0,
                    'interestWaiverPercent': 100,
                    'lateChargesWaiverPercent': 100
                }
            elif ageing_classification == "> 3 years":
                return {
                    'principalWaiverPercent': 0,
                    'bankFeeWaiverPercent': 25,
                    'interestWaiverPercent': 100,
                    'lateChargesWaiverPercent': 100
                }
        # Without Principal <= 0
        else:
            if ageing_classification == "3 years or less":
                return {
                    'principalWaiverPercent': 0,
                    'bankFeeWaiverPercent': 0,
                    'interestWaiverPercent': 100,
                    'lateChargesWaiverPercent': 100
                }
            elif ageing_classification == "> 3 years":
                return {
                    'principalWaiverPercent': 0,
                    'bankFeeWaiverPercent': 25,
                    'interestWaiverPercent': 100,
                    'lateChargesWaiverPercent': 100
                }
    
    elif settlement_type == "ATP":
        # With Principal > 0
        if has_principal:
            if ageing_classification == "3 years or less":
                if repayment_period == "<2 years":
                    return {
                        'principalWaiverPercent': 0,
                        'bankFeeWaiverPercent': 0,
                        'interestWaiverPercent': 100,
                        'lateChargesWaiverPercent': 100
                    }
                elif repayment_period == "2-5 years":
                    # st.error('Warning: Installments exceeding 2 years are not allowed for cases with principal > 0 and ageing ≤ 3 years. Please choose the <2 years option!', icon='⚠️')
                    return {
                        'principalWaiverPercent': 0,
                        'bankFeeWaiverPercent': 0,
                        'interestWaiverPercent': 100,
                        'lateChargesWaiverPercent': 100
                    }
            elif ageing_classification == "> 3 years":
                if repayment_period == "<2 years":
                    return {
                        'principalWaiverPercent': 0,
                        'bankFeeWaiverPercent': 25,
                        'interestWaiverPercent': 100,
                        'lateChargesWaiverPercent': 100
                    }
                elif repayment_period == "2-5 years":
                    return {
                        'principalWaiverPercent': 0,
                        'bankFeeWaiverPercent': 25,
                        'interestWaiverPercent': 100,
                        'lateChargesWaiverPercent': 100
                    }
        # Without Principal <= 0
        else:
            if ageing_classification == "3 years or less":
                if repayment_period == "<2 years":
                    return {
                        'principalWaiverPercent': 0,
                        'bankFeeWaiverPercent': 0,
                        'interestWaiverPercent': 100,
                        'lateChargesWaiverPercent': 100
                    }
                elif repayment_period == "2-5 years":
                    st.error('Warning: Installments exceeding 2 years are not allowed for cases with principal ≤ 0 and ageing ≤ 3 years. Please choose the <2 years option!', icon='⚠️')
                    return {
                        'principalWaiverPercent': 0,
                        'bankFeeWaiverPercent': 0,
                        'interestWaiverPercent': 0,
                        'lateChargesWaiverPercent': 0
                    }
            elif ageing_classification == "> 3 years":
                if repayment_period == "<2 years":
                    return {
                        'principalWaiverPercent': 0,
                        'bankFeeWaiverPercent': 25,
                        'interestWaiverPercent': 100,
                        'lateChargesWaiverPercent': 100
                    }
                elif repayment_period == "2-5 years":
                    st.error('Warning: Installments exceeding 2 years are not allowed for cases with principal ≤ 0 and ageing > 3 years. Please choose the <2 years option!', icon='⚠️')
                    return {
                        'principalWaiverPercent': 0,
                        'bankFeeWaiverPercent': 0,
                        'interestWaiverPercent': 0,
                        'lateChargesWaiverPercent': 0
                    }
    
    return {
        'principalWaiverPercent': 0,
        'bankFeeWaiverPercent': 0,
        'interestWaiverPercent': 0,
        'lateChargesWaiverPercent': 0
    }

def find_column(df, keywords):
    """Find column in dataframe that contains any of the keywords (case-insensitive)"""
    if isinstance(keywords, str):
        keywords = [keywords]
    
    for col in df.columns:
        col_lower = col.lower()
        for keyword in keywords:
            if keyword.lower() in col_lower:
                return col
    return None

def validate_columns(cif_data):
    """Validate that required columns exist for Hire Purchase calculations"""
    required_mappings = {
        'Write Off Date': ['write off date', 'writeoff date', 'charged off date'],
        'Write Off IIS': ['iis', 'write off iis'],
        'Current Balance': ['current balance'],
        'O/S Balance': ['o/s balance', 'os balance', 'outstanding balance'],
        'Misc Cost': ['misc cost', 'misc charge'],
        'Other Charge': ['other charge', 'other charges'],
        'Late': ['late', 'late/compensation charges', 'late compensation'],
        'Memo Late': ['memo late', 'memo late/compensation'],
        'Islamic Flag': ['islamic flag', 'islamic']
    }
    
    missing = []
    found_columns = {}
    
    for display_name, keywords in required_mappings.items():
        col = find_column(cif_data, keywords)
        if col:
            found_columns[display_name] = col
        else:
            missing.append(display_name)
    
    if missing:
        st.error(f"Missing required columns for Hire Purchase: {', '.join(missing)}")
        st.info("Expected keywords in column names: " + ", ".join([f"{k}: {v}" for k, v in required_mappings.items() if k in missing]))
        return False, {}
    
    return True, found_columns

def run_hire_purchase_calculator(cif_data):
    """Main Hire Purchase calculator logic"""
    
    is_valid, col_map = validate_columns(cif_data)
    if not is_valid:
        return
    
    # --- CALCULATION FOR PRINCIPAL, INTEREST, CHARGES & AGEING --- #
    
    # Get Islamic Flag
    islamic_flag_col = col_map['Islamic Flag']
    islamic_flag = cif_data[islamic_flag_col].iloc[0] if not cif_data[islamic_flag_col].empty else "No"
    islamic_flag = str(islamic_flag).strip().lower() in ['yes', 'y', 'true', '1']
    
    # Calculate Principal Outstanding
    # HP Formula: Principal = Current balance - IIS 
    current_balance_col = col_map['Current Balance']
    current_balance = cif_data[current_balance_col].sum(skipna=True)
    os_balance_col = col_map['O/S Balance']
    os_balance = cif_data[os_balance_col].sum(skipna=True)
    iis_col = col_map['Write Off IIS']
    iis = cif_data[iis_col].sum(skipna=True)
       
    # Interest / Profit
    interest_profit = iis
    
    # Others Charges = Misc Cost - Other Charge
    misc_cost_col = col_map['Misc Cost']
    misc_cost = cif_data[misc_cost_col].sum(skipna=True)
    other_charge_col = col_map['Other Charge']
    other_charge = cif_data[other_charge_col].sum(skipna=True)
    
    others_charges = misc_cost - other_charge
    
    # Late Payment Interest / Compensation Charges
    memo_late_col = col_map['Memo Late']
    memo_late = cif_data[memo_late_col].sum(skipna=True)
    late_col = col_map['Late'] 
    late = cif_data[late_col].sum(skipna=True)
    
    late_payment_charges = late + memo_late
    
    # Principal Outstanding    
    principal_outstanding = current_balance - iis
        
    # Total Current Outstanding Balance
    total_current_os = os_balance
    
    # Ageing Classification
    ageing_classification = "N/A"
    latest_writeoff_date = None
    writeoff_col = col_map['Write Off Date']
    
    if writeoff_col in cif_data and not cif_data[writeoff_col].dropna().empty:
        latest_writeoff_date = pd.to_datetime(cif_data[writeoff_col]).max()
        years_diff = (pd.Timestamp.today() - latest_writeoff_date).days / 365
        
        if years_diff <= 3:
            ageing_classification = "3 years or less"
        else:
            ageing_classification = "> 3 years"
    
    # Display metrics
    st.markdown("### Key Metrics")
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    with col1:
        st.metric("Principal Outstanding", f"RM{principal_outstanding:,.2f}")
    with col2:
        st.metric("Interest / Profit", f"RM{interest_profit:,.2f}")
    with col3:
        st.metric("Others Charges", f"RM{others_charges:,.2f}")
    with col4:
        st.metric("Late Payment Charges", f"RM{late_payment_charges:,.2f}")
    with col5:
        st.metric("Total Current O/S Balance", f"RM{total_current_os:,.2f}")
    with col6:
        flag_display = "Yes" if islamic_flag else "No"
        st.metric("Islamic Flag", flag_display)
    with col7:
        st.metric("Ageing from Charge Off Date", ageing_classification,
                help=f"Latest Write Off Date: {latest_writeoff_date.date() if latest_writeoff_date else 'N/A'}")
    
    st.markdown("---")
    
    # --- SETTLEMENT TYPE AND REPAYMENT PERIOD DROPDOWN --- #
    col1, col2 = st.columns(2)
    with col1:
        settlement_type = st.selectbox(
            "Proposed Settlement Type",
            options=["", "Lump Sum", "ATP"],
            key="settlement_type_hp"
        )

    with col2:
        repayment_options = []
        if settlement_type == "Lump Sum":
            repayment_options = ["1 month", "2 months", "3 months"]
        elif settlement_type == "ATP":
            repayment_options = ["<2 years", "2-5 years"]

        repayment_period = st.selectbox(
            "Repayment Period",
            options=[""] + repayment_options,
            disabled=(settlement_type == ""),
            key="repayment_period_hp"
        )

    if not repayment_period:
        return
    
    # --- WAIVER PERCENTAGE CALCULATION --- #
    waivers = get_waiver_percentage_hp(settlement_type, repayment_period, ageing_classification, principal_outstanding)
    
    # Display waivers
    st.markdown("### Waiver Percentages")
    cols = st.columns(4)
    with cols[0]:
        st.metric("Waiver % in Principal", f"{waivers['principalWaiverPercent']}%")
    with cols[1]:
        st.metric("Waiver % in Fees paid by Bank", f"{waivers['bankFeeWaiverPercent']}%")
    with cols[2]:
        st.metric("Waiver % on Interest", f"{waivers['interestWaiverPercent']}%")
    with cols[3]:
        st.metric("Waiver % in Late Charges", f"{waivers['lateChargesWaiverPercent']}%")
    
    st.markdown("")
    
    # --- REPAYMENT PERIOD IN MONTHS --- #
    default_repayment_months = 1
    if repayment_period == "1 month":
        default_repayment_months = 1
    elif repayment_period == "2 months":
        default_repayment_months = 2
    elif repayment_period == "3 months":
        default_repayment_months = 3
    elif repayment_period == "<2 years":
        default_repayment_months = 4
    elif repayment_period == "2-5 years":
        default_repayment_months = 24

    error_message_placeholder = st.empty()
    
    # --- PROJECTED LATE PAYMENT CHARGES (with Islamic Flag logic) --- #
    repayment_period_months = st.number_input(
        "Enter Repayment Period in Months",
        min_value=1,
        max_value=None,
        value=default_repayment_months,
        step=1,
        key="repayment_period_months_input_hp"
    )

    # Validate user input
    allowed_ranges = {
        "1 month": (1, 1),
        "2 months": (2, 2),
        "3 months": (3, 3),
        "<2 years": (4, 23),
        "2-5 years": (24, 60)
    }

    min_months, max_months = allowed_ranges.get(repayment_period, (1, 1))
    if not (min_months <= repayment_period_months <= max_months):
        error_message_placeholder.error(f"Repayment month(s) must be between {min_months} and {max_months} months for the selected Repayment Period.")
    
    # Calculate Projected Late Payment Interest / Compensation Charges
    if islamic_flag:
        # For Islamic: Late Payment Interest + (Late Payment Interest * ((Repayment Period + 2)/12)*(0.01))
        projected_late_payment = late_payment_charges + (late_payment_charges * ((repayment_period_months + 2) / 12) * 0.01)
    else:
        # For Non-Islamic: Late Payment Interest + (Late Payment Interest * ((Repayment Period + 2)/12)*(0.08))
        projected_late_payment = late_payment_charges + (late_payment_charges * ((repayment_period_months + 2) / 12) * 0.08)
    
    # Projected Outstanding Balance
    projected_outstanding_balance = principal_outstanding + interest_profit + others_charges + projected_late_payment
    
    st.markdown("### Projected Values")
    col1, col2, col3 = st.columns(3)
    with col1:
        rate_display = "1%" if islamic_flag else "8%"
        st.metric(
            f"Projected Late Payment Charges (@ {rate_display})",
            f"RM{projected_late_payment:,.2f}",
            help=f"Formula: Late Payment + (Late Payment × ((Months + 2)/12) × {rate_display})"
        )
    with col2:
        st.metric("Projected Outstanding Balance", f"RM{projected_outstanding_balance:,.2f}")
    
    with col3:
        # --- OPERATING COST CALCULATION (ATP only) --- #
        operating_cost = 0.0
        
        if settlement_type == "ATP":
            # Operating Cost = (5% / 12) × Repayment Period × (Principal outstanding + Others Charges)
            operating_cost = (0.05 / 12) * repayment_period_months * (principal_outstanding + others_charges)
            
            st.metric(
                "Operating Cost @ 5% p.a. on Principal + Others Charges",
                f"RM{operating_cost:,.2f}",
                help=f"Formula: (5% / 12) × {repayment_period_months} months × (Principal + Others Charges)"
            )
    
    st.markdown("---")
    
    # --- BANK SETTLEMENT MATRIX CALCULATION --- #
    principalWaiverPercent = waivers['principalWaiverPercent'] / 100
    bankFeeWaiverPercent = waivers['bankFeeWaiverPercent'] / 100
    interestWaiverPercent = waivers['interestWaiverPercent'] / 100
    lateChargesWaiverPercent = waivers['lateChargesWaiverPercent'] / 100
    
    # Bank Settlement Matrix (HP Formula) = 
    # Principal outstanding +
    # (Interest / Profit × (1 - Waiver % on interest)) +
    # (Others Charges × (1 - Waiver % in fees paid by the bank)) +
    # (Late Payment Interest/Compensation Charges × (1 - Waiver % in late charges)) +
    # Operating Cost 5%
    
    bank_settlement_matrix_amount = (
        principal_outstanding +
        (interest_profit * (1 - interestWaiverPercent)) +
        (others_charges * (1 - bankFeeWaiverPercent)) +
        (projected_late_payment * (1 - lateChargesWaiverPercent)) +
        operating_cost
    )
    
    col_proposed_amount, col_bank_matrix, col_as_per_bank = st.columns(3)

    # --- PROPOSED SETTLEMENT AMOUNT --- #
    with col_proposed_amount:
        if "proposed_settlement_amount_text_hp" not in st.session_state:
            st.session_state.proposed_settlement_amount_text_hp = "0.00"

        proposed_settlement_amount_str = st.text_input(
            "Proposed Settlement Amount",
            key="proposed_settlement_amount_text_hp"
        )
        
        try:
            proposed_settlement_amount = float(proposed_settlement_amount_str)
            if proposed_settlement_amount < 0:
                st.error("Proposed Settlement Amount cannot be negative.")
                proposed_settlement_amount = 0.0
        except ValueError:
            st.error("Invalid input for Proposed Settlement Amount. Please enter a number.")
            proposed_settlement_amount = 0.0

    with col_bank_matrix:
        calculation_steps = (
            "--- Bank Settlement Matrix Breakdown ---\n\n"
            f"1. Principal Outstanding:\n"
            f"   RM{principal_outstanding:,.2f} × (1 - {principalWaiverPercent*100:.0f}% Waiver) "
            f"= RM{principal_outstanding * (1 - principalWaiverPercent):,.2f}\n\n"
            
            f"2. Interest / Profit:\n"
            f"   RM{interest_profit:,.2f} × (1 - {interestWaiverPercent*100:.0f}% Waiver) "
            f"= RM{interest_profit * (1 - interestWaiverPercent):,.2f}\n\n"
            
            f"3. Others Charges:\n"
            f"   RM{others_charges:,.2f} × (1 - {bankFeeWaiverPercent*100:.0f}% Waiver) "
            f"= RM{others_charges * (1 - bankFeeWaiverPercent):,.2f}\n\n"
            
            f"4. Projected Late Payment Charges:\n"
            f"   RM{projected_late_payment:,.2f} × (1 - {lateChargesWaiverPercent*100:.0f}% Waiver) "
            f"= RM{projected_late_payment * (1 - lateChargesWaiverPercent):,.2f}\n\n"
            
            f"5. Operating Cost:\n"
            f"   RM{operating_cost:,.2f}\n\n"
        )

        st.metric(
            "Bank Settlement Matrix (Amount)",
            f"RM{bank_settlement_matrix_amount:,.2f}",
            help=calculation_steps
        )

    with col_as_per_bank:
        as_per_bank_matrix = "N/A"
        if proposed_settlement_amount > 0:
            rounded_proposed_amount = round(proposed_settlement_amount, 2)
            rounded_bank_matrix_amount = round(bank_settlement_matrix_amount, 2)
            as_per_bank_matrix = "✅ YES" if rounded_proposed_amount >= rounded_bank_matrix_amount else "❌ NO"

        metric_placeholder = st.empty()
        metric_placeholder.metric("As Per Bank Matrix (Yes / No)", as_per_bank_matrix)

        if as_per_bank_matrix == "❌ NO":
            color = "rgba(231, 76, 60, 0.12)"  # subtle red
        elif as_per_bank_matrix == "✅ YES":
            color = "rgba(46, 204, 113, 0.12)"  # subtle green
        else:
            color = None

        if color:
            color_fade = color.replace('0.12', '0.18')
            st.markdown(
                f"""
                <style>
                @keyframes highlight-fade-subtle {{
                    0%   {{ background-color: {color}; }}
                    50%  {{ background-color: {color_fade}; }}
                    100% {{ background-color: {color}; }}
                }}

                div[data-testid="stMetric"] {{
                    border-radius: 12px;
                    animation: highlight-fade-subtle 2.5s ease-in-out infinite;
                    transition: all 0.3s ease-in-out;
                }}
                </style>
                """,
                unsafe_allow_html=True
            )