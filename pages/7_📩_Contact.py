import streamlit as st

# --- PAGE STYLING ---
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
            """
            
            , unsafe_allow_html=True)

# --- CENTERED LAYOUT ---
# Using columns to create a "narrow" centered column for a professional look
_, center_col, _ = st.columns([1, 2, 1])

with center_col:
    st.markdown("<h2 style='text-align: center; color: #0033A0;'>Get in Touch</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Have questions about the AgLime Calculator? Send me a message below.</p>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("<h4 style='background-color: #0033A0; text-align: center; color: white; padding: 10px; border-radius: 5px;'>Mohammad Shamim</h4>", unsafe_allow_html=True)
        
        # Professional Info (Optional - feel free to edit)
        st.markdown("""
        <div style='text-align: center; margin-bottom: 20px;'>
            <p style='margin: 0;'><b>Crop Physiologist / Agronomist / Grain Corps Extension and Research Associate</b></p>
            <p style='font-size: 0.9em; color: #555;'>Specializing in echo-physiological responses of crop species, Data Analystics, & Decision Support Tools</p>
            <p style='font-size: 0.9em; color: #555;'>University of Kentucky Soybean and Canola Agronomist</p>
        </div>
        """, unsafe_allow_html=True)

        # Contact Form
        contact_form = """
        <form action="https://formsubmit.co/shamim.one@outlook.com" method="POST">
            <input type="hidden" name="_captcha" value="false">
            <div style="margin-bottom: 10px;">
                <input type="text" name="name" placeholder="Your Name" style="width: 100%; padding: 10px; border-radius: 5px; border: 1px solid #ccc;" required>
            </div>
            <div style="margin-bottom: 10px;">
                <input type="email" name="email" placeholder="Email Address" style="width: 100%; padding: 10px; border-radius: 5px; border: 1px solid #ccc;" required>
            </div>
            <div style="margin-bottom: 10px;">
                <textarea name="message" placeholder="How can I help you?" style="width: 100%; padding: 10px; border-radius: 5px; border: 1px solid #ccc; height: 100px;"></textarea>
            </div>
            <button type="submit" style="background-color: #0033A0; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; width: 100%; font-weight: bold;">
                Send Message
            </button>
        </form>
        """
        st.markdown(contact_form, unsafe_allow_html=True)

    # Sidebar or Footer Professional links
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center;'>
        <a href="mailto:shamim.one@outlook.com" style="text-decoration: none; color: #0033A0;">📧 Email</a> | 
        <a href="https://github.com/shamim-mj" style="text-decoration: none; color: #0033A0;">💻 GitHub</a>
    </div>
    """, unsafe_allow_html=True)

# --- CSS LOADING ---
def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass # Silently skip if style.css is not found locally

local_css("style.css")