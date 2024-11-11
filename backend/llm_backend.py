import os
import sys
import requests
from typing import List
from pydantic import BaseModel

from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define SearchQuery schema
class SearchQuery(BaseModel):
    search_query: str

# Define search instructions
search_instructions = """
You are an assistant that extracts search queries from conversation messages.
Given the following conversation, please provide a concise search query that encapsulates the user's intent.

Conversation:
{messages}

Output the search query in the following JSON format:
{{
    "search_query": "your search query here"
}}
"""
base_url1 = os.getenv("OLLAMA_BASE_URL_A6000")
base_url2 = os.getenv("OLLAMA_BASE_URL_4090")
# Initialize the language model
model_local = ChatOllama(model="mistral-nemo:latest", base_url=base_url2)

# Initialize LangChain components
print("Welcome!")

# Add these near the top where other env variables are loaded
NUTRITION_DB_URL = os.getenv("NUTRITION_DB_URL")
STRENGTH_DB_URL = os.getenv("STRENGTH_DB_URL")
MINDSET_DB_URL = os.getenv("MINDSET_DB_URL")

# Define the vector search functions
def search_nutrition_vector(query: str) -> List[str]:
    """Perform a local vector search using the nutrition embeddings API."""
    # Add nutrition-specific prompt template
    nutrition_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a nutrition expert. Extract a search query focused on nutrition, diet, 
        supplements, and meal planning. Focus on:
        - Macronutrients and micronutrients
        - Meal timing and composition
        - Dietary restrictions and preferences
        - Supplement recommendations
        Only extract nutrition-related aspects from the query."""),
        ("user", "{input}")
    ])
    
    # Create query chain
    nutrition_query_chain = nutrition_prompt | model_local | StrOutputParser()
    
    try:
        # Generate specialized nutrition query
        search_query = nutrition_query_chain.invoke({"input": query}).strip()
        print(f"Nutrition search query: {search_query}")
        
        headers = {"Content-Type": "application/json"}
        payload = {"query_text": search_query}
        
        response = requests.post(NUTRITION_DB_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error querying nutrition vector search: {e}")
        return []

def search_strength_vector(query: str) -> List[str]:
    """Perform a local vector search using the strength training embeddings API."""
    # Add strength-specific prompt template
    strength_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a strength and conditioning expert. Extract a search query focused on:
        - Exercise technique and form
        - Training programming and periodization
        - Recovery and injury prevention
        - Performance optimization
        Only extract strength training and exercise-related aspects from the query."""),
        ("user", "{input}")
    ])
    
    # Create query chain
    strength_query_chain = strength_prompt | model_local | StrOutputParser()
    
    try:
        # Generate specialized strength query
        search_query = strength_query_chain.invoke({"input": query}).strip()
        print(f"Strength search query: {search_query}")
        
        headers = {"Content-Type": "application/json"}
        payload = {"query_text": search_query}
        
        response = requests.post(STRENGTH_DB_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error querying strength training vector search: {e}")
        return []

def search_mindset_vector(query: str) -> List[str]:
    """Perform a local vector search using the mindset and psychology embeddings API."""
    # Add mindset-specific prompt template
    mindset_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a sports psychology and mindset expert. Extract a search query focused on:
        - Mental preparation and focus
        - Motivation and goal setting
        - Stress management and anxiety
        - Behavioral change and habit formation
        Only extract psychological and mindset-related aspects from the query."""),
        ("user", "{input}")
    ])
    
    # Create query chain
    mindset_query_chain = mindset_prompt | model_local | StrOutputParser()
    
    try:
        # Generate specialized mindset query
        search_query = mindset_query_chain.invoke({"input": query}).strip()
        print(f"Mindset search query: {search_query}")
        
        headers = {"Content-Type": "application/json"}
        payload = {"query_text": search_query}
        
        response = requests.post(MINDSET_DB_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error querying mindset vector search: {e}")
        return []

# Define InterviewState class
class InterviewState:
    def __init__(self, messages: List[dict]):
        self.messages = messages

# Function to perform all three searches and combine contexts
def perform_combined_vector_searches(query: str) -> dict:
    """Perform searches and return merged results with follow-up questions."""
    try:
        # Get results from each domain
        nutrition_context = search_nutrition_vector(query)
        strength_context = search_strength_vector(query)
        mindset_context = search_mindset_vector(query)
        
        # Handle empty results with default messages
        nutrition_context = nutrition_context if nutrition_context else ["No relevant nutrition information found."]
        strength_context = strength_context if strength_context else ["No relevant strength training information found."]
        mindset_context = mindset_context if mindset_context else ["No relevant mindset information found."]
        
        # Merge and analyze the results
        merged_response = merge_and_analyze_results(
            query,
            nutrition_context,
            strength_context,
            mindset_context
        )
        
        # Generate follow-up questions based on the merged response
        follow_up_questions = generate_follow_up_questions(merged_response)
        
        # Return both the response and follow-up questions
        return {
            "response": merged_response,
            "follow_up_questions": follow_up_questions
        }
    except Exception as e:
        print(f"Error in combined search: {e}")
        return {
            "response": "Error performing combined search and analysis.",
            "follow_up_questions": [
                "Would you like to try a different question?",
                "Can I help clarify anything specific?",
                "What other aspects would you like to explore?"
            ]
        }

def merge_and_analyze_results(query: str, nutrition_results: List[str], strength_results: List[str], mindset_results: List[str]) -> str:
    """Merge and analyze results from all three domains into a cohesive response."""
    
    merge_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a holistic wellness coach who specializes in integrating nutrition, 
        strength training, and mindset coaching. Analyze the provided information and create a 
        comprehensive response that:

        1. Identifies connections between the three domains
        2. Prioritizes the most relevant information for the user's query
        3. Provides actionable recommendations that combine insights from all areas
        4. Highlights how each domain supports the others

        Format your response with:
        - A brief summary of the main insights
        - Key recommendations that integrate multiple domains
        - Specific action items for implementation
        
        Keep your response clear, practical, and focused on the user's original query."""),
        ("user", """Original Query: {query}

        Nutrition Insights:
        {nutrition_data}

        Strength Training Insights:
        {strength_data}

        Mindset Insights:
        {mindset_data}

        Please provide an integrated analysis and recommendation.""")
    ])

    # Create merge chain
    merge_chain = merge_prompt | model_local | StrOutputParser()
    
    try:
        # Format the input data
        nutrition_formatted = "\n".join(nutrition_results)
        strength_formatted = "\n".join(strength_results)
        mindset_formatted = "\n".join(mindset_results)
        
        # Generate integrated response
        merged_response = merge_chain.invoke({
            "query": query,
            "nutrition_data": nutrition_formatted,
            "strength_data": strength_formatted,
            "mindset_data": mindset_formatted
        })
        
        return merged_response
    except Exception as e:
        print(f"Error merging results: {e}")
        return "Error generating integrated response."

