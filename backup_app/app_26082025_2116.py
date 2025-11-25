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

# Main UI
st.title("Credit Card Matrix Calculator 📊")

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
                st.session_state.selected_cif = selected_cif
    
    # Show selected CIF data
    if st.session_state.selected_cif:
        st.markdown("---")
        st.subheader(f"CIF: {st.session_state.selected_cif}")
                
        # Get data for selected CIF
        cif_data = st.session_state.df[st.session_state.df['CIF No.'] == st.session_state.selected_cif]
        
        # Show as table
        st.dataframe(cif_data, use_container_width=True)

else:
    st.info("Please upload an Excel file")