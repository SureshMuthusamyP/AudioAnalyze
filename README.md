# AudioAnalyze

Audio Analysis App
This application is designed for analyzing audio files to extract various metrics and insights from them. It supports the analysis of multiple audio files uploaded in a ZIP format.

## Features
- Transcription: The application transcribes audio files into text using a voice recognition API.
- Classification: It classifies transcribed text into predefined categories such as Cancellation, Flight Reschedule, Flight Refund Related, Flight Delay Complaint, Staff Behavior Complaint, and Miscellaneous.
- Silence Ratio Calculation: Calculates the ratio of silence to speech in the audio files.
- Error Rate: Analyzes the text for errors or misinformation based on predefined keywords.
- First Call Resolution (FCR) Percentage: Calculates the percentage of calls resolved on the initial interaction.
- Call Resolution Rate Percentage: Determines the percentage of calls that result in the caller's issue being resolved.
- Call Transfer Rate: Identifies the rate at which calls are transferred to another agent or department.
- Call Abandonment Rate: Calculates the percentage of calls that are abandoned by the caller.
- Call Duration Statistics: Provides statistics on the minimum, maximum, and average duration of calls.
- Overcall Rate Calculation: Calculates the percentage of calls exceeding a specified threshold duration.

## Usage
1. Upload a ZIP file containing audio files.
2. The application will process each audio file individually and display the results.
3. Results include transcription, classification, silence ratio, error rate, FCR percentage, resolution rate percentage, call transfer rate, call abandonment rate, call duration statistics, and overcall rate calculation.

## Dependencies
- streamlit: For building the web application interface.
- lyzr: For interacting with the voice recognition API.
- pydub: For audio file manipulation.
- librosa: For audio analysis.
- plotly: For generating interactive visualizations.
- requests: For making HTTP requests to the OpenAI API.
- python-dotenv: For loading environment variables.

## Setup
1. Install the required dependencies using `pip install -r requirements.txt`.
2. Obtain an API key for the voice recognition API and the OpenAI API.
3. Set up environment variables for the API keys in a `.env` file.

---




Audi Analyze Portal deployed on streamlit Cloud:https://audioanalyze.streamlit.app/
Feedback portal deployed:https://feedbackapp.streamlit.app/
Customer Feedback retrieval Portal:https://analyzesms.streamlit.app/
