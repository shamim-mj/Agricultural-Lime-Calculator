import streamlit as st
from pathlib import Path
import os

# --- 1. PAGE CONFIGURATION ---


st.set_page_config(
    page_title="AgLime Decision Support",
    page_icon="🚜",
    layout="centered",
    initial_sidebar_state="expanded" # This ensures it starts OPEN
)


st.markdown("""
    <style>
    /* 1. Ensure the 'Open Sidebar' button is ALWAYS visible and colored */
    [data-testid="collapsedControl"] {
        visibility: visible !important;
        display: flex !important;
        background-color: #0033A0 !important; /* Matches your Kentucky Blue */
        border-radius: 0 10px 10px 0 !important;
        width: 40px !important;
        height: 40px !important;
        top: 60px !important; /* Moves it down so it's not at the very top edge */
        left: 0 !important;
        z-index: 999999 !important; /* Puts it on top of everything else */
    }

    /* 2. Make the arrow icon inside it white so you can see it */
    [data-testid="collapsedControl"] svg {
        fill: white !important;
        width: 25px !important;
        height: 25px !important;
    }

    /* 3. Safety: If you have 'header {visibility: hidden;}' anywhere, 
       this line ensures the sidebar button is EXEMPT from that rule */
    header[data-testid="stHeader"] {
        visibility: visible !important;
        background: transparent !important;
    }
    </style>
""", unsafe_allow_html=True)



# --- 2. ADVANCED UI CSS ---
st.markdown("""
    <style>
    /* Global Background */
    .stApp {
        background-color: #f0f2f6;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Hero Header Styling */
    .hero-box {
        background: linear-gradient(135deg, #0033A0 0%, #002270 100%);
        padding: 45px 25px;
        border-radius: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,51,160,0.2);
        margin-bottom: 30px;
    }
    .hero-box h1 {
        font-size: 3.5rem !important;
        font-weight: 900 !important;
        margin-bottom: 5px !important;
        color: white !important;
        letter-spacing: -1px;
    }
    .precision-tag {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 3px;
        font-weight: 300;
        opacity: 0.8;
        margin-bottom: 20px;
        display: block;
    }
    .tech-terminology {
        font-size: 1.1rem;
        font-weight: 400;
        opacity: 0.95;
        border-top: 1px solid rgba(255,255,255,0.2);
        padding-top: 15px;
        margin-top: 15px;
    }
    
    /* Content Cards */
    .disclaimer-text {
        font-size: 0.95rem;
        color: #333;
        line-height: 1.7;
    }
    
    .section-label {
        color: #0033A0;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-size: 0.8rem;
        margin-bottom: 12px;
        display: block;
    }

    /* Links */
    a { text-decoration: none; color: #0033A0; font-weight: 700; }
    a:hover { text-decoration: underline; }

    /* Modernizing Font */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    </style>
""", unsafe_allow_html=True)

# --- 3. BOLD BLUE HERO SECTION ---
st.markdown("""
    <div class="hero-box">
        <span class="precision-tag">Precision Agronomy</span>
        <h1>Lime Calculator</h1>
        <div class="tech-terminology">
            Particle Analysis • CCE • RNV • pH • Buffer pH • Application Rate • Applicaiton Cost
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 4. IMAGE SECTION ---
current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
path_sieve = current_dir / "Sieves1.jpg"
path_lime = current_dir / "Lime particles .jpg"

col1, col2 = st.columns(2)
with col1:
    if path_sieve.exists():
        st.image(str(path_sieve), caption="Sieve Analysis", use_column_width=True)
with col2:
    if path_lime.exists():
        st.image(str(path_lime), caption="Particle Distribution", use_column_width=True)
st.caption("📷 Photo Credit: Robbie Williams")

# --- 5. MAIN CONTENT & CREDITS ---
with st.container(border=True):
    st.markdown('<span class="section-label">Disclaimer & Development</span>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="disclaimer-text">
        All rights reserved.<br>  <span style="color:#d32f2f; font-weight:bold;">Disclaimer:</span> 
        This open source web application was developed by 
        <a href='https://www.linkedin.com/in/mohammad-jan-shamim-693136112/'>Mohammad Shamim</a> 
        and <b>Robbie Williams</b> in Henderson, Kentucky, USA. 
        It comes with absolutely no warranty and the authors accept no liability. 
        You are welcome to distribute it for scientific uses following the authors' consent.
    </div>
    """, unsafe_allow_html=True)

st.write("") 

with st.container(border=True):
    st.markdown("""
    <div class="disclaimer-text">
    You can perform calculations either by manually inserting values (up to 5 sources) 
    or by uploading a <b>CSV file</b> for unlimited calculations. Choose your favorite 
    visual style from over 100 color palettes in the Settings menu.
    <br><br>
    This app utilizes the <b>Sikor-2 Buffer method</b> for Kentucky analysis and the 
    <b>Ohio State adopted method</b> for Ohio-specific calculations.
    <br><br>
    <small><i>Note: Please select your preferred color palette in Settings before entering data. Toggling between menus loses unsaved information.</i></small>
    </div>
    """, unsafe_allow_html=True)

# Acknowledgements
st.markdown('<br><span class="section-label">Acknowledgement</span>', unsafe_allow_html=True)
with st.container(border=True):
    st.write("We are greatly indebted to **Dr. Frank Sikora** (Regulatory Services, University of Kentucky) for his invaluable technical input.")

# --- 6. RESOURCES & FOOTER ---
st.markdown("---")
res1, res2 = st.columns(2)
with res1:
    st.markdown("🔗 [Ag Lime Recommendations (ID-163)](http://www2.ca.uky.edu/agcomm/pubs/id/id163/id163.pdf)")
with res2:
    st.markdown("🔗 [UKY Rock Quarry Reports](https://www.rs.uky.edu/soil/technical_info/)")

st.markdown("<br>", unsafe_allow_html=True)
st.link_button("📥 Download Excel Version of the Calculator", 
               "https://github.com/shamim-mj/Aglime_Calculator_in_Excel.git", 
               use_container_width=True)