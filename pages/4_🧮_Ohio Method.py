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
    styles={"container": {"background-color": "#ffe6e6"}, "nav-link-selected": {"background-color": "#0033A0"}})

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


#----------------------------------------------------------------------------------------------------------
# --- 1. Find ALL Most Economical (Lowest Cost) ---
     # --- 1. Find ALL Most Economical (Lowest Cost) ---

    # --- 1. Find ALL Most Economical (Lowest Cost) ---
df_oh['Cost_Per_Ton'] = df_oh['Cost'] / df_oh['Bulk_Rec']
min_cost = df_oh['Cost_Per_Ton'].min()
econ_winners = df_oh[df_oh['Cost_Per_Ton'] == min_cost]
econ_names = " & ".join(econ_winners['Quarry'].tolist())

# --- 2. Find ALL Highest Quality (Highest RNV) ---
max_rnv = df_oh['%_ENP'].max()
quality_winners = df_oh[df_oh['%_ENP'] == max_rnv]
quality_names = " & ".join(quality_winners['Quarry'].tolist())

# --- 3. THE WEIGHTED BEST OVERALL LOGIC ---
cost_range = df_oh['Cost'].max() - df_oh['Cost'].min()
rnv_range = df_oh['%_ENP'].max() - df_oh['%_ENP'].min()

# Normalization (handles cases where all costs or RNVs are the same)
df_oh['norm_cost'] = (df_oh['Cost'] - df_oh['Cost'].min()) / (cost_range + 1e-9)
df_oh['norm_rnv'] = (df_oh['%_ENP'] - df_oh['%_ENP'].min()) / (rnv_range + 1e-9)

# WEIGHTED SCORE: 70% Cost, 30% Quality
# (1 - norm_cost) because lower cost is better
df_oh['Overall_Score'] = (0.9 * (1 - df_oh['norm_cost'])) + (0.1 * df_oh['norm_rnv'])
df_oh['Overall_Score'] = df_oh['Overall_Score'].round(3)

# Find the Winner based on the new weighted score
max_score = df_oh['Overall_Score'].max()
overall_winners = df_oh[df_oh['Overall_Score'] == max_score]
overall_names = " & ".join(overall_winners['Quarry'].tolist())
best_overall = overall_winners.iloc[0]




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


with tab2:
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
with tab3:
    st.markdown("<h3 style='text-align: center; color: #0033A0;'>🏆 Lime Source Awards</h3>", unsafe_allow_html=True)
    st.write("")

    col_main, col_side = st.columns([1.5, 1.3])

    # CARD 2: Best Overall (The Gold "Hero" Card)
    with col_main:
        overall_title = "⭐ BEST OVERALL" if len(overall_winners) == 1 else "👯 OVERALL TIE"
        # Increased min-height and added professional styling
        st.markdown(f"""
            <div style="
                border: 2px solid #FFD700; 
                border-radius: 12px; 
                padding: 20px; 
                background-color: #FFFCF0; 
                text-align: center; 
                min-height: 300px;
                box-shadow: 0 4px 15px rgba(255, 215, 0, 0.2);
                display: flex;
                flex-direction: column;
                justify-content: center;
            ">
                <h5 style="margin: 0; color: #B8860B; text-transform: uppercase; letter-spacing: 1px;">{overall_title}</h5>
                <hr style="border: 0.5px solid #FFD700; margin: 10px 0;">
                <p style="font-size: 22px; font-weight: 800; color: #31333F; margin: 10px 0;">{overall_names}</p>
                <div style="background-color: #FFD700; color: black; border-radius: 5px; padding: 2px 10px; display: inline-block; margin-top: 10px; font-weight: bold; font-size: 12px;">
                    MAX VALUE SCORE - MOST ECONOMICAL
                </div>
            </div>
        """, unsafe_allow_html=True)

    # CARD 3: Highest Quality (Standard Container)
    with col_side:
        qual_title = "💎 HIGHEST QUALITY" if len(quality_winners) == 1 else "💎 QUALITY TIE"
        st.markdown(f"""
        <div style="
            border: 2px solid #ADD8E6; 
            border-radius: 12px; 
            padding: 20px; 
            background-color: #FFFFFF; 
            text-align: center; 
            min-height: 300px;
            box-shadow: 0 4px 15px rgba(255, 215, 0, 0.2);
            display: flex;
            flex-direction: column;
            justify-content: center;
        ">
            <h5 style="margin: 0; color: #B8860B; text-transform: uppercase; letter-spacing: 1px;">{qual_title}</h5>
            <hr style="border: 0.5px solid #ADD8E6; margin: 10px 0;">
            <p style="font-size: 22px; font-weight: 800; color: #31333F; margin: 10px 0;">{quality_names}</p>
            <div style="background-color: #ADD8E6; color: black; border-radius: 5px; padding: 2px 10px; display: inline-block; margin-top: 10px; font-weight: bold; font-size: 12px;">
                MAX QUALITY
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.write("---")
    # 2. "Hide and See" Calculation Logic (The Expander)
    with st.expander("🔬 How were these winners calculated?"):
        st.markdown("""
        **The scoring system uses a Multi-Criteria Decision Analysis (MCDA):**
        1. **Normalization:** Both **Total Cost** and **RNV** are scaled from 0 to 1 across all sources.
        2. **Inversion:** Cost is inverted so that a lower cost equals a higher score.
        3. **Weighting:** We apply a 10/90 weight to both Quality (RNV) and Economy (Cost).
        4. **Scoring:** """)
        st.latex(r"Score = (1 - \text{Normalized Cost}) + \text{Normalized RNV}")
        st.write("Sources with the highest total score are awarded the **Best Overall** title. If scores are within 0.001 of each other, a tie is declared.")

    # 3. Final Comparison Table
    st.markdown("##### Full Comparison Leaderboard")
    leaderboard_df = df_oh[['Quarry', '%_ENP', 'Bulk_Rec', 'Cost', 'Overall_Score']].copy()
    leaderboard_df.columns = ['Source', 'ENP (%)', 'Rate (t/ac)', 'Total Cost ($/ac)', 'Value Score']
    sorted_df = leaderboard_df.sort_values(by='Value Score', ascending=False)
        # 2. Use column_config to force decimal formatting
    st.dataframe(
        sorted_df,
        column_config={
            "ENP (%)": st.column_config.NumberColumn(
                "Quality (RNV %)",
                format="%.1f%%",  # Forces 1 decimal place (e.g., 81.0%)
            ),
            "Rate (t/ac)": st.column_config.NumberColumn(
                "Rec. Rate",
                format="%.2f 🚜", # Forces 2 decimal places
            ),
            "Total Cost ($/ac)": st.column_config.NumberColumn(
                "Total Cost",
                format="$ %.2f",  # Forces 2 decimal places (e.g., $ 22.00)
            ),
            "Value Score": st.column_config.NumberColumn(
                "Value Score",
                format="%.3f ⭐", # Forces 3 decimal places (e.g., 1.385 or 1.000)
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