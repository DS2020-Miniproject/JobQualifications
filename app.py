import streamlit as st
import numpy as np
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import ast 
from collections import Counter
import altair as alt

def main():

    st.markdown("# :wrench: Job Skills App :briefcase:")

    st.markdown("")
    
    st.markdown("This application is a Streamlit dashboard that can be used"
            " to find out what skills employers are looking for related to different job titles."
            " The data is is from 2019 and it is collected from online job applications for positions open in the UK.")
    
    st.markdown("")

    data = load_data()

    category = st.sidebar.selectbox(
        'Select a job category',
        data['category'])
    
    skills = get_skills(data, category)

    skill_no = st.sidebar.slider("Choose the number of skills displayed: ", min_value=1,   
                       max_value=10, value=10, step=1)
    
    sorted_skills = sort_skills(skills, skill_no)

    chart_skills(category, sorted_skills)
    word_cloud(skills)


@st.cache
def load_data():
    data = pd.read_csv('ad_skills.csv')
    return data

def get_skills(data, category):
    s = data.loc[data['category'] == category, ['skills']]
    skills = ast.literal_eval(s.iloc[0].values[0])
    return skills 

def sort_skills(skills, skill_no):
    sorted_skills = dict(Counter(skills).most_common(skill_no)) 
    return sorted_skills

def chart_skills(category, skills):
    df = pd.DataFrame.from_dict(skills, orient='index', columns=['occurrences'])
    "**Top 5 skills for**", category

    c = alt.Chart(df.reset_index()).mark_bar(color='firebrick', opacity=0.5).encode(
        alt.X('occurrences', title='Number of occurrences', axis=alt.Axis(tickMinStep=1)),
        alt.Y('index', title='Skill'),
        color=alt.Color('index', legend=None)
    ).properties(
        width=700,
        height=250
    ).configure_axis(grid=False)
    st.write(c)

def word_cloud(skills):
    wordcloud = WordCloud(background_color='white').generate_from_frequencies(skills)
    fig, ax = plt.subplots()
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()
    st.pyplot(fig)


if __name__ == "__main__":
    main()