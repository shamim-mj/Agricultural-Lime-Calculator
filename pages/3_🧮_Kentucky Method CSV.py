# import  libraries
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
from st_aggrid import AgGrid
import time
import math
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

#title
st.markdown("<h2 style='background-color: #0033A0; font-size:35px; text-align: center; color: 	white;'>Upload a CSV File</h2>", unsafe_allow_html=True)
# data input options
percent_weight = option_menu(None, ["Lab Results (Weight)", "Lab Results (Percentage)"], 
    icons=[], 
    menu_icon="cast", default_index=0, orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#ffe6e6"},
        "icon": {"color": "orange", "font-size": "20px"}, 
        "nav-link": {"font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#ff0000"},
    }
)


# Use this when a calculation or upload starts
with st.status("Analyzing Soil Data...", expanded=True) as status:
    st.write("Applying Sikora-2 Buffer Method...")
    time.sleep(0.5) # Simulating math
    st.write("Calculating Relative Neutralizing Value (RNV)...")
    status.update(label="Analysis Complete!", state="complete", expanded=False)


# ask the user what kind of data s/he has
if percent_weight=="Lab Results (Weight)":
    st.write("**:blue[Your file should look like this. The number of rows depends on the number of your samples]**")
    # A demo file used to show the users how their file should be
    st.dataframe(pd.DataFrame({"Lime Source":"Sample1", "Initial (g)": 100, "> #10 (g)": 10, "< #10": 90,"< #50 (g)":60,
    "cce": 97.8, 'wph':5.8, 'bph':6.5, 'tph':6.5, 'price': 20}, index =[1]))
    subcontainer1= st.container()
    # Lets give some instructions to users how to create file and how it should look like
    subcontainer1.markdown("""
    <div style="text-align: justify;">
    <span style='color: #0033A0; font-weight: bold; '>Tips:</span>
    Your file must be a CSV file and should have columns as shown above. If the number and order of the columns are incorrect, 
    the calculator will throw an error. </br>Please keep in mind that soil water pH (wph), buffer pH (bph), and 
    target pH (tph) must be the same for all samples. Here we assume various lime sources are calculated for the same soil.
    </div>
    """, unsafe_allow_html=True)
    uploadfile = st.file_uploader("upload Your  file", label_visibility= 'collapsed')
# Lets see if the data has problems or not. if it does have problems, then instruct the user to correct the data
# else, proceed
    try:
                # Lets give a condition if the upload file exist or not. If it exists then make it read it. 
        if uploadfile is not None:
            st.success("**File uploaded successfully!**")
            df = pd.read_csv(uploadfile)
            df.columns= ["Quarry", "initial", "gten", "lten", "lfifty", 'cce','wph', 'bph', 'tph','price']
            AgGrid(df.round(1),  columns_auto_size_mode=True, theme='alpine')
            st.caption("**:red[Here are the first five rows of your data]**")


            # adding  columns with new calculations
            df["Zero%_eff"] = (df.gten/df.initial)*100
            df['Fifty%_eff'] = ((((df.lten-df.lfifty)))/df.initial)*100
            df['Hund%_eff'] = (df.lfifty/df.initial)*100
            df["RNV"] = df.cce/100.00*((((df.lten-df.lfifty)/2.0)+df.lfifty)/df.initial)*100

            SWPH = df.wph
            BPH = df.bph
            TPH = df.tph
            SW  = 12
            RNV = df.RNV
            part1 = -1.1 *(TPH-SWPH)*(BPH-7.55)
            part2  = (BPH -(1.1*SWPH)+1.47)
            part3 = 13.75/SW
            ELR = part1/part2*part3
            cffa = ELR.map(lambda x: (3.62 - (0.734*x) if x <= 3 else x==1.42))
            pure_lime = cffa*ELR
            df['Bulk_Rec'] = pure_lime/df.RNV*100 if TPH[0]>SWPH[0] else df.RNV *0
            df['Cost'] = df.Bulk_Rec * df.price
            df_up = df.copy()
            st.session_state['df_up'] = df_up
    except:
        st.markdown("""
        <div style = 'text-align: justify; color:red; font-weight: bold; font-size: 20px;'>
        Your  data has been successfully uploaded but has compatibility issues.
        Take a look at the sample file above and confirm that:</br>
        😞 1. You are not using percentage-based data.</br>
        😞 2. The number of columns in the dataframe is exaclty 10.</br>
        😞 3. The order of the columns is correct. </br>
                                
        </div>
        """, unsafe_allow_html=True)

        

