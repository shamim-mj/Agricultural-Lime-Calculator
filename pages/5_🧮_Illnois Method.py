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
    /* 1. COMPACT INPUTS: Prevents text from hiding in 5-column layouts */
    .stNumberInput input, .stTextInput input {
        background-color: #f8f9fa !important;
        border-radius: 8px !important;
        padding: 4px 8px !important; /* Reduced padding from 10px to keep text visible */
        font-size: 14px !important;    /* Slightly smaller font for narrow columns */
    }
    
    /* Remove extra vertical space around inputs */
    div[data-testid="stMarkdownContainer"] p {
        margin-bottom: 0px !important;
    }

    /* 2. SNUG TABS: Moves tabs closer together */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px !important; /* Reduced from 24px to 4px to keep them close */
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 45px !important;
        white-space: nowrap !important; /* Prevents text from stacking weirdly */
        background-color: #f0f2f6;
        border-radius: 5px 5px 0px 0px !important; /* Rounded top corners only */
        padding: 5px 15px !important;
        border: 1px solid #e9ecef;
    }

    /* Active Tab Style */
    .stTabs [aria-selected="true"] {
        background-color: #0033A0 !important;
        color: white !important;
        border-bottom: 2px solid #0033A0 !important;
    }

    /* 3. METRIC STYLING */
    [data-testid="stMetricValue"] {
        color: #0033A0;
        font-size: 1.8rem !important;
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
        df_IL['Bulk_Rec'] = np.ceil(raw_bulk * 2) / 2
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
with tab1:
    #st.markdown("<h4 style='text-align: center;'>Illinois Particle Efficiency</h4>", unsafe_allow_html=True)
    # Sieve Stack
    with st.container(border=True):
        st.markdown("### Particle Efficiency")
        fig, axes = plt.subplots(4, 1, figsize=(8, 7), sharex=True)
        metrics = [("L8B0", "#8 Sieve (5%)"), ("L30B8", "#30 Sieve (20%)"), 
                ("L60B30", "#60 Sieve (50%)"), ("L60", "<#60 Sieve (100%)")]
        
        for i, (col, title) in enumerate(metrics):
            sns.barplot(data=df_IL, x=col, y='Quarry', ax=axes[i], palette=pallete)
            axes[i].set_xlim(0, 120)
            axes[i].set_ylabel("")
            axes[i].set_title(title, loc='center', fontsize=10)
            add_labels(axes[i])
        plt.tight_layout(pad=0.1)
        st.pyplot(fig)
    with st.container(border=True):
        st.markdown("### Effective Neutralizing Value (ENV, %)")
        # ENV Plot
        fig2, ax5 = plt.subplots(figsize=(8, 3))
        sns.barplot(data=df_IL, x='ENV', y='Quarry', ax=ax5, palette=pallete)
        #ax5.set_title("Effective Neutralizing Value (ENV, %)")
        ax5.set_ylabel("")
        ax5.set_xlabel("")
        ax5.set_xlim(0, 120)
        ax5.set_xticks([])
        ax5.set_xticklabels([])
        add_labels(ax5)
        st.pyplot(fig2)

with tab2:
    st.markdown("<h4 style='text-align: center;'>Application Strategy</h4>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("### Adjusted Lime Recommendation (t/ac)")
        # Recommendation
        fig3, ax6 = plt.subplots(figsize=(8, 3))
        sns.barplot(data=df_IL, x='Bulk_Rec', y='Quarry', ax=ax6, palette=pallete)
        #ax6.set_title("Adjusted Lime Recommendation (t/ac)")
        ax6.set_xlim(0, df_IL['Bulk_Rec'].max() * 1.3)
        ax6.set_xlabel("")
        ax6.set_ylabel("")
        ax5.set_xticks([])
        ax5.set_xticklabels([])
        add_labels(ax6)
        st.pyplot(fig3)

    # Cost
    with st.container(border=True):
        st.markdown("### Total Application Cost ($/ac)")
        fig4, ax7 = plt.subplots(figsize=(8, 3))
        sns.barplot(data=df_IL, x='Cost', y='Quarry', ax=ax7, palette=pallete)
        #ax7.set_title("Total Application Cost ($/ac)")
        ax7.set_xlim(0, df_IL['Cost'].max() * 1.3)
        ax7.set_xlabel("")
        ax5.set_xticks([])
        ax5.set_xticklabels([])
        ax7.set_ylabel("")
        add_labels(ax7)
        st.pyplot(fig4)

with tab3:
    st.info("Analysis based on the Illinois Voluntary Limestone Program. The 'Adjusted Recommendation' accounts for fineness efficiency and CCE to ensure target pH is met.")