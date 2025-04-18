import streamlit as st
import pandas as pd
import numpy as np
import json
import openai
from openai import OpenAI

# Set page configuration
st.set_page_config(
    page_title="Career Discovery Platform",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS for styling
st.markdown("""
<style>
    .main {
        padding: 1rem;
    }
    .step-header {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* Override Streamlit's button colors for selected state */
    .stButton button[data-baseweb="button"][kind="primary"] {
        background-color: #1976d2 !important;
        border-color: #1976d2 !important;
        color: white !important;
    }
    
    /* Hover state for selected buttons */
    .stButton button[data-baseweb="button"][kind="primary"]:hover {
        background-color: #1565c0 !important;
        border-color: #1565c0 !important;
    }
    
    /* Define styles directly for spans instead of using classes */
    span.tag {
        background-color: #f1f1f1;
        border-radius: 1rem;
        padding: 0.2rem 0.6rem;
        margin-right: 0.3rem;
        margin-bottom: 0.3rem;
        display: inline-block;
        font-size: 0.8rem;
    }
    
    span.interest-tag {
        background-color: #e1f5fe;
        color: #0277bd;
        border-radius: 1rem;
        padding: 0.2rem 0.6rem;
        margin-right: 0.3rem;
        margin-bottom: 0.3rem;
        display: inline-block;
        font-size: 0.8rem;
    }
    
    span.skill-tag {
        background-color: #e8f5e9;
        color: #2e7d32;
        border-radius: 1rem;
        padding: 0.2rem 0.6rem;
        margin-right: 0.3rem;
        margin-bottom: 0.3rem;
        display: inline-block;
        font-size: 0.8rem;
    }
    
    span.sdg-tag {
        background-color: #ede7f6;
        color: #5e35b1;
        border-radius: 1rem;
        padding: 0.2rem 0.6rem;
        margin-right: 0.3rem;
        margin-bottom: 0.3rem;
        display: inline-block;
        font-size: 0.8rem;
    }
    
    .career-card {
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        overflow: hidden;
        margin-bottom: 1.5rem;
        transition: all 0.2s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .career-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
    }
    
    .career-header {
        background-color: #1976d2;
        color: white;
        padding: 1rem;
    }
    
    .career-content {
        padding: 1rem;
    }
    
    .step-container {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    
    .progress-step {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
    }
    
    .progress-active {
        background-color: #1976d2;
        color: white;
    }
    
    .progress-complete {
        background-color: #4caf50;
        color: white;
    }
    
    .progress-inactive {
        background-color: #e0e0e0;
        color: #757575;
    }
    
    .top-match {
        border: 2px solid #1976d2;
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
    }
    
    .method-tabs {
        display: flex;
        margin-bottom: 1rem;
    }
    
    .method-tab {
        padding: 0.5rem 1rem;
        border-radius: 0.5rem 0.5rem 0 0;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .tab-active {
        background-color: #1976d2;
        color: white;
    }
    
    .tab-inactive {
        background-color: #e0e0e0;
        color: #757575;
    }
    
    /* Result comparison styling */
    .comparison-card {
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: #f8f9fa;
    }
    
    .verdict-card {
        background-color: #fff8e1;
        border: 1px solid #ffd54f;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-top: 1rem;
    }
    
    .manual-badge {
        background-color: #e0e0e0;
        color: #616161;
        border-radius: 1rem;
        padding: 0.2rem 0.6rem;
        margin-right: 0.3rem;
        font-size: 0.7rem;
    }
    
    .ai-badge {
        background-color: #bbdefb;
        color: #1565c0;
        border-radius: 1rem;
        padding: 0.2rem 0.6rem;
        margin-right: 0.3rem;
        font-size: 0.7rem;
    }
    
    .judge-badge {
        background-color: #fff8e1;
        color: #ff8f00;
        border-radius: 1rem;
        padding: 0.2rem 0.6rem;
        margin-right: 0.3rem;
        font-size: 0.7rem;
    }
</style>
""", unsafe_allow_html=True)

# Career data with mappings to interests, skills, and SDGs
@st.cache_data
def load_career_data():
    careers = [
        {
            "id": 1,
            "title": "Microfinance Specialist",
            "description": "Designs small loans and savings programs to support underserved communities.",
            "interests": ["Economics", "Business Studies / Entrepreneurship", "Global Politics / Civics"],
            "skills": ["Strategic thinking", "Data analysis", "Helping people", "Understanding cultures"],
            "sdgs": [1, 8, 10]  # No Poverty, Decent Work & Economic Growth, Reduced Inequalities
        },
        {
            "id": 2,
            "title": "Agroecologist",
            "description": "Applies ecological science to farming for healthier food systems and better soil.",
            "interests": ["Biology", "Environmental Systems & Societies / Environmental Science", "Agriculture / Sustainable Farming"],
            "skills": ["Working outdoors", "Problem solving", "Supporting the planet", "Working with animals"],
            "sdgs": [2, 13, 15]  # Zero Hunger, Climate Action, Life on Land
        },
        {
            "id": 3,
            "title": "Biomedical Engineer",
            "description": "Develops medical devices like prosthetics, diagnostic tools, and wearable tech.",
            "interests": ["Biology", "Physics", "Engineering (General or Applied)", "Design & Technology / Engineering"],
            "skills": ["Problem solving", "Building or fixing", "Using tools/machines", "Helping people"],
            "sdgs": [3, 9, 10]  # Good Health & Well-Being, Industry/Innovation/Infrastructure, Reduced Inequalities
        },
        {
            "id": 4,
            "title": "Digital Learning Developer",
            "description": "Creates educational games, apps, and platforms for digital learning.",
            "interests": ["Computer Science / Programming", "Education", "Design & Technology / Engineering"],
            "skills": ["Coding", "Designing digitally", "Writing or storytelling", "Explaining ideas"],
            "sdgs": [4, 9, 10]  # Quality Education, Industry/Innovation/Infrastructure, Reduced Inequalities
        },
        {
            "id": 5,
            "title": "Hydrologist",
            "description": "Studies the water cycle and helps improve clean water access and conservation.",
            "interests": ["Environmental Systems & Societies / Environmental Science", "Geography", "Chemistry"],
            "skills": ["Data analysis", "Working outdoors", "Supporting the planet", "Problem solving"],
            "sdgs": [6, 13, 14]  # Clean Water & Sanitation, Climate Action, Life Below Water
        },
        {
            "id": 6,
            "title": "Wind Turbine Technician",
            "description": "Installs and maintains turbines that convert wind into clean electricity.",
            "interests": ["Physics", "Engineering (General or Applied)", "Environmental Systems & Societies / Environmental Science"],
            "skills": ["Building or fixing", "Working outdoors", "Using tools/machines", "Supporting the planet"],
            "sdgs": [7, 8, 13]  # Affordable & Clean Energy, Decent Work & Economic Growth, Climate Action
        },
        {
            "id": 7,
            "title": "Waste Management Engineer",
            "description": "Designs systems for composting, recycling, and waste reduction.",
            "interests": ["Environmental Systems & Societies / Environmental Science", "Chemistry", "Engineering (General or Applied)"],
            "skills": ["Problem solving", "Strategic thinking", "Supporting the planet", "Building or fixing"],
            "sdgs": [11, 12, 13]  # Sustainable Cities, Responsible Consumption & Production, Climate Action
        },
        {
            "id": 8,
            "title": "Circular Economy Analyst",
            "description": "Redesigns how companies produce and reuse materials to reduce waste.",
            "interests": ["Business Studies / Entrepreneurship", "Environmental Systems & Societies / Environmental Science", "Economics"],
            "skills": ["Strategic thinking", "Data analysis", "Supporting the planet", "Standing up for causes"],
            "sdgs": [9, 12, 13]  # Industry/Innovation, Responsible Consumption & Production, Climate Action
        },
        {
            "id": 9,
            "title": "Sustainable Fashion Designer",
            "description": "Creates trendy clothing using ethical and eco-friendly materials.",
            "interests": ["Visual Arts (drawing, painting, sculpture)", "Graphic Design / Digital Media", "Product Design / Industrial Design"],
            "skills": ["Creative thinking", "Drawing or painting", "Supporting the planet", "Designing digitally"],
            "sdgs": [12, 13, 8]  # Responsible Consumption, Climate Action, Decent Work & Economic Growth
        },
        {
            "id": 10,
            "title": "Atmospheric Scientist",
            "description": "Studies weather and climate systems to understand and model change.",
            "interests": ["Physics", "Geography", "Environmental Systems & Societies / Environmental Science"],
            "skills": ["Data analysis", "Strategic thinking", "Supporting the planet", "Problem solving"],
            "sdgs": [13, 11, 17]  # Climate Action, Sustainable Cities, Partnerships for Goals
        },
        {
            "id": 11,
            "title": "Carbon Accounting Analyst",
            "description": "Tracks emissions and helps companies reduce their carbon footprint.",
            "interests": ["Economics", "Environmental Systems & Societies / Environmental Science", "Business Studies / Entrepreneurship"],
            "skills": ["Data analysis", "Strategic thinking", "Supporting the planet", "Decision-making"],
            "sdgs": [12, 13, 9]  # Responsible Consumption, Climate Action, Industry/Innovation
        },
        {
            "id": 12,
            "title": "Marine Biologist",
            "description": "Studies ocean ecosystems and works to protect marine biodiversity.",
            "interests": ["Biology", "Environmental Systems & Societies / Environmental Science", "Geography"],
            "skills": ["Working outdoors", "Data analysis", "Supporting the planet", "Working with animals"],
            "sdgs": [14, 13, 15]  # Life Below Water, Climate Action, Life on Land
        },
        {
            "id": 13,
            "title": "Urban City Planner",
            "description": "Designs greener, more connected cities using sustainable planning.",
            "interests": ["Geography", "Architecture / Interior Design", "Environmental Systems & Societies / Environmental Science"],
            "skills": ["Strategic thinking", "Designing digitally", "Problem solving", "Supporting the planet"],
            "sdgs": [11, 9, 13]  # Sustainable Cities, Industry/Innovation, Climate Action
        },
        {
            "id": 14,
            "title": "Resilience Engineer",
            "description": "Builds infrastructure that can withstand floods, heatwaves, and climate shocks.",
            "interests": ["Engineering (General or Applied)", "Physics", "Environmental Systems & Societies / Environmental Science"],
            "skills": ["Problem solving", "Strategic thinking", "Building or fixing", "Decision-making"],
            "sdgs": [9, 11, 13]  # Industry/Innovation, Sustainable Cities, Climate Action
        },
        {
            "id": 15,
            "title": "Disaster Relief Coordinator",
            "description": "Coordinates emergency response during disasters, from logistics to shelter.",
            "interests": ["Global Politics / Civics", "Geography", "Business Studies / Entrepreneurship"],
            "skills": ["Leading others", "Decision-making", "Helping people", "Resolving conflict"],
            "sdgs": [3, 11, 16]  # Good Health & Well-Being, Sustainable Cities, Peace & Justice
        },
        {
            "id": 16,
            "title": "Environmental Data Scientist",
            "description": "Uses data to predict and respond to environmental and climate issues.",
            "interests": ["Computer Science / Programming", "Mathematics", "Environmental Systems & Societies / Environmental Science"],
            "skills": ["Coding", "Data analysis", "Strategic thinking", "Supporting the planet"],
            "sdgs": [13, 14, 15]  # Climate Action, Life Below Water, Life on Land
        },
        {
            "id": 17,
            "title": "Food Systems Analyst",
            "description": "Analyzes global food supply chains and suggests improvements for sustainability.",
            "interests": ["Agriculture / Sustainable Farming", "Business Studies / Entrepreneurship", "Geography"],
            "skills": ["Data analysis", "Strategic thinking", "Supporting the planet", "Standing up for causes"],
            "sdgs": [2, 12, 13]  # Zero Hunger, Responsible Consumption, Climate Action
        },
        {
            "id": 18,
            "title": "Space Systems Engineer",
            "description": "Designs satellites and space tech used in communication and climate monitoring.",
            "interests": ["Physics", "Engineering (General or Applied)", "Mathematics"],
            "skills": ["Problem solving", "Strategic thinking", "Building or fixing", "Decision-making"],
            "sdgs": [9, 13, 17]  # Industry/Innovation, Climate Action, Partnerships for Goals
        },
        {
            "id": 19,
            "title": "AI Engineer",
            "description": "Develops intelligent systems that power apps, automation, and innovation.",
            "interests": ["Computer Science / Programming", "Mathematics", "Philosophy"],
            "skills": ["Coding", "Problem solving", "Strategic thinking", "Data analysis"],
            "sdgs": [9, 8, 4]  # Industry/Innovation, Decent Work, Quality Education
        },
        {
            "id": 20,
            "title": "Doctor",
            "description": "Diagnoses and treats patients, supporting health and well-being.",
            "interests": ["Biology", "Chemistry", "Health Science / Pre-Med"],
            "skills": ["Decision-making", "Helping people", "Listening well", "Problem solving"],
            "sdgs": [3, 5, 10]  # Good Health & Well-Being, Gender Equality, Reduced Inequalities
        },
        {
            "id": 21,
            "title": "Product Manager",
            "description": "Leads product teams from idea to launch across industries.",
            "interests": ["Business Studies / Entrepreneurship", "Psychology", "Design & Technology / Engineering"],
            "skills": ["Leading others", "Strategic thinking", "Decision-making", "Explaining ideas"],
            "sdgs": [8, 9, 12]  # Decent Work, Industry/Innovation, Responsible Consumption
        },
        {
            "id": 22,
            "title": "Graphic Designer",
            "description": "Creates visual content like logos, posters, and digital assets.",
            "interests": ["Visual Arts (drawing, painting, sculpture)", "Graphic Design / Digital Media", "Design & Technology / Engineering"],
            "skills": ["Creative thinking", "Drawing or painting", "Designing digitally", "Explaining ideas"],
            "sdgs": [8, 9, 12]  # Decent Work, Industry/Innovation, Responsible Consumption
        },
        {
            "id": 23,
            "title": "Journalist",
            "description": "Reports and writes news stories for TV, social media, or publications.",
            "interests": ["English Literature / Language Arts", "Global Politics / Civics", "Psychology"],
            "skills": ["Writing or storytelling", "Listening well", "Explaining ideas", "Standing up for causes"],
            "sdgs": [16, 10, 17]  # Peace & Justice, Reduced Inequalities, Partnerships for Goals
        },
        {
            "id": 24,
            "title": "Investment Banker",
            "description": "Advises companies on financial deals, growth, and capital strategies.",
            "interests": ["Economics", "Business Studies / Entrepreneurship", "Mathematics"],
            "skills": ["Strategic thinking", "Data analysis", "Decision-making", "Explaining ideas"],
            "sdgs": [8, 9, 17]  # Decent Work, Industry/Innovation, Partnerships for Goals
        },
        {
            "id": 25,
            "title": "Game Designer",
            "description": "Builds interactive games for entertainment and education.",
            "interests": ["Computer Science / Programming", "Visual Arts (drawing, painting, sculpture)", "Psychology"],
            "skills": ["Creative thinking", "Coding", "Designing digitally", "Writing or storytelling"],
            "sdgs": [4, 8, 9]  # Quality Education, Decent Work, Industry/Innovation
        },
        {
            "id": 26,
            "title": "Biotech Researcher",
            "description": "Develops breakthroughs like vaccines, clean meat, or gene therapy.",
            "interests": ["Biology", "Chemistry", "Health Science / Pre-Med"],
            "skills": ["Problem solving", "Data analysis", "Supporting the planet", "Helping people"],
            "sdgs": [3, 2, 9]  # Good Health, Zero Hunger, Industry/Innovation
        },
        {
            "id": 27,
            "title": "Neuroscientist",
            "description": "Studies the human brain to understand memory, emotions, and health.",
            "interests": ["Biology", "Psychology", "Health Science / Pre-Med"],
            "skills": ["Data analysis", "Problem solving", "Helping people", "Decision-making"],
            "sdgs": [3, 9, 10]  # Good Health, Industry/Innovation, Reduced Inequalities
        },
        {
            "id": 28,
            "title": "UX Designer",
            "description": "Designs interfaces that make tech easy, ethical, and human-centered.",
            "interests": ["Psychology", "Graphic Design / Digital Media", "Computer Science / Programming"],
            "skills": ["Creative thinking", "Designing digitally", "Listening well", "Problem solving"],
            "sdgs": [9, 10, 4]  # Industry/Innovation, Reduced Inequalities, Quality Education
        }
    ]
    return careers

# Interests data structured by category
@st.cache_data
def load_interest_categories():
    interest_categories = {
        "Humanities & Social Sciences": [
            "English Literature / Language Arts",
            "World Languages (e.g., French, Spanish, Mandarin, Hindi)",
            "History",
            "Geography",
            "Global Politics / Civics",
            "Philosophy",
            "Psychology",
            "Social & Cultural Anthropology",
            "Economics",
            "Business Studies / Entrepreneurship",
            "Ethics / TOK (Theory of Knowledge)"
        ],
        "Sciences": [
            "Biology",
            "Chemistry",
            "Physics",
            "Environmental Systems & Societies / Environmental Science",
            "General Science / Integrated Science",
            "Sports, Exercise & Health Science",
            "Food Science / Food Technology"
        ],
        "Math & Technology": [
            "Mathematics",
            "Computer Science / Programming",
            "Design & Technology / Engineering"
        ],
        "Arts & Creativity": [
            "Visual Arts (drawing, painting, sculpture)",
            "Graphic Design / Digital Media",
            "Film / Media Studies",
            "Drama / Theatre",
            "Music",
            "Dance"
        ],
        "Applied & Vocational": [
            "Architecture / Interior Design",
            "Product Design / Industrial Design",
            "Health Science / Pre-Med",
            "Agriculture / Sustainable Farming",
            "Hospitality / Culinary Arts",
            "Engineering (General or Applied)"
        ],
        "Lifestyle & Physical Education": [
            "Physical Education / Sports Science",
            "Coaching & Athletics"
        ]
    }
    return interest_categories

# Skills data structured by category
@st.cache_data
def load_skill_categories():
    skill_categories = {
        "Thinking & Solving": [
            "Creative thinking",
            "Problem solving",
            "Strategic thinking",
            "Data analysis",
            "Decision-making"
        ],
        "People & Communication": [
            "Teamwork",
            "Leading others",
            "Explaining ideas",
            "Listening well",
            "Resolving conflict"
        ],
        "Hands-On": [
            "Building or fixing",
            "Cooking or crafting",
            "Working outdoors",
            "Using tools/machines"
        ],
        "Digital Skills": [
            "Coding",
            "Designing digitally",
            "Editing videos",
            "Working with data",
            "Troubleshooting tech"
        ],
        "Creative Skills": [
            "Drawing or painting",
            "Writing or storytelling",
            "Performing",
            "Music or audio",
            "Photography or video"
        ],
        "Purpose & Values": [
            "Helping people",
            "Supporting the planet",
            "Standing up for causes",
            "Understanding cultures",
            "Working with animals"
        ]
    }
    return skill_categories

# SDGs data
@st.cache_data
def load_sdgs():
    sdgs = [
        {"id": 1, "name": "No Poverty"},
        {"id": 2, "name": "Zero Hunger"},
        {"id": 3, "name": "Good Health & Well-Being"},
        {"id": 4, "name": "Quality Education"},
        {"id": 5, "name": "Gender Equality"},
        {"id": 6, "name": "Clean Water & Sanitation"},
        {"id": 7, "name": "Affordable & Clean Energy"},
        {"id": 8, "name": "Decent Work & Economic Growth"},
        {"id": 9, "name": "Industry, Innovation & Infrastructure"},
        {"id": 10, "name": "Reduced Inequalities"},
        {"id": 11, "name": "Sustainable Cities & Communities"},
        {"id": 12, "name": "Responsible Consumption & Production"},
        {"id": 13, "name": "Climate Action"},
        {"id": 14, "name": "Life Below Water"},
        {"id": 15, "name": "Life on Land"},
        {"id": 16, "name": "Peace, Justice & Strong Institutions"},
        {"id": 17, "name": "Partnerships for the Goals"}
    ]
    return sdgs

# Initialize session state variables if they don't exist
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'selected_interests' not in st.session_state:
    st.session_state.selected_interests = []
if 'current_skills' not in st.session_state:
    st.session_state.current_skills = []
if 'desired_skills' not in st.session_state:
    st.session_state.desired_skills = []
if 'selected_sdgs' not in st.session_state:
    st.session_state.selected_sdgs = []
if 'manual_career_matches' not in st.session_state:
    st.session_state.manual_career_matches = []
if 'ai_career_matches' not in st.session_state:
    st.session_state.ai_career_matches = []
if 'judge_career_matches' not in st.session_state:
    st.session_state.judge_career_matches = []
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "manual"  # Default to manual tab
if 'has_api_key' not in st.session_state:
    st.session_state.has_api_key = False

# Try to get OpenAI API key
try:
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.has_api_key = True
except Exception as e:
    openai_api_key = None
    st.session_state.has_api_key = False

# Load data
careers = load_career_data()
interest_categories = load_interest_categories()
skill_categories = load_skill_categories()
sdgs = load_sdgs()

# Helper functions for selections
def handle_interest_select(interest):
    if interest in st.session_state.selected_interests:
        st.session_state.selected_interests.remove(interest)
    else:
        if len(st.session_state.selected_interests) < 3:
            st.session_state.selected_interests.append(interest)

def handle_current_skill_select(skill):
    if skill in st.session_state.current_skills:
        st.session_state.current_skills.remove(skill)
    else:
        if len(st.session_state.current_skills) < 3:
            st.session_state.current_skills.append(skill)

def handle_desired_skill_select(skill):
    if skill in st.session_state.desired_skills:
        st.session_state.desired_skills.remove(skill)
    else:
        if len(st.session_state.desired_skills) < 3:
            st.session_state.desired_skills.append(skill)

def handle_sdg_select(sdg_id):
    if sdg_id in st.session_state.selected_sdgs:
        st.session_state.selected_sdgs.remove(sdg_id)
    else:
        if len(st.session_state.selected_sdgs) < 3:
            st.session_state.selected_sdgs.append(sdg_id)

def get_sdg_names(sdg_ids):
    return [sdg["name"] for sdg in sdgs if sdg["id"] in sdg_ids]

# Manual career matching algorithm
def match_careers_manually():
    # Score each career based on matches
    scored_careers = []
    
    for career in careers:
        score = 0
        match_details = {
            "interest_matches": [],
            "skill_matches": {
                "current": [],
                "desired": []
            },
            "sdg_matches": []
        }
        
        # Score for matching interests (highest weight)
        for interest in st.session_state.selected_interests:
            if interest in career["interests"]:
                score += 3
                match_details["interest_matches"].append(interest)
        
        # Score for matching current skills
        for skill in st.session_state.current_skills:
            if skill in career["skills"]:
                score += 2
                match_details["skill_matches"]["current"].append(skill)
        
        # Score for matching desired skills (lower weight than current)
        for skill in st.session_state.desired_skills:
            if skill in career["skills"]:
                score += 1
                match_details["skill_matches"]["desired"].append(skill)
        
        # Score for matching SDGs (high weight - values are important)
        for sdg_id in st.session_state.selected_sdgs:
            if sdg_id in career["sdgs"]:
                score += 3
                match_details["sdg_matches"].append(sdg_id)
        
        career_with_score = career.copy()
        career_with_score["score"] = score
        career_with_score["match_details"] = match_details
        # Calculate match percentage (max score would be 3*3 + 3*2 + 3*1 + 3*3 = 27)
        career_with_score["match_score"] = int((score / 27) * 100)
        scored_careers.append(career_with_score)
    
    # Sort by score and take top 6
    top_matches = sorted(
        [c for c in scored_careers if c["score"] > 0],
        key=lambda x: x["score"],
        reverse=True
    )[:6]
    
    return top_matches

# AI-based career matching using OpenAI
def get_ai_career_matches():
    if not st.session_state.has_api_key:
        st.error("OpenAI API key not found in secrets. Please add it to your Streamlit secrets.toml file.")
        return []
    
    try:
        # Create the client
        client = OpenAI(api_key=openai_api_key)
        
        # Format interests, skills, and SDGs
        interests_str = ", ".join(st.session_state.selected_interests)
        current_skills_str = ", ".join(st.session_state.current_skills)
        desired_skills_str = ", ".join(st.session_state.desired_skills)
        sdgs_str = ", ".join([f"SDG {sdg_id}: {[s['name'] for s in sdgs if s['id'] == sdg_id][0]}" for sdg_id in st.session_state.selected_sdgs])
        
        # Construct the career data
        career_data = []
        for career in careers:
            career_info = {
                "id": career["id"],
                "title": career["title"],
                "description": career["description"],
                #"interests": career["interests"],
                #"skills": career["skills"],
                #"sdgs": [f"SDG {sdg_id}: {[s['name'] for s in sdgs if s['id'] == sdg_id][0]}" for sdg_id in career["sdgs"]]
            }
            career_data.append(career_info)
        
        career_data_json = json.dumps(career_data)
        
        # Construct the prompt for OpenAI
        system_prompt = f"""You are a career counselor AI that helps students find the best career matches based on their interests, skills, and values.

        You'll be given:
        1. A student's interests, current skills, desired skills, and values (UN SDGs they care about)
        2. A list of potential careers with descriptions

        Your task is to:
        1. Analyze the student's profile
        2. Find the 6 best career matches from the provided list
        3. Return a JSON response with these matches, including explanations for why each match is good

        For each career match, include:
        - Career title and description
        - Detailed explanation of why this is a good match based on interests, skills, and SDGs
        - Key interests, skills, and SDGs that align with this career
        - A "match_score" between 1-100 indicating how good the match is (highest score first)
        """

        user_prompt = f"""
        Here is the student's profile:

        Interests: {interests_str}
        Current Skills: {current_skills_str}
        Skills to Develop: {desired_skills_str}
        Values (SDGs): {sdgs_str}

        Here are the available careers to match from:
        {career_data_json}

        Return a JSON object with exactly 6 career matches in this format:
        {{
          "career_matches": [
            {{
              "id": career_id,
              "title": "Career Title",
              "description": "Career description",
              "match_score": score_between_1_and_100,
              "explanation": "Detailed explanation of why this is a good match",
              "matching_interests": ["interest1", "interest2"],
              "matching_skills": {{"current": ["skill1", "skill2"], "desired": ["skill3"]}},
              "matching_sdgs": ["SDG1: Name", "SDG2: Name"]
            }},
            ...
          ]
        }}

        Ensure each career has a different match_score and sort by match_score in descending order.
        """

        # Get completion from OpenAI
        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",  # Using gpt-4o-mini for AI scoring
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5  # Lower temperature for more consistent results
            )
            
            # Extract and parse the JSON response
            response_content = completion.choices[0].message.content
            
            try:
                parsed_response = json.loads(response_content)
                return parsed_response["career_matches"]
            except json.JSONDecodeError:
                st.error("Failed to parse AI response. Please try again.")
                return []
                
        except Exception as e:
            st.error(f"Error connecting to OpenAI API: {str(e)}")
            return []
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return []