# Add this new function to k4-test.py
def process_rag_response(user_query, context):
    """Process a user query with the given context using the RAG chain."""
    after_rag_template = """You are a personal AI fitness and wellness coach analyzing the user's Whoop data. 

    Instructions for data analysis:
    1. The Whoop data is provided in JSON format - parse it carefully
    2. When analyzing metrics:
       - Focus on relevant data points
       - Highlight notable patterns or concerns
       - Provide meaningful insights
    3. Format your responses in a clear, conversational way:
       - Use bullet points for key insights
       - Focus on actionable insights rather than raw data

    Previous conversation and Whoop data context:
    {context}

    Current question: {question4}

    Instructions for response:
    1. Answer the question directly and decide if it is a question about the user's Whoop data or not
    2. If it is a question about the user's Whoop data, answer the question directly and concisely
    3. Focus on providing actionable insights rather than raw data

    Remember: Answer the question directly and concisely."""

    after_rag_prompt = ChatPromptTemplate.from_template(after_rag_template)
    
    # Set up the RAG chain
    after_rag_chain = (
        {
            "context": lambda x: context,
            "question4": lambda x: x
        }
        | after_rag_prompt
        | model_local
        | StrOutputParser()
    )
    
    response = after_rag_chain.invoke(user_query)
    
    # Generate follow-up questions based on the response
    follow_up_questions = generate_follow_up_questions(response)
    
    return {
        "response": response,
        "follow_up_questions": follow_up_questions
    }

def generate_follow_up_questions(response: str) -> list:
    """Generate 3 potential user questions based on the AI's response content."""
    
    question_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an AI assistant helping to identify questions a user might have about the given response.
        
        Analyze the response and generate 3 questions that:
        1. A user might ask to clarify specific points mentioned
        2. Questions about details that weren't fully explained
        3. Questions that probe deeper into the recommendations or insights provided
        
        For example, if the response discusses sleep patterns and mentions "sleep efficiency",
        a user might ask "What exactly is sleep efficiency and how is it calculated?"
        
        Guidelines:
        - Put yourself in the user's shoes - what would they want to know more about?
        - Focus on terms, concepts, or recommendations that might need more explanation
        - Ask about specific details or numbers mentioned in the response
        - Question the "why" and "how" behind statements made
        
        Return exactly three questions in this format:
        1. First user question here?
        2. Second user question here?
        3. Third user question here?
        
        Keep questions natural and conversational, as if a real user is asking them."""),
        ("user", "AI Response: {response}\n\nWhat questions might a user have about this response?")
    ])
    
    # Create question generation chain
    question_chain = question_prompt | model_local | StrOutputParser()
    
    try:
        # Generate questions
        questions_str = question_chain.invoke({"response": response})
        
        # Parse the numbered questions
        questions = []
        for line in questions_str.split('\n'):
            if line.strip() and any(line.startswith(f"{i}.") for i in range(1, 4)):
                # Remove the number and leading/trailing whitespace
                question = line.split('.', 1)[1].strip()
                questions.append(question)
        
        # Ensure we have exactly 3 questions
        if len(questions) > 3:
            questions = questions[:3]
        while len(questions) < 3:
            questions.append("Can you explain more about what you just mentioned?")
            
        return questions
    except Exception as e:
        print(f"Error generating follow-up questions: {e}")
        return [
            "Could you explain that in more detail?",
            "Why is this important for my health?",
            "How can I implement these suggestions?"
        ]

# Main execution block
if __name__ == "__main__":
    # Example user query
    user_query = "hydration recovery plan recommendation"
    
    # Get merged response
    final_response = perform_combined_vector_searches(user_query)
    