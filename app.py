import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

# ---------- Streamlit page config ----------
st.set_page_config(page_title="Smart Flow", layout="centered")
st.title("🧠 Smart Flow")
st.markdown("""
Upload your Excel report below, and download the processed output after magic happens ✨.
""")

# ---------- File uploader ----------
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    try:
        # Stage 1: Basic filtering and formatting
        df = pd.read_excel(uploaded_file)
        df = df[df['packageprice'].notna() & (df['packageprice'] != 0)].reset_index(drop=True)

        output_df = pd.DataFrame()
        output_df['n'] = range(1, len(df) + 1)
        output_df['date'] = datetime.today().strftime('%d/%m/%Y')
        output_df['name'] = df['patientname']
        output_df['location'] = df['locationcenter']
        output_df['package'] = df['servicename']
        output_df['payment'] = ''
        output_df['time'] = df['billtime']
        output_df['shopify'] = df['transactionno']
        output_df['desc code'] = df['discountcode']
        output_df['price'] = df['netamt']
        output_df['hrs'] = ''
        output_df['under process'] = df['availeddatetime'].apply(lambda x: 'UNDER PROCESS' if pd.notnull(x) else 'SAMPLE PENDING')

        # Stage 2: Calculate hours
        hours_dict = {
            "UAE National Pre-employment": "72hrs", "Wellness Package - Premium": "96hrs",
            "Food Intolerance Test": "96hrs", "Respiratory Allergy Test": "48hrs",
            "Body Composition Analysis Test": "0", "ECG": "0",
            "Wellness Package - Enhanced": "72hrs", "Wellness Package - Standard": "36hrs",
            "Lipid Profile Test": "24hrs", "Food Allergy Test": "48hrs",
            "Female Hormone Profile": "48hrs", "Gut Health": "6 Weeks"
        }

        def get_hours(package_name):
            if not isinstance(package_name, str): return None
            if "SMART DNA" in package_name: return "6 Weeks"
            if "CONSULTATION" in package_name.upper(): return "0"
            for key in hours_dict:
                if key in package_name:
                    return hours_dict[key]
            return None

        output_df['hrs'] = output_df['package'].apply(get_hours)

        # Stage 3: Pivot tables (keep original packages)
        mapping_pivot = {"UAE National Pre-employment": "UAE-National Pre-Employment Test", "Wellness Package - Premium": "Premium Package", "Food Intolerance Test (Stand Alone)": "Food Intolerance", "Respiratory Allergy Test (Add On)": "Respiratory Allergy", "Body Composition Analysis Test (Add On)": "Body Composition Analysis Test (Add On)", "ECG and Doctor Consult (Stand Alone)": "ECG and Doctor Consult (Stand Alone)", "Wellness Package - Enhanced": "Enhanced Package", "Wellness Package - Standard": "Standard Package", "Lipid Profile Test (Add On with Wellness)": "Lipid Profile", "Food Allergy Test (Add On)": "Food Allergy", "Female Hormone Profile (Add On with Wellness)": "Female Hormone Profile", "Food Intolerance Test (Add On)": "Food Intolerance", "Smart DNA - Age Well Package": "Age-Well"}
        packages_pivot = ['Standard Package', 'Enhanced Package', 'Premium Package', 'Lipid Profile', 'Food Allergy', 'Food Intolerance', 'Respiratory Allergy', 'Female Hormone Profile', 'Mag & Zinc', 'Coeliac Profile Test', 'Active Package', 'Womens Comprehensive Health Screening', 'Healthy Heart Package', 'Right Fit', 'Athletes Package', 'NutriGen', 'UAE-National Pre-Employment Test', 'Age-Well', 'Acne Profile', 'Hair Loss']
        locations = ['CITY WALK', 'DKP', 'INDEX']

        output_df['location'] = output_df['location'].str.strip().str.upper()
        output_df['package'] = output_df['package'].str.strip().str.upper()

        pivot_df = pd.DataFrame(0, index=packages_pivot, columns=locations)

        for _, row in output_df.iterrows():
            package_value = str(row['package']).upper()
            location_value = str(row['location']).upper()
            mapped_package = next((mapping_pivot.get(k) for k in mapping_pivot.keys() if k.upper() in package_value), None)
            if mapped_package is None and any(pkg.upper() in package_value for pkg in packages_pivot):
                mapped_package = next(pkg for pkg in packages_pivot if pkg.upper() in package_value)
            if mapped_package in packages_pivot:
                if 'CITY WALK' in location_value:
                    pivot_df.at[mapped_package, 'CITY WALK'] += 1
                elif 'DUBAI KNOWLEDGE PARK' in location_value or 'DKP' in location_value:
                    pivot_df.at[mapped_package, 'DKP'] += 1
                elif 'INDEX TOWER' in location_value or 'INDEX' in location_value:
                    pivot_df.at[mapped_package, 'INDEX'] += 1

        pivot_df = pivot_df.reindex(columns=['CITY WALK', 'INDEX', 'DKP'])

        # Stage 4: Unique Patients with updated logic
        packages_unique = [
            'Standard Package',
            'Enhanced Package',
            'Premium Package',
            'Lipid Profile',
            'Food Allergy',
            'Food Intolerance',
            'Respiratory Allergy',
            'Female Hormone Profile',
            'Mag & Zinc',
            'Coeliac Profile Test',
            'Active Package',
            'Athletes Package',
            'BCA',
            'Right Fit',
            'ECG',
            'Pulmonary Function Test',
            'UAE-National Pre-Employment Test',
            'Travel Fit Assessment',
            'Movement Assessment',
            'H&U Vaccination',
            'Influenza Vaccination',
            'Healthy Heart',
            'Womens Comprehensive Health Screening',
            'Gym Partnership Package - Athlete Plus',
            'NutriGen',
            'Age-Well',
            'Acne Profile',
            'Hair Loss',
            'GUT Health',
            'OPC'
        ]

        mapping_unique = {
            "UAE National Pre-employment": "UAE-National Pre-Employment Test",
            "Wellness Package - Premium": "Premium Package",
            "Food Intolerance Test (Stand Alone)": "Food Intolerance",
            "Food Intolerance Test (Add On)": "Food Intolerance",
            "Respiratory Allergy Test (Add On)": "Respiratory Allergy",
            "Body Composition Analysis Test": "BCA",
            "Body Composition Analysis Test (Add On)": "BCA",
            "ECG and Doctor Consult (Stand Alone)": "ECG",
            "Wellness Package - Enhanced": "Enhanced Package",
            "Wellness Package - Standard": "Standard Package",
            "Lipid Profile Test (Add On with Wellness)": "Lipid Profile",
            "Food Allergy Test (Add On)": "Food Allergy",
            "Female Hormone Profile (Add On with Wellness)": "Female Hormone Profile",
            "Smart DNA - Age Well Package": "Age-Well",
            "Gut Health": "GUT Health",
            "Healthy Heart Package": "Healthy Heart",
            "Womens Comprehensive Health Screening": "Womens Comprehensive Health Screening",
            "Athletes Package": "Athletes Package",
            "Right Fit": "Right Fit",
            "NutriGen": "NutriGen",
            "Acne Profile": "Acne Profile",
            "Hair Loss": "Hair Loss",
            "Coeliac Profile Test": "Coeliac Profile Test",
            "Active Package": "Active Package",
            "Mag & Zinc": "Mag & Zinc",
            "Pulmonary Function Test": "Pulmonary Function Test",
            "Travel Fit Assessment": "Travel Fit Assessment",
            "Movement Assessment": "Movement Assessment",
            "H&U Vaccination": "H&U Vaccination",
            "Influenza Vaccination": "Influenza Vaccination",
            "Gym Partnership Package - Athlete Plus": "Gym Partnership Package - Athlete Plus",
            "OPC": "OPC"
        }

        unique_patients_pivot = pd.DataFrame(0, index=packages_unique + ['Unique Patients'], columns=locations)

        def match_package(service_name):
            if not isinstance(service_name, str):
                return None
            service_name = service_name.strip().upper()
            # Try exact match from mapping
            for key, value in mapping_unique.items():
                if key.upper() == service_name:
                    return value
            # Try partial match
            for key, value in mapping_unique.items():
                if key.upper() in service_name:
                    return value
            # If no match found in mapping, check if service_name contains any package name
            for pkg in packages_unique:
                if pkg.upper() in service_name:
                    return pkg
            return None

        for _, row in output_df.iterrows():
            package_value = match_package(row['package'])
            location_value = str(row['location']).strip().upper()

            if package_value in packages_unique:
                if 'CITY WALK' in location_value:
                    unique_patients_pivot.at[package_value, 'CITY WALK'] += 1
                elif 'DUBAI KNOWLEDGE PARK' in location_value or 'DKP' in location_value:
                    unique_patients_pivot.at[package_value, 'DKP'] += 1
                elif 'INDEX TOWER' in location_value or 'INDEX' in location_value:
                    unique_patients_pivot.at[package_value, 'INDEX'] += 1

        for location in locations:
            if location == 'CITY WALK':
                mask = output_df['location'].str.contains('CITY WALK', case=False, na=False)
            elif location == 'DKP':
                mask = output_df['location'].str.contains('DUBAI KNOWLEDGE PARK|DKP', case=False, na=False)
            elif location == 'INDEX':
                mask = output_df['location'].str.contains('INDEX TOWER|INDEX', case=False, na=False)

            unique_count = output_df[mask]['name'].nunique()
            unique_patients_pivot.at['Unique Patients', location] = unique_count

        unique_patients_pivot = unique_patients_pivot.reindex(columns=['CITY WALK', 'INDEX', 'DKP'])

        # Stage 5: Filtered table for QLAB
        stage4_df = output_df.copy()
        stage4_df = stage4_df[~stage4_df['package'].str.contains('GUT HEALTH|CONSULTATION', case=False, na=False)]
        stage4_df = stage4_df[stage4_df['hrs'] != '0']
        stage4_df['n'] = range(1, len(stage4_df) + 1)

        # Write to Excel in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            pivot_df.to_excel(writer, sheet_name='DR 1 - QLAB')
            unique_patients_pivot.to_excel(writer, sheet_name='DR 1 - SS')
            output_df.to_excel(writer, sheet_name='DR 2', index=False)
            stage4_df.to_excel(writer, sheet_name='DR QLAB', index=False)

        st.success("✅ File processed successfully!")
        st.download_button(
            label="📥 Download Final Output",
            data=output.getvalue(),
            file_name="final_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"⚠️ An error occurred while processing the file: {e}")

# ---------- Footer ----------
st.markdown("""
    <hr style="margin-top: 50px;">
    <br>
    <div style='text-align: center; font-size: small;'>
       
    </div>
""", unsafe_allow_html=True)

st.markdown(
    """
    <div style="text-align: center;">
        <img src="https://cdn.shopify.com/oxygen-v2/36277/27243/56770/2052185/assets/favicon-BeEK2tfQ.svg" width="100"/>
        <div style="margin-top: 10px;">
            <sub>Made with ❤️ by Khaled Abdelhamid</sub><br>
            
        
    </div>
    """,
    unsafe_allow_html=True
)
