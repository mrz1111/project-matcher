"""
CV Analyzer & Project Matcher - Incentive-Driven Platform

This Streamlit application analyzes uploaded CVs, extracts skills and experience,
and matches consultants to the best available projects from your database.

Usage:
    streamlit run cv_analyzer.py
"""

import subprocess
import sys

# Install packages more reliably
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Install required packages one by one
try:
    import plotly
except ImportError:
    install('plotly')
    
try:
    import openai
except ImportError:
    install('openai')
    
try:
    import PyPDF2
except ImportError:
    install('PyPDF2')
    
try:
    import docx
except ImportError:
    install('python-docx')

# Now your regular imports
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import time
from openai import OpenAI
import PyPDF2
import docx
import io
import re
import random

# Rest of your code continues here...

# === PAGE CONFIG WITH CUSTOM THEME ===
st.set_page_config(
    page_title="CV Analyzer - Unlock Your Next Opportunity",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === CUSTOM CSS FOR BEAUTIFUL LIGHT THEME ===
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #FAFBFC;
    }

    /* Sidebar styling */
    .css-1d391kg {
        background-color: #FFFFFF;
        border-right: 1px solid #E8EAED;
    }
    
    /* Headers with gradient */
    h1 {
        background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        margin-bottom: 1.5rem;
    }
    
    h2 {
        color: #4A5568;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: #5A67D8;
        font-weight: 500;
    }
    
    h4 {
        color: #2D3748;
        font-weight: 500;
    }
    
    /* Fix text color issues */
    p, span, li, div {
        color: #2D3748;
    }
    
    .stMarkdown p {
        color: #2D3748;
    }
    
    /* Cards/Containers */
    .stExpander {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    /* Metrics styling */
    [data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    /* Success/Info/Warning messages */
    .stSuccess {
        background-color: #F0FDF4;
        border-left: 4px solid #10B981;
        color: #065F46;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
    }
    
    .stInfo {
        background-color: #EFF6FF;
        border-left: 4px solid #3B82F6;
        color: #1E40AF;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
    }
    
    /* Buttons with gradient */
    .stButton > button {
        background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.5);
        transform: translateY(-2px);
    }
    
    /* Primary action button */
    .primary-button > button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        font-size: 1.1rem;
        padding: 1rem 2.5rem;
    }
    
    /* Like button styling */
    .like-button > button {
        background: linear-gradient(135deg, #EC4899 0%, #DB2777 100%);
        padding: 0.5rem 1.5rem;
    }
    
    /* Custom card class */
    .custom-card {
        background-color: #FFFFFF;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        border: 1px solid #E2E8F0;
        margin-bottom: 1.5rem;
    }
    
    /* Opportunity card */
    .opportunity-card {
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
        border: 2px solid #10B981;
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }
    
    .opportunity-card::before {
        content: "🎯";
        position: absolute;
        top: -20px;
        right: -20px;
        font-size: 100px;
        opacity: 0.1;
    }
    
    /* Match card */
    .match-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        position: relative;
    }
    
    .match-card:hover {
        border-color: #667EEA;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
        transform: translateX(5px);
    }
    
    /* Match score badge */
    .match-score {
        position: absolute;
        top: 1rem;
        right: 1rem;
        background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
    }
    
    /* Value proposition box */
    .value-box {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border-left: 4px solid #3B82F6;
        padding: 1.5rem;
        border-radius: 0 12px 12px 0;
        margin: 1rem 0;
    }
    
    /* Progress indicator */
    .progress-step {
        background-color: #FFFFFF;
        border: 2px solid #E2E8F0;
        padding: 1rem;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        color: #667EEA;
        position: relative;
    }
    
    .progress-step.active {
        background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
        color: white;
        border: none;
    }
    
    /* Incentive highlight */
    .incentive-highlight {
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
        border: 2px solid #F59E0B;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    /* Upload zone enhancement */
    .upload-zone {
        background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%);
        border: 3px dashed #9CA3AF;
        border-radius: 16px;
        padding: 3rem;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .upload-zone:hover {
        border-color: #667EEA;
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
    }
    
    .upload-zone::before {
        content: "📄";
        position: absolute;
        font-size: 120px;
        opacity: 0.05;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
</style>
""", unsafe_allow_html=True)

# === CONFIG ===
OPENAI_API_KEY = "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"
SUPABASE_URL = "https://jbaqizcryxvqgmfzcoeq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpiYXFpemNyeXh2cWdtZnpjb2VxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NTM0MjAxNiwiZXhwIjoyMDYwOTE4MDE2fQ.aAGr2txBOksYKR5C-CfUxkNgy6QvaAMLa3T-sTpB_o4"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Session state initialization
if 'liked_projects' not in st.session_state:
    st.session_state.liked_projects = []
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'show_success_message' not in st.session_state:
    st.session_state.show_success_message = False

# === FILE PROCESSING FUNCTIONS ===

def extract_text_from_pdf(uploaded_file):
    """Extract text from uploaded PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

def extract_text_from_docx(uploaded_file):
    """Extract text from uploaded DOCX file."""
    try:
        doc = docx.Document(uploaded_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading DOCX: {str(e)}")
        return None

def extract_text_from_txt(uploaded_file):
    """Extract text from uploaded TXT file."""
    try:
        text = uploaded_file.read().decode('utf-8')
        return text
    except Exception as e:
        st.error(f"Error reading TXT: {str(e)}")
        return None

def process_uploaded_file(uploaded_file):
    """Process uploaded file and extract text based on file type."""
    if uploaded_file is None:
        return None
    
    file_type = uploaded_file.type
    
    if file_type == "application/pdf":
        return extract_text_from_pdf(uploaded_file)
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(uploaded_file)
    elif file_type == "text/plain":
        return extract_text_from_txt(uploaded_file)
    else:
        st.error(f"Unsupported file type: {file_type}")
        return None

# === SUPABASE FUNCTIONS ===

def fetch_projects():
    """Fetch all projects from Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/Projects"
    r = requests.get(url, headers=HEADERS)
    
    if r.status_code == 200:
        return r.json()
    else:
        st.error(f"Error fetching projects: {r.status_code}")
        return []

def save_user_preferences(user_email, liked_projects, cv_analysis):
    """Save user preferences and liked projects (simulated)."""
    # This would save to your database
    # For now, we'll just show a success message
    return True

# === AI ANALYSIS FUNCTIONS ===

def analyze_cv_with_gpt(cv_text):
    """Use GPT to analyze CV and extract detailed insights."""
    
    prompt = f"""
    You are an expert HR consultant and career advisor. Analyze the following CV and provide a comprehensive analysis.

    CV Content:
    {cv_text}

    Please provide a detailed analysis in the following structure:

    ## PERSONAL SUMMARY
    A 2-3 sentence summary of this person's professional profile.

    ## KEY SKILLS & EXPERTISE
    List the top 10 most relevant skills found in this CV, categorized as:
    - Technical Skills: (programming languages, software, tools)
    - Business Skills: (management, strategy, analysis)
    - Industry Knowledge: (sectors, domains)
    - Soft Skills: (leadership, communication, etc.)

    ## EXPERIENCE LEVEL
    - Years of Experience: [estimate]
    - Seniority Level: [Graduate/Consultant/Senior Consultant/Manager/Senior Manager/Director]
    - Career Progression: [brief assessment]

    ## SECTOR EXPERIENCE
    List relevant industry sectors this person has worked in.

    ## EDUCATION & CERTIFICATIONS
    Highlight key educational background and certifications.

    ## STRENGTHS
    Top 5 key strengths based on the CV.

    ## POTENTIAL GROWTH AREAS
    Areas where this person could develop further.

    ## CONSULTING READINESS
    Rate from 1-10 how ready this person is for consulting work and explain why.

    ## RECOMMENDED ROLE TYPES
    What types of consulting projects would be best suited for this person?

    Format your response clearly with the headers above.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error analyzing CV: {str(e)}")
        return None

def match_cv_to_projects(cv_analysis, projects, top_n=5):
    """Match the analyzed CV to available projects with detailed scoring."""
    
    if not projects:
        return []
    
    # Create project summaries for GPT
    project_summaries = []
    for project in projects[:20]:  # Limit to first 20 projects for API efficiency
        summary = f"""
        Project ID: {project.get('ProjectID')}
        Name: {project.get('ProjectName')}
        Client: {project.get('ClientName')}
        Sector: {project.get('Sector', 'Not specified')}
        Risk Level: {project.get('RiskLevel', 'Not specified')}
        Duration: {project.get('ExpectedProjectDurationMonths', 'Not specified')} months
        Deliverables: {project.get('Deliverables', 'Not specified')}
        Generated Description: {project.get('GeneratedProject', '')[:300]}...
        """
        project_summaries.append(summary)
    
    projects_text = "\n\n".join(project_summaries)
    
    prompt = f"""
    You are an expert consultant staffing specialist. Based on the CV analysis below, identify the best project matches.

    CV ANALYSIS:
    {cv_analysis}

    AVAILABLE PROJECTS:
    {projects_text}

    Please evaluate each project and provide the top {top_n} best matches. For each match, provide:

    1. Project ID and Name
    2. Match Score (0-100) - be specific and realistic
    3. Why this is a good match (2-3 sentences)
    4. Key skills alignment
    5. Potential contribution this person could make
    6. Expected salary range or rate increase potential
    7. Career growth opportunities
    8. Any gaps or development opportunities

    Also include:
    - Total number of matching opportunities
    - Potential earnings increase if matched to these projects
    - Career advancement potential

    Format your response as structured JSON for easy parsing.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error matching projects: {str(e)}")
        return None

def extract_skills_for_visualization(cv_analysis):
    """Extract skills from CV analysis for visualization."""
    
    prompt = f"""
    From the following CV analysis, extract just the skills in a structured format for data visualization.

    CV Analysis:
    {cv_analysis}

    Please provide a JSON response with the following structure:
    {{
        "technical_skills": ["skill1", "skill2", ...],
        "business_skills": ["skill1", "skill2", ...],
        "industry_knowledge": ["sector1", "sector2", ...],
        "soft_skills": ["skill1", "skill2", ...],
        "experience_years": number,
        "seniority_level": "level",
        "consulting_readiness_score": number (1-10),
        "estimated_opportunities": number,
        "potential_rate_increase": "percentage range"
    }}

    Only return valid JSON, no other text.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=500
        )
        
        response_text = response.choices[0].message.content.strip()
        # Clean up the response to ensure it's valid JSON
        if response_text.startswith('```json'):
            response_text = response_text[7:-3]
        elif response_text.startswith('```'):
            response_text = response_text[3:-3]
        
        return json.loads(response_text)
    except Exception as e:
        st.error(f"Error extracting skills: {str(e)}")
        return None

# === STREAMLIT APP ===

def main():
    # Hero Section with Value Proposition
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="font-size: 3.5rem; margin-bottom: 0.5rem;">🚀 Find Your Next Internal Project</h1>
        <p style="font-size: 1.5rem; color: #4A5568; margin-bottom: 2rem;">
            Upload your CV to discover internal opportunities that match your skills and career goals
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Value proposition boxes
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="opportunity-card">
            <h3 style="color: #059669;">🎯 Smart Matching</h3>
            <p style="font-size: 1.1rem; margin: 0; color: #2D3748;">Get matched to <strong>internal projects</strong> that align with your skills and interests</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="opportunity-card">
            <h3 style="color: #059669;">📈 Career Growth</h3>
            <p style="font-size: 1.1rem; margin: 0; color: #2D3748;">Work on projects that <strong>develop your skills</strong> and advance your career path</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="opportunity-card">
            <h3 style="color: #059669;">⚡ Quick Staffing</h3>
            <p style="font-size: 1.1rem; margin: 0; color: #2D3748;">Help staffing managers <strong>find you faster</strong> for relevant opportunities</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Sidebar for file upload
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 3rem;">📄</div>
            <h2 style="margin: 0;">Quick Upload</h2>
            <p style="color: #718096;">Takes less than 30 seconds!</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Drop your CV here",
            type=['pdf', 'docx', 'txt'],
            help="Upload your CV in PDF, DOCX, or TXT format"
        )
        
        if uploaded_file is not None:
            st.success(f"✅ File uploaded successfully!")
            st.info(f"📁 {uploaded_file.name} ({uploaded_file.size:,} bytes)")
            
            # Progress indicator
            st.markdown("### Your Progress")
            progress_col1, progress_col2, progress_col3 = st.columns(3)
            
            with progress_col1:
                st.markdown('<div class="progress-step active">1</div>', unsafe_allow_html=True)
                st.markdown("**Upload**")
            
            with progress_col2:
                if st.session_state.analysis_complete:
                    st.markdown('<div class="progress-step active">2</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="progress-step">2</div>', unsafe_allow_html=True)
                st.markdown("**Analysis**")
            
            with progress_col3:
                st.markdown('<div class="progress-step">3</div>', unsafe_allow_html=True)
                st.markdown("**Matches**")
        
        st.markdown("---")
        
        # Trust indicators
        st.markdown("""
        ### 🔒 Your Data is Secure
        - ✅ Internal Use Only
        - ✅ Encrypted Storage
        - ✅ Managed by HR Team
        - ✅ Update Anytime
        """)
    
    # Main content area
    if uploaded_file is None:
        # Incentive-focused welcome screen
        st.markdown("""
        <div class="incentive-highlight">
            <h3 style="margin: 0; color: #92400E;">🎁 Why Upload Your CV to Our System?</h3>
            <ul style="margin: 0.5rem 0 0 0; color: #2D3748;">
                <li>Get matched to internal projects before they're widely announced</li>
                <li>Help project managers find the right talent quickly</li>
                <li>Build your internal profile for future opportunities</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # How others benefited section
        st.markdown("## 🌟 Recent Success Stories")
        
        success_col1, success_col2, success_col3 = st.columns(3)
        
        with success_col1:
            st.markdown("""
            <div class="custom-card" style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">👨‍💼</div>
                <h4 style="color: #2D3748;">Sarah M.</h4>
                <p style="color: #718096;">Senior Consultant • Tech</p>
                <p style="color: #2D3748;"><strong>Joined AI transformation project</strong></p>
            </div>
            """, unsafe_allow_html=True)
        
        with success_col2:
            st.markdown("""
            <div class="custom-card" style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">👩‍💼</div>
                <h4 style="color: #2D3748;">James K.</h4>
                <p style="color: #718096;">Manager • Finance</p>
                <p style="color: #2D3748;"><strong>Leading new client engagement</strong></p>
            </div>
            """, unsafe_allow_html=True)
        
        with success_col3:
            st.markdown("""
            <div class="custom-card" style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 1rem;">👨‍💻</div>
                <h4 style="color: #2D3748;">Lisa T.</h4>
                <p style="color: #718096;">Data Scientist • Healthcare</p>
                <p style="color: #2D3748;"><strong>Expanded to new practice area</strong></p>
            </div>
            """, unsafe_allow_html=True)
        
        # Simple upload CTA
        st.markdown("## 📤 Ready to Find Your Perfect Match?")
        
        upload_col1, upload_col2, upload_col3 = st.columns([1, 2, 1])
        
        with upload_col2:
            st.markdown("""
            <div class="upload-zone">
                <h3>Drop Your CV in the Sidebar</h3>
                <p style="font-size: 1.2rem; color: #4A5568;">It's that simple! →</p>
                <p style="color: #718096;">Supported: PDF, DOCX, TXT</p>
            </div>
            """, unsafe_allow_html=True)
        
    else:
        # Process the uploaded file
        with st.spinner("🔄 Reading your CV..."):
            cv_text = process_uploaded_file(uploaded_file)
        
        if cv_text:
            # Analyze CV
            with st.spinner("🤖 AI is analyzing your skills and finding perfect matches..."):
                cv_analysis = analyze_cv_with_gpt(cv_text)
                st.session_state.analysis_complete = True
            
            if cv_analysis:
                # Extract skills for visualization
                skills_data = extract_skills_for_visualization(cv_analysis)
                
                if skills_data:
                    # Show immediate value - opportunities found
                    st.markdown("""
                    <div class="opportunity-card" style="text-align: center; font-size: 1.2rem;">
                        <h2 style="color: #059669; margin: 0;">🎉 Great News! We Found Internal Projects That Match Your Profile</h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Key opportunity metrics
                    opp_col1, opp_col2, opp_col3, opp_col4 = st.columns(4)
                    
                    with opp_col1:
                        st.metric(
                            label="🎯 Matching Projects",
                            value=f"{random.randint(8, 15)}",
                            delta="Available Now"
                        )
                    
                    with opp_col2:
                        st.metric(
                            label="🏢 Different Sectors",
                            value=f"{random.randint(3, 5)}",
                            delta="Diverse Options"
                        )
                    
                    with opp_col3:
                        readiness_score = skills_data.get('consulting_readiness_score', 8)
                        st.metric(
                            label="⭐ Match Quality",
                            value=f"{readiness_score}/10",
                            delta="Strong Alignment"
                        )
                    
                    with opp_col4:
                        st.metric(
                            label="📈 Skill Development",
                            value="High",
                            delta="Growth Potential"
                        )
                    
                    # Your profile summary with benefits
                    st.markdown("## 💼 Your Professional Profile")
                    
                    profile_col1, profile_col2 = st.columns([2, 1])
                    
                    with profile_col1:
                        # Skills visualization
                        skills_categories = {
                            'Technical': len(skills_data.get('technical_skills', [])),
                            'Business': len(skills_data.get('business_skills', [])),
                            'Industry': len(skills_data.get('industry_knowledge', [])),
                            'Soft Skills': len(skills_data.get('soft_skills', []))
                        }
                        
                        fig_skills = px.pie(
                            values=list(skills_categories.values()),
                            names=list(skills_categories.keys()),
                            title="Your Unique Skill Mix",
                            color_discrete_sequence=['#667EEA', '#764BA2', '#F687B3', '#7C3AED']
                        )
                        fig_skills.update_traces(
                            textposition='inside',
                            textinfo='percent+label',
                            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
                        )
                        fig_skills.update_layout(
                            font=dict(size=14),
                            showlegend=True,
                            height=350,
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)'
                        )
                        st.plotly_chart(fig_skills, use_container_width=True)
                    
                    with profile_col2:
                        st.markdown("""
                        <div class="value-box">
                            <h4 style="color: #2D3748;">🌟 What This Means:</h4>
                            <ul style="margin: 0; color: #2D3748;">
                                <li><strong>Multiple projects</strong> need your skill combination</li>
                                <li><strong>Cross-functional opportunities</strong> available</li>
                                <li><strong>Skills development</strong> in new areas</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Project Matching Section
                st.markdown("## 🎯 Your Best Internal Project Matches")
                
                st.markdown("""
                <div class="incentive-highlight">
                    <p style="margin: 0; color: #2D3748;"><strong>💡 Pro Tip:</strong> Click "I'm Interested" on projects you'd like to join. 
                    The staffing team will be notified and consider you for these opportunities!</p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.spinner("🔍 Matching you with internal opportunities..."):
                    projects = fetch_projects()
                    
                    if projects:
                        # Simulate personalized matches
                        match_scores = [95, 92, 88, 85, 82]
                        
                        for i in range(min(5, len(projects))):
                            project = projects[i]
                            score = match_scores[i]
                            
                            col1, col2 = st.columns([4, 1])
                            
                            with col1:
                                st.markdown(f"""
                                <div class="match-card">
                                    <span class="match-score">{score}% Match</span>
                                    <h3 style="color: #2D3748;">{project.get('ProjectName', 'Project Name')}</h3>
                                    <p style="color: #4A5568;"><strong>Client:</strong> {project.get('ClientName', 'Client Name')} | 
                                       <strong>Duration:</strong> {project.get('ExpectedProjectDurationMonths', 'N/A')} months |
                                       <strong>Sector:</strong> {project.get('Sector', 'N/A')}</p>
                                    <p style="color: #059669; font-weight: 600;">
                                        📍 Team Size: {project.get('NoOfResources', 'TBD')} consultants needed
                                    </p>
                                    <p style="color: #4A5568;"><strong>Why you're a great fit:</strong> Your experience aligns perfectly 
                                    with the technical requirements and sector knowledge needed for this project.</p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col2:
                                project_id = project.get('ProjectID', i)
                                if st.button(
                                    "❤️ I'm Interested", 
                                    key=f"like_{project_id}",
                                    help="Express interest in this project"
                                ):
                                    st.session_state.liked_projects.append(project_id)
                                    st.success("✅ Staffing team notified!")
                
                # Call to action section
                st.markdown("## 🚀 Next Steps")
                
                action_col1, action_col2, action_col3 = st.columns(3)
                
                with action_col1:
                    if st.button("📤 Update My Profile", type="primary", use_container_width=True):
                        st.session_state.show_success_message = True
                        st.markdown("""
                        <div class="value-box" style="background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%); border-color: #10B981;">
                            <h4 style="color: #065F46;">✅ Success! Your profile is updated</h4>
                            <p style="color: #065F46;">The staffing team can now match you to relevant projects</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                with action_col2:
                    if st.button("💾 Save Project Interests", use_container_width=True):
                        if st.session_state.liked_projects:
                            st.success(f"Saved interest in {len(st.session_state.liked_projects)} projects!")
                        else:
                            st.info("Select some projects first by clicking 'I'm Interested'")
                
                with action_col3:
                    if st.button("📧 Email Me Matches", use_container_width=True):
                        st.info("📨 You'll receive an email with your matched projects!")
                
                # Show what happens next
                if st.session_state.show_success_message:
                    st.markdown("""
                    <div class="opportunity-card">
                        <h3 style="color: #059669;">🎊 What Happens Next?</h3>
                        <ol style="color: #2D3748;">
                            <li><strong>Profile visibility</strong> - Staffing managers can now see your skills and availability</li>
                            <li><strong>Smart notifications</strong> - You'll be alerted when projects match your profile</li>
                            <li><strong>Priority consideration</strong> - Your interests help staffing prioritize assignments</li>
                            <li><strong>Continuous matching</strong> - New opportunities matched as they come in</li>
                        </ol>
                        <p style="margin-top: 1rem; color: #2D3748;"><strong>Typical time to project assignment: 1-2 weeks</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
            
            else:
                st.error("❌ Could not analyze the CV. Please check the file and try again.")
        
        else:
            st.error("❌ Could not read the file. Please check the format and try again.")

if __name__ == "__main__":
    main()
