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
        color: white; 
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
        "nav-link-selected": {"background-color": "#ff0000"},
    }
)

# --- Lime Data Input ---
st.markdown("<h4 class='main-header'>Lime Data</h4>", unsafe_allow_html=True)
ncol = st.number_input("Number of Samples", 1, 5, 1)
cols = st.columns(ncol)


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

ELR = ((-1.1 * (tph - wph) * (bph - 7.55)) / (bph - (1.1 * wph) + 1.47)) * (13.75 / 12)
cffa = 3.62 - (0.734 * ELR) if ELR <= 3 else 1.42
pure_lime = cffa * ELR
df['Bulk_Rec'] = (pure_lime / df.RNV * 100) if (tph > wph and not df.empty) else 0
df['Bulk_Rec'] = df['Bulk_Rec'].apply(math.ceil)
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

with tab1:
   # st.markdown("<h4 style='text-align: center;'>Particle Size & RNV</h4>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("### Particle Size")
        # 1. Fineness Triple Plot
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 5 + len(df)*0.2), sharex=True)
        metrics = [("Zero%_eff", ax1, "#10 Sieve"), ("Fifty%_eff", ax2, "#50 Sieve"), ("Hund%_eff", ax3, "<#50 Sieve")]
        
        for col, ax, label in metrics:
            sns.barplot(data=df, x=col, y='Quarry', ax=ax, palette=pallete)
            ax.set_xlim(0, 120) # Plenty of room for text
            ax.set_ylabel("")
            ax.set_xlabel("")
            ax.set_xticks([])
            ax.set_xticklabels([])
            ax.set_title(label, loc='center', fontsize=10)
            add_labels(ax)
        
        plt.tight_layout(pad=0.1)
        st.pyplot(fig)
        plt.close()
    
    with st.container(border=True):
        st.markdown("### Relative Neutralizing Value (RNV, %)")
        # 2. RNV Plot
        fig2, ax4 = plt.subplots(figsize=(8, 2 + len(df)*0.2))
        sns.barplot(data=df, x='RNV', y='Quarry', ax=ax4, palette=pallete)
       # ax4.set_title("Relative Neutralizing Value (RNV %)", pad=15)
        ax4.set_xlim(0, 120)
        ax4.set_ylabel("")
        ax4.set_xticks([])
        ax4.set_xticklabels([])
        ax4.set_xlabel("")
        add_labels(ax4)
        st.pyplot(fig2)
        plt.close()

with tab2:
    st.markdown("<h4 style='text-align: center;'>Recommendations</h4>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("### Lime Amount")
        # Rec Plot
        fig3, ax5 = plt.subplots(figsize=(8, 2 + len(df)*0.2))
        sns.barplot(data=df, x='Bulk_Rec', y='Quarry', ax=ax5, palette=pallete)
        ax5.set_title(f"Adjusted lime amount (t/ac) required to raise \nsoil pH of {wph} to a target pH of {tph}", pad=15)
        ax5.set_xlim(0, (df['Bulk_Rec'].max() * 1.3) if not df.empty else 10)
        ax5.set_ylabel("")
        ax5.set_xticks([])
        ax5.set_xticklabels([])
        ax5.set_xlabel("")
        add_labels(ax5)
        st.pyplot(fig3)
        plt.close()
    with st.container(border=True):
        st.markdown("### Total Lime and Application Cost (t/ac)")
    # Cost Plot
        fig4, ax6 = plt.subplots(figsize=(8, 2 + len(df)*0.2))
        sns.barplot(data=df, x='Cost', y='Quarry', ax=ax6, palette=pallete)
        #ax6.set_title("Total lime and applicaiton cost ($/ac)", pad=15)
        ax6.set_xlim(0, (df['Cost'].max() * 1.3) if not df.empty else 10)
        ax6.set_ylabel("")
        ax6.set_xticks([])
        ax6.set_xticklabels([])
        ax6.set_xlabel("")
        add_labels(ax6)
        st.pyplot(fig4)
        plt.close()


    #-----------------------------------------------------------------------------------
with tab3:
    if not df.empty:
        # 1. Calculation Logic: Sort by Cost (Low to High), then RNV (High to Low)
        # This ensures that if costs are equal, the higher quality wins.
        df_sorted = df.sort_values(by=['Cost', 'RNV'], ascending=[True, False])
        
        # The first row is now our "Best Pick"
        best_value = df_sorted.iloc[0]
        
        # 2. The Header Container (Metrics)
        with st.container(border=True):
            st.markdown("### 🏆 Top Performance Summary")
            m1, m2, m3 = st.columns(3)
            
            m1.metric("Top Value Source", best_value["Quarry"], 
                    help="Lowest cost per acre. If costs match, highest RNV is chosen.")
            m2.metric("Application Rate (t/ac)", f"{df['Bulk_Rec'].min():.1f} t/a", "Efficiency")
            m3.metric("RNV Quality (%)", f"{df['RNV'].max():.1f}%", "RNV")

        st.markdown("### 📊 Detailed Comparison")
        
        # 3. The Styled Table
        # I corrected the key from "ENV" to "RNV" to match your dataframe slice
        st.dataframe(
            df[['Quarry', 'RNV', 'Bulk_Rec', 'Cost']],
            column_config={
                "Quarry": st.column_config.TextColumn("Lime Source", width="medium"),
                "RNV": st.column_config.ProgressColumn(
                    "Quality (RNV %)",
                    help="Relative Neutralizing Value",
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