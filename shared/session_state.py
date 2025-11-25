import streamlit as st

def initialize_session_state():
    """Initialize all session state variables"""
    
    # Global data
    if 'df' not in st.session_state:
        st.session_state.df = None
    
    # Enabled tabs based on Product Group
    if 'enabled_tabs' not in st.session_state:
        st.session_state.enabled_tabs = set()
    
    # Active tab tracking (0=CC, 1=PL, 2=HP)
    if 'active_tab_index' not in st.session_state:
        st.session_state.active_tab_index = None
    
    # Selected CIF per financing type
    if 'selected_cif_cc' not in st.session_state:
        st.session_state.selected_cif_cc = None
    if 'selected_cif_pl' not in st.session_state:
        st.session_state.selected_cif_pl = None
    if 'selected_cif_hp' not in st.session_state:
        st.session_state.selected_cif_hp = None
    
    # Previous CIF tracking (for reset detection)
    if 'previous_selected_cif_cc' not in st.session_state:
        st.session_state.previous_selected_cif_cc = None
    if 'previous_selected_cif_pl' not in st.session_state:
        st.session_state.previous_selected_cif_pl = None
    if 'previous_selected_cif_hp' not in st.session_state:
        st.session_state.previous_selected_cif_hp = None

def reset_cif_selection(financing_type):
    """Reset CIF selection for a specific financing type"""
    if financing_type == 'CC':
        st.session_state.selected_cif_cc = None
        st.session_state.previous_selected_cif_cc = None
    elif financing_type == 'PL':
        st.session_state.selected_cif_pl = None
        st.session_state.previous_selected_cif_pl = None
    elif financing_type == 'HP':
        st.session_state.selected_cif_hp = None
        st.session_state.previous_selected_cif_hp = None