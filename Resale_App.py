import streamlit as st

st.set_page_config(
    page_title="Resale Price",
    page_icon="🏠",
    layout="wide",
)

st.write("# Welcome to HDB Resale app! (Beta)")

st.sidebar.success("Select a demo above.")

st.markdown(
    """
    ## This is an application for HDB resale price analysis and prediction.

    This is best viewed in a desktop browser. If you are on mobile, the plots may not be displayed properly. \n
    The search nearby feature still works.

    ### The application is divided into 3 parts:
    - Basic plots
    - Map plot of areas
    - Search nearby 
    - Prediction (Coming soon!)\n\n\n

    ### Data 
    The data used in this application is from [data.gov.sg](https://beta.data.gov.sg/collections/189/view).

""")
with st.expander("Additional details on data", expanded=False):
    st.markdown(
    """
    Not all the data was used in the application. Only the latest details from 2017 onwards were used.
    Reason being that most users would be interested in the latest data. The newer data allows for a more accurate prediction with a smaller dataset.
    It is debatable whether the older data should be included for more variance, but this is quite experimental. 

    
    """
    )
st.markdown(
    """

    ### Privacy

    This application does not store any data. All data is processed on the fly. 
    The source code is available in the github repo in the top right corner.

    ### Contact
    """ 
    )

with st.expander("About me", expanded=False):


    st.markdown('<a href="https://www.linkedin.com/in/wheyne-lau"><img src="https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg" width="30" height="30" alt="LinkedIn Logo"></a> Click [here](https://www.linkedin.com/in/wheyne-lau/) to view my LinkedIn Profile.', unsafe_allow_html=True)

    st.markdown('<a href="https://github.com/wheynelau"><img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="30" height="30" alt="GitHub Logo"></a> Click [here](https://github.com/wheynelau) to view my GitHub Repository.', unsafe_allow_html=True)