# AI Judge function to evaluate and combine both methods
def get_ai_judge_career_matches(manual_matches, ai_matches):
    if not st.session_state.has_api_key:
        st.error("OpenAI API key not found in secrets. Please add it to your Streamlit secrets.toml file.")
        return []
        
    try:
        # Create the client
        client = OpenAI(api_key=openai_api_key)
        
        # Format interests, skills, and SDGs for context
        interests_str = ", ".join(st.session_state.selected_interests)
        current_skills_str = ", ".join(st.session_state.current_skills)
        desired_skills_str = ", ".join(st.session_state.desired_skills)
        sdgs_str = ", ".join([f"SDG {sdg_id}: {[s['name'] for s in sdgs if s['id'] == sdg_id][0]}" for sdg_id in st.session_state.selected_sdgs])
        
        # Prepare manual matches for the prompt
        manual_matches_json = json.dumps(manual_matches)
        
        # Prepare AI matches for the prompt  
        ai_matches_json = json.dumps(ai_matches)
        
        # Construct the prompt for OpenAI Judge
        system_prompt = f"""You are an expert AI career counselor who evaluates career recommendations.

        You'll be given:
        1. A student's profile (interests, skills, and values)
        2. Two sets of career recommendations:
           - One set from a manual algorithm that uses weighted scoring
           - One set from an AI system that uses more advanced matching

        Your task is to:
        1. Don't look at their scores but look at their matches and come with a more accurate response - ACT LIKE AN EXPERIENCED CAREER COUNSELLOR 
        2. Analyze both sets of recommendations and suggest why you picking one over the other
        3. Create a refined set of 6 career suggestions that represents the best matches by combining insights from both methods
        4. Provide a brief explanation of why each career made your final list
        5. Assign a match score to each career (1-100) and sort by descending score

        Your response should be more accurate than either method alone by leveraging the strengths of both approaches.
        """

        user_prompt = f"""
        Here is the student's profile:

        Interests: {interests_str}
        Current Skills: {current_skills_str}
        Skills to Develop: {desired_skills_str}
        Values (SDGs): {sdgs_str}

        Here are the career matches from the manual algorithm:
        {manual_matches_json}

        Here are the career matches from the AI algorithm:
        {ai_matches_json}

        Provide your expert judgment on the best 6 career matches in this JSON format:
        {{
          "career_matches": [
            {{
              "id": career_id,
              "title": "Career Title",
              "description": "Career description",
              "match_score": score_between_1_and_100,
              "explanation": "Your expert reasoning on why this is a good match",
              "analysis": "Brief comparison of how this career was ranked in both systems",
              "matching_interests": ["interest1", "interest2"],
              "matching_skills": {{"current": ["skill1", "skill2"], "desired": ["skill3"]}},
              "matching_sdgs": ["SDG1: Name", "SDG2: Name"]
            }},
            ...
          ]
        }}

        Make sure each career has a unique match score and sort them by match_score in descending order.
        """

        # Get completion from OpenAI
        try:
            completion = client.chat.completions.create(
                model="gpt-4.1-mini",  # Using a more powerful model for the judge
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3  # Lower temperature for more consistent results
            )
            
            # Extract and parse the JSON response
            response_content = completion.choices[0].message.content
            
            try:
                parsed_response = json.loads(response_content)
                return parsed_response["career_matches"]
            except json.JSONDecodeError:
                st.error("Failed to parse AI Judge response. Please try again.")
                return []
                
        except Exception as e:
            st.error(f"Error connecting to OpenAI API: {str(e)}")
            return []
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return []

