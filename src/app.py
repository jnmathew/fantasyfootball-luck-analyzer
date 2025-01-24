import streamlit as st

def display_page():
    st.title("ESPN Fantasy Football Luck Analyzer")
    st.write("Welcome to the Fantasy Football Luck Analyzer!")
    st.write("This tool will help you determine how lucky or unlucky you've been in your fantasy football league.") 

    # Input Fields
    st.header("Enter Your League Information")
    league_id = st.text_input("League ID", help="Your ESPN Fantasy Football League ID")
    swid = st.text_input("SWID", help="Find this in your browser cookies for ESPN.")
    espn_s2 = st.text_input("ESPN_S2", help="Find this in your browser cookies for ESPN.", type="password")

    with st.expander("How to find your SWID and ESPN_S2 tokens"):
        st.write("""
            1. Open your web browser and go to the ESPN Fantasy Football website.
            2. Log in to your account.
            3. Open the developer tools (usually by right-clicking on the page and selecting "Inspect" or pressing F12).
            4. Go to the "Application" tab.
            5. Under "Cookies", find the cookies for `espn.com`.
            6. Look for the `SWID` and `ESPN_S2` cookies and copy their values.
        """)

    # Submit Button
    if st.button("Submit"):
        if not league_id or not swid or not espn_s2:
            st.error("Please fill in all fields.")
        else:
            st.success("Credentials submitted! Fetching data...")
            # TODO: Use these credentials to connect to ESPN API


def main():
    display_page()


if __name__ == "__main__":
    main()