if percent_weight=="Lab Results (Percentage)":
    st.write("**:blue[Your file should look like this. The number of rows depends on the number of your sample]**")
    # A demo data frame
    st.dataframe(pd.DataFrame({"Lime Source":"Sample1","> #10 (%)": 10, "< #10 (%)":90,
    "< #50 (%)": 60, "cce": 97.8, 'wph':5.8, 'bph':6.5, 'tph':6.5,'price': 20}, index =[1]))
    subcontainer1= st.container()
    # instruction on how to create a file
    subcontainer1.markdown("""
    <div style="text-align: justify;">
    <span style='color: #0033A0; font-weight: bold;'>Tips:</span>
    Your file must be a CSV file and should have columns as shown above. If the number and order of the columns are incorrect, 
    the calculator will through an error. </br>Please keep in mind that soil water pH (wph), buffer pH (bph), and 
    target pH (tph) must be the same for all samples. Here we assume various lime sources are calculated for the same soil.
    </div>
    """, unsafe_allow_html=True)
    uploadfile = st.file_uploader("")

# Lets see if the data has problems or not. if it does have problems, then instruct the user to correct the data
# else, proceed
    try:
        if uploadfile is not None: # upload a file if it exists. Skip if it doesn't
            st.success("**File uploaded successfully!**")
            df = pd.read_csv(uploadfile)
            df.columns= ["Quarry", "gten", "lten", "lfifty", 'cce', "wph", "bph", 'tph','price']
            AgGrid(df.round(1), columns_auto_size_mode='FIT_ALL_COLUMNS_TO_VIEW', theme='alpine')
            # st.caption("**:red[Here are the first few rows of your data]**")

        # adding  columns with new calculations
            df["Zero%_eff"] = df.gten
            df['Fifty%_eff'] = (df.lten-df.lfifty)
            df['Hund%_eff'] = df.lfifty
            df["RNV"] = df.cce/100.00*(((df.lten-df.lfifty)/2.0)+df.lfifty)
            SWPH =df.wph
            BPH = df.bph
            TPH = df.tph
            SW  = 12
            RNV = df.RNV
            part1 = -1.1 *(TPH-SWPH)*(BPH-7.55)
            part2  = (BPH -(1.1*SWPH)+1.47)
            part3 = 13.75/SW
            ELR = part1/part2*part3 #Equation LR
            cffa = ELR.map(lambda x: (3.62 - (0.734*x) if x <= 3 else x==1.42))
            pure_lime = cffa*ELR
            df['Bulk_Rec'] = pure_lime/df.RNV*100 if TPH[0]>SWPH[0] else df.RNV *0
            df['Bulk_Rec'] = df['Bulk_Rec'].apply(lambda x: math.ceil(x * 2) / 2)
            df['Cost'] = df.Bulk_Rec * df.price
            df_up = df.copy()
            st.session_state['df_up'] = df_up

    except:
        st.markdown("""
        <div style = 'text-align: justify; color:red; font-weight: bold; font-size: 20px;'>
        Your  data has been successfully uploaded but has compatibility issues.
        Take a look at the sample file above and confirm that:</br>
        😞 1. You are not using weight-based data.</br>
        😞 2. The number of columns in the dataframe is exactly 9.</br>
        😞 3. The order of the columns is correct. </br>
                            
    </div>
    """, unsafe_allow_html=True)
