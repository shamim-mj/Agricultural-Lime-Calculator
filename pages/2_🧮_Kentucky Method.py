import pandas as pd
import math
import time
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu

# --- Page Config ---
st.set_page_config(page_title="Lime & Soil Data", layout="centered")

# Custom CSS for styling
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .main-header {
        background-color: #0033A0; 
        color: white !important;
        text-align: center; 
        padding: 10px; 
        border-radius: 5px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 class='main-header'>Lime and Soil Data</h2>", unsafe_allow_html=True)

st.markdown("""
    <style>
    /* Responsive Padding for Mobile */
    @media (max-width: 640px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 2rem;
        }
        h2 { font-size: 24px !important; }
    }

    /* Make the Number Input boxes easier to tap with thumbs */
    div[data-baseweb="input"] {
        min-height: 45px;
    }

    /* Style the sidebar to look cleaner on mobile */
    section[data-testid="stSidebar"] {
        background-color: #f0f2f6;
    }
    </style>
""", unsafe_allow_html=True)



# --- Selection Menu ---
percent_weight = option_menu(None, ["Lab Results (Weight)", "Lab Results (Percentage)"], 
    icons=[], menu_icon="cast", default_index=0, orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#ffe6e6"},
        "nav-link-selected": {"background-color": "#0033A0"}})

# --- Lime Data Input ---
st.markdown("<h4 class='main-header'>Lime Data</h4>", unsafe_allow_html=True)
ncol = st.number_input("Number of Samples", 1, 5, 1)
cols = st.columns(ncol)


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

# not used
def ag_round(x):
    if x <= 0: return 0
    
    whole = math.floor(x)
    decimal = x - whole
    
    if decimal <= 0.2:
        return float(whole)
    elif decimal <= 0.5:
        return whole + 0.5
    else:
        return float(whole + 1)




data_list = []
for i in range(ncol):
    with cols[i]:
        st.write(f"**Sample {i+1}**")
        name = st.text_input('Source Name', value=f'Sample {i+1}', key=f"q_{i}_n")
        
        if percent_weight == "Lab Results (Weight)":
            init = st.number_input('Initial (g)', value=100.0, key=f"q_{i}_i", format="%.2f")
            g10 = st.number_input('> #10 (g)', value=10.0, key=f"q_{i}_10", format="%.2f")
            l50 = st.number_input('< #50 (g)', value=60.0, key=f"q_{i}_50", format="%.2f")
            l10 = init - g10
        else:
            init = 100.0
            g10 = st.number_input('% > #10', value=10.0, key=f"q_{i}_10p", format="%.2f")
            l50 = st.number_input('% < #50', value=60.0, key=f"q_{i}_50p", format="%.2f")
            l10 = 100.0 - g10

        cce = st.number_input("CCE (%)", value=90.0, key=f'cce{i}', format="%.2f")
        price = st.number_input("Price ($/t)", value=20.0, key=f'p{i}', format="%.2f")
        
        data_list.append({
            "Quarry": name, "initial": init, "gten": g10, "lten": l10, "lfifty": l50, "cce": cce, "price": price
        })

df = pd.DataFrame(data_list)

# --- Soil Data Input ---
st.markdown("<h4 class='main-header'>Soil Data</h4>", unsafe_allow_html=True)
sc1, sc2, sc3 = st.columns(3)
wph = sc1.slider('Soil Water pH', 4.0, 8.0, 5.9, 0.1)
bph = sc2.slider('Buffer pH', 4.0, 8.0, 6.8, 0.1)
tph = sc3.slider('Target pH', 4.0, 8.0, 6.4, 0.1)

# --- Calculations ---
df["Zero%_eff"] = (df.gten / df.initial) * 100
df['Fifty%_eff'] = ((df.lten - df.lfifty) / df.initial) * 100
df['Hund%_eff'] = (df.lfifty / df.initial) * 100
df["RNV"] = (df.cce / 100.0) * ((((df.lten - df.lfifty) / 2.0) + df.lfifty) / df.initial) * 100
df['wph'] = wph
df['bph'] = bph
df['tph'] = tph
ELR = -1.1 * (tph - wph) * (bph - 7.55) / ((bph - (1.1 * wph) + 1.47)) * (13.75 / 12)
cffa = [(3.62 - (0.734 * ELR)) if ELR <= 3 else 1.42][0]
pure_lime = cffa * ELR
df['Bulk_Rec'] = pure_lime / df.RNV * 100 if tph > wph else df.RNV * 0
df['Bulk_Rec'] = df['Bulk_Rec'].round(1)
df['Cost'] = df.Bulk_Rec * df.price
st.session_state['df'] = df # this is used in downnloads


# --- Manual Labeling Function (Fail-Safe) ---
def add_labels(ax, fmt="%.2f"):
    """Manually iterates through patches to add labels at the end of bars."""
    for p in ax.patches:
        width = p.get_width()
        if width >= 0: # Ensure we don't label empty data
            ax.text(width + (ax.get_xlim()[1] * 0.02), # X position (width + 2% offset)
                    p.get_y() + p.get_height() / 2,    # Y position (center of bar)
                    fmt % width, 
                    ha='left', va='center', fontsize=10, fontweight='bold')

# --- Visualization ---
# check if pallete is in session_sate.
if "pallete" not in st.session_state:
    pallete = "Dark2"
else:
    pallete = st.session_state['pallete']


# ---------------------------------------------------------------------------------------------------------

# Use this when a calculation or upload starts
with st.status("Analyzing Soil Data...", expanded=True) as status:
    st.write("Applying Sikora-2 Buffer Method...")
    time.sleep(0.5) # Simulating math
    st.write("Calculating Relative Neutralizing Value (RNV)...")
    status.update(label="Analysis Complete!", state="complete", expanded=False)


