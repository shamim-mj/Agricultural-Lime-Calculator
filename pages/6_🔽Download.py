import pandas as pd
import streamlit as st
import datetime

# --- PAGE CONFIG & STYLING ---
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
st.markdown("<h2 style='background-color: #0033A0; color: white; text-align: center; padding: 15px; border-radius: 5px;'>📊 Output & Export Center</h2>", unsafe_allow_html=True)

# Date and Time for unique filenames
date_now = datetime.date.today()
time_now = datetime.datetime.now().strftime("%H-%M")

# --- DATA SELECTION AREA ---
st.write("### 1. Select Dataset")
# Using horizontal radio for maximum compatibility
radio = st.radio(
    "Which analysis results would you like to view?",
    options=['Kentucky Manual', 'Kentucky CSV', 'Ohio', 'Illinois'],
    horizontal=True
)
st.markdown("---")

# --- REUSABLE PROCESSOR ---
def process_download(state_key, display_cols, descriptions, filename_prefix):
    if state_key not in st.session_state:
        st.error(f"❌ **No data found for {radio}.** Please go to the {radio} tab and enter your data first.")
    else:
        df = st.session_state[state_key].copy()
        df = df.round(2)
        
        # Mapping technical names to meaningful headers
        friendly_headers = {
            "Quarry": "Source / Quarry",
            "Zero%_eff": "Ineffective (%)",
            "Fifty%_eff": "50% Effective (%)",
            "Hund%_eff": "100% Effective (%)",
            "RNV": "Quality (RNV %)",
            "Bulk_Rec": "Rec. Rate (t/a)",
            "Cost": "Total Cost ($/ac)",
            "FI": "Fineness Index",
            "%_ENP": "ENP (%)",
            "t_ENP": "ENP per Ton",
            "ENV": "ENV (%)",
            "TFEV": "Fineness Value"
        }

        with st.container(border=True):
            st.markdown(f"#### 📄 {radio} Report Preview")
            
            # Applying the meaningful names using column_config
            st.dataframe(
                df[display_cols], 
                column_config={col: friendly_headers.get(col, col) for col in display_cols},
                use_container_width=True, 
                hide_index=True
            )
            
            col_left, col_right = st.columns([2, 1])
            with col_left:
                with st.expander("📖 View Column Descriptions"):
                    st.markdown(descriptions, unsafe_allow_html=True)
            
            with col_right:
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"{filename_prefix}_{date_now}_{time_now}.csv",
                    mime='text/csv',
                    key=f"btn_{state_key}"
                )

# Glossaries
ky_desc = "<b>RNV:</b> Relative Neutralizing Value<br><b><b>Cost:</b> $ per acre"
oh_desc = "<b>FI:</b> Fineness Index<br><b>ENP:</b> Effective Neutralizing Power<br><b>Cost:</b> Total applied cost"
il_desc = "<b>TFEV:</b> Total Fineness Effective Value<br><b>ENV:</b> Effective Neutralizing Value<br><b>B8-L60:</b> Particle sizes"

# --- ROUTING ---
if radio == 'Kentucky Manual':
    process_download('df', ['Quarry', 'Zero%_eff', 'Fifty%_eff', 'Hund%_eff', "RNV", 'Bulk_Rec', 'Cost'], ky_desc, "KY_Manual")

elif radio == 'Kentucky CSV':
    process_download('df_up', ['Quarry', 'Zero%_eff', 'Fifty%_eff', 'Hund%_eff', "RNV", 'Bulk_Rec', 'Cost'], ky_desc, "KY_Upload")

elif radio == "Ohio":
    process_download('df_oh', ['Quarry','FI', "%_ENP", "t_ENP", "Bulk_Rec", "Cost"], oh_desc, "Ohio_Report")

elif radio == "Illinois":
    # Ensure these match your actual DataFrame columns exactly
    il_cols = ['Quarry', 'B8', 'L30B8', 'L60B30','L60', "TFEV","ENV" ,'Bulk_Rec', 'Cost']
    process_download('df_IL', il_cols, il_desc, "Illinois_Report")

# --- EXCEL SECTION ---
st.markdown("<br>", unsafe_allow_html=True)
with st.container(border=True):
    st.write("### 📗 Excel Offline Version")
    st.write("Download the master Excel template for offline calculations.")
    st.markdown(
        """
        <a href='https://github.com/shamim-mj/Aglime_Calculator_in_Excel.git' target='_blank' style='text-decoration:none;'>
            <div style='background-color:#217346; color:white; padding:12px; border-radius:8px; text-align:center; font-weight:bold;'>
                🟢 Download Excel Calculator Template
            </div>
        </a>
        """, 
        unsafe_allow_html=True
    )