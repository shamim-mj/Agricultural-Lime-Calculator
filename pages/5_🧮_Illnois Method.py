import pandas as pd
import streamlit as st
import seaborn as sns
import time
import matplotlib.pyplot as plt
import numpy as np
from streamlit_option_menu import option_menu

# --- Page Config ---
st.set_page_config(page_title="Illinois Lime Method", layout="centered")

# Custom CSS
st.markdown("""
    <style>
    #MainMenu, footer {}
    .main-header {
        background-color: #0033A0; color: white !important; text-align: center; 
        padding: 10px; border-radius: 5px; margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)



# Changes ----------------------------------------------------------------------------------------
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





st.markdown("<h2 class='main-header'>Illinois Method: Lime and Soil Data</h2>", unsafe_allow_html=True)

# --- Selection Menu ---
percent_weight = option_menu(None, ["Manual Analysis"], 
    icons=[], menu_icon="cast", default_index=0, orientation="horizontal",
    styles={"container": {"background-color": "#ffe6e6"}, "nav-link-selected": {"background-color": "#ff0000"}})

# --- Data Input Logic ---
data_list = []

if percent_weight == "Manual Analysis":
    st.markdown("<h4 class='main-header'>Manual Sieve Entry</h4>", unsafe_allow_html=True)
    ncol = st.number_input("Number of Samples", 1, 5, 1)
    cols = st.columns(ncol)
    
    for i, x in enumerate(cols):
        name = x.text_input('Source Name', value=f'Sample {i+1}', key=f"q_{i}_n")
        m8 = x.number_input('% < #8', value=85.0, key=f"q_{i}_8", format="%.2f")
        m30 = x.number_input('% < #30', value=35.0, key=f"q_{i}_30", format="%.2f")
        m60 = x.number_input('% < #60', value=22.0, key=f"q_{i}_60", format="%.2f")
        cce = x.number_input("CCE (%)", value=90.0, key=f'cce{i}', format="%.1f")
        
        # Fixed: min_value=0.0 allows entering values below 2.0
        rec_ton = x.number_input("Rec. Amount (t/a)", min_value=0.0, value=2.0, key=f'rt{i}', format="%.1f")
        
        l_p = x.number_input("Lime ($/t)", value=5.0, key=f'lp{i}')
        d_p = x.number_input("Delivery ($/t)", value=5.0, key=f'dp{i}')
        s_p = x.number_input("Spreading ($/t)", value=5.0, key=f'sp{i}')
        
        data_list.append({
            "Quarry": name, "B8": m8, "l30_raw": m30, "l60_raw": m60, 
            "cce": cce/100, "recton": rec_ton, "price": (l_p + d_p + s_p)
        })

    df_IL = pd.DataFrame(data_list)
    if not df_IL.empty:
        # Illinois Specific Calculation
        p = 0.01
        df_IL["L8B0"] = 100 - df_IL.B8 # lower than 8 bigger than o
        df_IL["L30B8"] = df_IL.B8 - df_IL.l30_raw # lower than 30 and bigger than 8
        df_IL["L60B30"] = df_IL.l30_raw - df_IL.l60_raw # lower than 60 and bigger than 30
        df_IL["L60"] = df_IL.l60_raw # lower than 60
        
        df_IL['TFEV'] = (1 - df_IL.B8*p)*5 + (df_IL.L30B8*p)*20 + (df_IL.L60B30*p)*50 + (df_IL.L60*p)*100
        df_IL['ENV'] = df_IL.TFEV * df_IL.cce
        df_IL['OYAR'] = 46.35 / df_IL.ENV
        
        # Round UP to nearest 0.5
        raw_bulk = df_IL.OYAR * df_IL.recton
        df_IL['Bulk_Rec'] = raw_bulk.round(1)
        df_IL['Cost'] = df_IL.Bulk_Rec * df_IL.price

        st.session_state['df_IL'] = df_IL
# --- Manual Labeling Function ---
def add_labels(ax, fmt="%.2f"):
    for p in ax.patches:
        width = p.get_width()
        if width > 0:
            ax.text(width + (ax.get_xlim()[1] * 0.02), p.get_y() + p.get_height()/2, 
                    fmt % width, va='center', fontweight='bold', fontsize=8)

# --- Visualization ---

# check if pallete is in session_sate.
if "pallete" not in st.session_state:
    pallete = "Dark2"
else:
    pallete = st.session_state['pallete']

# Use this when a calculation or upload starts
with st.status("Analyzing Soil Data...", expanded=True) as status:
    st.write("Applying Illinois method...")
    time.sleep(0.5) # Simulating math
    st.write("Effective Neutralizing Value (ENV, %)...")
    status.update(label="Analysis Complete!", state="complete", expanded=False)



tab1, tab2, tab3 = st.tabs(["**Lime Quality**", "**Amount & Cost**", "**Note**"])

base_height = 1.5  # Minimum height for the "cute" look
height_per_quarry = 0.5
dynamic_height = base_height + (len(df_IL) * height_per_quarry)

with tab1:
    # Sieve Stack (4 plots for Illinois)
    with st.container(border=True):
        st.markdown("### Particle Efficiency")
        # Multiplied by 1.5 because there are 4 subplots here
        fig, axes = plt.subplots(4, 1, figsize=(8, dynamic_height * 1.5), sharex=True)
        metrics = [("L8B0", "#8 Sieve (5%)"), ("L30B8", "#30 Sieve (20%)"), 
                   ("L60B30", "#60 Sieve (50%)"), ("L60", "<#60 Sieve (100%)")]
        
        for i, (col, title) in enumerate(metrics):
            sns.barplot(data=df_IL, x=col, y='Quarry', ax=axes[i], palette=pallete, width=0.4)
            axes[i].set_xlim(0, 120)
            axes[i].set_ylabel("")
            axes[i].set_title(title, loc='center', fontsize=10)
            axes[i].set_xticks([]) # Hide the numbers on the x-axis for a clean look
            add_labels(axes[i])
        plt.tight_layout(pad=1.0)
        st.pyplot(fig)
        plt.close()

    with st.container(border=True):
        st.markdown("### Effective Neutralizing Value (ENV, %)")
        fig2, ax5 = plt.subplots(figsize=(8, dynamic_height * 0.6))
        sns.barplot(data=df_IL, x='ENV', y='Quarry', ax=ax5, palette=pallete, width=0.4)
        ax5.set_ylabel("")
        ax5.set_xlabel("")
        ax5.set_xlim(0, 120)
        ax5.set_xticks([])
        add_labels(ax5)
        st.pyplot(fig2)
        plt.close()

with tab2:
    st.markdown("<h4 style='text-align: center;'>Application Strategy</h4>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("### Adjusted Lime Recommendation (t/ac)")
        fig3, ax6 = plt.subplots(figsize=(8, dynamic_height * 0.6))
        sns.barplot(data=df_IL, x='Bulk_Rec', y='Quarry', ax=ax6, palette=pallete, width=0.4)
        
        # FIXED: Ensure we use ax6 limits and labels
        ax6.set_xlim(0, (df_IL['Bulk_Rec'].max() * 1.3) if not df_IL.empty else 10)
        ax6.set_xlabel("")
        ax6.set_ylabel("")
        ax6.set_xticks([]) # FIXED: Was ax5 previously
        add_labels(ax6)
        st.pyplot(fig3)
        plt.close()

    with st.container(border=True):
        st.markdown("### Total Application Cost ($/ac)")
        fig4, ax7 = plt.subplots(figsize=(8, dynamic_height * 0.6))
        sns.barplot(data=df_IL, x='Cost', y='Quarry', ax=ax7, palette=pallete, width=0.4)
        
        # FIXED: Ensure we use ax7 limits and labels
        ax7.set_xlim(0, (df_IL['Cost'].max() * 1.3) if not df_IL.empty else 10)
        ax7.set_xlabel("")
        ax7.set_ylabel("")
        ax7.set_xticks([]) # FIXED: Was ax5 previously
        add_labels(ax7)
        st.pyplot(fig4)
        plt.close()
    with st.container(border=True):
        st.markdown("#### 🚜 Management Note")
        st.info("""
            **Recommendation:** You may round your bulk lime application rates to the nearest 
            **half-ton (0.5)** or **whole ton** based on the calibration limits of your 
            spreading equipment.
        """)
with tab3:
    st.info("Analysis based on the Illinois Voluntary Limestone Program. The 'Adjusted Recommendation' accounts for fineness efficiency and CCE to ensure target pH is met.")