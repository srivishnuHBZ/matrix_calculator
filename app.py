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
    page_title="Matrix Calculator",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
initialize_session_state()

st.markdown(
    """
    <div style='display: flex; justify-content: center; align-items: center;'>
        <h1 style='text-align: center; margin-bottom: 0;'>Proclass and Partners Matrix Calculator 💰</h1>
    </div>
    """,
    unsafe_allow_html=True
)

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
            
            # Set default active tab to the first enabled tab
            if st.session_state.enabled_tabs:
                # Priority: PL > HP > CC
                if 'PL' in st.session_state.enabled_tabs:
                    st.session_state.active_tab_index = 1
                elif 'HP' in st.session_state.enabled_tabs:
                    st.session_state.active_tab_index = 2
                else:
                    st.session_state.active_tab_index = 0
            
            # Hide uploader
            uploader_container.empty()
            st.rerun()

# Main content - Tabs navigation
if st.session_state.df is not None and st.session_state.enabled_tabs:
       
    # Determine which tabs to show
    cc_enabled = 'CC' in st.session_state.enabled_tabs
    pl_enabled = 'PL' in st.session_state.enabled_tabs
    hp_enabled = 'HP' in st.session_state.enabled_tabs
    
    # Create tabs with all three labels
    tab_labels = ["Credit Card", "Personal Financing", "Hire Purchase"]
    
    # Use session state to track active tab
    if 'active_tab_index' not in st.session_state:
        # Default to first enabled tab
        if pl_enabled:
            st.session_state.active_tab_index = 1
        elif hp_enabled:
            st.session_state.active_tab_index = 2
        else:
            st.session_state.active_tab_index = 0
    
    # Create a container for tab selection
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📇 Credit Card", 
                    type="primary" if st.session_state.active_tab_index == 0 else "secondary",
                    disabled=not cc_enabled,
                    width='stretch'):
            st.session_state.active_tab_index = 0
            st.rerun()
    
    with col2:
        if st.button("💳 Personal Financing", 
                    type="primary" if st.session_state.active_tab_index == 1 else "secondary",
                    disabled=not pl_enabled,
                    width='stretch'):
            st.session_state.active_tab_index = 1
            st.rerun()
    
    with col3:
        if st.button("🚗 Hire Purchase", 
                    type="primary" if st.session_state.active_tab_index == 2 else "secondary",
                    disabled=not hp_enabled,
                    width='stretch'):
            st.session_state.active_tab_index = 2
            st.rerun()
    
    st.divider()
    
    # Display content based on active tab
    active_tab = st.session_state.active_tab_index
    
    # --- CREDIT CARD TAB ---
    if active_tab == 0:
        if cc_enabled:
            # Filter data for CC
            cc_df = filter_data_by_product_group(st.session_state.df, 'CC')
            
            if cc_df is not None and not cc_df.empty:
                # Display CIF selector
                selected_cif = display_cif_selector(cc_df, 'CC')
                
                if selected_cif:
                    # Display CIF data table
                    cif_data = display_cif_data_table(cc_df, selected_cif)
                    
                    if cif_data is not None:
                        # Run Credit Card calculator
                        run_credit_card_calculator(cif_data)
            else:
                st.warning("No Credit Card (CC) records found in the uploaded file.")
        else:
            st.warning("⚠️ Credit Card tab is disabled. The uploaded file contains Personal Financing or Hire Purchase records only.")
            st.info("💡 To use Credit Card calculator, please upload an Excel file with 'CC' in the Product Group column.")
    
    # --- PERSONAL FINANCING TAB ---
    elif active_tab == 1:
        if pl_enabled:
            # Filter data for PL
            pl_df = filter_data_by_product_group(st.session_state.df, 'PL')
            
            if pl_df is not None and not pl_df.empty:
                # Display CIF selector
                selected_cif = display_cif_selector(pl_df, 'PL')
                
                if selected_cif:
                    # Display CIF data table
                    cif_data = display_cif_data_table(pl_df, selected_cif)
                    
                    if cif_data is not None:
                        # Run Personal Financing calculator
                        run_personal_financing_calculator(cif_data)
            else:
                st.warning("No Personal Financing (PL) records found in the uploaded file.")
        else:
            st.warning("⚠️ Personal Financing tab is disabled. The uploaded file contains Credit Card or Hire Purchase records only.")
            st.info("💡 To use Personal Financing calculator, please upload an Excel file with 'PL' in the Product Group column.")
    
    # --- HIRE PURCHASE TAB ---
    elif active_tab == 2:
        if hp_enabled:
            # Filter data for HP
            hp_df = filter_data_by_product_group(st.session_state.df, 'HP')
            
            if hp_df is not None and not hp_df.empty:
                # Display CIF selector
                selected_cif = display_cif_selector(hp_df, 'HP')
                
                if selected_cif:
                    # Display CIF data table
                    cif_data = display_cif_data_table(hp_df, selected_cif)
                    
                    if cif_data is not None:
                        # Run Hire Purchase calculator
                        run_hire_purchase_calculator(cif_data)
            else:
                st.warning("No Hire Purchase (HP) records found in the uploaded file.")
        else:
            st.warning("⚠️ Hire Purchase tab is disabled. The uploaded file contains Credit Card or Personal Financing records only.")
            st.info("💡 To use Hire Purchase calculator, please upload an Excel file with 'HP' in the Product Group column.")

elif st.session_state.df is None:
    st.info("👆 Please upload an Excel file to get started")
else:
    st.error("❌ No valid Product Group detected in the uploaded file. Please ensure your Excel has a 'Product Group' column with values: CC, PL, or HP.")