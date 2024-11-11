import os
import sys
import requests
from typing import List
from pydantic import BaseModel
import json

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
def perform_combined_vector_searches(query: str, whoop_data: dict = None) -> dict:
    """Perform intelligent domain-specific searches based on query relevance."""
    try:
        # Analyze domain relevance
        relevance_scores = analyze_query_relevance(query, whoop_data or {})
        
        # Initialize results
        results = {
            "nutrition": [],
            "strength": [],
            "mindset": []
        }
        
        # Process each domain based on relevance
        if relevance_scores["nutrition"] > 0.3:
            specialized_query = generate_specialized_query("nutrition", query, whoop_data)
            results["nutrition"] = search_nutrition_vector(specialized_query)
            
        if relevance_scores["strength"] > 0.3:
            specialized_query = generate_specialized_query("strength", query, whoop_data)
            results["strength"] = search_strength_vector(specialized_query)
            
        if relevance_scores["mindset"] > 0.3:
            specialized_query = generate_specialized_query("mindset", query, whoop_data)
            results["mindset"] = search_mindset_vector(specialized_query)
        
        # Merge and analyze results with enhanced context
        merged_response = merge_and_analyze_results(
            query,
            results["nutrition"],
            results["strength"],
            results["mindset"],
            whoop_data
        )
        
        # Generate personalized follow-up questions
        follow_up_questions = generate_follow_up_questions(merged_response)
        
        return {
            "response": merged_response,
            "follow_up_questions": follow_up_questions,
            "domain_relevance": relevance_scores
        }
    except Exception as e:
        print(f"Error in combined search: {e}")
        return {
            "response": "Error performing combined search and analysis.",
            "follow_up_questions": [
                "Would you like to try a different question?",
                "Can I help clarify anything specific?",
                "What other aspects would you like to explore?"
            ],
            "domain_relevance": {"nutrition": 0, "strength": 0, "mindset": 0}
        }

def merge_and_analyze_results(query: str, nutrition_results: List[str], 
                            strength_results: List[str], mindset_results: List[str], 
                            whoop_data: dict = None) -> str:
    """Merge and analyze results with enhanced personalization and actionable recommendations."""
    
    merge_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a holistic wellness coach providing personalized recommendations.
        
        Analysis Guidelines:
        1. Integrate insights from all available domains
        2. Reference specific Whoop data metrics when relevant
        3. Prioritize high-impact, achievable recommendations
        4. Consider the interconnections between domains
        
        Response Format:
        1. Key Insights
           - Summary of main findings
           - Relevant Whoop data patterns
           
        2. Personalized Recommendations
           - Prioritized by impact and feasibility
           - SMART goals (Specific, Measurable, Achievable, Relevant, Time-bound)
           
        3. Implementation Strategy
           - Specific steps for each recommendation
           - Progress tracking metrics
           - Potential challenges and solutions"""),
        ("user", """Query: {query}
        
        Whoop Data: {whoop_data}
        
        Domain Insights:
        Nutrition: {nutrition_data}
        Strength: {strength_data}
        Mindset: {mindset_data}
        
        Provide personalized analysis and recommendations.""")
    ])
    
    # Create merge chain
    merge_chain = merge_prompt | model_local | StrOutputParser()
    
    try:
        merged_response = merge_chain.invoke({
            "query": query,
            "whoop_data": json.dumps(whoop_data or {}),
            "nutrition_data": "\n".join(nutrition_results),
            "strength_data": "\n".join(strength_results),
            "mindset_data": "\n".join(mindset_results)
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
    1. The Whoop data is provided in JSON format - parse it carefully and analyze ALL available days
    2. When analyzing metrics:
       - Focus on relevant data points across the entire time period
       - Highlight notable patterns or trends across all days
       - Compare metrics between different days
       - Identify both positive trends and areas of concern
    3. Format your responses in a clear, conversational way:
       - Use bullet points for key insights
       - Include specific data points from multiple days when relevant
       - Provide context for your observations
       - Make recommendations based on the complete dataset

    Previous conversation and Whoop data context:
    {context}

    Current question: {question4}

    Instructions for response:
    1. First, scan through ALL days of data provided
    2. Look for patterns and trends across the entire time period
    3. When answering, reference specific dates and data points to support your insights
    4. Provide a comprehensive analysis that considers the full dataset
    5. If data is missing for certain days, acknowledge this in your response

    Remember: 
    - Analyze the complete dataset, not just recent days
    - Support your insights with specific data points from multiple days
    - Provide actionable recommendations based on the full picture"""

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

