# Survey Sight: AI-powered Freetext Feedback Analyzer

Survey Sight is a Streamlit application designed to effortlessly analyze free-text responses from surveys. By leveraging the power of OpenAI's GPT-4, Survey Sight provides users with a synthesized understanding of what respondents are communicating, general consensus on the subject, and common positive and negative feedback, without the need for manual review of individual responses.

## Features

- Upload Excel or CSV files containing free-text survey responses.
- Automatic detection of the column containing the free-text responses.
- Random sampling of responses to provide a quick glimpse of data.
- Integration with OpenAI's GPT-4 to analyze and synthesize feedback. (Will add feature to choose a specific model soon)
- Generation of a summary including common positive/negative comments, sentiment analysis, and recommendations.

## Check it out in action

You can either check the app out right now by going to: [https://surveysight.streamlit.app/](https://surveysight.streamlit.app/)

Or install it yourself below:

## Installation 

To run Survey Sight on your local machine, clone the repository, navigate to the project directory, and then install the requirements.

```bash
git clone https://github.com/yourusername/Streamlit-OpenAI-Survey-Analyzer.git
cd Streamlit-OpenAI-Survey-Analyzer
pip install -r requirements.txt
```

## Usage

To start the Streamlit application, run the following command in the terminal:

```bash
streamlit run app.py
```

Once the app is running, follow these steps:

1. Upload your survey response file (in Excel `.xlsx` or CSV `.csv` format).
2. Select the column from your file that contains the free-text responses.
3. Provide a short description of the survey context to aid the AI model.
4. Paste your OpenAI API key to power the analysis with GPT-4.

The app will process the file and utilize AI to derive meaningful insights from your survey data.

## API Key

You will need an OpenAI API key to use this application. Your API key is necessary for interacting with the OpenAI platform to perform analysis of the survey responses. You can obtain an API key from [OpenAI](https://platform.openai.com/).

Note: Your API key is not stored and will only be used for the duration of the analysis.

## Limitations

- The application currently supports only files in Excel or CSV format.
- A sample of 100 random responses is used for analysis to ensure performance; however, I may add functonality so you can adapt the sample size in the app.
- Users must provide their OpenAI API key each time they use the application.

## Acknowledgements

Survey Sight utilizes Streamlit for the creation of the web application and OpenAI's GPT-4 model for the analysis of survey responses.

