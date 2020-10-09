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

    all_skills, unique_skills = get_all_skills(data)

    selected_skills = st.sidebar.multiselect("Select skills to match with a job title:", unique_skills)

    skill_df = create_matrix(all_skills, data)

    if selected_skills:
        top_jobs = match_jobs(skill_df, selected_skills)
        visualize_jobs(top_jobs)

    word_cloud(skills)


@st.cache
def load_data():
    data = pd.read_csv('Data/skills2.csv')
    for ind in data.index: 
        data["skills"][ind] = ast.literal_eval(data["skills"][ind])

    return data

def get_skills(data, category):
    skills = data.loc[data['category'] == category, ['skills']]

    return skills.iloc[0][0]

@st.cache
def get_all_skills(data):
    skill_list = []
    for d in data["skills"]:
        skill_list = skill_list + list(d.keys()) 

    list_set = set(skill_list) 
    unique_list = list(list_set)

    return skill_list, unique_list

def sort_skills(skills, skill_no):
    sorted_skills = dict(Counter(skills).most_common(skill_no)) 

    return sorted_skills

def chart_skills(category, skills):
    df = pd.DataFrame.from_dict(skills, orient='index', columns=['occurrences'])
    "**Top 5 skills for**", category

    c = alt.Chart(df.reset_index()).mark_bar(color='firebrick', opacity=0.5).encode(
        alt.X('occurrences', title='Skill popularity', axis=alt.Axis(tickMinStep=1)),
        alt.Y('index', title='Skill'),
        color=alt.Color('index', legend=None)
    ).properties(
        width=700,
        height=250
    ).configure_axis(grid=False)
    st.write(c)

@st.cache(allow_output_mutation=True)
def create_matrix(all_skills, data):
    skills_matrix = []
    for job_skill in data["skills"]:
        vector = [0] * len(all_skills)
        for skill in job_skill.keys():
            vector[all_skills.index(skill)] = 1
        skills_matrix.append(vector)
    SkillsDf = pd.DataFrame(skills_matrix, columns=all_skills)
    SkillsDf['Job'] = data.category
    SkillsDf["count"] = [0] * len(SkillsDf.index)
    
    return SkillsDf

def match_jobs(skillDf, selected_skills):
    skill_df = skillDf.copy()
    for skill in selected_skills:
        skill_df["count"] = skill_df.apply(lambda x: x["count"] + x[skill], axis=1)
    skill_df = skill_df[["Job", "count"]]
    skill_df = skill_df.sort_values("count", ascending=False)
    top_skills = skill_df.iloc[0:5]

    return top_skills

def visualize_jobs(top_jobs):
    top_jobs = top_jobs[top_jobs['count'] > 0]
    names = top_jobs['Job'].tolist()
    size = top_jobs['count'].tolist()
    "**Top jobs for selected skills**"
    fig, ax = plt.subplots()
    my_circle=plt.Circle( (0,0), 0.7, color='white')
    plt.pie(size, labels=names)
    p=plt.gcf()
    p.gca().add_artist(my_circle)
    plt.show()
    st.pyplot(fig)


def word_cloud(skills):
    wordcloud = WordCloud(background_color='white').generate_from_frequencies(skills)
    fig, ax = plt.subplots()
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()
    st.pyplot(fig)


if __name__ == "__main__":
    main()