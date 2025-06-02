import streamlit as st
from analyze_excel import analyze_and_flag
import os
import shutil
import streamlit as st
import streamlit_authenticator as stauth

st.set_page_config(page_title="Dental Billing AI", layout="centered")
st.title("🦷 Dental Billing Assistant (Powered by DANA)")

names = ['Javon Magee']
usernames = ['javon']
passwords = ['secure123']

# ✅ FIXED: Updated Hasher usage
hashed_passwords = stauth.Hasher(passwords).generate()

authenticator = stauth.Authenticate(
    names,
    usernames,
    hashed_passwords,
    'billing_app',
    'auth_token_secret',
    cookie_expiry_days=1
)

name, auth_status, username = authenticator.login('Login', 'main')

if auth_status is False:
    st.error("Incorrect username or password.")
elif auth_status is None:
    st.warning("Please enter your credentials.")
elif auth_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Welcome, {name}!")

    # ...place your app content below this



# Auto-clear temp folder on each app run
def clear_temp_folder(folder_path="temp"):
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)  # remove file
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # remove subfolders if any
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
    else:
        os.makedirs(folder_path)

clear_temp_folder()


col1, col2 = st.columns(2)
with col1:
    production_file = st.file_uploader("Upload Production and Income Report", type=["xlsx"])
with col2:
    uncollected_file = st.file_uploader("Upload Patient Portion Uncollected Report", type=["xlsx"])

if production_file and uncollected_file:
    with st.spinner("Analyzing..."):
        # Save files locally
        prod_path = os.path.join("temp", production_file.name)
        unc_path = os.path.join("temp", uncollected_file.name)

        with open(prod_path, "wb") as f:
            f.write(production_file.read())
        with open(unc_path, "wb") as f:
            f.write(uncollected_file.read())

        summary, output_path = analyze_and_flag(prod_path, unc_path)

    st.success("✅ Analysis Complete!")
    st.markdown("### Executive Summary")
    st.code(summary)

    with open(output_path, "rb") as f:
        st.download_button("📥 Download Flagged Report", f, file_name="flagged_report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
