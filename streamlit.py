import os
import streamlit as st
from lyzr import VoiceBot
from models import process
from pydub import AudioSegment
import librosa
import warnings
import numpy as np
import zipfile
import plotly.graph_objects as go

warnings.filterwarnings("ignore")

# Create an instance of the processing model
p = process()

class Processor:
    def __init__(self):
        self.vb = VoiceBot(api_key="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")

    def transcribe_audio(self, audio_file_path):
        transcript = self.vb.transcribe(audio_file_path)
        return transcript

    def classify_text(self, trans_data):
        prompt = """
          As a classifier, you need to classify the provided text into one of the following categories: 
          Cancellation, Flight Reschedule, Flight Refund Related, Flight Delay Complaint, Staff Behavior Complaint, Miscellaneous. 
          
          Provide the contents in the format: category"
          """
        res = prompt + "Conversations start here:\n" + trans_data
        output = p.send_message(res)
        return output
    
    def calculate_first_call_resolution(self, trans_data):
        prompt="""
        Develop a system to evaluate customer service agent performance based on First Call Resolution (FCR). FCR measures the percentage of calls resolved on the initial interaction. Use transcribed data to identify keywords indicating subsequent conversations, allowing accurate determination of FCR success. Return True or False.
        either give me :
        True or False as the return value
        """
        res = prompt + "Conversations start here:\n" + trans_data
        output = p.send_message(res)
        return output
    
    def calculate_call_resolution_rate(self, trans_data):
        prompt="""
        Calculate the Call Resolution Rate: The percentage of calls that result in the caller's issue being resolved, indicating the effectiveness of the agents' problem-solving skills. Return a value in boolean:
        either give me :
        True or False as the return value
        """
        res = prompt + "Conversations start here:\n" + trans_data
        output = p.send_message(res)
        return output
    
    def identify_call_transfers(self, trans_data):
        # prompt="""
        # Calculate the Call Transfer Rate: Measures how often calls are transferred to another agent or department, which can indicate the need for better first-contact resolution or agent training,the agent who made the transfer.
        # do need of 
        # """
        prompt = """
        Just analyze the transcribed data thus the call transfer has been carried out in the call.Assume that as your knowledge words that will be used while transfering the call occuring
        return Either True  or False
        """
        res = prompt + "Conversations start here:\n" + trans_data
        output = p.send_message(res)
        return output
    def identify_call_abandonment(self, trans_data):
        # Placeholder for logic to identify call abandonment
        # This could be specific phrases in the transcript that indicate abandonment
        abandonment_keywords = [
    "call ended unexpectedly",
    "caller disconnected",
    "hung up",
    "disconnected",
    "no response",
    "line dead",
    "dropped the call"
]
        return any(keyword in trans_data.lower() for keyword in abandonment_keywords)
    
    def error_rate(self, transdata):
        misinformation_keywords = ["Incorrectly stated", "Mistakenly", "Erroneously", "Inaccurately", "Misinformed", "Wrongly", "Falsely", "Incorrect", "Not true", "Apologies, we were mistaken", "Correction", "Reevaluation", "Clarification", "Contrary to what was stated", "I misspoke", "I stand corrected", "Contrary to earlier information", "My earlier statement was inaccurate", "Upon further review", "Upon double-checking", "Falsehood", "Error", "Mistake", "Misinterpretation", "Misrepresentation", "Flawed", "In error", "Not accurate", "Not correct", "Contradictory", "Not factual", "Not reliable", "Misleading", "Misconception", "Inconsistency", "Inexact", "Misunderstanding", "Debunked", "Refuted", "Discredited", "Unverified", "Speculative", "Assumption-based", "Unconfirmed", "Hypothetical", "Presumptive", "Misguiding", "Ill-informed", "Unsubstantiated", "Baseless", "Factually incorrect", "Disproven", "Invalidated", "Questionable", "Dubious", "Suspect", "Uncertain", "In dispute", "Controversial", "Disputed", "Deceptive", "Fraudulent"]
        
        # Normalize the transcription to lower case for comparison
        transdata_lower = transdata.lower()
        
        # Count occurrences of each misinformation keyword
        keyword_count = sum(transdata_lower.count(keyword.lower()) for keyword in misinformation_keywords)
        
        # Simple error rate calculation (for illustration)
        # This part is highly simplified and would need adjustment based on the length of the text,
        # the severity of each keyword, context, etc.
        words = transdata.split()
        if len(words) == 0: return 0  # Avoid division by zero
        
        error_rate = (keyword_count / len(words)) * 100  # Basic error rate as a percentage of keywords to total words
        
        return error_rate

    def calculate_silence_ratio_librosa(self, audio_file_path, frame_length=2048, hop_length=512):
        y, sr = librosa.load(audio_file_path, sr=None)
        # Calculate the energy (squared amplitude) of the signal
        energy = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
        
        # Dynamically determine a threshold based on the energy; this might need tuning
        threshold = np.percentile(energy, 10)  # Using the 10th percentile as threshold
        
        # Count frames below the threshold as silent
        silent_frames = np.sum(energy < threshold)
        total_frames = len(energy)
        
        # Calculate durations
        total_duration = len(y) / sr  # Total duration in seconds
        silence_duration = silent_frames * hop_length / sr  # Silence duration in seconds
        
        # Calculate the silence ratio
        silence_ratio = (silence_duration / total_duration) * 100
        
        return silence_ratio