# Lets see if the data has problems or not. if it does have problems, then instruct the user to correct the data
# else, proceed
st.write("___")
try:
    #@st.cache_data
    def graph_h():
        if df.shape[0]>1:
            eff_h = 5+(df.shape[0]-5)*0.46
            others = 2+(df.shape[0]-2)*0.15
            rotation = 0
            data_labels = 'edge'
            return eff_h, others, rotation, data_labels
        else:
            return 4,  1, 0, 'edge'
    eff_h, others, rotation, data_labels= graph_h()


    if "pallete" not in st.session_state:
        pallete = "Dark2"
    else:
        pallete = st.session_state['pallete']
    tab1, tab2= st.tabs(["**Lime Quality**", "**Lime Amount and Cost**"])   
    with tab1:
        st.markdown("<h5 style='background-color: #0033A0; font-size:35px; text-align: center; color: 	white;'>Lime Quality</h5>", unsafe_allow_html=True)
        st.write("___")
        fig,(ax1, ax2, ax3) = plt.subplots(3, 1, figsize = (7, eff_h), sharex=True, gridspec_kw={'hspace':0.19})
        Fplot = sns.barplot(x = "Zero%_eff", y = 'Quarry', data=df, ax=ax1, palette=pallete)
        ax1.set_ylabel(None)
        ax1.set_xlabel(None)
        ax1.axes.xaxis.set_visible(False)
        ax1.text(0.45, -0.13, s="#10 Seive", transform = ax1.transAxes)
        ax1.text(0.95, 0.18+eff_h*0.012, "RNV (0%)", rotation =270, transform= ax1.transAxes, fontsize=8)
        ax1.bar_label(Fplot.containers[0], fmt="%.2f", rotation =0)
        ax1.set_title("Lime Fineness (%)", fontsize = 18)


        Splot =sns.barplot(x = "Fifty%_eff", y = 'Quarry', data=df, ax=ax2, palette=pallete)
        ax2.set_ylabel(None)
        ax2.set_xlabel(None)
        ax2.axes.xaxis.set_visible(False)
        ax2.text(0.45, -0.13, s="#50 Seive", transform = ax2.transAxes)
        ax2.text(0.95, 0.18+eff_h*0.012, "RNV (50%)", rotation =270, transform= ax2.transAxes, fontsize=8)
        ax2.bar_label(Splot.containers[0], fmt="%.2f", rotation = 0)


        Tplot = sns.barplot(x = "Hund%_eff", y = 'Quarry', data=df, ax=ax3, palette=pallete)
        ax3.set_xlim((0, 100))
        ax3.set_ylabel(None)
        ax3.set_xlabel(None)
        ax3.text(0.95, 0.08+eff_h*0.012, "RNV (100%)", rotation =270, transform= ax3.transAxes, fontsize=8)
        ax3.bar_label(Tplot.containers[0],fmt="%.2f", rotation = 0)
        ax3.set_xlabel("", fontsize = 14)
        ax3.axes.xaxis.set_visible(False)
        ax3.set_xticklabels([])

        rect = plt.Rectangle(
            # (lower-left corner), width, height
            (0.1232, 0.11), 0.776, 0.77, fill=False, color="k", lw=1, 
            zorder=1000, transform=fig.transFigure, figure=fig
        )
        fig.patches.extend([rect]);

        # plot for RNV_______________

        fig1, ax4= plt.subplots(figsize = (7,others))
        ax4.set_xlabel('RNV (%)')
        ax4.set_ylabel(None)
        ax4.set_title("Relative Neutralizaing Value (RNV (%))", fontsize = 18)

        FrPlot = sns.barplot(x='RNV', y = 'Quarry', data=df, ax=ax4, palette=pallete)
        ax4.set_xlim((0, 100))
        ax4.bar_label(FrPlot.containers[0], fmt="%.2f", rotation=0)
        ax4.set_ylabel(None)
        ax4.set_xlabel("", fontsize = 14)
        ax4.axes.xaxis.set_visible(False)
        ax4.set_xticklabels([])
        st.pyplot(fig)
        st.pyplot(fig1)


    with tab2:
        st.markdown("<h5 style='background-color: #0033A0; font-size:35px; text-align: center; color: 	white;'>Lime Recommendation and Application Cost</h5>", unsafe_allow_html=True)
        st.markdown("___")    
        # Here I also want to give an option 
        st.markdown("<h3 style='text-align: center; color: blue;'>""</h3>", unsafe_allow_html=True)
        fig2, ax5 = plt.subplots(figsize =(7,others) )
        ax5.set_ylabel(None)
        ax5.set_title(f"Adjusted lime amount required to raise soil pH of {round(SWPH[0], 1)} to a target pH of {round(TPH[0],1)}", fontsize = 14)

        FiPlot = sns.barplot(x='Bulk_Rec', y = 'Quarry', data=df, ax=ax5, palette=pallete)
        ax5.bar_label(FiPlot.containers[0], fmt="%.2f", rotation = rotation, label_type=data_labels)
        ax5.set_ylabel(None)
        ax5.set_xlim([0, max(df.Bulk_Rec)+max(df.Bulk_Rec)*0.1]) # This syntax max the x axis length dynamic. Without it the data lable makes a problem
        ax5.set_xlabel("Lime amount (t/ac)", fontsize = 14)
        ax5.axes.xaxis.set_visible(False)
        ax5.set_xticklabels([])
            
            # Plot for Cost of  Lime

        fig3, ax6 = plt.subplots(figsize =(7,others) )
        ax6.set_ylabel(None)
        ax6.set_title(f"Total applicaiotn costs to raise soil water pH of {round(SWPH[0], 1)} to a target pH of {round(TPH[0],1)}", fontsize = 14)

        SiPlot = sns.barplot(x='Cost', y = 'Quarry', data=df, ax=ax6, palette=pallete)
        ax6.bar_label(SiPlot.containers[0], fmt="%.2f", rotation = rotation, label_type=data_labels)
        ax6.set_ylabel(None)
        ax6.set_xlabel("Total applicaiton costs ($/ac)")
        ax6.set_xlim([0, max(df.Cost)+max(df.Cost)*0.1])
        ax6.axes.xaxis.set_visible(False)
        ax6.set_xticklabels([])
        st.pyplot(fig2)
        st.pyplot(fig3)
except:
    pass