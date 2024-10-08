import os
import time
import random
import numpy as np
import pandas as pd
import streamlit as st
from openai import OpenAI
import plotly.express as px
from datetime import datetime
import plotly.graph_objects as go
from elasticsearch import Elasticsearch
from rag import gpt, build_prompt
from retrieval import elastic_search


es_client = Elasticsearch(
    ['https://0981a799a5854a61a951f3aa35152e54.europe-west1.gcp.cloud.es.io:443'],
    api_key=(elastic_api_key)
)
activities_df = pd.read_csv("./data/activities.csv")
client = OpenAI()
FEEDBACK_FILE = "./data/feedback_data.csv"

# Function to simulate itinerary generation
def generate_itinerary(duration, month, activities):
    
    # Query RAG/LLM for the response
    query = f"Travel itinerary for {duration} days"
    plan = elastic_search(query)[0]
    
    # Build the prompt based on user input
    params = {
        "days": duration,
        "activities": activities,
        "month": month,
        "plan": plan,
        "activity_list": activities_df[activities_df['activity'].isin(activities)],
    }
    
    # Generate the itinerary using GPT or your RAG system
    prompt = build_prompt(params)
    response = gpt(prompt)
    
    return response

def load_feedback_data():
    if os.path.exists(FEEDBACK_FILE):
        return pd.read_csv(FEEDBACK_FILE)
    return pd.DataFrame(columns=['timestamp', 'type', 'duration', 'month', 'activities'])

def save_feedback_data(df):
    df.to_csv(FEEDBACK_FILE, index=False)

def give_feedback(feedback_type):
    st.session_state.feedback_given = True
    st.session_state.feedback_type = feedback_type
    
    # Capture feedback with timestamp
    feedback = pd.DataFrame([{
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'type': feedback_type,
        'duration': st.session_state.duration,
        'month': st.session_state.month,
        'activities': ', '.join(st.session_state.activities)
    }])
    
    # Load existing feedback data
    df = load_feedback_data()
    
    # Concatenate new feedback
    df = pd.concat([df, feedback], ignore_index=True)
    
    # Save updated feedback data
    save_feedback_data(df)

def reset_app():
    st.session_state.feedback_given = False
    st.session_state.feedback_type = None
    st.session_state.itinerary_generated = False
    st.session_state.itinerary_response = None

def main():
    st.title("Barcelona Travel Itinerary Planner")

    # Initialize session state variables
    if 'page' not in st.session_state:
        st.session_state.page = 'planner'
    if "feedback_given" not in st.session_state:
        st.session_state.feedback_given = False
    if "feedback_type" not in st.session_state:
        st.session_state.feedback_type = None
    if "itinerary_generated" not in st.session_state:
        st.session_state.itinerary_generated = False
    if "itinerary_response" not in st.session_state:
        st.session_state.itinerary_response = None

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ('Itinerary Planner', 'Feedback Dashboard'))

    if page == 'Itinerary Planner':
        show_planner()
    else:
        show_dashboard()

