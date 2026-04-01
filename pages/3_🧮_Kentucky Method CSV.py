import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
from st_aggrid import AgGrid
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
import time
import math
import io

# --- Page Config ---
st.set_page_config(page_title="UKY Soil Lime Calculator", layout="centered")

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


# Hide Streamlit Branding
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDownloadButton {text-align: center;}
</style> """, unsafe_allow_html=True)

# --- HELPER: Create Template Data ---
def get_template(mode):
    if mode == "Lab Results (Weight)":
        df_temp = pd.DataFrame({
            "Lime Source": ["Quarry_A", "Quarry_B"], 
            "Initial (g)": [100.0, 100.0], 
            "> #10 (g)": [10.0, 5.0], 
            "< #10": [90.0, 95.0], 
            "< #50 (g)": [60.0, 70.0], 
            "cce": [95.0, 98.0], 
            'wph': [5.8, 5.8], 
            'bph': [6.5, 6.5], 
            'tph': [6.5, 6.5], 
            'price': [25.0, 30.0]
        })
    else:
        df_temp = pd.DataFrame({
            "Lime Source": ["Quarry_A", "Quarry_B"], 
            "> #10 (%)": [10.0, 5.0], 
            "< #10 (%)": [90.0, 95.0], 
            "< #50 (%)": [60.0, 70.0], 
            "cce": [95.0, 98.0], 
            'wph': [5.8, 5.8], 
            'bph': [6.5, 6.5], 
            'tph': [6.5, 6.5], 
            'price': [25.0, 30.0]
        })
    return df_temp.to_csv(index=False).encode('utf-8')

# --- Header ---
st.markdown("<h2 style='background-color: #0033A0; padding: 15px; border-radius: 10px; font-size:30px; text-align: center; color: white;'>Agricultural Lime Quality & Cost Calculator</h2>", unsafe_allow_html=True)
st.write("")
st.write("This method is useful when you have more than 5 samples and when you need to download the analysis")
st.write("")

# --- Step 1: Configuration ---
with st.container(border=True):
    st.markdown("### 🛠️ Step 1: Select Lab Data Format")
    percent_weight = option_menu(
        menu_title=None, 
        options=["Lab Results (Weight)", "Lab Results (Percentage)"], 
        icons=['calculator', 'percent'], 
        default_index=0,
        orientation="horizontal",
        styles={"container": {"padding": "0!important", "background-color": "#f0f2f6"}}
    )
    
    if percent_weight == "Lab Results (Weight)":
        st.caption("📝 **Weight Mode:** Provide raw grams from the sieve analysis.")
    else:
        st.caption("📝 **Percentage Mode:** Provide the calculated percentages passing each sieve.")

# --- Step 2: Template & Upload ---
st.write("")
st.markdown("### 🛠️ Step 2: Use template or upload your csv file")
col_temp, col_up = st.columns([1.2, 1.6], gap="small")

with col_temp:
    with st.container(border=True):
        st.markdown("##### 📄 Need a template?")
        st.write("Ensure your file matches our system.")
        st.download_button(
            label="📥 Download CSV",
            data=get_template(percent_weight),
            file_name="lime_calc_template.csv",
            mime="text/csv",
            use_container_width=True
        )
st.write("**Note**: Files with differnt header names or mispalced columns will result in an error. Please use the template to avoid file errors.You may upload as many samples as you want")
with col_up:
    with st.container(border=True):
        st.markdown("##### 📤 Upload Data")
        uploadfile = st.file_uploader(
            "Select your CSV file", 
            type=["csv"], 
            label_visibility="collapsed"
        )

# --- Processing & Visualization ---
if uploadfile is not None:
    st.divider()
    try:
        with st.status("Calculating Recommendations...", expanded=False) as status:
            df = pd.read_csv(uploadfile)
            
            # 1. Standardization & RNV Logic
            if percent_weight == "Lab Results (Weight)":
                df.columns = ["Quarry", "initial", "gten", "lten", "lfifty", 'cce','wph', 'bph', 'tph','price']
                df["Zero%_eff"] = (df.gten/df.initial)*100
                df['Fifty%_eff'] = ((df.lten-df.lfifty)/df.initial)*100
                df['Hund%_eff'] = (df.lfifty/df.initial)*100
                df["RNV"] = df.cce/100.00*((((df.lten-df.lfifty)/2.0)+df.lfifty)/df.initial)*100
            else:
                df.columns = ["Quarry", "gten", "lten", "lfifty", 'cce', "wph", "bph", 'tph','price']
                df["Zero%_eff"] = df.gten
                df['Fifty%_eff'] = (df.lten-df.lfifty)
                df['Hund%_eff'] = df.lfifty
                df["RNV"] = df.cce/100.00*(((df.lten-df.lfifty)/2.0)+df.lfifty)

            # 2. Sikora-2 Buffer Engine
            SWPH, BPH, TPH = df.wph, df.bph, df.tph
            part1 = -1.1 *(TPH-SWPH)*(BPH-7.55)
            part2 = (BPH -(1.1*SWPH)+1.47)
            # Factor 13.75 for Sikora-2 Calibration
            ELR = (part1/part2) * (13.75/12)
            cffa = ELR.map(lambda x: (3.62 - (0.734*x)) if x <= 3 else 1.42)
            pure_lime = cffa * ELR
            
            df['Bulk_Rec'] = (pure_lime/df.RNV*100).round(1)
            df.loc[df['tph'] <= df['wph'], 'Bulk_Rec'] = 0.0
            df['Cost'] = (df.Bulk_Rec * df.price).round(2)
            status.update(label="Calculations Finished!", state="complete")

        # --- 1. Define the specific columns we want to show (and their order) ---
        # This ignores the "raw" math columns like 'lten', 'lfifty', etc.
        cols_to_show = [
            "Quarry", "Zero%_eff","Fifty%_eff", "Hund%_eff", "wph", "bph", "tph", "cce", "RNV", 
            "Bulk_Rec", "price", "Cost"
        ]

        # --- 2. Define the Professional Mapping ---
        column_mapping = {
            "Quarry"    : "Source / Quarry",
            "Zero%_eff" : "Effective (0%)", 
            "Fifty%_eff": "Effective (50%)",
            "Hund%_eff" : "Effective (100%)",
            "wph"       : "Soil pH",
            "bph"       : "Buffer pH",
            "tph"       : "Target pH",
            "cce"       : "CCE (%)",
            "RNV"       : "RNV (%)",
            "Bulk_Rec"  : "Bulk Lime (t/ac)",
            "price"     : "Unit Price ($/t)",
            "Cost"      : "Total Cost ($/ac)"
        }

        # --- 3. Create the Display Version ---
        st.subheader("📋 Calculated Recommendations")

        # Select only the columns we want, then rename them
        # This prevents "double columns" because we are being explicit
        df_display = df[cols_to_show].copy()
        df_display = df_display.rename(columns=column_mapping)

        # Display in AgGrid
       # AgGrid(df_display.round(2), theme='alpine', columns_auto_size_mode=True)
        # This creates a professional, scrollable, and sortable table
        st.dataframe(
            df_display.round(2), 
            use_container_width=False, # This forces the horizontal scrollbar if columns are wide
            hide_index=True,
            column_config={
                "Source / Quarry": st.column_config.TextColumn(width="medium"),
                "Total Cost ($/ac)": st.column_config.NumberColumn(format="$%.2f"),
                "Bulk Lime (t/ac)": st.column_config.NumberColumn(format="%.1f")
            }
        )

        # --- 4. Download Processed Data ---
        with st.container():
            st.write("")
            processed_csv = df_display.to_csv(index=False).encode('utf-8')

            st.download_button(
                label="💾 Download Professional Report (CSV)",
                data=processed_csv,
                file_name="UKY_Lime_Recommendation.csv",
                mime="text/csv",
                help="Download the results with professional headers for your records.",
                use_container_width=True
            )
            st.write("---")


        # 4. Visualization Setup
        num_rows = len(df)
        eff_h = max(5, 4 + (num_rows - 2) * 0.5)
        others_h = max(4, 2 + (num_rows - 1) * 0.6)
        pallete = "viridis"

        tab1, tab2, tab3 = st.tabs(["📊 **Lime Quality Analysis**", "💰 **Field Rates & Economics**", "🏆 **Best Source Recommendation**"])


        base_height = 1.5  # Minimum height for the "cute" look
        height_per_quarry = 0.5
        dynamic_height = base_height + (len(df) * height_per_quarry)
        width = 0.6

        # --- 1. Find ALL Most Economical (Lowest Cost) ---
        min_cost = df['Cost'].min()
        econ_winners = df[df['Cost'] == min_cost]
        econ_names = " & ".join(econ_winners['Quarry'].tolist())

        # --- 2. Find ALL Highest Quality (Highest RNV) ---
        max_rnv = df['RNV'].max()
        quality_winners = df[df['RNV'] == max_rnv]
        quality_names = " & ".join(quality_winners['Quarry'].tolist())

        # --- 3. Find ALL Best Overall (The Scoring Logic) ---
        cost_range = df['Cost'].max() - df['Cost'].min()
        rnv_range = df['RNV'].max() - df['RNV'].min()
        df['norm_cost'] = (df['Cost'] - df['Cost'].min()) / (cost_range + 1e-9)
        df['norm_rnv'] = (df['RNV'] - df['RNV'].min()) / (rnv_range + 1e-9)
        df['Overall_Score'] = ((1 - df['norm_cost']) + df['norm_rnv']).round(3)

        max_score = df['Overall_Score'].max()
        overall_winners = df[df['Overall_Score'] == max_score]
        overall_names = " & ".join(overall_winners['Quarry'].tolist())
        best_overall = overall_winners.iloc[0] # Representative for stats



        with tab1:
            with st.container(border=True):
                st.markdown("#### Sieve Analysis")
            
                # FIG 1: Fineness Subplots
                fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, dynamic_height * 1.2), sharex=True)
                # Sieve > 10
                sns.barplot(x="Zero%_eff", y='Quarry', data=df, ax=ax1, palette=pallete, width=width)
                for c in ax1.containers: ax1.bar_label(c, fmt="%.1f%%", padding=3)
                ax1.set_title("Fineness Fractions (%)", fontsize=12)
                ax1.set_ylabel("")
                ax1.set_xlabel("")
                ax1.set_xticklabels([])
                ax1.set_xticks([])
                ax1.text(1.02, 0.5, "> #10 Sieve", transform=ax1.transAxes, rotation=270, va='center')

                # Sieve 10-50
                sns.barplot(x="Fifty%_eff", y='Quarry', data=df, ax=ax2, palette=pallete, width=width)
                for c in ax2.containers: ax2.bar_label(c, fmt="%.1f%%", padding=3)
                ax2.set_ylabel("")
                ax2.set_xlabel("")
                ax2.set_xticklabels([])
                ax2.set_xticks([])
                ax2.text(1.02, 0.5, "#10-#50 Sieve", transform=ax2.transAxes, rotation=270, va='center')

                # Pass 50
                sns.barplot(x="Hund%_eff", y='Quarry', data=df, ax=ax3, palette=pallete, width=width)
                for c in ax3.containers: ax3.bar_label(c, fmt="%.1f%%", padding=3)
                ax3.set_ylabel("")
                ax3.set_xlabel("Percent of Total Weight")
                ax3.text(1.02, 0.5, "Pass #50", transform=ax3.transAxes, rotation=270, va='center')
                ax3.set_xlim(0, 120)
                ax3.set_xticklabels([])
                ax3.set_xticks([])
                st.pyplot(fig)
                plt.tight_layout(pad=0.5)

            # FIG 2: RNV Plot
            with st.container(border=True):
                st.markdown("#### Relative Neutralizing Value (RNV, %)")
                fig_rnv, ax_rnv = plt.subplots(figsize=(8, dynamic_height * 0.45), sharex=True)
                sns.barplot(x='RNV', y='Quarry', data=df, ax=ax_rnv, palette=pallete, width=width)
                for c in ax_rnv.containers: ax_rnv.bar_label(c, fmt="%.1f%%", padding=3)
                #ax_rnv.set_title("Relative Neutralizing Value (RNV %)", fontsize=12)
                ax_rnv.set_xlim(0, 120)
                ax_rnv.set_ylabel("")
                ax_rnv.set_xticklabels([])
                ax_rnv.set_xticks([])
                ax_rnv.set_xlabel("")
                st.pyplot(fig_rnv)
                plt.tight_layout(pad=0.5)

        with tab2:
            # st.markdown("<h4 style='text-align: center; color: #0033A0;'>Recommendation Breakdown</h4>", unsafe_allow_html=True)
            
            # Recommendation Bars
            with st.container(border=True):
                st.markdown("#### Adjusted Bulk Lime Rate (t/ac)")
                fig_rec, ax_rec = plt.subplots(figsize=(8, dynamic_height * 0.45), sharex=True)
                sns.barplot(x='Bulk_Rec', y='Quarry', data=df, ax=ax_rec, palette=pallete, width=width)
                for c in ax_rec.containers: ax_rec.bar_label(c, padding=3)
                # ax_rec.set_title("Adjusted Bulk Lime (Tons/Acre)", fontsize=12)
                ax_rec.set_xlim(0, df.Bulk_Rec.max() * 1.3)
                ax_rec.set_ylabel("")
                ax_rec.set_xticklabels([])
                ax_rec.set_xticks([])
                ax_rec.set_xlabel("")
                st.pyplot(fig_rec)

            # Cost Bars
            with st.container(border=True):
                st.markdown("#### Total Application Cost ($/ac)")
                fig_cost, ax_cost = plt.subplots(figsize=(8, dynamic_height * 0.45), sharex=True)
                sns.barplot(x='Cost', y='Quarry', data=df, ax=ax_cost, palette=pallete, width=width)
                for c in ax_cost.containers: ax_cost.bar_label(c, fmt="$%.2f", padding=3)
                # ax_cost.set_title("Total Cost ($/Acre)", fontsize=12)
                ax_cost.set_xlim(0, df.Cost.max() * 1.3)
                ax_cost.set_ylabel("")
                ax_cost.set_xticklabels([])
                ax_cost.set_xticks([])
                ax_cost.set_xlabel("")
                st.pyplot(fig_cost)

            # Management Note Section
            with st.container(border=True):
                st.markdown("#### 🚜 Management Note")
                st.info(f"The amount of lime required to raise the soil pH of **{df.wph.iloc[0]}** to a target pH of **{df.tph.iloc[0]}**.")
                st.info("""
                        **Recommendation:** You may round your bulk lime application rates to the nearest 
                        **half-ton (0.5)** or **whole ton** based on the calibration limits of your spreading equipment.""")

        with tab3:
            st.markdown("<h3 style='text-align: center; color: #0033A0;'>🏆 Lime Source Awards</h3>", unsafe_allow_html=True)
            st.write("")

            col1, col2, col3 = st.columns(3)

            # CARD 1: Most Economical
            with col1:
                with st.container(border=True):
                    econ_title = "💸 MOST ECONOMICAL" if len(econ_winners) == 1 else "💸 ECONOMY TIE"
                    st.markdown(f"##### {econ_title}")
                    st.metric("Lowest Cost", f"${min_cost:.2f}/ac")
                    st.success(f"**{econ_names}**")
                    st.caption("Best for tight budgets.")

            # CARD 2: Best Overall (The Balanced Pick)
            with col2:
                overall_title = "⭐ BEST OVERALL" if len(overall_winners) == 1 else "👯 OVERALL TIE"
                st.markdown(f"""
                    <div style="border: 2px solid #FFD700; border-radius: 10px; padding: 10px; background-color: #FFFDF0; text-align: center; min-height: 150px;">
                        <h4 style="margin: 0; color: #B8860B;">{overall_title}</h4>
                        <p style="font-size: 18px; font-weight: bold; margin: 10px 0;">{overall_names}</p>
                        <p style="font-size: 13px; color: #555;">Best Balance of RNV & Cost</p>
                    </div>
                """, unsafe_allow_html=True)

            # CARD 3: Highest Quality
            with col3:
                with st.container(border=True):
                    qual_title = "💎 HIGHEST QUALITY" if len(quality_winners) == 1 else "💎 QUALITY TIE"
                    st.markdown(f"##### {qual_title}")
                    st.metric("Top RNV", f"{max_rnv:.1f}%")
                    st.info(f"**{quality_names}**")
                    st.caption("Best for high-efficiency.")

            st.write("---")
        
            # 1. Management Info (Keep it, but keep it tight)
            with st.container(border=True):
                st.markdown("#### 🚜 Management Recommendation")
                display_name = "the Selected Winners" if len(overall_winners) > 1 else best_overall['Quarry']
                st.info(f"Based on your soil test (pH {best_overall['wph']} → {best_overall['tph']}), **{display_name}** represents the best overall value. High-quality lime reacts faster and requires fewer total tons to be hauled and spread.")

            # 2. "Hide and See" Calculation Logic (The Expander)
            with st.expander("🔬 How were these winners calculated?"):
                st.markdown("""
                **The scoring system uses a Multi-Criteria Decision Analysis (MCDA):**
                1. **Normalization:** Both **Total Cost** and **RNV** are scaled from 0 to 1 across all sources.
                2. **Inversion:** Cost is inverted so that a lower cost equals a higher score.
                3. **Weighting:** We apply a 50/50 weight to both Quality (RNV) and Economy (Cost).
                4. **Scoring:** """)
                st.latex(r"Score = (1 - \text{Normalized Cost}) + \text{Normalized RNV}")
                st.write("Sources with the highest total score are awarded the **Best Overall** title. If scores are within 0.001 of each other, a tie is declared.")

            # 3. Final Comparison Table
            st.markdown("##### Full Comparison Leaderboard")
            leaderboard_df = df[['Quarry', 'RNV', 'Bulk_Rec', 'Cost', 'Overall_Score']].copy()
            leaderboard_df.columns = ['Source', 'RNV (%)', 'Rate (t/ac)', 'Total Cost ($/ac)', 'Value Score']
            st.dataframe(leaderboard_df.sort_values(by='Value Score', ascending=False), hide_index=True, use_container_width=True)        
    except Exception as e:
        st.error(f"⚠️ **File Compatibility Error:** {e}")
        st.warning("Please ensure your CSV exactly matches the column order shown in the downloadable template.")