import streamlit as st

# --- PAGE CONFIG ---
st.markdown("""
    <style>
    /* 1. GLOBAL OVERFLOW FIX: Target every layer of the tab container */
    [data-testid="stTabs"], 
    [data-testid="stTabs"] > div, 
    [data-testid="stTabs"] [data-baseweb="tab-list"],
    [data-testid="stTabs"] [data-baseweb="tab"],
    .stTabs [data-baseweb="tab-panel"] {
        overflow: visible !important;
    }

    /* 2. TAB BUTTON STYLING: Ensuring icons don't get clipped */
    .stTabs [data-baseweb="tab"] {
        height: 45px !important;
        white-space: nowrap !important;
        background-color: #f0f2f6;
        border-radius: 5px 5px 0px 0px !important;
        padding: 5px 15px !important;
        border: 1px solid #e9ecef;
        /* Allow the help icon to pop out */
        display: flex !important;
        align-items: center !important;
    }

    /* 3. TOOLTIP Z-INDEX: Force tooltips to stay on top of everything */
    div[data-testid="stTooltipHoverTarget"], 
    .st-emotion-cache-1pxm6on, /* Common tooltip container cache */
    [role="tooltip"] {
        z-index: 999999 !important;
        overflow: visible !important;
    }

    /* 4. HELP ICON POSITION: Aligning the '?' inside the tab */
    .stTabs [data-testid="stHelpIcon"] {
        margin-left: 6px !important;
        flex-shrink: 0 !important; /* Prevents icon from squishing */
    }

    /* 5. ACTIVE TAB GLOW: Highlighting the selection */
    .stTabs [aria-selected="true"] {
        background-color: #0033A0 !important;
        color: white !important;
        box-shadow: 0px 4px 10px rgba(0, 51, 160, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h2 style='text-align: center; color: #0033A0;'>🎨 Visualization Settings</h2>", unsafe_allow_html=True)
st.markdown("---")

# Main Container
with st.container():
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.markdown("<p class='settings-title'>Chart Color Palette</p>", unsafe_allow_html=True)
        st.caption("Select a theme for your particle analysis charts.")
        
        # Organize the long list into a clean selectbox
        palettes = [
            "viridis", "plasma", "inferno", "magma", "cividis", # Popular ones first
            "Dark2","Accent", "Accent_r", "autumn", "Blues", "Blues_r", "bright", "BuGn", 
            "BuGn_r", "BuPu", "BuPu_r", "binary", "binary_r", "bone", "bone_r", "bwr", "colorblind",  "cool", "coolwarm", "copper", "cubehelix", "dark",
            "Dark2_r", "deep","GnBu", "GnBu_r", "gnuplot" ,"gnuplot2","Greens", "Greens_r", "Greys", "Greys_r" ,"gray", "hot", "hot_r" ,"jet_r","nipy_spectral", "muted",
            "OrRd", "OrRd_r","ocean", "ocean_r" ,"Oranges", "Oranges_r", "PRGn", "PRGn_r", "pink", "pink_r" ,"Paired", "Paired_r","pastel", "Pastel1", "Pastel1_r",
            "Pastel2", "Pastel2_r", "PiYG", "PiYG_r",  "PuBu", "PuBuGn", "PuBuGn_r", "PuBu_r", "PuOr", "PuOr_r", "PuRd", "PuRd_r",
            "Purples", "Purples_r","rainbow","rainbow_r" ,"RdBu", "RdBu_r", "RdGy", "RdGy_r", "RdPu", "RdPu_r", "RdYlBu", "RdYlGn", "Reds", "Reds_r", "Set1", "Set1_r",
            "Set2", "Set2_r", "Set3", "Set3_r", "Spectral", "Spectral_r" , "seismic", "seismic_r" ,"spring","spring_r", "summer","summer_r", "YlGn", "YlGnBu", "YlOrBr", "YlOrRd",
            "prism", "terrain", "terrain_r","winter", "winter_r"
        ]
        
        selected_pallete = st.selectbox(
            "Choose color palette", 
            options=palettes,
            index=0,
            label_visibility='collapsed'
        )
        
        st.session_state['pallete'] = selected_pallete
        
        st.success(f"**Active Theme:** {selected_pallete}")

    with col2:
        # A visual placeholder to make the page look full and professional
        with st.container(border=True):
            st.markdown("<p style='text-align: center; color: #666;'><b>Palette Preview Tip</b></p>", unsafe_allow_html=True)
            st.info(f"""
            The **{selected_pallete}** palette will be applied to:
            * Particle size distribution bars
            * Cost-benefit analysis curves
            * Soil pH response charts
            """)
            st.warning("Note: Some palettes (like 'binary' or 'Greys') may be harder to read in dark mode.")

st.markdown("---")
st.caption("Settings are saved automatically for the duration of this session.")