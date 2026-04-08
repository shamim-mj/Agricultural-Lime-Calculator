import streamlit as st
import numpy as np
import math


# --- Page Config ---
st.set_page_config(page_title="Ohio Method - Lime Data", layout="centered")


st.markdown("""
<style>
.result-card {
    background-color: #f8f9fb;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #e6e9ef;
    box-shadow: 0 4px 10px rgba(0,0,0,0.04);
    text-align: center;
}

.result-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #0033A0;
    margin-bottom: 12px;
}

.big-metric {
    font-size: 2.2rem;
    font-weight: 800;
    color: #1b5e20;
    margin: 8px 0;
}

.sub-metric {
    font-size: 1.05rem;
    color: #444;
    margin-top: 6px;
}

.cost-metric {
    font-size: 1.15rem;
    font-weight: 600;
    color: #4a148c;
    margin-top: 12px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    /* This targets the container with border=True */
    div[data-testid="stVerticalBlockBorderPrerender"] {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0 !important;
        border-radius: 15px !important;
        padding: 20px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    /* Style the subheaders inside the cards */
    .card-header {
        color: #666;
        font-size: 1rem;
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: 15px;
        border-bottom: 2px solid #FFD700;
        padding-bottom: 10px;
        text-align: center;
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

st.markdown(
    "<h2 class='main-header'>Explore Lime Recommendation Methods</h2>",
    unsafe_allow_html=True
)

st.subheader("Target pH and Lime Inputs")
c1, c2, c3 = st.columns(3)

with c1:
    TPH = st.slider("Target pH",  min_value=5.0, max_value=8.0, value=6.5, step=0.05, key="tph")
with c2:
    lime_price = st.slider("Lime Price ($/ton)",  min_value=5.0, max_value=60.0, value=25.0, step=0.05, key="price_m3")
with c3: 
    ECCE = st.slider("ECCE (%)", 40.0, 100.0, 90.0, step=0.05, key="ecce_m3") / 100.0


st.subheader("Method-Specific Inputs")

m1, m2, m3 = st.columns(3)

# --- MEHLICH III ---
with m1:
    with st.container(border=True):
        st.markdown('<p class="card-header">Mehlich III</p>', unsafe_allow_html=True)
        SPH_m3 = st.slider("Soil pH", 4.5, 9.0, 5.8, 0.05, key="sph_m3")
        BPH_m3 = st.slider("Buffer pH", 4.5, 9.0, 6.85, 0.05, key="m3_bph")
        
        # 1. Calculate AC, but cap it at 0 minimum
        # If Buffer pH is > 6.6, AC should be 0
        raw_ac = (6.6 - BPH_m3) / 0.25
        AC = max(0, raw_ac)
        
        # 2. Calculate Base Lime Requirement
        # Using max(0, ...) here prevents negative results if Soil pH > Target pH
        if (6.6 - SPH_m3) != 0:
            LR_m = AC * (max(0, TPH - SPH_m3) / (6.6 - SPH_m3))
        else:
            LR_m = 0
            
        # 3. Apply adjustments
        LR_ad_me = (LR_m / 0.9) / ECCE if LR_m > 0 else 0
        total_cost_m = LR_ad_me * lime_price

# --- ADAM EVANS ---
with m2:
    with st.container(border=True):
        st.markdown('<p class="card-header">Adam Evans</p>', unsafe_allow_html=True)
        SPH_a = st.slider("Soil pH", 4.5, 9.0, 6.0, 0.05, key="sph_a")
        BPH_ae = st.slider("Buffer pH", 4.5, 9.0, 6.5, 0.05, key="bph_a")
        Depth_raw = st.slider("Sample Depth (in)", 6, 8, 6, 2, key="depth_a")
        
        Depth = 0.90 if Depth_raw == 6 else 1.18
        
        def calculate_hsat(val):
            return (5.55 - math.sqrt(max(0, (5.55**2) - 4 * 2.27 * (7.79 - val)))) / (2 * 2.27)
        
        Hsat1 = calculate_hsat(BPH_ae)
        Hsat2 = calculate_hsat(TPH)
        LR_ae = ((8000 * (8.0 - BPH_ae)) / Hsat1 * (Hsat1 - Hsat2) * (1/ECCE) * Depth) / 2000
        LR_ad = (LR_ae / 0.67) * ECCE if LR_ae > 0 else 0
        total_cost = LR_ad * lime_price

# --- SIKORA SMP ---
with m3:
    with st.container(border=True):
        st.markdown('<p class="card-header">Sikora SMP</p>', unsafe_allow_html=True)
        SPH_s = st.slider("Soil pH", 4.5, 9.0, 6.0, 0.05, key="sph_s")
        BPH_s = st.slider("Buffer pH", 4.5, 9.0, 6.5, 0.05, key="bph_s")
        RNV = st.slider("RNV (%)", 20.0, 100.0, 67.5, 0.05, key="rnv_s")
        
        # Using 11.8 for the 10cc scoop adjustment as per your code
        ELR = -1.1 * (TPH - SPH_s) * (BPH_s - 7.55) / ((BPH_s - (1.1 * SPH_s) + 1.47)) * (13.75/11.8)
        cffa = (3.62 - (0.734 * ELR)) if ELR <= 3 else 1.42
        LR_lab = cffa * ELR
        LR_ad_s = (LR_lab / RNV * 100) if TPH > SPH_s else 0
        total_cost_s = LR_ad_s * lime_price




st.info("**NOTE:** You can calculate %RNV from the Kentucky Method Tab.")
st.info("Effective Calcium Carbonate Equivalent (ECCE) values could be retrieved from the seller")
# --- Header ---
st.markdown("---")
st.markdown("""
    <h2 style="text-align:center; color: #333; margin-bottom: 30px; font-family: sans-serif;">
        Adjusted Lime Requirement & Cost
    </h2>
""", unsafe_allow_html=True)

# Helper function to generate the card HTML to keep code clean
def create_card(title, base, adjusted, cost):
    # Using a single string to avoid parsing errors
    html_code = f"""
    <div style="border:1px solid #E0E0E0; border-radius:15px; padding:20px; background-color:#FFFFFF; text-align:center; box-shadow: 0 4px 6px rgba(0,0,0,0.05); font-family:sans-serif;">
        <div style="color:#666; font-size:1rem; font-weight:bold; text-transform:uppercase; margin-bottom:15px; border-bottom:2px solid #FFD700; padding-bottom:10px;">
            {title}
        </div>
        <div style="margin-bottom:10px;">
            <p style="margin:0; color:#888; font-size:0.8rem;">Base Rate</p>
            <p style="margin:0; color:#222; font-size:1.1rem; font-weight:bold;">{base:.2f} t/ac</p>
        </div>
        <div style="margin-bottom:15px;">
            <p style="margin:0; color:#888; font-size:0.8rem;">Adjusted Rate</p>
            <p style="margin:0; color:#222; font-size:1.1rem; font-weight:bold;">{adjusted:.2f} t/ac</p>
        </div>
        <div style="background-color:#F9F9F9; padding:10px; border-radius:8px;">
            <p style="margin:0; color:#888; font-size:0.8rem;">Estimated Cost</p>
            <p style="margin:0; color:#B22222; font-size:1.2rem; font-weight:bold;">${cost:.2f}</p>
        </div>
    </div>
    """
    return html_code

r1, r2, r3 = st.columns(3)

with r1:
    st.markdown(create_card("Mehlich III", LR_m, LR_ad_me, total_cost_m), unsafe_allow_html=True)

with r2:
    st.markdown(create_card("Adam Evans", LR_ae, LR_ad, total_cost), unsafe_allow_html=True)

with r3:
    st.markdown(create_card("Sikora SMP", LR_lab, LR_ad_s, total_cost_s), unsafe_allow_html=True)