# Travel Itinerary Planner (TIP)
<p align="center">
  <img src="./media/banner.webp">
</p>

# Overview
As the seasons change, so do the activities available during a vacation. Living in Barcelona, one of Europe’s top travel destinations, I’m often asked by friends and family for suggestions on things to do when they visit. Typically, these trips are short (1 - 7 days), lasting just one to three days. To make planning easier, I’m developing TIP, an AI-powered Travel Itinerary Planner using Retrieval-Augmented Generation (RAG). This tool tailors itineraries for short trips in Barcelona, taking into account the weather, activity preferences, and duration of stay.

# Data
This project relies on two data sources:
- Local Attractions and Activities 
- Travel Guides and Blogs

The attractions and activities data is obtained using Google Places API, while web scrapping is used to get the travel guides and blogs.

# Ingestion
The ingestion of the data is done through the ``ingestion.ipynb`` notebook. To execute this, it is important to have a Google Places API key.
# RAG flow 
<p align="center">
  <img src="./media/tip.webp">
</p>
The image above summarizes the RAG flow. Data is obtained using Google Places API and web scrapping and then ingested into two knowledge-based systems: Elastic search and FAISS (Facebook AI Similarity Search). In all, there are three possibilities considered for retrieving data from the knowledge base:

- Keyword Search with Elastic
- Semantic Search with Elastic (Cosine Similarity)
- Semantic Search with FAISS (L2 Distance)

Finally, the generation is done with openAI chatGPT 4o-mini implemented in the ``rag.py`` script.

# Evaluation
 The three retrieval approaches were evaluated using Hit-rate. Although the first two have the same scores, keyword search with Elastic was chosen since it has a lower computational requirement (no need for encoding). Details of the retrieval evaluation are in the ``retrieval.ipynb`` notebook.
 <p align="center">
  <img src="./media/hitrate.png">
</p>

Using LLM as a judge, the RAG was evaluated on 140 prompts; it got an average score of 8.58 out of 10.
 <p align="center">
  <img src="./media/rag_score.png">
</p>

# Demo
The main application can be found in the ``tip_app.py`` file. The user interface is done using Streamlit, and here is a short demo.

[![Barcelona Travel Itinerary Planner](https://img.youtube.com/vi/ZtX04XflwiA/0.jpg)](https://youtu.be/ZtX04XflwiA)

# Deployement
The application is deployed and available on Streamlit Streamlit Community Cloud, [click here](https://f-u-njoku-travel-itinerary-builder-tip-app-fagzoi.streamlit.app/)

# Monitoring
Feedback is collected from each user via a thumbs-up and down button. This is stored and monitored in a Plotly dashboard displayed using Streamlit, and below is a video demonstrating this.

[![IMonitoring](https://img.youtube.com/vi/SWm8kX58fZg/0.jpg)](https://youtu.be/SWm8kX58fZg)

# Remarks
This project can be extended to more cities and will be my next step. Also, trying other LLMs besides ChatGPT will be an exciting experiment.

# Acknowledgement
I thank the Datatalks club for putting such a practical course together for free and giving me the first dive into Large Language Models. Thanks to Alexey and the entire team.
