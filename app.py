import streamlit as st
import pandas as pd
import time

# Configure page
st.set_page_config(
    page_title="Proclass and Partners",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'filtered_options' not in st.session_state:
    st.session_state.filtered_options = []

def load_excel_file(uploaded_file):
    """Load Excel file"""
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()
        
        # Important columns only
        important_columns = [
            'Account No', 'Current O/S Balance', 'Current O/S Balance (Customer Level)',
            'CIF No.', 'Write Off Date', 'Last Amount Paid', 'Total Write Off Amount'
        ]
        
        existing_columns = [col for col in important_columns if col in df.columns]
        df = df[existing_columns]
        
        # Clean data
        if 'Account No' in df.columns:
            df['Account No'] = df['Account No'].astype(str)
        if 'CIF No.' in df.columns:
            df['CIF No.'] = df['CIF No.'].astype(str)
        
        df = df.dropna(subset=['CIF No.', 'Account No'])
        df = df[df['CIF No.'] != 'nan']
        df = df[df['Account No'] != 'nan']
        
        return df, None
        
    except Exception as e:
        return None, str(e)

def filter_data(df, search_text):
    """Filter data based on search text"""
    if not search_text or df is None:
        return []
    
    search_text = search_text.upper().strip()
    
    # Search in both CIF and Account columns
    mask = (df['CIF No.'].str.upper().str.contains(search_text, na=False)) | \
           (df['Account No'].str.upper().str.contains(search_text, na=False))
    
    filtered_df = df[mask]
    
    # Create unique CIF options
    options = []
    if not filtered_df.empty:
        cif_groups = filtered_df.groupby('CIF No.')['Account No'].apply(list).to_dict()
        
        for cif_no, accounts in cif_groups.items():
            unique_accounts = list(set(accounts))
            if len(unique_accounts) == 1:
                display = f"CIF: {cif_no} | Account: {unique_accounts[0]}"
            else:
                display = f"CIF: {cif_no} | Accounts: {len(unique_accounts)} accounts"
            
            options.append((display, cif_no))
    
    return options

def get_waiver_percentage(settlement_type, repayment_period, ageing_classification, principal_outstanding): 
    # Returns: dict: {'bankFeeWaiverPercent': %, 'interestWaiverPercent': %}

    has_principal = principal_outstanding > 0
    
    if settlement_type == "Lump Sum":
        # Without Principal <=0
        if not has_principal:  
            if ageing_classification == "<5 years":
                if repayment_period == "1 month":
                    return {'bankFeeWaiverPercent': 0, 'interestWaiverPercent': 75}
                elif repayment_period == "3 months":
                    return {'bankFeeWaiverPercent': 0, 'interestWaiverPercent': 50}
                    
            elif ageing_classification == "5-10 years":
                if repayment_period == "1 month":
                    return {'bankFeeWaiverPercent': 0, 'interestWaiverPercent': 80}
                elif repayment_period == "3 months":
                    return {'bankFeeWaiverPercent': 0, 'interestWaiverPercent': 70}
                    
            elif ageing_classification == ">10 years":
                if repayment_period == "1 month":
                    return {'bankFeeWaiverPercent': 80, 'interestWaiverPercent': 100}
                elif repayment_period == "3 months":
                    return {'bankFeeWaiverPercent': 80, 'interestWaiverPercent': 100}
        
        # With Principal > 0
        if ageing_classification == "<5 years":
            if repayment_period == "1 month":
                return {'bankFeeWaiverPercent': 0, 'interestWaiverPercent': 65}
            elif repayment_period == "3 months":
                return {'bankFeeWaiverPercent': 0, 'interestWaiverPercent': 45}
                
        elif ageing_classification == "5-10 years":
            if repayment_period == "1 month":
                return {'bankFeeWaiverPercent': 0, 'interestWaiverPercent': 75}
            elif repayment_period == "3 months":
                return {'bankFeeWaiverPercent': 0, 'interestWaiverPercent': 65}
                
        elif ageing_classification == ">10 years":
            if repayment_period == "1 month":
                return {'bankFeeWaiverPercent': 80, 'interestWaiverPercent': 100}
            elif repayment_period == "3 months":
                return {'bankFeeWaiverPercent': 70, 'interestWaiverPercent': 100}
                
    elif settlement_type == "ATP":
        # Without Principal <=0
        if not has_principal: 
            if ageing_classification == "<5 years":
                if repayment_period == "< 2 years":
                    return {'bankFeeWaiverPercent': 0, 'interestWaiverPercent': 50}
                elif repayment_period == "2-5 years":
                    st.error('Warning: Installments exceeding 2 years are not allowed for cases with zero principal. Please choose the < 2 years option!', icon='⚠️')
                    return {'bankFeeWaiverPercent': 0, 'interestWaiverPercent': 0}
                elif repayment_period == "> 5-7 years":
                    st.error('Warning: Installments exceeding 2 years are not allowed for cases with zero principal. Please choose the < 2 years option!', icon='⚠️')
                    return {'bankFeeWaiverPercent': 0, 'interestWaiverPercent': 0}
                    
            elif ageing_classification == "5-10 years":
                if repayment_period == "< 2 years":
                    return {'bankFeeWaiverPercent': 0, 'interestWaiverPercent': 75}
                elif repayment_period == "2-5 years":
                    st.error('Warning: Installments exceeding 2 years are not allowed for cases with zero principal. Please choose the < 2 years option!', icon='⚠️')
                    return {'bankFeeWaiverPercent': 0, 'interestWaiverPercent': 0}
                elif repayment_period == "> 5-7 years":
                    st.error('Warning: Installments exceeding 2 years are not allowed for cases with zero principal. Please choose the < 2 years option!', icon='⚠️')
                    return {'bankFeeWaiverPercent': 0, 'interestWaiverPercent': 0}
                    
            elif ageing_classification == ">10 years":
                if repayment_period == "< 2 years":
                    return {'bankFeeWaiverPercent': 50, 'interestWaiverPercent': 90}
                elif repayment_period == "2-5 years":
                    return {'bankFeeWaiverPercent': 0, 'interestWaiverPercent': 0}
                elif repayment_period == "> 5-7 years":
                    return {'bankFeeWaiverPercent': 0, 'interestWaiverPercent': 0}
        
        # Principal > 0
        if ageing_classification == "<5 years":
            if repayment_period == "< 2 years":
                return {'bankFeeWaiverPercent': 0, 'interestWaiverPercent': 40}
            elif repayment_period == "2-5 years":
                return {'bankFeeWaiverPercent': 0, 'interestWaiverPercent': 25}
            elif repayment_period == "> 5-7 years":
                return {'bankFeeWaiverPercent': 0, 'interestWaiverPercent': 10}
                
        elif ageing_classification == "5-10 years":
            if repayment_period == "< 2 years":
                return {'bankFeeWaiverPercent': 0, 'interestWaiverPercent': 60}
            elif repayment_period == "2-5 years":
                return {'bankFeeWaiverPercent': 0, 'interestWaiverPercent': 30}
            elif repayment_period == "> 5-7 years":
                return {'bankFeeWaiverPercent': 0, 'interestWaiverPercent': 20}
                
        elif ageing_classification == ">10 years":
            if repayment_period == "< 2 years":
                return {'bankFeeWaiverPercent': 75, 'interestWaiverPercent': 100}
            elif repayment_period == "2-5 years":
                return {'bankFeeWaiverPercent': 50, 'interestWaiverPercent': 100}
            elif repayment_period == "> 5-7 years":
                return {'bankFeeWaiverPercent': 25, 'interestWaiverPercent': 100}
    
    return {'bankFeeWaiverPercent': 0, 'interestWaiverPercent': 0}

# Main UI
st.title("Credit Card Matrix Calculator 💰")

uploader_container = st.empty()
if st.session_state.df is None:
    uploaded_file = uploader_container.file_uploader("Upload Excel file", type=['xlsx', 'xls'])

    if uploaded_file is not None:
        with st.spinner("✨ Please wait while we prepare your data... ✨"):
            df, error = load_excel_file(uploaded_file)
        
        if error:
            st.error(f"Error: {error}")
        elif df is not None:
            st.session_state.df = df
            # Hide uploader
            uploader_container.empty()
            success_message = st.empty()
            success_message.success("File loaded successfully!")
            time.sleep(1) 
            success_message.empty() 


# Search section
if st.session_state.df is not None:
    
    # Initialize selected CIF in session state
    if 'selected_cif' not in st.session_state:
        st.session_state.selected_cif = None
    
    # Get all CIF options for dropdown
    all_cif_options = []
    if st.session_state.df is not None: 
        cif_groups = st.session_state.df.groupby('CIF No.')['Account No'].apply(list).to_dict()
        for cif_no, accounts in cif_groups.items():
            unique_accounts = list(set(accounts))
            if len(unique_accounts) == 1:
                display = f"CIF: {cif_no} | Account: {unique_accounts[0]}"
            else:
                display = f"CIF: {cif_no} | Accounts: {len(unique_accounts)} accounts"
            all_cif_options.append((display, cif_no))
    
    # Search dropdown (searchable selectbox)
    if all_cif_options:
        option_labels = [opt[0] for opt in all_cif_options]
        selected_label = st.selectbox(
            "Type to search CIF or Account Number:",
            options=[""] + option_labels,
            index=0,
            placeholder="Start typing to filter...",
            help="Type to search, then select from dropdown"
        )
        
        if selected_label:
            # Find selected CIF
            selected_cif = None
            for label, cif in all_cif_options:
                if label == selected_label:
                    selected_cif = cif
                    break
            
            if selected_cif:
                # Check if CIF has changed and reset settlement fields if needed
                if 'previous_selected_cif' not in st.session_state:
                    st.session_state.previous_selected_cif = None
                
                if st.session_state.previous_selected_cif != selected_cif:
                    # CIF has changed, explicitly set settlement fields to empty string
                    st.session_state.settlement_type = ""
                    st.session_state.repayment_period = ""
                    # Update the previous CIF tracker
                    st.session_state.previous_selected_cif = selected_cif
                
                st.session_state.selected_cif = selected_cif
    
    # Show selected CIF data
    if st.session_state.selected_cif:

        st.subheader(f"CIF: {st.session_state.selected_cif}")
                    
        # Get data for selected CIF and show in table
        cif_data = st.session_state.df[st.session_state.df['CIF No.'] == st.session_state.selected_cif]
        st.dataframe(cif_data, width='stretch')
        
        # --- CALCULATION FOR PRINCIPAL, O/S BALANCE & AGEING DATE --- #
        principal_outstanding = cif_data['Total Write Off Amount'].sum(skipna=True) if 'Total Write Off Amount' in cif_data else 0
        current_os_balance = cif_data['Current O/S Balance (Customer Level)'].iloc[0] if 'Current O/S Balance (Customer Level)' in cif_data and not cif_data['Current O/S Balance (Customer Level)'].empty else 0
        
        ageing_classification = "N/A"
        if 'Write Off Date' in cif_data and not cif_data['Write Off Date'].dropna().empty:
            latest_writeoff_date = pd.to_datetime(cif_data['Write Off Date']).max()
            years_diff = (pd.Timestamp.today() - latest_writeoff_date).days / 365
            
            if years_diff < 5:
                ageing_classification = "<5 years"
            elif 5 <= years_diff <= 10:
                ageing_classification = "5-10 years"
            else:
                ageing_classification = ">10 years"
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Principal Outstanding", f"{principal_outstanding:,.2f}")
        with col2:
            st.metric("Total Current Outstanding Balance", f"{current_os_balance:,.2f}")
        with col3:
            st.metric("Ageing from Charge Off Date", ageing_classification,
                    help=f"Latest Write Off Date: {latest_writeoff_date.date() if latest_writeoff_date else 'N/A'}")
            
        # --- SETTLEMENT TYPE AND REPAYMENT PERIOD DROPDOWN  --- #
        col1, col2 = st.columns(2)
        with col1:
            # Dropdown 1: Settlement Type
            settlement_type = st.selectbox(
                "Proposed Settlement Type",
                options=["", "Lump Sum", "ATP"],
                key="settlement_type"
            )

        with col2:
            # Dropdown 2: Repayment Period (depends on Settlement Type)
            repayment_options = []
            if settlement_type == "Lump Sum":
                repayment_options = ["1 month", "3 months"]
            elif settlement_type == "ATP":
                repayment_options = ["< 2 years", "2-5 years", "> 5-7 years"]

            repayment_period = st.selectbox(
                "Repayment Period",
                options=[""] + repayment_options,
                disabled=(settlement_type == ""),
                key="repayment_period"
            )

        if repayment_period:
            
            # --- WAIVER PERCENTAGE & INTEREST CALCULATION --- #
            if settlement_type and repayment_period:
                waivers = get_waiver_percentage(settlement_type, repayment_period, ageing_classification, principal_outstanding)
                bank_fee_waiver_percent_display = f"{waivers['bankFeeWaiverPercent']}%"
                interest_waiver_percent_display = f"{waivers['interestWaiverPercent']}%"
            
            # Calculate interest-related metrics
            total_interest = current_os_balance - principal_outstanding
            projected_interest_60 = total_interest * 0.60
            projected_late_fee_30 = total_interest * 0.30
            projected_bank_fees_10 = total_interest * 0.10

            cols = st.columns(8) 
            with cols[0]:
                st.metric("Waiver % in Fees paid by Bank", bank_fee_waiver_percent_display)
            with cols[1]:
                st.metric("Waiver % on Interest", interest_waiver_percent_display)
            with cols[2]:
                st.metric("Total Interest / Late Charge / Other Charges", f"{total_interest:,.2f}")
            with cols[3]:
                st.metric("Projected Interest (60%)", f"{projected_interest_60:,.2f}")
            with cols[4]:
                st.metric("Projected Late Fee (30%)", f"{projected_late_fee_30:,.2f}")
            with cols[5]:
                st.metric("Projected Fees paid by Bank (10%)", f"{projected_bank_fees_10:,.2f}")
            with cols[6]:
                st.metric("Waiver % in Late Charges", "100%")
            with cols[7]:
                st.metric("Waiver in Principal", "0%")


            # --- REPAYMENT PERIOD IN MONTHS --- #
            default_repayment_months = 1 # Default to 1 month
            if repayment_period == "1 month":
                default_repayment_months = 1
            elif repayment_period == "3 months":
                default_repayment_months = 3
            elif repayment_period == "< 2 years":
                default_repayment_months = 23  # Assuming 2 years max
            elif repayment_period == "2-5 years":
                default_repayment_months = 60  # Assuming 5 years max
            elif repayment_period == "> 5-7 years":
                default_repayment_months = 84  # Assuming 7 years max

            error_message_placeholder = st.empty()
            col1, col2, col3 = st.columns(3)
            with col1:
                # Integer input for months
                repayment_period_months_user_input = st.number_input(
                    "Enter Repayment Period in Months",
                    min_value=1,
                    max_value=None,
                    value=default_repayment_months,
                    step=1,
                    key="repayment_period_months_input"
                )

                # Initialize the actual value to be used for calculations
                repayment_period_months = repayment_period_months_user_input

                # Define allowed ranges for each repayment period type
                allowed_ranges = {
                    "1 month": (1, 1),
                    "3 months": (2, 3),
                    "< 2 years": (4, 23),
                    "2-5 years": (24, 60),
                    "> 5-7 years": (61, 84)
                }

                # Validate user input
                min_months, max_months = allowed_ranges.get(repayment_period, (1, 1))
                if not (min_months <= repayment_period_months_user_input <= max_months):
                    error_message_placeholder.error(f"Repayment month(s) must be between {min_months} and {max_months} months for the selected Repayment Period.")


            # --- OPERATING COST CALCULATION --- #
            if repayment_period_months == 1:
                # For a 1-month lump sum repayment, operating costs are set to zero
                operating_cost_principal_pos_default = 0.0
                operating_cost_principal_neg_default = 0.0
            else:
                operating_cost_principal_pos_default = (
                    (0.05 / 12 * (principal_outstanding + projected_bank_fees_10)) * repayment_period_months
                    if principal_outstanding > 0 else 0.0
                )
                operating_cost_principal_neg_default = (
                    (0.05 / 12 * (principal_outstanding + projected_bank_fees_10)) * repayment_period_months
                    if principal_outstanding < 0 else 0.0
                )

            # Update session state when repayment period changes
            if "last_repayment_months" not in st.session_state:
                st.session_state.last_repayment_months = repayment_period_months
                st.session_state.operating_cost_pos_value = f"{float(operating_cost_principal_pos_default):.2f}"
                st.session_state.operating_cost_neg_value = f"{float(operating_cost_principal_neg_default):.2f}"
            elif st.session_state.last_repayment_months != repayment_period_months:
                # Repayment period has changed, update the default values
                st.session_state.last_repayment_months = repayment_period_months
                st.session_state.operating_cost_pos_value = f"{float(operating_cost_principal_pos_default):.2f}"
                st.session_state.operating_cost_neg_value = f"{float(operating_cost_principal_neg_default):.2f}"

            with col2:
                operating_cost_principal_pos_str = st.text_input(
                    "Operating cost (Principal > 0) @ 5.0p.a. x Fees paid by Bank",
                    value=st.session_state.operating_cost_pos_value,
                    key="operating_cost_principal_pos_input"
                )

                # Validate and convert to float
                try:
                    operating_cost_principal_pos = float(operating_cost_principal_pos_str)
                    if operating_cost_principal_pos < 0:
                        st.error("Operating cost (Principal > 0) cannot be negative.")
                        operating_cost_principal_pos = 0.0
                except ValueError:
                    st.error("Invalid input. Please enter a number.")
                    operating_cost_principal_pos = 0.0

            with col3:
                operating_cost_principal_neg_str = st.text_input(
                    "Operating cost (Principal < 0) @ 5.0p.a. x Fees paid by Bank",
                    value=st.session_state.operating_cost_neg_value,
                    key="operating_cost_principal_neg_input"
                )

                # Validate and convert to float
                try:
                    operating_cost_principal_neg = float(operating_cost_principal_neg_str)
                    if operating_cost_principal_neg < 0:
                        st.error("Operating cost (Principal < 0) cannot be negative.")
                        operating_cost_principal_neg = 0.0
                except ValueError:
                    st.error("Invalid input. Please enter a number.")
                    operating_cost_principal_neg = 0.0
            
            
            # --- BANK SETTLEMENT MATRIX CALCULATION --- #
            bankFeeWaiverPercent = waivers['bankFeeWaiverPercent'] / 100
            interestWaiverPercent = waivers['interestWaiverPercent'] / 100

            # Formula from Excel:
            # Bank Settlement Matrix (Amount) = (AS*(1-AV)) + (AT*(1-AW)) + (AU*(1-AX)) + AY*((1-AZ)) + BA + BB
            bank_settlement_matrix_amount = (
                (projected_interest_60 * (1 - interestWaiverPercent)) +
                (projected_late_fee_30 * (1 - 1)) +  # (1-100%) is 0, so this term becomes 0
                (projected_bank_fees_10 * (1 - bankFeeWaiverPercent)) +
                (principal_outstanding * (1 - 0)) +  # (1-0%) is 1, so this term becomes principal_outstanding
                operating_cost_principal_pos +
                operating_cost_principal_neg
            )
            
            col_proposed_amount, col_bank_matrix, col_as_per_bank = st.columns(3)


            # --- PROPOSED SETTLEMENT AMOUNT --- #
            with col_proposed_amount:
                # Use st.text_input for better input experience, then validate
                if "proposed_settlement_amount_text" not in st.session_state:
                    st.session_state.proposed_settlement_amount_text = "0.00"

                proposed_settlement_amount_str = st.text_input(
                    "Proposed Settlement Amount",
                    key="proposed_settlement_amount_text"
                )
                
                # Validate and convert to float
                try:
                    proposed_settlement_amount = float(proposed_settlement_amount_str)
                    if proposed_settlement_amount < 0:
                        st.error("Proposed Settlement Amount cannot be negative.")
                        proposed_settlement_amount = 0.0 # Reset to 0 if invalid
                except ValueError:
                    st.error("Invalid input for Proposed Settlement Amount. Please enter a number.")
                    proposed_settlement_amount = 0.0 # Reset to 0 if invalid

            
            with col_bank_matrix:
                calculation_steps = (
                    "--- Bank Settlement Matrix Breakdown ---\n\n"

                    f"1. Projected Interest (60%):\n"
                    f"   RM{projected_interest_60:,.2f} * (1 - {interestWaiverPercent*100:.0f}% Interest Waiver) "
                    f"= RM{projected_interest_60 * (1 - interestWaiverPercent):,.2f}\n\n"

                    f"2. Projected Late Fee (30%):\n"
                    f"   RM{projected_late_fee_30:,.2f} * (1 - 100% Waiver) = RM0.00\n\n"

                    f"3. Projected Bank Fees (10%):\n"
                    f"   RM{projected_bank_fees_10:,.2f} * (1 - {bankFeeWaiverPercent*100:.0f}% Bank Fee Waiver) "
                    f"= RM{projected_bank_fees_10 * (1 - bankFeeWaiverPercent):,.2f}\n\n"

                    f"4. Principal Outstanding:\n"
                    f"   RM{principal_outstanding:,.2f} * (1 - 0% Waiver) = RM{principal_outstanding:,.2f}\n\n"

                    f"5. Operating Costs:\n"
                    f"   - Principal > 0: RM{operating_cost_principal_pos:,.2f}\n"
                    f"   - Principal < 0: RM{operating_cost_principal_neg:,.2f}\n\n"
                )

                st.metric(
                    "Bank Settlement Matrix (Amount)",
                    f"RM{bank_settlement_matrix_amount:,.2f}",
                    help=calculation_steps
                )

            with col_as_per_bank:
                # --- BANK MATRIX & METRICS STYLING --- #
                as_per_bank_matrix = "N/A"
                if proposed_settlement_amount > 0:
                    # Round amounts for comparison.
                    rounded_proposed_amount = round(proposed_settlement_amount, 2)
                    rounded_bank_matrix_amount = round(bank_settlement_matrix_amount, 2)
                    as_per_bank_matrix = "✅ YES" if rounded_proposed_amount >= rounded_bank_matrix_amount else "❌ NO"

                metric_placeholder = st.empty()  # placeholder so we can style it
                metric_placeholder.metric("As Per Bank Matrix (Yes / No)", as_per_bank_matrix)

                if as_per_bank_matrix == "❌ NO":
                    color = "rgba(231, 76, 60, 0.12)"  # subtle red
                elif as_per_bank_matrix == "✅ YES":
                    color = "rgba(46, 204, 113, 0.12)"  # subtle green
                else:
                    color = None

                if color:
                    # Replace literal } inside f-string with }}
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
     
else:
    st.info("Please upload an Excel file")