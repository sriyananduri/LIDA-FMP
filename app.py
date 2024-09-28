import streamlit as st
import pandas as pd
import requests
import json
from lida import Manager, llm, TextGenerationConfig
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
import io
import base64

API_KEY = ''
OPENAI_API_KEY =''

#LIDA
lida_manager = Manager(text_gen=llm("openai", api_key=OPENAI_API_KEY))

#fetch data and generate goals
def fetch_data_and_generate_goals(company_symbol):
    url = f'https://financialmodelingprep.com/api/v3/historical-chart/5min/{company_symbol}?apikey={API_KEY}'
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data)
    
    textgen_config = TextGenerationConfig(n=1, temperature=0.5, model="gpt-4o-mini", use_cache=True)
    summary = lida_manager.summarize(df, summary_method="default", textgen_config=textgen_config)
    goals = lida_manager.goals(summary, n=3, textgen_config=textgen_config)
    return goals, summary, df

#streamlit app
st.title("Financial Data Visualization")

#input field for company symbol
company_symbol = st.text_input("Enter company symbol")

#fetch data and generate goals
if st.button("Fetch Data"):
    goals, summary, df = fetch_data_and_generate_goals(company_symbol)

    #store in session_state
    st.session_state.goals = goals
    st.session_state.summary = summary
    st.session_state.df = df

#check if the goal is stored in session_state
if 'goals' in st.session_state:
    goals = st.session_state.goals
    summary = st.session_state.summary
    df = st.session_state.df

    st.write("CSV File Preview:")
    st.write(df.head())

    col1, col2 = st.columns([3, 1])

    #selectbox for goals
    with col1:
        st.markdown("<div style='width:500px'>", unsafe_allow_html=True)
        selected_goal = st.selectbox("Select a goal", goals)
        st.markdown("</div>", unsafe_allow_html=True)

    #text field for custom goal and a button to generate visualization 
    with col2:
        st.markdown("<div style='width:200px'>", unsafe_allow_html=True)
        custom_goal = st.text_input("Enter custom goal (optional)")
        if st.button("Generate Visualization"):
            if custom_goal:
                goal = custom_goal
            else:
                goal = selected_goal

            #generate visualization
            textgen_config = TextGenerationConfig(n=1, temperature=0.2, use_cache=True)
            summary = lida_manager.summarize(df, summary_method="default", textgen_config=textgen_config)
            charts = lida_manager.visualize(summary=summary, goal=goal, textgen_config=textgen_config, library="seaborn")
            chart = charts[0]

        st.markdown("</div>", unsafe_allow_html=True)

    #display chart
    if 'chart' in locals():
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write("\n")
        img = Image.open(io.BytesIO(base64.b64decode(chart.raster)))
        st.image(img, caption="Visualization", use_column_width=True, width=1000)

        #generate explanation for chart
        summary = lida_manager.summarize(df, summary_method="default", textgen_config=textgen_config)
        explanation = lida_manager.explain(code=chart.code)
        st.write("\n")
        st.write("\n")
        st.write("Explanation:")
        st.write(explanation[0][0]["explanation"])