def go_to_next_step():
    if st.session_state.step == 1 and len(st.session_state.selected_interests) == 3:
        st.session_state.step = 2
    elif st.session_state.step == 2 and len(st.session_state.current_skills) == 3 and len(st.session_state.desired_skills) == 3:
        st.session_state.step = 3
    elif st.session_state.step == 3 and len(st.session_state.selected_sdgs) > 0:
        # Generate career matches using all methods
        with st.spinner("Generating career matches..."):
            # Get manual matches
            st.session_state.manual_career_matches = match_careers_manually()
            
            # Get AI matches if API key is available
            if st.session_state.has_api_key:
                st.session_state.ai_career_matches = get_ai_career_matches()
                
                # Get AI Judge matches if both other methods have results
                if st.session_state.manual_career_matches and st.session_state.ai_career_matches:
                    st.session_state.judge_career_matches = get_ai_judge_career_matches(
                        st.session_state.manual_career_matches, 
                        st.session_state.ai_career_matches
                    )
        
        st.session_state.step = 4

def restart():
    st.session_state.step = 1
    st.session_state.selected_interests = []
    st.session_state.current_skills = []
    st.session_state.desired_skills = []
    st.session_state.selected_sdgs = []
    st.session_state.manual_career_matches = []
    st.session_state.ai_career_matches = []
    st.session_state.judge_career_matches = []
    st.session_state.active_tab = "manual"

