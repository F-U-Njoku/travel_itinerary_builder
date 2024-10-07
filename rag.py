import os
from openai import OpenAI
OPENAI_API_KEY = "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"
client = OpenAI(api_key=OPENAI_API_KEY)


def build_prompt(params):
    prompt = f"""
    You are a travel assistant specialized in creating personalized short-trip itineraries for Barcelona.
    Your task is to plan a {params["days"]}-day itinerary by referring to a list of sample travel plans, taking into account the traveler’s activity preferences and the time of year.
    
    - Prioritize activities from the ACTIVITY-CATALOGUE that align with the traveler’s interests.
    - Adapt the itinerary to be suitable for the weather and season during the month of {params["month"]}.
    - Ensure that the chosen activities are spread across the duration of the trip to provide a balanced and enjoyable experience.
    
    Below are the details for your reference:
    
    DURATION: {params["days"]} days
    ACTIVITIES: {params["activities"]}
    MONTH: {params["month"]}
    
    SAMPLE PLANS: 
    {params["plan"]}
    
    ACTIVITY-CATALOGUE:
    {params["activity_list"]}
    
    Please create a thoughtful and well-structured itinerary considering these details.
    """.strip()
    
    return prompt

def gpt(prompt):
    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = [{"role":"user", "content": prompt}]
    )
    return response.choices[0].message.content