# Create an instance of the Processor class
processor = Processor()

# Streamlit app
def main():
    st.title("Audio Analysis App")

    uploaded_file = st.file_uploader("Upload a zip file containing audio files", type="zip")
    if uploaded_file is not None:
        # Save the uploaded zip file
        with open("temp.zip", "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Unzip the file
        with zipfile.ZipFile("temp.zip", "r") as zip_ref:
            zip_ref.extractall("data")
        
        # Get all audio files in the directory
        audio_files_directory = "data\Audiofiles"
        audio_files = [os.path.join(audio_files_directory, f) for f in os.listdir(audio_files_directory) if f.endswith(".mp3")]
        
        # Initialize variables for metrics
        total_calls = 0
        fcr_calls = 0
        resolved_calls = 0
        call_transfers = 0
        abandoned_calls = 0
        total_duration_seconds = 0
        total_files = 0
        over_duration_calls = 0
        min_duration = float('inf')  # Initialize to positive infinity
        max_duration = 0 
        overcall_rate_list=[]

        # Process each audio file
        for audio_file_path in audio_files:
            # Perform transcription
            transcription = processor.transcribe_audio(audio_file_path)
            st.header(f"Results for {os.path.basename(audio_file_path)}:")
            # st.write(transcription)
            classification_result = processor.classify_text(transcription)
            st.write(f"Classification result for {os.path.basename(audio_file_path)}: {classification_result}")

            # Calculate silence ratio
            silence_ratio = processor.calculate_silence_ratio_librosa(audio_file_path)
            st.subheader(f"Silence Ratio")
            st.write(f"Silence Ratio for {os.path.basename(audio_file_path)}: {silence_ratio:.2f}%")
            # Calculate error rate
            error_rate = processor.error_rate(transcription)
            st.subheader("Error Rate")
            st.write(f"Error Rate for {os.path.basename(audio_file_path)}: {error_rate:.2f}%")

            # Check if FCR was achieved
            fcr_result = processor.calculate_first_call_resolution(transcription)
            if fcr_result =="True" :
                fcr_calls += 1

            # Check if the call was resolved
            resolved_result = processor.calculate_call_resolution_rate(transcription)
            if resolved_result == "True":
                resolved_calls += 1

            # Identify call transfers
            transfer_details = processor.identify_call_transfers(transcription)
            if transfer_details == "True":
                # call_transfers.append((os.path.basename(audio_file_path), transfer_details))
                call_transfers+=1

            total_calls += 1
            if processor.identify_call_abandonment(transcription):
                abandoned_calls += 1
                # Skip further analysis for abandoned calls
            
            audio_duration_seconds = librosa.get_duration(filename=audio_file_path)
            audio_duration_minutes = audio_duration_seconds/60
            overcall_rate_list.append(audio_duration_minutes)
            if audio_duration_seconds > max_duration:
                max_duration = audio_duration_seconds
            if audio_duration_seconds < min_duration:
                min_duration = audio_duration_seconds

            threshold_seconds = 180

            if audio_duration_seconds > threshold_seconds:
                over_duration_calls += 1
            total_duration_seconds += audio_duration_seconds
            total_files += 1

        # Calculate FCR percentage
        if total_calls > 0:
            fcr_percentage = (fcr_calls / total_calls) * 100
            # st.header(f"First Call Resolution Percentage: {fcr_percentage}%")
            st.header("First Call Resolution Percentage")
            fig = go.Figure(data=[go.Pie(labels=['FCR', 'Not FCR'], values=[fcr_percentage, 100 - fcr_percentage])])
            fig.update_layout()
            st.plotly_chart(fig)
        else:   
            st.write("No audio files found for processing.")

        # Calculate Call Resolution Rate percentage
        if total_calls > 0:
            resolution_rate_percentage = (resolved_calls / total_calls) * 100
            # st.write(f"Call Resolution Rate Percentage: {resolution_rate_percentage}%")
            st.header("Call Resolution Rate Percentage")
            fig = go.Figure(data=[go.Pie(labels=['RR(Resolution Rate)', 'Not RR'], values=[resolution_rate_percentage, 100 - resolution_rate_percentage])])
            fig.update_layout(title='Resolution Rate')
            st.plotly_chart(fig)
        else:
            st.write("No audio files found for processing.")

        # Print call transfers
        if call_transfers>0:
            # st.write("Call Transfers:")
            # for audio_file, transfer_details in call_transfers:
            #     st.write(f"Audio File: {audio_file}")
            #     st.write(transfer_details)
            call_percentage = (call_transfers/total_calls)*100
            # st.write(f"Transfer Rate: {call_percentage}%")
            st.header("Transfer Rate")
            fig = go.Figure(data=[go.Pie(labels=['CT(Call Transfer)', 'Not CT'], values=[call_percentage, 100 - call_percentage])])
            fig.update_layout(title='Call Transfer Rate')
            st.plotly_chart(fig)
        else:
            st.write("No call transfers found.")

        # Calculate Call Abandonment Rate percentage
        if total_calls > 0:
            abandonment_rate_percentage = (abandoned_calls / total_calls) * 100
            st.header(f"Call Abandonment Rate: {abandonment_rate_percentage:.2f}%")
        else:
            st.write("No audio files found for processing.")
        #averagetime
        if total_files > 0:
            average_duration_minutes = (total_duration_seconds / total_files) / 60
            
            min_duration_minutes = min_duration / 60
            max_duration_minutes = max_duration / 60

# Create a bar chart
            fig = go.Figure(data=[
    go.Bar(name='Minimum Duration', x=['Duration'], y=[min_duration_minutes]),
    go.Bar(name='Maximum Duration', x=['Duration'], y=[max_duration_minutes]),
    go.Bar(name='Average Duration', x=['Duration'], y=[average_duration_minutes])
])

# Update the layout of the chart
            fig.update_layout(title='Call Duration Statistics',
                  xaxis=dict(title='Duration'),
                  yaxis=dict(title='Duration (minutes)'),
                  barmode='group')

# Display the chart
            st.plotly_chart(fig)
            st.subheader(f"Average Duration per Call: {average_duration_minutes:.2f} minutes")
        else:
            st.write("No audio files found for processing.")

        if total_files > 0:

            overcall_rate = (over_duration_calls / total_files) * 100
            # Create a horizontal bar chart
            st.header("Overcall Rate Calculation")
            fig = go.Figure(go.Bar(
                y=[f'Call {i}' for i in range(1, len(overcall_rate_list)+1)],  # Labels for each call
                x=overcall_rate_list,
                orientation='h'
            ))

            # Update the layout of the chart
            fig.update_layout(title='Call Duration',
                            xaxis=dict(title='Duration (minutes)'),
                            yaxis=dict(title='Call'))

            # Display the chart
            st.plotly_chart(fig)
            st.subheader(f"Overcall rate: {overcall_rate:.2f}%")
        else:
            st.sheader("No audio files found for processing.")

        # Cleanup
        os.remove("temp.zip")
        st.success("Processing complete!")


if __name__ == "__main__":
    main()


