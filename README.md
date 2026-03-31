AgLime Quality & Cost Calculator 🚜
A Precision Agronomy Tool for Soil Fertility Management

Developed by Mohammad Shamim and Robbie Williams in Henderson, Kentucky, USA.

📌 Overview
The AgLime Quality & Cost Calculator is an open-source web application designed to help farmers, agronomists, and researchers determine the most efficient and cost-effective agricultural lime applications. By integrating laboratory particle analysis with regional chemical standards, the tool provides precise recommendations for soil pH adjustment.

Key Technical Features:
Particle Size Analysis: Calculates Effective Neutralizing Value (ENV) and Relative Neutralizing Value (RNV) based on sieve data.

Dual-State Methodology: * Kentucky Standards: Utilizes the Sikor-2 Buffer method (developed by Dr. Frank Sikora, University of Kentucky).

Ohio Standards: Implements the Ohio State University adopted method for ENP-based calculations.

Batch Processing: Support for manual entry (up to 5 sources) or CSV bulk upload for unlimited quarry reports.

Economic Analysis: Compares different lime sources based on cost per acre and quality.

Data Visualization: Dynamic charts with over 100 customizable color palettes to match professional reporting styles.

🛠 Installation & Usage
1. Local Setup
To run this application on your local machine, ensure you have Python 3.8+ installed:

Bash
# Clone the repository
git clone https://github.com/shamim-mj/Agricultural-Lime-Calculator.git

# Navigate to the folder
cd Agricultural-Lime-Calculator

# Install dependencies
pip install streamlit matplotlib
2. Launch the App
Bash
streamlit run app.py
🤝 Acknowledgements & References
We are greatly indebted to Dr. Frank Sikora (Regulatory Services, University of Kentucky) for his invaluable technical input and guidance in developing the algorithms for this application.

Supporting Literature:

Agricultural Lime Recommendations Based on Lime Quality (ID-163)

University of Kentucky Rock Quarry Lime Reports

⚖️ Disclaimer
This application is provided "as-is" for scientific and educational purposes. The authors accept no liability for agricultural outcomes. Users are encouraged to distribute this tool for scientific use following the authors' consent.

📥 Offline Version
An Excel version of this calculator, including advanced master templates, is available for download:
Download AgLime Excel Master