# Sidebar with info about the app
with st.sidebar:
    st.title("Career Discovery Platform")
    st.write("Find your ideal career path based on your interests, skills, and values.")
    
    st.markdown("---")
    
    st.markdown("### How It Works")
    st.write("1. Select 3 interests you enjoy")
    st.write("2. Choose your current skills and skills to develop")
    st.write("3. Pick the UN SDGs you value most")
    st.write("4. Get career matches using three methods:")
    st.markdown("- **Manual Algorithm**: Simple scoring based on direct matches")
    st.markdown("- **AI Matching**: Advanced analysis using OpenAI's GPT models")
    st.markdown("- **AI Judge**: Combined analysis that evaluates both methods")
    
    st.markdown("---")
    
    if not st.session_state.has_api_key:
        st.warning("OpenAI API key not found. The AI features will be disabled.")
    else:
        st.success("OpenAI API key found. All features are enabled.")

# Header
st.title("Career Discovery Platform")
st.write("Find careers that match your interests, skills, and values using multiple approaches")

# Progress indicators
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="progress-step {'progress-active' if st.session_state.step == 1 else 'progress-complete' if st.session_state.step > 1 else 'progress-inactive'}">
        1
    </div>
    <div style="text-align: center; font-size: 0.8rem;">Interests</div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="progress-step {'progress-active' if st.session_state.step == 2 else 'progress-complete' if st.session_state.step > 2 else 'progress-inactive'}">
        2
    </div>
    <div style="text-align: center; font-size: 0.8rem;">Skills</div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="progress-step {'progress-active' if st.session_state.step == 3 else 'progress-complete' if st.session_state.step > 3 else 'progress-inactive'}">
        3
    </div>
    <div style="text-align: center; font-size: 0.8rem;">Values</div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
    <div class="progress-step {'progress-active' if st.session_state.step == 4 else 'progress-complete' if st.session_state.step > 4 else 'progress-inactive'}">
        4
    </div>
    <div style="text-align: center; font-size: 0.8rem;">Results</div>
    """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# Step 1: Interests
if st.session_state.step == 1:
    with st.container():
        st.markdown('<div class="step-container">', unsafe_allow_html=True)
        st.markdown('<h2 class="step-header" style="background-color: #e3f2fd; color: #1565c0;">Step 1: Select 3 Interests</h2>', unsafe_allow_html=True)
        st.write("Choose three subjects that you enjoy the most in school.")
        
        for category, interests in interest_categories.items():
            with st.expander(f"{category}"):
                col1, col2 = st.columns(2)
                
                half_length = len(interests) // 2 + len(interests) % 2
                
                for i, interest in enumerate(interests[:half_length]):
                    with col1:
                        selected = interest in st.session_state.selected_interests
                        if st.button(
                            f"{'✓ ' if selected else ''}{interest}",
                            key=f"int_{interest}",
                            type="primary" if selected else "secondary",
                            use_container_width=True
                        ):
                            handle_interest_select(interest)
                            st.rerun()
                
                for i, interest in enumerate(interests[half_length:]):
                    with col2:
                        selected = interest in st.session_state.selected_interests
                        if st.button(
                            f"{'✓ ' if selected else ''}{interest}",
                            key=f"int_{interest}",
                            type="primary" if selected else "secondary",
                            use_container_width=True
                        ):
                            handle_interest_select(interest)
                            st.rerun()
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"Selected: {len(st.session_state.selected_interests)}/3")
            if st.session_state.selected_interests:
                st.write("Your selections:")
                for interest in st.session_state.selected_interests:
                    st.markdown(f"- {interest}")
        with col2:
            if st.button("Next: Skills", disabled=len(st.session_state.selected_interests) != 3, type="primary", use_container_width=True):
                go_to_next_step()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# Step 2: Skills
elif st.session_state.step == 2:
    with st.container():
        st.markdown('<div class="step-container">', unsafe_allow_html=True)
        st.markdown('<h2 class="step-header" style="background-color: #e8f5e9; color: #2e7d32;">Step 2: Select Your Skills</h2>', unsafe_allow_html=True)
        
        # Current skills selection
        st.markdown("### Select 3 skills you're good at:")
        for category, skills in skill_categories.items():
            with st.expander(f"{category}"):
                col1, col2 = st.columns(2)
                
                half_length = len(skills) // 2 + len(skills) % 2
                
                for i, skill in enumerate(skills[:half_length]):
                    with col1:
                        selected = skill in st.session_state.current_skills
                        if st.button(
                            f"{'✓ ' if selected else ''}{skill}",
                            key=f"current_{skill}",
                            type="primary" if selected else "secondary",
                            use_container_width=True
                        ):
                            handle_current_skill_select(skill)
                            st.rerun()
                
                for i, skill in enumerate(skills[half_length:]):
                    with col2:
                        selected = skill in st.session_state.current_skills
                        if st.button(
                            f"{'✓ ' if selected else ''}{skill}",
                            key=f"current_{skill}",
                            type="primary" if selected else "secondary",
                            use_container_width=True
                        ):
                            handle_current_skill_select(skill)
                            st.rerun()
        
        st.write(f"Selected: {len(st.session_state.current_skills)}/3")
        if st.session_state.current_skills:
            st.write("Your current skills:")
            for skill in st.session_state.current_skills:
                st.markdown(f"- {skill}")
        
        st.markdown("---")
        
        # Desired skills selection
        st.markdown("### Select 3 skills you'd like to improve:")
        for category, skills in skill_categories.items():
            with st.expander(f"{category}"):
                col1, col2 = st.columns(2)
                
                half_length = len(skills) // 2 + len(skills) % 2
                
                for i, skill in enumerate(skills[:half_length]):
                    with col1:
                        selected = skill in st.session_state.desired_skills
                        if st.button(
                            f"{'✓ ' if selected else ''}{skill}",
                            key=f"desired_{skill}",
                            type="primary" if selected else "secondary",
                            use_container_width=True
                        ):
                            handle_desired_skill_select(skill)
                            st.rerun()
                
                for i, skill in enumerate(skills[half_length:]):
                    with col2:
                        selected = skill in st.session_state.desired_skills
                        if st.button(
                            f"{'✓ ' if selected else ''}{skill}",
                            key=f"desired_{skill}",
                            type="primary" if selected else "secondary",
                            use_container_width=True
                        ):
                            handle_desired_skill_select(skill)
                            st.rerun()
        
        st.write(f"Selected: {len(st.session_state.desired_skills)}/3")
        if st.session_state.desired_skills:
            st.write("Skills you want to improve:")
            for skill in st.session_state.desired_skills:
                st.markdown(f"- {skill}")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Back", use_container_width=True):
                st.session_state.step = 1
                st.rerun()
        with col2:
            if st.button(
                "Next: Values",
                disabled=len(st.session_state.current_skills) != 3 or len(st.session_state.desired_skills) != 3,
                type="primary",
                use_container_width=True
            ):
                go_to_next_step()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# Step 3: SDG Values
elif st.session_state.step == 3:
    with st.container():
        st.markdown('<div class="step-container">', unsafe_allow_html=True)
        st.markdown('<h2 class="step-header" style="background-color: #ede7f6; color: #5e35b1;">Step 3: Select Your Values</h2>', unsafe_allow_html=True)
        st.write("Choose up to 3 UN Sustainable Development Goals that you value most.")
        
        # Create 3 columns and divide SDGs among them
        col1, col2, col3 = st.columns(3)
        columns = [col1, col2, col3]
        
        sdgs_per_column = len(sdgs) // 3 + (1 if len(sdgs) % 3 > 0 else 0)
        
        for i, sdg in enumerate(sdgs):
            col_index = i // sdgs_per_column
            with columns[col_index]:
                selected = sdg["id"] in st.session_state.selected_sdgs
                if st.button(
                    f"{sdg['id']}. {'✓ ' if selected else ''}{sdg['name']}",
                    key=f"sdg_{sdg['id']}",
                    type="primary" if selected else "secondary",
                    use_container_width=True
                ):
                    handle_sdg_select(sdg["id"])
                    st.rerun()
        
        st.markdown("---")
        st.write(f"Selected: {len(st.session_state.selected_sdgs)}/3")
        if st.session_state.selected_sdgs:
            st.write("Your values:")
            sdg_names = get_sdg_names(st.session_state.selected_sdgs)
            for i, name in enumerate(sdg_names):
                st.markdown(f"- SDG {st.session_state.selected_sdgs[i]}: {name}")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Back", use_container_width=True):
                st.session_state.step = 2
                st.rerun()
        with col2:
            if st.session_state.has_api_key:
                button_text = "Generate All Career Matches"
            else:
                button_text = "Generate Manual Career Matches"
                
            if st.button(
                button_text,
                disabled=len(st.session_state.selected_sdgs) == 0,
                type="primary",
                use_container_width=True
            ):
                go_to_next_step()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# Step 4: Results with method comparison
elif st.session_state.step == 4:
    with st.container():
        st.markdown('<div class="step-container">', unsafe_allow_html=True)
        st.markdown('<h2 class="step-header" style="background-color: #e1f5fe; color: #0277bd;">Career Match Results</h2>', unsafe_allow_html=True)
        
        # Display tabs for different methods
        col1, col2, col3 = st.columns(3)
        with col1:
            manual_active = st.session_state.active_tab == "manual"
            manual_button_type = "primary" if manual_active else "secondary"
            if st.button("Manual Algorithm", type=manual_button_type, use_container_width=True):
                st.session_state.active_tab = "manual"
                st.rerun()
                
        with col2:
            ai_active = st.session_state.active_tab == "ai"
            ai_button_type = "primary" if ai_active else "secondary"
            ai_disabled = not st.session_state.has_api_key or not st.session_state.ai_career_matches
            if st.button("AI Analysis", type=ai_button_type, use_container_width=True, disabled=ai_disabled):
                st.session_state.active_tab = "ai"
                st.rerun()
                
        with col3:
            judge_active = st.session_state.active_tab == "judge"
            judge_button_type = "primary" if judge_active else "secondary"
            judge_disabled = not st.session_state.has_api_key or not st.session_state.judge_career_matches
            if st.button("AI Judge", type=judge_button_type, use_container_width=True, disabled=judge_disabled):
                st.session_state.active_tab = "judge"
                st.rerun()
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Display results based on active tab
        if st.session_state.active_tab == "manual":
            if st.session_state.manual_career_matches:
                st.markdown("### Manual Algorithm Results")
                st.write("These career matches are based on a simple scoring system that weighs your interests, skills, and values.")
                
                # Display top match
                top_match = st.session_state.manual_career_matches[0]
                st.markdown("## 🏆 Top Career Match")
                
                # Create card for top match
                st.markdown(
                    f"""
                    <div style="border: 2px solid #1976d2; border-radius: 0.5rem; margin-bottom: 2rem;">
                        <div style="background-color: #1976d2; color: white; padding: 1rem; border-radius: 0.5rem 0.5rem 0 0;">
                            <h3 style="margin: 0;">{top_match['title']} <span style="float:right; font-size:0.9rem;">Match Score: {top_match['match_score']}%</span></h3>
                        </div>
                        <div style="padding: 1rem;">
                            <p>{top_match['description']}</p>
                        </div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
                # Display matching elements for top match
                col1, col2 = st.columns(2)
                
                with col1:
                    # Display interests
                    st.markdown("<strong style='color: #1565c0;'>Matching Interests:</strong>", unsafe_allow_html=True)
                    interests_html = " ".join([f"<span class='interest-tag'>{interest}</span>" 
                                           for interest in top_match['match_details']['interest_matches']])
                    st.markdown(f"<div>{interests_html}</div>", unsafe_allow_html=True)
                    
                    # Display skills
                    st.markdown("<strong style='color: #2e7d32;'>Matching Skills:</strong>", unsafe_allow_html=True)
                    
                    # Current skills
                    current_skills_html = " ".join([f"<span class='skill-tag'>{skill}</span>" 
                                                 for skill in top_match['match_details']['skill_matches']['current']])
                    st.markdown(f"<div>{current_skills_html}</div>", unsafe_allow_html=True)
                    
                with col2:
                    # Display SDGs
                    st.markdown("<strong style='color: #5e35b1;'>Matching SDGs:</strong>", unsafe_allow_html=True)
                    sdgs_html = " ".join([f"<span class='sdg-tag'>SDG {sdg_id}: {[s['name'] for s in sdgs if s['id'] == sdg_id][0]}</span>" 
                                       for sdg_id in top_match['match_details']['sdg_matches']])
                    st.markdown(f"<div>{sdgs_html}</div>", unsafe_allow_html=True)
                    
                    # Desired skills
                    st.markdown("<strong style='color: #2e7d32;'>Skills to Develop:</strong>", unsafe_allow_html=True)
                    desired_skills_html = " ".join([f"<span class='skill-tag'>{skill}</span>" 
                                                 for skill in top_match['match_details']['skill_matches']['desired']])
                    st.markdown(f"<div>{desired_skills_html}</div>", unsafe_allow_html=True)
                
                # Display other matches in a grid
                st.markdown("## Other Matches")
                
                # Create rows with 2 cards per row
                other_matches = st.session_state.manual_career_matches[1:]
                
                for i in range(0, len(other_matches), 2):
                    cols = st.columns(2)
                    for j in range(2):
                        if i + j < len(other_matches):
                            career = other_matches[i + j]
                            with cols[j]:
                                # Display title and description with match score
                                st.markdown(f"""
                                <div style="border: 1px solid #ddd; border-radius: 0.5rem; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                                    <div style="background-color: #1976d2; color: white; padding: 0.7rem; border-radius: 0.5rem 0.5rem 0 0;">
                                        <h4 style="margin: 0; font-size: 1.1rem;">{career['title']} <span style="float:right; font-size:0.8rem;">Match: {career['match_score']}%</span></h4>
                                    </div>
                                    <div style="padding: 0.7rem;">
                                        <p style="font-size: 0.9rem;">{career['description']}</p>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Display interests
                                st.markdown("<strong style='color: #1565c0; font-size: 0.8rem;'>Matching Interests:</strong>", unsafe_allow_html=True)
                                interests_html = " ".join([f"<span class='interest-tag'>{interest}</span>" 
                                                       for interest in career['match_details']['interest_matches']])
                                st.markdown(f"<div>{interests_html}</div>", unsafe_allow_html=True)
                                
                                # Display SDGs
                                st.markdown("<strong style='color: #5e35b1; font-size: 0.8rem;'>Matching SDGs:</strong>", unsafe_allow_html=True)
                                sdgs_html = " ".join([f"<span class='sdg-tag'>SDG {sdg_id}: {[s['name'] for s in sdgs if s['id'] == sdg_id][0]}</span>" 
                                                   for sdg_id in career['match_details']['sdg_matches']])
                                st.markdown(f"<div>{sdgs_html}</div>", unsafe_allow_html=True)
            else:
                st.warning("No manual matches found. Please try again with different selections.")
        
        elif st.session_state.active_tab == "ai":
            if st.session_state.ai_career_matches:
                st.markdown("### AI Analysis Results")
                st.write("These career matches are generated using OpenAI's GPT model to provide more nuanced analysis.")
                
                # Display top match with special emphasis
                top_match = st.session_state.ai_career_matches[0]
                
                st.markdown("## 🏆 Top Career Match")
                
                # Create the main card first with just the basic info
                st.markdown(f"""
                <div class="career-card top-match">
                    <div class="career-header">
                        <h3 style="margin: 0;">{top_match['title']} <span style="float:right; font-size:0.9rem;">Match Score: {top_match['match_score']}%</span></h3>
                    </div>
                    <div class="career-content">
                        <p>{top_match['description']}</p>
                        <p><strong>Why this fits you:</strong> {top_match['explanation']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Display matching interests separately
                st.markdown("<strong style='color: #1565c0;'>Matching Interests:</strong>", unsafe_allow_html=True)
                interests_html = " ".join([f"<span class='interest-tag'>{interest}</span>" 
                                       for interest in top_match['matching_interests']])
                st.markdown(f"<div>{interests_html}</div>", unsafe_allow_html=True)
                
                # Display matching skills separately
                st.markdown("<strong style='color: #2e7d32;'>Matching Skills:</strong>", unsafe_allow_html=True)
                
                # Current skills
                st.markdown("<strong style='font-size: 0.8rem;'>Current:</strong>", unsafe_allow_html=True)
                current_skills_html = " ".join([f"<span class='skill-tag'>{skill}</span>" 
                                             for skill in top_match['matching_skills']['current']])
                st.markdown(f"<div>{current_skills_html}</div>", unsafe_allow_html=True)
                
                # Skills to develop
                st.markdown("<strong style='font-size: 0.8rem;'>To Develop:</strong>", unsafe_allow_html=True)
                desired_skills_html = " ".join([f"<span class='skill-tag'>{skill}</span>" 
                                             for skill in top_match['matching_skills']['desired']])
                st.markdown(f"<div>{desired_skills_html}</div>", unsafe_allow_html=True)
                
                # Display matching SDGs separately
                st.markdown("<strong style='color: #5e35b1;'>Matching SDGs:</strong>", unsafe_allow_html=True)
                sdgs_html = " ".join([f"<span class='sdg-tag'>{sdg}</span>" 
                                   for sdg in top_match['matching_sdgs']])
                st.markdown(f"<div>{sdgs_html}</div>", unsafe_allow_html=True)
                
                # Other matches
                st.markdown("## Other Recommended Careers")
                
                # Create rows with 2 cards per row
                other_matches = st.session_state.ai_career_matches[1:]
                
                for i in range(0, len(other_matches), 2):
                    cols = st.columns(2)
                    for j in range(2):
                        if i + j < len(other_matches):
                            career = other_matches[i + j]
                            with cols[j]:
                                # Display title and description with match score
                                st.markdown(f"""
                                <div style="border: 1px solid #ddd; border-radius: 0.5rem; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                                    <div style="background-color: #1976d2; color: white; padding: 0.7rem; border-radius: 0.5rem 0.5rem 0 0;">
                                        <h4 style="margin: 0; font-size: 1.1rem;">{career['title']} <span style="float:right; font-size:0.8rem;">Match: {career['match_score']}%</span></h4>
                                    </div>
                                    <div style="padding: 0.7rem;">
                                        <p style="font-size: 0.9rem;">{career['description']}</p>
                                        <p style="font-size: 0.9rem;"><strong>Why this fits you:</strong> {career['explanation']}</p>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Display interests
                                st.markdown("<strong style='color: #1565c0; font-size: 0.8rem;'>Matching Interests:</strong>", unsafe_allow_html=True)
                                interests_html = " ".join([f"<span class='interest-tag'>{interest}</span>" 
                                                       for interest in career['matching_interests']])
                                st.markdown(f"<div>{interests_html}</div>", unsafe_allow_html=True)
                                
                                # Display SDGs
                                st.markdown("<strong style='color: #5e35b1; font-size: 0.8rem;'>Matching SDGs:</strong>", unsafe_allow_html=True)
                                sdgs_html = " ".join([f"<span class='sdg-tag'>{sdg}</span>" 
                                                   for sdg in career['matching_sdgs'][:2]])
                                st.markdown(f"<div>{sdgs_html}</div>", unsafe_allow_html=True)
            else:
                if st.session_state.has_api_key:
                    st.warning("No AI matches found. Please try again with different selections.")
                else:
                    st.error("OpenAI API key not found. The AI analysis is unavailable.")
        
        elif st.session_state.active_tab == "judge":
            if st.session_state.judge_career_matches:
                st.markdown("### AI Judge Results")
                st.write("These career matches combine insights from both the manual algorithm and AI analysis to provide the most accurate recommendations.")
                
                # Display top match with special emphasis
                top_match = st.session_state.judge_career_matches[0]
                
                st.markdown("## 🏆 Top Career Match")
                
                # Create the main card with enhanced info
                st.markdown(f"""
                <div class="career-card top-match">
                    <div class="career-header">
                        <h3 style="margin: 0;">{top_match['title']} <span style="float:right; font-size:0.9rem;">Match Score: {top_match['match_score']}%</span></h3>
                    </div>
                    <div class="career-content">
                        <p>{top_match['description']}</p>
                        <p><strong>Expert Analysis:</strong> {top_match['explanation']}</p>
                        <div class="verdict-card">
                            <p><strong>Comparison:</strong> {top_match['analysis']}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Display matching elements
                col1, col2 = st.columns(2)
                
                with col1:
                    # Display interests
                    st.markdown("<strong style='color: #1565c0;'>Matching Interests:</strong>", unsafe_allow_html=True)
                    interests_html = " ".join([f"<span class='interest-tag'>{interest}</span>" 
                                           for interest in top_match['matching_interests']])
                    st.markdown(f"<div>{interests_html}</div>", unsafe_allow_html=True)
                    
                    # Current skills
                    st.markdown("<strong style='color: #2e7d32;'>Current Skills:</strong>", unsafe_allow_html=True)
                    current_skills_html = " ".join([f"<span class='skill-tag'>{skill}</span>" 
                                                 for skill in top_match['matching_skills']['current']])
                    st.markdown(f"<div>{current_skills_html}</div>", unsafe_allow_html=True)
                
                with col2:
                    # Display SDGs
                    st.markdown("<strong style='color: #5e35b1;'>Matching SDGs:</strong>", unsafe_allow_html=True)
                    sdgs_html = " ".join([f"<span class='sdg-tag'>{sdg}</span>" 
                                       for sdg in top_match['matching_sdgs']])
                    st.markdown(f"<div>{sdgs_html}</div>", unsafe_allow_html=True)
                    
                    # Skills to develop
                    st.markdown("<strong style='color: #2e7d32;'>Skills to Develop:</strong>", unsafe_allow_html=True)
                    desired_skills_html = " ".join([f"<span class='skill-tag'>{skill}</span>" 
                                                 for skill in top_match['matching_skills']['desired']])
                    st.markdown(f"<div>{desired_skills_html}</div>", unsafe_allow_html=True)
                
                # Other matches
                st.markdown("## Other Expert Recommendations")
                
                # Create rows with 2 cards per row
                other_matches = st.session_state.judge_career_matches[1:]
                
                for i in range(0, len(other_matches), 2):
                    cols = st.columns(2)
                    for j in range(2):
                        if i + j < len(other_matches):
                            career = other_matches[i + j]
                            with cols[j]:
                                # Display title and description with match score
                                st.markdown(f"""
                                <div style="border: 1px solid #ddd; border-radius: 0.5rem; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                                    <div style="background-color: #1976d2; color: white; padding: 0.7rem; border-radius: 0.5rem 0.5rem 0 0;">
                                        <h4 style="margin: 0; font-size: 1.1rem;">{career['title']} <span style="float:right; font-size:0.8rem;">Match: {career['match_score']}%</span></h4>
                                    </div>
                                    <div style="padding: 0.7rem;">
                                        <p style="font-size: 0.9rem;">{career['description']}</p>
                                        <p style="font-size: 0.9rem;"><strong>Expert Analysis:</strong> {career['explanation']}</p>
                                        <div style="background-color: #fff8e1; border-radius: 0.3rem; padding: 0.5rem; font-size: 0.8rem; margin-top: 0.5rem;">
                                            <p style="margin: 0;"><strong>Comparison:</strong> {career['analysis']}</p>
                                        </div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Display interests and SDGs in a more compact form
                                st.markdown(f"""
                                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem;">
                                    <span class="judge-badge">AI Judge</span>
                                    <span class="interest-tag">{len(career['matching_interests'])} Interests</span>
                                    <span class="skill-tag">{len(career['matching_skills']['current']) + len(career['matching_skills']['desired'])} Skills</span>
                                    <span class="sdg-tag">{len(career['matching_sdgs'])} SDGs</span>
                                </div>
                                """, unsafe_allow_html=True)
            else:
                if st.session_state.has_api_key:
                    st.warning("No AI Judge matches found. This could happen if there aren't enough matches from either the manual or AI methods.")
                else:
                    st.error("OpenAI API key not found. The AI Judge feature is unavailable.")
        
        # Comparison view (to show all three side by side)
        if st.session_state.has_api_key and st.session_state.manual_career_matches and st.session_state.ai_career_matches and st.session_state.judge_career_matches:
            with st.expander("View Side-by-Side Comparison of Top Matches"):
                st.markdown("### Career Match Comparison")
                st.write("Compare the top career match from each method to see how they differ.")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    manual_top = st.session_state.manual_career_matches[0]
                    st.markdown(f"""
                    <div style="border: 1px solid #ddd; border-radius: 0.5rem; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <div style="background-color: #e0e0e0; color: #616161; padding: 0.7rem; border-radius: 0.5rem 0.5rem 0 0;">
                            <h4 style="margin: 0; font-size: 1rem;">Manual Algorithm <span style="float:right; font-size:0.8rem;">{manual_top['match_score']}%</span></h4>
                        </div>
                        <div style="padding: 0.7rem;">
                            <h5>{manual_top['title']}</h5>
                            <p style="font-size: 0.8rem;">{manual_top['description']}</p>
                            <p style="font-size: 0.8rem;"><strong>Matching:</strong> {len(manual_top['match_details']['interest_matches'])} interests, {len(manual_top['match_details']['skill_matches']['current'])} current skills, {len(manual_top['match_details']['sdg_matches'])} SDGs</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    ai_top = st.session_state.ai_career_matches[0]
                    st.markdown(f"""
                    <div style="border: 1px solid #ddd; border-radius: 0.5rem; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <div style="background-color: #bbdefb; color: #1565c0; padding: 0.7rem; border-radius: 0.5rem 0.5rem 0 0;">
                            <h4 style="margin: 0; font-size: 1rem;">AI Analysis <span style="float:right; font-size:0.8rem;">{ai_top['match_score']}%</span></h4>
                        </div>
                        <div style="padding: 0.7rem;">
                            <h5>{ai_top['title']}</h5>
                            <p style="font-size: 0.8rem;">{ai_top['description']}</p>
                            <p style="font-size: 0.8rem;"><strong>Key Point:</strong> {ai_top['explanation'][:100]}...</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    judge_top = st.session_state.judge_career_matches[0]
                    st.markdown(f"""
                    <div style="border: 1px solid #ffd54f; border-radius: 0.5rem; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <div style="background-color: #fff8e1; color: #ff8f00; padding: 0.7rem; border-radius: 0.5rem 0.5rem 0 0;">
                            <h4 style="margin: 0; font-size: 1rem;">AI Judge <span style="float:right; font-size:0.8rem;">{judge_top['match_score']}%</span></h4>
                        </div>
                        <div style="padding: 0.7rem;">
                            <h5>{judge_top['title']}</h5>
                            <p style="font-size: 0.8rem;">{judge_top['description']}</p>
                            <p style="font-size: 0.8rem;"><strong>Analysis:</strong> {judge_top['analysis'][:100]}...</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        if st.button("Start Over", type="primary"):
            restart()
            st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("Career Discovery Platform &copy; 2025 | Helping you find your ideal career path")
