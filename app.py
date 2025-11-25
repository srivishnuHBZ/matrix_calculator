import streamlit as st
import time
from shared.session_state import initialize_session_state, reset_cif_selection
from shared.data_handler import (
    load_excel_file, 
    detect_financing_types, 
    filter_data_by_product_group,
    display_cif_selector,
    display_cif_data_table
)
from calculators.credit_card import run_credit_card_calculator
from calculators.personal_financing import run_personal_financing_calculator
from calculators.hire_purchase import run_hire_purchase_calculator

# Configure page
st.set_page_config(
    page_title="Proclass and Partners",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
initialize_session_state()

# Main UI
st.title("Matrix Calculator 💰")

# File upload section
uploader_container = st.empty()
if st.session_state.df is None:
    uploaded_file = uploader_container.file_uploader(
        "Upload Excel file (Credit Card, Personal Financing, or Hire Purchase)", 
        type=['xlsx', 'xls']
    )

    if uploaded_file is not None:
        with st.spinner("✨ Please wait while we prepare your data... ✨"):
            df, error = load_excel_file(uploaded_file)
        
        if error:
            st.error(f"Error: {error}")
        elif df is not None:
            st.session_state.df = df
            st.session_state.enabled_tabs = detect_financing_types(df)
            
            # Hide uploader
            uploader_container.empty()
            success_message = st.empty()
            success_message.success(f"✅ File loaded successfully! Detected financing types: {', '.join(st.session_state.enabled_tabs)}")
            time.sleep(2) 
            success_message.empty()

# Main content - Tabs navigation
if st.session_state.df is not None and st.session_state.enabled_tabs:
    
    st.divider()
    
    # Determine which tabs to show and their order
    cc_enabled = 'CC' in st.session_state.enabled_tabs
    pl_enabled = 'PL' in st.session_state.enabled_tabs
    hp_enabled = 'HP' in st.session_state.enabled_tabs
    
    # Create ordered list of enabled tabs
    enabled_order = []
    if cc_enabled:
        enabled_order.append(('CC', 'Credit Card'))
    if pl_enabled:
        enabled_order.append(('PL', 'Personal Financing'))
    if hp_enabled:
        enabled_order.append(('HP', 'Hire Purchase'))
    
    # Create tab labels in order of enabled tabs
    tab_labels = [label for _, label in enabled_order]
    tabs = st.tabs(tab_labels)
    
    # Render tabs dynamically based on enabled order
    for idx, (tab_type, tab_label) in enumerate(enabled_order):
        with tabs[idx]:
            if tab_type == 'CC':
                # --- CREDIT CARD TAB ---
                cc_df = filter_data_by_product_group(st.session_state.df, 'CC')
                
                if cc_df is not None and not cc_df.empty:
                    selected_cif = display_cif_selector(cc_df, 'CC')
                    
                    if selected_cif:
                        cif_data = display_cif_data_table(cc_df, selected_cif)
                        
                        if cif_data is not None:
                            st.divider()
                            run_credit_card_calculator(cif_data)
                else:
                    st.warning("No Credit Card (CC) records found in the uploaded file.")
            
            elif tab_type == 'PL':
                # --- PERSONAL FINANCING TAB ---
                pl_df = filter_data_by_product_group(st.session_state.df, 'PL')
                
                if pl_df is not None and not pl_df.empty:
                    selected_cif = display_cif_selector(pl_df, 'PL')
                    
                    if selected_cif:
                        cif_data = display_cif_data_table(pl_df, selected_cif)
                        
                        if cif_data is not None:
                            st.divider()
                            run_personal_financing_calculator(cif_data)
                else:
                    st.warning("No Personal Financing (PL) records found in the uploaded file.")
            
            elif tab_type == 'HP':
                # --- HIRE PURCHASE TAB ---
                hp_df = filter_data_by_product_group(st.session_state.df, 'HP')
                
                if hp_df is not None and not hp_df.empty:
                    selected_cif = display_cif_selector(hp_df, 'HP')
                    
                    if selected_cif:
                        cif_data = display_cif_data_table(hp_df, selected_cif)
                        
                        if cif_data is not None:
                            st.divider()
                            run_hire_purchase_calculator(cif_data)
                else:
                    st.warning("No Hire Purchase (HP) records found in the uploaded file.")

elif st.session_state.df is None:
    st.info("👆 Please upload an Excel file to get started")
else:
    st.error("❌ No valid Product Group detected in the uploaded file. Please ensure your Excel has a 'Product Group' column with values: CC, PL, or HP.")