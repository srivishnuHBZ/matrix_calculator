import pandas as pd
import streamlit as st

def load_excel_file(uploaded_file):
    """Load Excel file and perform basic cleaning"""
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()
        
        # Ensure required columns exist
        required_columns = ['Account No', 'CIF No.', 'Product Group']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return None, f"Missing required columns: {', '.join(missing_columns)}"
        
        # Clean data
        df['Account No'] = df['Account No'].astype(str)
        df['CIF No.'] = df['CIF No.'].astype(str)
        df['Product Group'] = df['Product Group'].astype(str).str.strip().str.upper()
        
        # Remove invalid rows
        df = df.dropna(subset=['CIF No.', 'Account No', 'Product Group'])
        df = df[df['CIF No.'] != 'nan']
        df = df[df['Account No'] != 'nan']
        df = df[df['Product Group'] != 'nan']
        
        return df, None
        
    except Exception as e:
        return None, str(e)

def detect_financing_types(df):
    """Detect which financing types are present in the dataframe"""
    if df is None or 'Product Group' not in df.columns:
        return set()
    
    product_groups = df['Product Group'].unique()
    enabled_tabs = set()
    
    for pg in product_groups:
        if pg == 'CC':
            enabled_tabs.add('CC')
        elif pg == 'PL':
            enabled_tabs.add('PL')
        elif pg == 'HP':
            enabled_tabs.add('HP')
    
    return enabled_tabs

def filter_data_by_product_group(df, product_group):
    """Filter dataframe by Product Group"""
    if df is None:
        return None
    return df[df['Product Group'] == product_group].copy()

def get_cif_options(df):
    """Generate CIF dropdown options from filtered dataframe"""
    if df is None or df.empty:
        return []
    
    options = []
    cif_groups = df.groupby('CIF No.')['Account No'].apply(list).to_dict()
    
    for cif_no, accounts in cif_groups.items():
        unique_accounts = list(set(accounts))
        if len(unique_accounts) == 1:
            display = f"CIF: {cif_no} | Account: {unique_accounts[0]}"
        else:
            display = f"CIF: {cif_no} | Accounts: {len(unique_accounts)} accounts"
        
        options.append((display, cif_no))
    
    return options

def display_cif_selector(df, financing_type):
    """Display searchable CIF selector and return selected CIF"""
    
    # Get session state variable names based on financing type
    selected_cif_key = f'selected_cif_{financing_type.lower()}'
    previous_cif_key = f'previous_selected_cif_{financing_type.lower()}'
    
    # Get CIF options
    cif_options = get_cif_options(df)
    
    if not cif_options:
        st.warning(f"No valid CIF records found for {financing_type}")
        return None
    
    # Create searchable selectbox
    option_labels = [opt[0] for opt in cif_options]
    selected_label = st.selectbox(
        "Type to search CIF or Account Number:",
        options=[""] + option_labels,
        index=0,
        placeholder="Start typing to filter...",
        help="Type to search, then select from dropdown",
        key=f"cif_selector_{financing_type}"
    )
    
    if selected_label:
        # Find selected CIF
        selected_cif = None
        for label, cif in cif_options:
            if label == selected_label:
                selected_cif = cif
                break
        
        if selected_cif:
            # Check if CIF has changed and reset if needed
            if st.session_state.get(previous_cif_key) != selected_cif:
                # Reset settlement-related session state for this financing type
                reset_settlement_state(financing_type)
                st.session_state[previous_cif_key] = selected_cif
            
            st.session_state[selected_cif_key] = selected_cif
            return selected_cif
    
    return None

def reset_settlement_state(financing_type):
    """Reset settlement-related session state when CIF changes"""
    prefix = financing_type.lower()
    
    # Reset settlement type and repayment period
    if f'settlement_type_{prefix}' in st.session_state:
        st.session_state[f'settlement_type_{prefix}'] = ""
    if f'repayment_period_{prefix}' in st.session_state:
        st.session_state[f'repayment_period_{prefix}'] = ""

def display_cif_data_table(df, cif_no):
    """Display data table for selected CIF"""
    if df is None or cif_no is None:
        return None
    
    cif_data = df[df['CIF No.'] == cif_no]
    
    if not cif_data.empty:
        st.subheader(f"CIF: {cif_no}")
        st.dataframe(cif_data, width='stretch')
        return cif_data
    
    return None