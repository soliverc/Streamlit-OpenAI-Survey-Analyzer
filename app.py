import streamlit as st
import pandas as pd

st.set_page_config(page_title="Survey Sight", page_icon= ":bar_chart:")

st.title("Survey:blue[Sight]")
st.header("Freetext Survey Feedback Analyzer")
st.header("Powered by :blue[Chat GPT] :robot_face:",divider='rainbow')
st.write("Upload your freetext survey responses to get a detailed summary of what" 
        " your respondents are saying. No need to read through hundreds "
        "of responses ever again!")

st.write("⚠️ This only works with Excel or CSV files. "
        "Your survey responses should be contained in a"
         " single column, with one row per response.")
st.write("📝 Your Excel / CSV file can contain other non related columns too, as we will choose the specific response column after upload.")


st.write("First of all, do you have your own data?")

data = st.radio(options= ["Yes", "No"], label='hello', label_visibility ="hidden")

if data == "No":

    st.write("That's fine! If you don't currently have a dataset to play around with, "
            "you can use this. It's a collection of Google Play Store reviews "
            "for an app called Any.do. The user reviews are in the *content* column."
            " Click the button below to download the dataset and continue onto the next step." )

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

else:
    st.write("Great! Upload your file below. ")

uploaded_file = st.file_uploader("🚽 Your data is deleted when you close the browser tab!", type=['xlsx','csv'])


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

# Using the "with" syntax
# with st.form(key='my_form'):
# 	theme = st.text_area(label='Enter some text')
# 	submit_button = st.form_submit_button(label='Submit')

from openai import OpenAI

st.write("Please paste your Open AI API Key below. This information is not saved or shared.")
url = 'https://platform.openai.com/'
api_key_user = st.text_input(label="Note, if you don't have an Open AI API key yet, you can get one [by clicking here](%s)" % url, type="password")

if st.button("Submit to begin survey analysis"):
    client = OpenAI(api_key = api_key_user)


    def get_completion(prompt, model="gpt-4"):
        messages = [{"role": "user", "content": prompt}]
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0
        )
        return response.choices[0].message.content

    # some cleaning steps of te df first

    # Filter rows where the content is not just one word
    df = df[df[selected_column].str.split().apply(len) > 1]

    import emoji
    # Function to remove emojis
    def remove_emojis(text):
        return emoji.demojize(text)

    # Apply the function to the 'Responses' column
    df[selected_column] = df[selected_column].apply(remove_emojis)
    # final cleaning step. gets rid of ::smiley:: type text
    df[selected_column] = df[selected_column].str.replace(':[^:]+:', '', regex=True)


    # next, get the number of tokens for each response
    # we don't want to over load GPT. There is a token limit of 8000 currently.
    # so the data we send to the api should be less than this, by about 1000
    # which leaves some tokens for the api response

    # token counter
    import tiktoken

    def num_tokens_from_string(string: str, encoding_name: str) -> int:
        encoding = tiktoken.encoding_for_model(encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens

    # getting count of tokens
    df['Tokens'] = df.apply(lambda row: num_tokens_from_string(row[selected_column], encoding_name="gpt-4"), axis=1)

    # Shuffle DataFrame to randomize the order
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Calculate cumulative tokens
    df['CumulativeTokens'] = df['Tokens'].cumsum()

    # Select responses within the token limit of 7000
    selected_responses = df[df['CumulativeTokens'] <= 7000][selected_column].to_list()

    # def createlistfromcolumn(df_column):
    #     return ["```" + text + "```" for text in df_column if len(text) > 5]

    number_of_responses = len(selected_responses)

    prompt = f"""
    You will be provided by a list of comments taken from a survey. The person who uploaded the survey data has written a short desrcription of what the survey is about. Here is the context of the survey: {theme}. 

    After reading the context and background to the survey, you will assume the role of an expert in this area. 

    Your goal is to read through the responses and give the following outputs:
    
    Positive Comments: Summarise common positive feedback in three sentences or less. Write in sentences, not bullet points. Add a title in bold to this section called "Positive Comments:"
    Negative Comments: Summarise common negative feedback in three sentences or less.  Write in sentences, not bullet points. Add a title in bold to this section called "Negative Comments:"
    Sentiment Summary: Give a general summary of sentiment of the overall respondents.  Write in sentences, not bullet points. Add a heatitleder in bold to this section called "Sentiment Summary:"
    Recommendations.  Give recommendations going forward, while keeping the context in mind.  Write in sentences, not bullet points. Add a heatitleer in bold to this section called "Recommendations:"

    Here is the feedback for you to study: {selected_responses}
    """
    with st.spinner(f"Analysing {number_of_responses} responses..."):

        response = get_completion(prompt)
    st.success("Analysis Complete!", icon ="🤖")
    st.write(response)
    # some cleaning steps of te df first

    # Filter rows where the content is not just one word
    df = df[df[selected_column].str.split().apply(len) > 1]

    import emoji
    # Function to remove emojis
    def remove_emojis(text):
        return emoji.demojize(text)

    # Apply the function to the 'Responses' column
    df[selected_column] = df[selected_column].apply(remove_emojis)
    # final cleaning step. gets rid of ::smiley:: type text
    df[selected_column] = df[selected_column].str.replace(':[^:]+:', '', regex=True)


    # next, get the number of tokens for each response
    # we don't want to over load GPT. There is a token limit of 8000 currently.
    # so the data we send to the api should be less than this, by about 1000
    # which leaves some tokens for the api response

    # token counter
    import tiktoken

    def num_tokens_from_string(string: str, encoding_name: str) -> int:
        encoding = tiktoken.encoding_for_model(encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens

    # getting count of tokens
    df['Tokens'] = df.apply(lambda row: num_tokens_from_string(row[selected_column], encoding_name="gpt-4"), axis=1)

    # Shuffle DataFrame to randomize the order
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Calculate cumulative tokens
    df['CumulativeTokens'] = df['Tokens'].cumsum()

    # Select responses within the token limit of 7000
    selected_responses = df[df['CumulativeTokens'] <= 7000][selected_column].to_list()

    # def createlistfromcolumn(df_column):
    #     return ["```" + text + "```" for text in df_column if len(text) > 5]

    number_of_responses = len(selected_responses)

    prompt = f"""
    You will be provided by a list of comments taken from a survey. The person who uploaded the survey data has written a short desrcription of what the survey is about. Here is the context of the survey: {theme}. 

    After reading the context and background to the survey, you will assume the role of an expert in this area. 

    Your goal is to read through the responses and give the following outputs:
    
    Positive Comments: Summarise common positive feedback in three sentences or less. Write in sentences, not bullet points. Add a title in bold to this section called "Positive Comments:"
    Negative Comments: Summarise common negative feedback in three sentences or less.  Write in sentences, not bullet points. Add a title in bold to this section called "Negative Comments:"
    Sentiment Summary: Give a general summary of sentiment of the overall respondents.  Write in sentences, not bullet points. Add a heatitleder in bold to this section called "Sentiment Summary:"
    Recommendations.  Give recommendations going forward, while keeping the context in mind.  Write in sentences, not bullet points. Add a heatitleer in bold to this section called "Recommendations:"

    Here is the feedback for you to study: {selected_responses}
    """
    with st.spinner(f"Analysing {number_of_responses} responses..."):

        response = get_completion(prompt)
    st.success("Analysis Complete!", icon ="🤖")
    st.write(response)
