import streamlit as st
import pandas as pd

st.set_page_config(page_title="Survey Sight", page_icon= ":bar_chart:")

st.title("Survey :blue[Sight]")
st.header("Freetext Survey Feedback Analyzer")
st.header("Powered by :blue[Chat GPT] :robot_face:",divider='rainbow')
st.write("Upload your freetext survey responses to get a detailed summary of what" 
        " your respondents are saying. No need to read through hundreds "
        "of responses ever again!")


st.write("Note: If you don't currently have a dataset to play around with, "
         "you can use this. It's a collection of Google Play Store reviews "
         "for a single app. The user reviews are in the *content* column."
          " Click the button below to download the dataset.")

url1 = "https://raw.githubusercontent.com/soliverc/Streamlit-OpenAI-Survey-Analyzer/main/.testdata/anydo.csv"

@st.cache_data
def download_sample(link):
    dfdownload = pd.read_csv(link)
    return dfdownload

freefile = download_sample(url1)

import io

csv_buffer = io.StringIO()
freefile.to_csv(csv_buffer)

st.download_button(
    label="Download data as CSV",
    data=csv_buffer.getvalue(),
    file_name='PlayStoreReviews.csv',
    mime='text/csv',
)

st.write("This only works with Excel or CSV files.")
st.write("After uploading, you will be able to choose in which column the responses are located.")

uploaded_file = st.file_uploader("Choose your file", type=['xlsx','csv'])


if uploaded_file is None:
    st.info("Upload your Excel or CSV file above. 📂")
    st.stop()

@st.cache_data
def load_data(file):
    try:
        data = pd.read_csv(file)
    except:
        data = pd.read_excel(file)
    return data

df = load_data(uploaded_file)
st.write(f"Great! Here's a sample of your data. There are {df.shape[1]} columns and {df.shape[0]:,} rows.")
st.dataframe(df.head())


st.write("Now please select which column contains the free-text user responses")
selected_column = st.selectbox(index=None, options = df.columns, label='👇')

@st.cache_data
def showsample(col):
    for thing in col.sample(5):
        st.write("✒️" + thing)

if selected_column:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Here are five random responses.")
    showsample(df[selected_column])
    st.markdown("<hr>", unsafe_allow_html=True)

st.subheader("We are ready to extract the relevant topics.")
def getsample(dataframe, samplenum):
    return dataframe.sample(samplenum)

st.write("Please write a short description of what "
         "this survey is about. This will aid the model in "
         "interpreting the results. For example: "
         "***'These responses are comments from customers "
         "of a large retail store that sells "
         "a range of food, electronics and clothing. They were asked "
         "how customer service could be improved'***")

theme = st.text_area(label='👇')

from openai import OpenAI

st.write("Please paste your Open AI API Key below. This information is not saved.")
url = 'https://platform.openai.com/'
api_key_user = st.text_input(label="Note, if you don't have an Open AI API key yet, you can get one [by clicking here](%s)" % url, type="password")
if st.button("Submit to begin survey analysis"):
    client = OpenAI(api_key = api_key_user)


    def get_completion(prompt, model="gpt-4-1106-preview"):
        messages = [{"role": "user", "content": prompt}]
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0
        )
        return response.choices[0].message.content

    df = getsample(df, 100)

    def createlistfromcolumn(df_column):
        return ["```" + text + "```" for text in df_column if len(text) > 5]

    userfeedback = createlistfromcolumn(df['content'])

    prompt = f"""
    You will be provided by a list of comments taken from a survey. The person who uploaded the survey data has written a short desrcription of what the survey is about. Here is the context of the survey: {theme}. 

    After reading the context and background to the survey, you will assume the role of an expert in this area. 

    Each response of the survey is delimited by triple quotes, which will be supplied to you below.

    Your goal is to read through the responses and give the following outputs..
    

    Positive Comments: Summarise common negative feedback in three sentences or less. Write in sentences, not bullet points. Add a header to this section called "Positive Comments"
    Negative Comments: Summarise common positive feedback in three sentences or less.  Write in sentences, not bullet points. Add a header to this section called "Negative Comments"
    Sentiment Summary: Give a general summary of sentiment of the overall respondents.  Write in sentences, not bullet points. Add a header to this section called "Sentiment Summary"
    Recommendations.  Give recommendations going forward, while keeping the context in mind.  Write in sentences, not bullet points. Add a header to this section called "Recommendations"

    Here is the feedback for you to study: {userfeedback}
    """
    with st.spinner("Analysing responses..."):

        response = get_completion(prompt)
    st.success("Analysis Complete!", icon ="🤖")
    st.write(response)