tab1, tab2, tab3 = st.tabs(["**Lime Quality**", "**Amount & Cost**", "**Summary Results**"])

# --- 1. SET A BASE HEIGHT LOGIC ---
# This ensures 1 sample doesn't look "chunky" and 20 samples don't look "cramped"
base_height = 1.5  # Minimum height for the "cute" look
height_per_quarry = 0.5
dynamic_height = base_height + (len(df) * height_per_quarry)


#------------------------------------------------

base_height = 1.5  # Minimum height for the "cute" look
height_per_quarry = 0.5
dynamic_height = base_height + (len(df) * height_per_quarry)
width = 0.6

# --- 1. Find ALL Most Economical (Lowest Cost) ---
df['Cost_Per_Ton'] = df['Cost'] / df['Bulk_Rec']
min_cost = df['Cost_Per_Ton'].min()
econ_winners = df[df['Cost_Per_Ton'] == min_cost]
econ_names = " & ".join(econ_winners['Quarry'].tolist())

# --- 2. Find ALL Highest Quality (Highest RNV) ---
max_rnv = df['RNV'].max()
quality_winners = df[df['RNV'] == max_rnv]
quality_names = " & ".join(quality_winners['Quarry'].tolist())

# --- 3. THE WEIGHTED BEST OVERALL LOGIC ---
cost_range = df['Cost'].max() - df['Cost'].min()
rnv_range = df['RNV'].max() - df['RNV'].min()

# Normalization (handles cases where all costs or RNVs are the same)
df['norm_cost'] = (df['Cost'] - df['Cost'].min()) / (cost_range + 1e-9)
df['norm_rnv'] = (df['RNV'] - df['RNV'].min()) / (rnv_range + 1e-9)

# WEIGHTED SCORE: 70% Cost, 30% Quality
# (1 - norm_cost) because lower cost is better
df['Overall_Score'] = (0.9 * (1 - df['norm_cost'])) + (0.1 * df['norm_rnv'])
df['Overall_Score'] = df['Overall_Score'].round(3)

# Find the Winner based on the new weighted score
max_score = df['Overall_Score'].max()
overall_winners = df[df['Overall_Score'] == max_score]
overall_names = " & ".join(overall_winners['Quarry'].tolist())
best_overall = overall_winners.iloc[0]



with tab1:
    with st.container(border=True):
        st.markdown("### Particle Size")
        # Adjust figsize to be dynamic based on row count
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, dynamic_height * 1.2), sharex=True)
        metrics = [("Zero%_eff", ax1, "#10 Sieve"), ("Fifty%_eff", ax2, "#50 Sieve"), ("Hund%_eff", ax3, "<#50 Sieve")]
        
        for col, ax, label in metrics:
            # Set 'width' to 0.4 or 0.5 to keep bars slim even if there is only 1 row
            sns.barplot(data=df, x=col, y='Quarry', ax=ax, palette=pallete, width=0.4)
            ax.set_xlim(0, 120)
            ax.set_ylabel("")
            ax.set_xlabel("")
            ax.set_xticks([])
            ax.set_title(label, loc='center', fontsize=10)
            add_labels(ax)
        
        plt.tight_layout(pad=1.0)
        st.pyplot(fig)
        plt.close()

    with st.container(border=True):
        st.markdown("### Relative Neutralizing Value (RNV, %)")
        # Apply the same dynamic height and width here
        fig2, ax4 = plt.subplots(figsize=(8, dynamic_height * 0.5))
        sns.barplot(data=df, x='RNV', y='Quarry', ax=ax4, palette=pallete, width=0.4)
        ax4.set_xlim(0, 120)
        ax4.set_ylabel("")
        ax4.set_xticks([])
        ax4.set_xlabel("")
        add_labels(ax4)
        st.pyplot(fig2)
        plt.close()


with tab2:
    # --- Apply the same pattern to Recommendation and Cost plots ---
    with st.container(border=True):
        st.markdown("### Lime Amount")
        fig3, ax5 = plt.subplots(figsize=(8, dynamic_height * 0.5))
        sns.barplot(data=df, x='Bulk_Rec', y='Quarry', ax=ax5, palette=pallete, width=0.4)
        ax5.set_xlim(0, (df['Bulk_Rec'].max() * 1.3) if not df.empty else 10)
        ax5.set_ylabel("")
        ax5.set_xticks([])
        add_labels(ax5)
        st.pyplot(fig3)
        plt.close()

    with st.container(border=True):
        st.markdown("### Total Cost ($/ac)")
        fig4, ax6 = plt.subplots(figsize=(8, dynamic_height * 0.5))
        sns.barplot(data=df, x='Cost', y='Quarry', ax=ax6, palette=pallete, width=0.4)
        ax6.set_xlim(0, (df['Cost'].max() * 1.3) if not df.empty else 10)
        ax6.set_ylabel("")
        ax6.set_xticks([])
        add_labels(ax6)
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
        leaderboard_df = df[['Quarry', 'RNV', 'Bulk_Rec', 'Cost', 'Overall_Score']].copy()
        leaderboard_df.columns = ['Source', 'RNV (%)', 'Rate (t/ac)', 'Total Cost ($/ac)', 'Value Score']
        sorted_df = leaderboard_df.sort_values(by='Value Score', ascending=False)
        # 2. Use column_config to force decimal formatting
        st.dataframe(
            sorted_df,
            column_config={
                "RNV (%)": st.column_config.NumberColumn(
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