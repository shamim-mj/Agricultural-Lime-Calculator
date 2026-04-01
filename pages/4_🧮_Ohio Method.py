import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import time
import math
from streamlit_option_menu import option_menu

# --- Page Config ---
st.set_page_config(page_title="Ohio Method - Lime Data", layout="centered")


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
            
              /* Add a soft glow when hovering over a result card */
    div[data-testid="stVerticalBlock"] > div:has(div.stExpander), 
    .st-emotion-cache-12w0slk { /* Targets container-bordered divs */
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }

    div[data-testid="element-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,51,160,0.1);

            

    </style>
""", unsafe_allow_html=True)




# Custom CSS for styling
st.markdown("""
    <style>
    #MainMenu, footer {visibility: hidden;}
    .main-header {
        background-color: #0033A0; color: white !important; text-align: center; 
        padding: 10px; border-radius: 5px; margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 class='main-header'>Ohio Method: Lime & Soil Data</h2>", unsafe_allow_html=True)

# --- Selection Menu ---
percent_weight = option_menu(None, ["Lab Results (Weight)", "Lab Results (Percentage)"], 
    icons=[], menu_icon="cast", default_index=0, orientation="horizontal",
    styles={"container": {"background-color": "#ffe6e6"}, "nav-link-selected": {"background-color": "#ff0000"}})

# --- Lime Data Input ---
st.markdown("<h4 class='main-header'>Lime Data Input</h4>", unsafe_allow_html=True)
ncol = st.number_input("Number of Samples", 1, 5, 1)
cols = st.columns(ncol)

data_list = []
for i in range(ncol):
    with cols[i]:
        st.write(f"**Sample {i+1}**")
        name = st.text_input('Source Name', value=f'Sample {i+1}', key=f"q_{i}_n")
        
        if percent_weight == "Lab Results (Weight)":
            init = st.number_input('Initial (g)', value=550.0, key=f"q_{i}_i")
            m8 = st.number_input('< #8 (g)', value=430.0, key=f"q_{i}_8")
            m20 = st.number_input('< #20 (g)', value=370.0, key=f"q_{i}_20")
            m60 = st.number_input('< #60 (g)', value=300.0, key=f"q_{i}_60")
        else:
            init = 100.0
            m8 = st.number_input('% < #8', value=80.0, key=f"q_{i}_8p")
            m20 = st.number_input('% < #20', value=50.0, key=f"q_{i}_20p")
            m60 = st.number_input('% < #60', value=40.0, key=f"q_{i}_60p")

        cce = st.number_input("TNP/CCE (%)", value=90.0, key=f'cce{i}')
        wet = st.number_input("Wet Weight (g)", value=600.0, key=f'wet{i}')
        dry = st.number_input("Dry Weight (g)", value=560.0, key=f'dry{i}')
        rec_ton = st.number_input("Rec. Amount (t/a)",value= 2.0, min_value=0.0, step=0.1, key=f'rt{i}')
        
        # Costs
        l_p = st.number_input("Lime ($/t)", value= 2.0, min_value=0.0, step=0.1, key=f'lp{i}')
        d_p = st.number_input("Delivery ($/t)", value= 5.0, min_value=0.0, step=0.1, key=f'dp{i}')
        s_p = st.number_input("Spreading ($/t)", value=5.0, min_value=0.0, step=0.1, key=f'sp{i}')
        
        data_list.append({
            "Quarry": name, "initial": init, "l8": m8, "l20": m20, "l60": m60, 
            "cce": cce, "wetw": wet, "dryw": dry, "recton": rec_ton, "price": (l_p + d_p + s_p)
        })

df_oh = pd.DataFrame(data_list)

# --- Ohio Method Calculations ---
if not df_oh.empty:
    if percent_weight == "Lab Results (Weight)":
        df_oh["Zero%_eff"] = ((df_oh.initial - df_oh.l8) / df_oh.initial) * 100
        df_oh['twenty%_eff'] = ((df_oh.l8 - df_oh.l20) / df_oh.initial) * 100
        df_oh['fifty%_eff'] = ((df_oh.l20 - df_oh.l60) / df_oh.initial) * 100
        df_oh['Hund%_eff'] = (df_oh.l60 / df_oh.initial) * 100
        df_oh['FI'] = (0.2 * (df_oh.l8 - df_oh.l20) / df_oh.initial + 0.6 * (df_oh.l20 - df_oh.l60) / df_oh.initial + df_oh.l60 / df_oh.initial) * 100
    else:
        df_oh["Zero%_eff"] = 100 - df_oh.l8
        df_oh['twenty%_eff'] = df_oh.l8 - df_oh.l20
        df_oh['fifty%_eff'] = df_oh.l20 - df_oh.l60
        df_oh['Hund%_eff'] = df_oh.l60
        df_oh['FI'] = (0.2 * (df_oh.l8 - df_oh.l20) + 0.6 * (df_oh.l20 - df_oh.l60) + df_oh.l60)

    df_oh['%_dry'] = 100 - ((df_oh.wetw - df_oh.dryw) / df_oh.wetw * 100)
    df_oh['%_ENP'] = (df_oh.FI / 100) * df_oh.cce
    df_oh['t_ENP'] = 2000 * (df_oh['%_ENP'] / 100) * (df_oh['%_dry'] / 100)
    
    # Calculate and Round UP to nearest 0.5
    raw_bulk = (2000 / df_oh.t_ENP * df_oh.recton)
    df_oh['Bulk_Rec'] =  raw_bulk.round(1)
    df_oh['Cost'] = df_oh.Bulk_Rec * df_oh.price
st.session_state['df_oh'] = df_oh # this is used in downnloads



# --- Helper Function for Labels ---
def add_labels(ax, fmt="%.2f"):
    for p in ax.patches:
        width = p.get_width()
        ax.text(width + (ax.get_xlim()[1] * 0.02), p.get_y() + p.get_height()/2, 
                fmt % width, va='center', fontweight='bold')

# --- Tabs ---

# check if pallete is in session_sate.
if "pallete" not in st.session_state:
    pallete = "Dark2"
else:
    pallete = st.session_state['pallete']
    # Use this when a calculation or upload starts
with st.status("Analyzing Soil Data...", expanded=True) as status:
    st.write("Applying Ohio method...")
    time.sleep(0.5) # Simulating math
    st.write("Effective Neutralizing Power (ENP, %)...")
    status.update(label="Analysis Complete!", state="complete", expanded=False)

tab1, tab2, tab3 = st.tabs(["**Lime Quality**", "**Amount & Cost**", "**Summary Results**"])

base_height = 1.5  # Minimum height for the "cute" look
height_per_quarry = 0.5
dynamic_height = base_height + (len(df_oh) * height_per_quarry)


with tab1:
    #st.markdown("<h4 style='text-align: center;'>Fineness & ENP</h4>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("### Lime Fineness")
        # Fineness Stack
        fig, axes = plt.subplots(4, 1, figsize=(8, dynamic_height * 1.2), sharex=True)
        metrics = [("Zero%_eff", "#8 Sieve"), ("twenty%_eff", "#20 Sieve"), 
                ("fifty%_eff", "#60 Sieve"), ("Hund%_eff", "< #60 Sieve")]
        
        for i, (col, title) in enumerate(metrics):
            sns.barplot(data=df_oh, x=col, y='Quarry', ax=axes[i], palette=pallete)
            axes[i].set_xlim(0, 120)
            axes[i].set_ylabel("")
            axes[i].set_xticks([])
            axes[i].set_xticklabels([])
            axes[i].set_title(title, loc='center', fontsize=10)
            add_labels(axes[i])
        plt.tight_layout(pad=0.2)
        st.pyplot(fig)


with tab1:
    # ... Particle Size code here (ensure width=0.4 is there too) ...

    with st.container(border=True):
        st.markdown("### Effective Neutralizing Power (ENP, %)")
        # Lowered multiplier to 0.6 because single plots don't need as much vertical space as the triple stack
        fig2, ax5 = plt.subplots(figsize=(8, dynamic_height * 0.6))
        
        # ADDED width=0.4 HERE
        sns.barplot(data=df_oh, x='%_ENP', y='Quarry', ax=ax5, palette=pallete, width=0.4)
        
        ax5.set_ylabel("")
        ax5.set_xlabel("")
        ax5.set_xlim(0, 120)
        ax5.set_xticks([])
        ax5.set_xticklabels([])
        add_labels(ax5)
        st.pyplot(fig2)
        plt.close()

with tab2:
    with st.container(border=True):
        st.markdown("### Adjusted Lime Recommendation (t/ac)")
        fig3, ax6 = plt.subplots(figsize=(8, dynamic_height * 0.6))
        
        # ADDED width=0.4 HERE
        sns.barplot(data=df_oh, x='Bulk_Rec', y='Quarry', ax=ax6, palette=pallete, width=0.4)
        
        ax6.set_xlim(0, (df_oh['Bulk_Rec'].max() * 1.3) if not df_oh.empty else 10)
        ax6.set_ylabel("")
        ax6.set_xlabel("")
        ax6.set_xticks([])
        ax6.set_xticklabels([])
        add_labels(ax6)
        st.pyplot(fig3)
        plt.close()

    with st.container(border=True):
        st.markdown("### Total application cost ($/ac)")
        fig4, ax7 = plt.subplots(figsize=(8, dynamic_height * 0.6))
        
        # ADDED width=0.4 HERE
        sns.barplot(data=df_oh, x='Cost', y='Quarry', ax=ax7, palette=pallete, width=0.4)
        
        ax7.set_xlim(0, (df_oh['Cost'].max() * 1.3) if not df_oh.empty else 10)
        ax7.set_ylabel("")
        ax7.set_xlabel("")
        ax7.set_xticks([])
        ax7.set_xticklabels([])
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
    #-----------------------------------------------------------------------------------
with tab3:
    if not df_oh.empty:
        # 1. Calculation Logic: Sort by Cost (Low to High), then RNV (High to Low)
        # This ensures that if costs are equal, the higher quality wins.
        df_oh_sorted = df_oh.sort_values(by=['Cost', '%_ENP'], ascending=[True, False])
        
        # The first row is now our "Best Pick"
        best_value = df_oh_sorted.iloc[0]
        
        # 2. The Header Container (Metrics)
        with st.container(border=True):
            st.markdown("### 🏆 Top Performance Summary")
            m1, m2, m3 = st.columns(3)
            
            m1.metric("Top Value Source", best_value["Quarry"], 
                    help="Lowest cost per acre. If costs match, highest RNV is chosen.")
            m2.metric("Application Rate (t/ac)", f"{df_oh['Bulk_Rec'].min():.1f} t/a", "Efficiency")
            m3.metric("ENP Quality (%)", f"{df_oh['%_ENP'].max():.1f}%", "%_ENP")

        st.markdown("### 📊 Detailed Comparison")
        
        # 3. The Styled Table
        # I corrected the key from "ENV" to "RNV" to match your dataframe slice
        st.dataframe(
            df_oh[['Quarry', '%_ENP', 'Bulk_Rec', 'Cost']],
            column_config={
                "Quarry": st.column_config.TextColumn("Lime Source", width="medium"),
                "%_ENP": st.column_config.ProgressColumn(
                    "Quality (ENP %)",
                    help="Relative Neutralizing Power",
                    format="%.1f%%",
                    min_value=0,
                    max_value=100,
                ),
                "Bulk_Rec": st.column_config.NumberColumn(
                    "Rec. (t/a)",
                    help="Adjusted Bulk Recommendation",
                    format="%.2f 🚜",
                ),
                "Cost": st.column_config.NumberColumn(
                    "Total Cost ($)",
                    help="Total per acre (Lime + Delivery + Spreading)",
                    format="$ %.2f",
                ),
            },
            hide_index=True,
            use_container_width=True
        )
    with st.container(border=True):
        st.markdown("#### 🚜 Management Note")
        st.info("""
            **Recommendation:** You may round your bulk lime application rates to the nearest 
            **half-ton (0.5)** or **whole ton** based on the calibration limits of your 
            spreading equipment.
        """)