def show_planner():
    # Input section
    st.session_state.duration = st.selectbox("Duration (in days)", ["one", "two", "three", "four", "five", "six", "seven"])
    st.session_state.month = st.selectbox("Month of Travel", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
    st.session_state.activities = st.multiselect("Activities", ['sightseeing', 'dining', 'adventure', 'relaxation', 'culture'])
    search_string = f"Curating your {st.session_state.duration}-day travel itinerary to Barcelona in {st.session_state.month} with {', '.join(st.session_state.activities)} activities."

    # Button to generate itinerary
    if st.button("Generate Itinerary"):
        if not st.session_state.activities:
            st.warning("Please select at least one activity.")
        else:
            st.info(search_string)
            
            with st.spinner("Generating your itinerary..."): 
                response = generate_itinerary(st.session_state.duration, st.session_state.month, st.session_state.activities)
                
            st.session_state.itinerary_response = response
            st.session_state.itinerary_generated = True

    # Display itinerary if generated
    if st.session_state.itinerary_generated:
        st.success("Here's your itinerary:")
        st.write(st.session_state.itinerary_response)

        # Feedback section
        if not st.session_state.feedback_given:
            st.write("Was this itinerary helpful?")
            col1, col2 = st.columns([1, 1])
            with col1:
                st.button("👍 Yes", on_click=give_feedback, args=('positive',))
            with col2:
                st.button("👎 No", on_click=give_feedback, args=('negative',))

        # Show feedback message after thumbs up or down
        if st.session_state.feedback_given:
            if st.session_state.feedback_type == 'positive':
                st.success("Thanks for your positive feedback!")
            else:
                st.success("Thanks for your feedback! We'll work on improving.")
            
            if st.button("Generate another itinerary"):
                reset_app()
                st.rerun()

def show_dashboard():
    st.header("Feedback Dashboard")
    
    df = load_feedback_data()
    
    if df.empty:
        st.write("No feedback data available yet.")
        return
    
    # 1. Overall satisfaction
    positive_feedback = df['type'].value_counts().get('positive', 0)
    total_feedback = len(df)
    satisfaction_rate = (positive_feedback / total_feedback) * 100 if total_feedback > 0 else 0
    
    st.subheader("1. Overall Satisfaction")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Satisfaction Rate", f"{satisfaction_rate:.2f}%")
    with col2:
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = satisfaction_rate,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Satisfaction"},
            gauge = {'axis': {'range': [0, 100]},
                     'bar': {'color': "darkblue"},
                     'steps' : [
                         {'range': [0, 50], 'color': "lightgray"},
                         {'range': [50, 75], 'color': "gray"},
                         {'range': [75, 100], 'color': "lightblue"}],
                     'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 90}}))
        st.plotly_chart(fig)

    # 2. Feedback over time
    st.subheader("2. Feedback Trend Over Time")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    feedback_counts = df.groupby(['date', 'type']).size().reset_index(name='count')
    
    fig = px.line(feedback_counts, x='date', y='count', color='type', 
                  title='Feedback Trend', labels={'count': 'Number of Feedbacks', 'date': 'Date'})
    st.plotly_chart(fig)
    
# 3. Popular activities
    st.subheader("3. Popular Activities")
    all_activities = []
    for activities in df['activities']:
        if isinstance(activities, str):  # Check if the value is a string
            all_activities.extend([activity.strip() for activity in activities.split(',')])
        elif pd.notna(activities):  # If it's not a string but also not NaN
            st.warning(f"Unexpected value in activities: {activities}")
    
    if all_activities:
        activity_counts = pd.Series(all_activities).value_counts()
        fig = px.bar(x=activity_counts.index, y=activity_counts.values, 
                     title='Activity Popularity', labels={'x': 'Activity', 'y': 'Count'})
        st.plotly_chart(fig)
    else:
        st.write("No activity data available.")
    
    # 4. Feedback distribution by trip duration
    st.subheader("4. Feedback Distribution by Trip Duration")
    duration_feedback = df.groupby('duration')['type'].value_counts().unstack()
    duration_feedback_pct = duration_feedback.div(duration_feedback.sum(axis=1), axis=0) * 100
    fig = px.bar(duration_feedback_pct, x=duration_feedback_pct.index, y=['positive', 'negative'],
                 title='Feedback Distribution by Trip Duration',
                 labels={'value': 'Percentage', 'duration': 'Trip Duration (days)'},
                 barmode='stack')
    st.plotly_chart(fig)

    # 5. Monthly satisfaction trends
    st.subheader("5. Monthly Satisfaction Trends")
    df['month'] = pd.to_datetime(df['timestamp']).dt.strftime('%B')
    monthly_satisfaction = df.groupby('month')['type'].value_counts().unstack()
    monthly_satisfaction_pct = monthly_satisfaction['positive'] / (monthly_satisfaction['positive'] + monthly_satisfaction['negative']) * 100
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    monthly_satisfaction_pct = monthly_satisfaction_pct.reindex(month_order)
    fig = px.line(x=monthly_satisfaction_pct.index, y=monthly_satisfaction_pct.values,
                  title='Monthly Satisfaction Trends',
                  labels={'x': 'Month', 'y': 'Satisfaction Rate (%)'})
    st.plotly_chart(fig)

    # Raw data
    st.subheader("Raw Feedback Data")
    st.dataframe(df)

# Run the app
if __name__ == "__main__":
    main()