# Add these new functions after the existing imports

def analyze_query_relevance(query: str, whoop_data: dict) -> dict:
    """Determine the relevance of each domain based on the query and Whoop data."""
    
    relevance_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert in analyzing fitness and wellness queries. 
        Determine the relevance of each domain (nutrition, strength, mindset) for the given query 
        and Whoop data. Score each domain from 0-1 based on relevance.
        
        Consider:
        1. Query keywords and intent
        2. Patterns in the Whoop data
        3. Potential impact on user's goals
        
        You must respond with ONLY a valid JSON object in this exact format:
        {{
            "nutrition": 0.5,
            "strength": 0.5,
            "mindset": 0.5
        }}
        
        - Each score must be a number between 0 and 1
        - Do not include any other text or explanation
        - Ensure the response is valid JSON"""),
        ("user", """Query: {query}
        Whoop Data: {whoop_data}
        
        Return domain relevance scores as JSON.""")
    ])
    
    # Create relevance analysis chain
    relevance_chain = relevance_prompt | model_local | StrOutputParser()
    
    try:
        # Generate relevance scores
        response = relevance_chain.invoke({
            "query": query,
            "whoop_data": json.dumps(whoop_data)
        }).strip()
        
        # Clean the response to ensure it's valid JSON
        # Remove any leading/trailing text that isn't part of the JSON
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response[json_start:json_end]
            try:
                scores = json.loads(json_str)
                # Validate and clean the scores
                cleaned_scores = {
                    "nutrition": min(max(float(scores.get("nutrition", 0.5)), 0), 1),
                    "strength": min(max(float(scores.get("strength", 0.5)), 0), 1),
                    "mindset": min(max(float(scores.get("mindset", 0.5)), 0), 1)
                }
                return cleaned_scores
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error parsing JSON response: {e}")
                print(f"Raw response: {response}")
        else:
            print(f"Could not find valid JSON in response: {response}")
        
        # Return default scores if parsing fails
        return {"nutrition": 0.5, "strength": 0.5, "mindset": 0.5}
    except Exception as e:
        print(f"Error analyzing query relevance: {e}")
        print(f"Full error: {str(e)}")
        return {"nutrition": 0.5, "strength": 0.5, "mindset": 0.5}

def generate_specialized_query(domain: str, query: str, whoop_insights: dict) -> str:
    """Generate a specialized query for a specific domain incorporating Whoop insights."""
    
    specialization_prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are a {domain} specialist creating a focused search query.
        Consider:
        1. The user's original question
        2. Relevant Whoop data insights
        3. Key metrics and patterns
        
        Generate a specific query that will retrieve the most relevant {domain} information.
        
        Examples:
        Original: "How can I improve recovery?"
        Specialized (Nutrition): "nutrition strategies optimal recovery athletes hydration protein timing"
        Specialized (Strength): "workout recovery techniques active recovery training load management"
        Specialized (Mindset): "mental recovery strategies stress management sleep optimization"
        """),
        ("user", """Original Query: {query}
        Whoop Insights: {insights}
        
        Generate specialized search query.""")
    ])
    
    # Create specialization chain
    specialization_chain = specialization_prompt | model_local | StrOutputParser()
    
    try:
        # Generate specialized query
        specialized_query = specialization_chain.invoke({
            "query": query,
            "insights": json.dumps(whoop_insights)
        })
        return specialized_query.strip()
    except Exception as e:
        print(f"Error generating specialized query: {e}")
        return query

# Main execution block
if __name__ == "__main__":
    # Example user query
    user_query = "hydration recovery plan recommendation"
    
    # Get merged response
    final_response = perform_combined_vector_searches(user_query)
    