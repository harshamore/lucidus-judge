import streamlit as st
import pandas as pd
import numpy as np
import json
import openai
import time
import random
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
    
    .verdict-card {
        background-color: #fff8e1;
        border: 1px solid #ffd54f;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Progress message definitions
progress_messages = {
    "analyzing": [
        "Analyzing your unique constellation of interests...",
        "Diving deep into your skill profile...",
        "Connecting your values to potential career paths...",
        "Exploring the intersection of your talents and passions...",
        "Mapping your abilities to future opportunities..."
    ],
    "matching": [
        "Discovering careers where you'll thrive...",
        "Finding professional paths aligned with your values...",
        "Matching your unique talents to meaningful work...",
        "Uncovering careers where your skills make an impact...",
        "Identifying roles where your strengths shine brightest..."
    ],
    "judging": [
        "Our AI career counselor is crafting personalized recommendations...",
        "Combining data and intuition to find your ideal matches...",
        "Applying expert career knowledge to your unique profile...",
        "Evaluating which careers offer your greatest potential...",
        "Finalizing your personalized career matches..."
    ]
}

# Career data with mappings to interests, skills, and SDGs
@st.cache_data
def load_career_data():
    csv_filename = "lucidus_career_mapping_all_125_corrected.csv"
    
    try:
        # Read the CSV file
        df = pd.read_csv(csv_filename)
        
        # Check if required columns exist
        required_columns = ["career", "subjects", "skill_tags", "sdg_tags"]
        for col in required_columns:
            if col not in df.columns:
                st.error(f"Required column '{col}' not found in CSV file. Please check your CSV format.")
                return []
        
        # Log success message (will only show in debug mode)
        st.write(f"CSV file loaded successfully. Found {len(df)} career entries.")
        
        # Convert the DataFrame to the required format
        careers = []
        for _, row in df.iterrows():
            career_title = row["career"]
            
            # Use career title as description if none provided
            description = f"A professional role in {career_title}."
            
            # Parse interests (subjects)
            interests = []
            if pd.notna(row["subjects"]) and row["subjects"]:
                interests = [s.strip() for s in row["subjects"].split(",")]
            
            # Parse skills
            skills = []
            if pd.notna(row["skill_tags"]) and row["skill_tags"]:
                skills = [s.strip() for s in row["skill_tags"].split(",")]
            
            # Parse SDGs
            sdgs = []
            if pd.notna(row["sdg_tags"]) and row["sdg_tags"]:
                # Try to extract numbers from the SDG tags
                for sdg_tag in row["sdg_tags"].split(","):
                    sdg_tag = sdg_tag.strip()
                    # Extract digits, handling formats like "SDG 1" or just "1"
                    digits = ''.join(c for c in sdg_tag if c.isdigit())
                    if digits and int(digits) >= 1 and int(digits) <= 17:
                        sdgs.append(int(digits))
            
            career = {
                "id": len(careers) + 1,  # Generate sequential IDs
                "title": career_title,
                "description": description,
                "interests": interests,
                "skills": skills,
                "sdgs": sdgs
            }
            careers.append(career)
        
        if not careers:
            st.error("No career data was loaded from the CSV. Please check your CSV file.")
            return []
            
        return careers
    except FileNotFoundError:
        st.error(f"CSV file '{csv_filename}' not found in the application directory.")
        
        # For Streamlit Cloud: Display the current directory and its contents
        import os
        current_dir = os.getcwd()
        files_in_dir = os.listdir(current_dir)
        
        # Dynamically check for similar CSV files
        csv_files = [f for f in files_in_dir if f.endswith('.csv')]
        
        if csv_files:
            st.warning(f"Found these CSV files instead: {', '.join(csv_files)}")
            st.info("Try renaming one of these files to 'lucidus_career_mapping_all_125_corrected.csv'")
        else:
            st.warning(f"No CSV files found in {current_dir}")
            
        # Hard-coded fallback data with note that this is limited
        st.warning("Using limited fallback data (28 careers) until CSV is properly loaded.")
        
        # Return a minimal set of careers to allow the app to function
        return [
            {
                "id": 1,
                "title": "Microfinance Specialist",
                "description": "Designs small loans and savings programs to support underserved communities.",
                "interests": ["Economics", "Business Studies / Entrepreneurship", "Global Politics / Civics"],
                "skills": ["Strategic thinking", "Data analysis", "Helping people", "Understanding cultures"],
                "sdgs": [1, 8, 10]
            },
            # Additional fallback careers would be here
            {
                "id": 28,
                "title": "UX Designer",
                "description": "Designs interfaces that make tech easy, ethical, and human-centered.",
                "interests": ["Psychology", "Graphic Design / Digital Media", "Computer Science / Programming"],
                "skills": ["Creative thinking", "Designing digitally", "Listening well", "Problem solving"],
                "sdgs": [9, 10, 4]
            }
        ]
    except Exception as e:
        st.error(f"Error loading CSV data: {str(e)}")
        import traceback
        st.error(f"Detailed error: {traceback.format_exc()}")
        return []

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
if 'selected_sdgs' not in st.session_state:
    st.session_state.selected_sdgs = []
if 'manual_career_matches' not in st.session_state:
    st.session_state.manual_career_matches = []
if 'ai_career_matches' not in st.session_state:
    st.session_state.ai_career_matches = []
if 'judge_career_matches' not in st.session_state:
    st.session_state.judge_career_matches = []
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "judge"  # Default to judge tab
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
    
    # Log the total number of careers being processed
    st.write(f"Processing {len(careers)} careers for manual matching...")
    
    for career in careers:
        score = 0
        match_details = {
            "interest_matches": [],
            "skill_matches": {
                "current": []
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
    
    # First check if we have any matches with score > 0
    matches_with_score = [c for c in scored_careers if c["score"] > 0]
    
    # If we have fewer than 6 matches with score > 0, include some with score = 0
    if len(matches_with_score) < 6:
        st.warning(f"Only found {len(matches_with_score)} careers with matching criteria. Including some additional options.")
        
        # Add careers with score 0 until we have 6 or run out of careers
        zero_score_careers = [c for c in scored_careers if c["score"] == 0]
        additional_needed = min(6 - len(matches_with_score), len(zero_score_careers))
        
        # Take a random selection of zero-score careers
        import random
        random.shuffle(zero_score_careers)
        matches_with_score.extend(zero_score_careers[:additional_needed])
    
    # Sort by score and take top 6
    top_matches = sorted(
        matches_with_score,
        key=lambda x: x["score"],
        reverse=True
    )[:6]
    
    # Log the top matches for debugging
    st.write(f"Found {len(top_matches)} top career matches")
    for match in top_matches:
        st.write(f"- {match['title']} (Score: {match['match_score']}%)")
    
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
        sdgs_str = ", ".join([f"SDG {sdg_id}: {[s['name'] for s in sdgs if s['id'] == sdg_id][0]}" for sdg_id in st.session_state.selected_sdgs])
        
        # Log the total number of careers being processed
        st.write(f"Processing {len(careers)} careers for AI matching...")
        
        # Construct the career data - ONLY include title (as requested)
        career_data = []
        for career in careers:
            career_info = {
                "id": career["id"],
                "title": career["title"],
                # Only use career title for AI matching as requested
            }
            career_data.append(career_info)
        
        # Check if we have too many careers for a single API call
        if len(career_data) > 100:
            st.warning(f"Large dataset detected ({len(career_data)} careers). Processing in batches.")
            # Process in batches to avoid token limits
            batches = [career_data[i:i+100] for i in range(0, len(career_data), 100)]
            all_results = []
            
            for batch_index, batch in enumerate(batches):
                st.write(f"Processing batch {batch_index+1}/{len(batches)}...")
                batch_json = json.dumps(batch)
                # Process this batch and collect results
                # Code for processing batch will be added here
                # For now, just add to all_results
                # We'll implement batch processing in the next update
            
            # For now, just use the first batch to avoid complexity
            career_data = batches[0]
            career_data_json = json.dumps(career_data)
            st.warning("Using only the first 100 careers for this demo. Full batch processing will be implemented soon.")
        else:
            career_data_json = json.dumps(career_data)
        
        # Construct the prompt for OpenAI
        system_prompt = f"""You are a career counselor AI that helps students find the best career matches based on their interests, skills, and values.

        You'll be given:
        1. A student's interests, skills, and values (UN SDGs they care about)
        2. A list of potential careers (only career titles)

        Your task is to:
        1. Analyze the student's profile
        2. Find the 6 best career matches from the provided list
        3. Return a JSON response with these matches, including explanations for why each match is good

        For each career match, include:
        - Career title
        - Detailed explanation of why this is a good match based on interests, skills, and SDGs
        - Key interests, skills, and SDGs that align with this career
        - A "match_score" between 1-100 indicating how good the match is (highest score first)
        """

        user_prompt = f"""
        Here is the student's profile:

        Interests: {interests_str}
        Current Skills: {current_skills_str}
        Values (SDGs): {sdgs_str}

        Here are the available careers to match from:
        {career_data_json}

        Return a JSON object with exactly 6 career matches in this format:
        {{
          "career_matches": [
            {{
              "id": career_id,
              "title": "Career Title",
              "description": "A professional role in this field.",
              "match_score": score_between_1_and_100,
              "explanation": "Detailed explanation of why this is a good match",
              "matching_interests": ["interest1", "interest2", "interest3"],
              "matching_skills": {{"current": ["skill1", "skill2", "skill3"]}},
              "matching_sdgs": ["SDG1: Name", "SDG2: Name", "SDG3: Name"]
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
              "analysis": "Brief comparison of how this career was ranked in both systems, dont show the score but explain it was handpicked and then AI analysed",
              "matching_interests": ["interest1", "interest2", "interes3"],
              "matching_skills": {{"current": ["skill1", "skill2", "skill3"]}},
              "matching_sdgs": ["SDG1: Name", "SDG2: Name", "SDG3: Name"]
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
    elif st.session_state.step == 2 and len(st.session_state.current_skills) == 3:
        st.session_state.step = 3
    elif st.session_state.step == 3 and len(st.session_state.selected_sdgs) > 0:
        # Generate career matches using all methods
        with st.spinner("Finding your ideal career matches..."):
            # Create a container for debug information
            debug_container = st.container()
            
            with debug_container:
                st.write("### Debug Information")
                st.write("This information will help diagnose any issues with career matching.")
                # Display total number of careers loaded
                st.write(f"Total careers loaded from CSV: {len(careers)}")
                
                # Display a sample of careers to verify data loading
                st.write("Sample of careers loaded:")
                for i, career in enumerate(careers[:5]):
                    st.write(f"{i+1}. {career['title']}")
                if len(careers) > 5:
                    st.write(f"... and {len(careers)-5} more")
            
            # Set up progress bar for career matching
            progress_bar = st.progress(0)
            progress_text = st.empty()
            
            # First phase: analyze profile
            progress_text.markdown(f"<div style='text-align: center; font-style: italic;'>{random.choice(progress_messages['analyzing'])}</div>", unsafe_allow_html=True)
            for i in range(20):
                progress_bar.progress(i)
                time.sleep(0.05)
                
            # Get manual matches
            with debug_container:
                st.write("### Manual Matching Process")
            st.session_state.manual_career_matches = match_careers_manually()
            
            if st.session_state.has_api_key:
                # Second phase: matching careers
                progress_text.markdown(f"<div style='text-align: center; font-style: italic;'>{random.choice(progress_messages['matching'])}</div>", unsafe_allow_html=True)
                for i in range(20, 50):
                    progress_bar.progress(i)
                    time.sleep(0.05)
                
                # Get AI matches
                with debug_container:
                    st.write("### AI Matching Process")
                st.session_state.ai_career_matches = get_ai_career_matches()
                
                # Third phase: AI Judge evaluation
                progress_text.markdown(f"<div style='text-align: center; font-style: italic;'>{random.choice(progress_messages['judging'])}</div>", unsafe_allow_html=True)
                for i in range(50, 100):
                    progress_bar.progress(i)
                    time.sleep(0.05)
                
                # Get AI Judge matches if both other methods have results
                if st.session_state.manual_career_matches and st.session_state.ai_career_matches:
                    with debug_container:
                        st.write("### AI Judge Evaluation Process")
                        st.write(f"Manual matches: {len(st.session_state.manual_career_matches)}")
                        st.write(f"AI matches: {len(st.session_state.ai_career_matches)}")
                    
                    st.session_state.judge_career_matches = get_ai_judge_career_matches(
                        st.session_state.manual_career_matches, 
                        st.session_state.ai_career_matches
                    )
            else:
                # If no API key, just animate progress for manual matching
                for i in range(20, 100):
                    progress_bar.progress(i)
                    time.sleep(0.02)
            
            # Finish the progress bar
            progress_bar.progress(100)
            time.sleep(0.5)
            
            # Hide debug information in final view
            debug_container.empty()
            
        st.session_state.step = 4

def restart():
    st.session_state.step = 1
    st.session_state.selected_interests = []
    st.session_state.current_skills = []
    st.session_state.selected_sdgs = []
    st.session_state.manual_career_matches = []
    st.session_state.ai_career_matches = []
    st.session_state.judge_career_matches = []
    st.session_state.active_tab = "judge"

# Sidebar with info about the app
with st.sidebar:
    st.title("Career Discovery Platform")
    st.write("Find your ideal career path based on your interests, skills, and values.")
    
    st.markdown("---")
    
    st.markdown("### How It Works")
    st.write("1. Select 3 interests you enjoy")
    st.write("2. Choose your current skills")
    st.write("3. Pick the UN SDGs you value most")
    st.write("4. Get expert career recommendations from our AI Career Counselor")
    
    st.markdown("---")
    
    if not st.session_state.has_api_key:
        st.warning("OpenAI API key not found. Only manual matching will be available.")
    else:
        st.success("OpenAI API key found. AI Career Counselor is ready.")
        
    # Add a debug section to check CSV loading
    st.markdown("---")
    if st.checkbox("Show CSV Debug Info"):
        import os
        current_dir = os.getcwd()
        
        st.write("### CSV File Debug")
        csv_filename = "lucidus_career_mapping_all_125_corrected.csv"
        
        if os.path.exists(csv_filename):
            st.success(f"✅ CSV file '{csv_filename}' exists")
            
            # Show file size
            file_size = os.path.getsize(csv_filename)
            st.write(f"File size: {file_size} bytes")
            
            # Try to read it
            try:
                temp_df = pd.read_csv(csv_filename)
                st.write(f"Careers in CSV: {len(temp_df)}")
                st.write(f"Columns: {', '.join(temp_df.columns.tolist())}")
                
                # Show first few careers
                st.write("Sample careers:")
                for i, career in enumerate(temp_df["career"].head(5).tolist()):
                    st.write(f"{i+1}. {career}")
                
                # Check for specific career
                search_career = "Conservation Drone Operator"
                if search_career in temp_df["career"].values:
                    st.success(f"'{search_career}' found in CSV!")
                else:
                    st.error(f"'{search_career}' NOT found in CSV.")
                
            except Exception as e:
                st.error(f"Error reading CSV: {str(e)}")
        else:
            st.error(f"❌ CSV file '{csv_filename}' not found")
            
            # List all files in directory
            files = os.listdir(current_dir)
            csv_files = [f for f in files if f.endswith('.csv')]
            
            if csv_files:
                st.write("CSV files found:")
                for csv_file in csv_files:
                    st.write(f"- {csv_file}")
            else:
                st.write("No CSV files found in directory.")
            
            st.write(f"Current directory: {current_dir}")
            st.write(f"All files ({len(files)}):")
            for file in files[:10]:  # Show first 10 files
                st.write(f"- {file}")
            if len(files) > 10:
                st.write(f"... and {len(files)-10} more files")

# Header
st.title("Career Discovery Platform")
st.write("Find careers that match your interests, skills, and values using our expert AI Career Counselor")

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
          
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Back", use_container_width=True):
                st.session_state.step = 1
                st.rerun()
        with col2:
            if st.button(
                "Next: Values",
                disabled=len(st.session_state.current_skills) != 3,
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
                button_text = "Find Your Ideal Careers"
            else:
                button_text = "Generate Career Matches"
                
            if st.button(
                button_text,
                disabled=len(st.session_state.selected_sdgs) == 0,
                type="primary",
                use_container_width=True
            ):
                go_to_next_step()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# Step 4: Results - Only show AI Judge results
elif st.session_state.step == 4:
    with st.container():
        st.markdown('<div class="step-container">', unsafe_allow_html=True)
        st.markdown('<h2 class="step-header" style="background-color: #e1f5fe; color: #0277bd;">Your Ideal Career Matches</h2>', unsafe_allow_html=True)
        
        # Only show AI Judge results if available
        if st.session_state.has_api_key and st.session_state.judge_career_matches:
            st.markdown("### AI Career Counselor Recommendations")
            st.write("Based on your unique profile, our AI Career Counselor has identified these ideal career matches for you.")
            
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
                        <p><strong>Why This Stands Out:</strong> {top_match['analysis']}</p>
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
                
          
            # Other matches
            st.markdown("## Other Strong Career Matches")
            
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
                                    <p style="font-size: 0.9rem;"><strong>Why This Fits You:</strong> {career['explanation']}</p>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Display tags for interests, skills, and SDGs
                            st.markdown(f"""
                            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem;">
                                <span class="interest-tag">{len(career['matching_interests'])} Interests</span>
                                <span class="skill-tag">{len(career['matching_skills']['current'])} Skills</span>
                                <span class="sdg-tag">{len(career['matching_sdgs'])} SDGs</span>
                            </div>
                            """, unsafe_allow_html=True)
        
        # If we don't have AI Judge results but have manual results, show those instead
        elif st.session_state.manual_career_matches:
            st.markdown("### Career Match Results")
            st.write("Based on your selections, we've found these career matches for you.")
            
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
        else:
            if st.session_state.has_api_key:
                st.warning("No career matches found. Please try again with different selections.")
            else:
                st.error("OpenAI API key not found. Unable to generate AI career recommendations.")
        
        if st.button("Start Over", type="primary"):
            restart()
            st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("Career Discovery Platform &copy; 2025 | Helping you find your ideal career path")
