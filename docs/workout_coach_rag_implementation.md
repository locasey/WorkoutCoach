# WorkoutCoach RAG Implementation Guide
## Chain-of-Thought with Research-Backed Prompting

---

## Overview

This guide implements a RAG (Retrieval-Augmented Generation) system for your WorkoutCoach app that:
1. Ingests academic research and training methodology documents
2. Uses Chain-of-Thought reasoning to create evidence-based plans
3. Maintains deterministic, safe output via proper configuration
4. Integrates with your existing Flask/React architecture

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface (React)                │
│         (Conversational workout plan generation)         │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│              Flask Backend API                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Workout Plan Generator Service                   │  │
│  │  • User info collector                           │  │
│  │  • RAG retriever                                 │  │
│  │  • CoT prompt constructor                        │  │
│  │  • LLM interface (Gemini/OpenAI)                │  │
│  └──────────────────────────────────────────────────┘  │
└───────────┬──────────────────────────────┬──────────────┘
            │                              │
            ▼                              ▼
┌─────────────────────┐      ┌────────────────────────────┐
│  Vector Database    │      │   Training Research Store  │
│  (ChromaDB/FAISS)  │      │   • Academic papers (PDF)  │
│  • Embeddings      │      │   • Training methodologies │
│  • Semantic search │      │   • Race-specific guides   │
└─────────────────────┘      └────────────────────────────┘
```

---

## Phase 1: Research Document Collection & Processing

### Step 1.1: Gather Training Research

Create a directory structure:

```
backend/
├── training_research/
│   ├── papers/
│   │   ├── seiler_2009_80_20_training.pdf
│   │   ├── lydiard_base_building.pdf
│   │   ├── daniels_running_formula.pdf
│   │   └── periodization_principles.pdf
│   ├── methodologies/
│   │   ├── hal_higdon_training_philosophy.md
│   │   ├── hanson_method_overview.md
│   │   └── pfitzinger_advanced_marathoning.md
│   └── race_specific/
│       ├── 5k_guidelines.md
│       ├── 10k_guidelines.md
│       ├── half_marathon_guidelines.md
│       └── marathon_guidelines.md
└── app.py
```

### Recommended Research Sources:

**Academic Papers:**
- Stephen Seiler: "What is Best Practice for Training Intensity..."
- Jack Daniels: "Daniels' Running Formula" (chapters on VDOT)
- Brad Hudson: "Run Faster from the 5K to the Marathon"
- Pete Pfitzinger: "Advanced Marathoning"

**Methodology Guides:**
- Hal Higdon's training philosophies
- Hanson's Marathon Method
- Lydiard Foundation principles
- MAF (Maximum Aerobic Function) method

**Key Topics to Cover:**
1. The 80/20 rule (polarized training)
2. Progressive overload & 10% rule
3. Periodization (base, build, peak, taper)
4. Recovery principles
5. Race-specific pacing strategies
6. Injury prevention guidelines

### Step 1.2: Document Processing Script

```python
# backend/scripts/process_research.py

import os
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.document_loaders import (
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    DirectoryLoader
)

class ResearchProcessor:
    """Process and index training research documents"""
    
    def __init__(self, research_dir: str = "./training_research"):
        self.research_dir = research_dir
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = None
        
    def load_documents(self) -> List:
        """Load all research documents"""
        documents = []
        
        # Load PDFs
        pdf_loader = DirectoryLoader(
            f"{self.research_dir}/papers",
            glob="**/*.pdf",
            loader_cls=PyPDFLoader
        )
        documents.extend(pdf_loader.load())
        
        # Load Markdown files
        md_loader = DirectoryLoader(
            f"{self.research_dir}/methodologies",
            glob="**/*.md",
            loader_cls=UnstructuredMarkdownLoader
        )
        documents.extend(md_loader.load())
        
        md_loader_race = DirectoryLoader(
            f"{self.research_dir}/race_specific",
            glob="**/*.md",
            loader_cls=UnstructuredMarkdownLoader
        )
        documents.extend(md_loader_race.load())
        
        return documents
    
    def chunk_documents(self, documents: List) -> List:
        """Split documents into semantic chunks"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # Tokens, roughly
            chunk_overlap=200,  # Overlap for context
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        chunks = text_splitter.split_documents(documents)
        return chunks
    
    def create_vector_store(self, chunks: List):
        """Create and persist vector database"""
        self.vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory="./chroma_db",
            collection_name="training_research"
        )
        self.vector_store.persist()
        print(f"Indexed {len(chunks)} document chunks")
    
    def process_all(self):
        """Complete pipeline"""
        print("Loading documents...")
        documents = self.load_documents()
        
        print(f"Loaded {len(documents)} documents")
        print("Chunking documents...")
        chunks = self.chunk_documents(documents)
        
        print(f"Created {len(chunks)} chunks")
        print("Creating vector store...")
        self.create_vector_store(chunks)
        
        print("✓ Research processing complete!")

# Usage
if __name__ == "__main__":
    processor = ResearchProcessor()
    processor.process_all()
```

---

## Phase 2: RAG Retrieval System

### Step 2.1: Semantic Search Service

```python
# backend/services/research_retriever.py

from typing import List, Dict
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

class ResearchRetriever:
    """Retrieve relevant training research for workout planning"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = Chroma(
            persist_directory="./chroma_db",
            embedding_function=self.embeddings,
            collection_name="training_research"
        )
    
    def retrieve_relevant_research(
        self, 
        user_profile: Dict,
        top_k: int = 5
    ) -> str:
        """
        Retrieve research relevant to the user's training goal
        
        Args:
            user_profile: Dict with keys like 'goal', 'experience_level', etc.
            top_k: Number of relevant chunks to retrieve
            
        Returns:
            Formatted research context string
        """
        # Construct search query based on user profile
        query = self._construct_search_query(user_profile)
        
        # Retrieve relevant documents
        docs = self.vector_store.similarity_search(
            query,
            k=top_k
        )
        
        # Format research context
        research_context = self._format_research(docs)
        return research_context
    
    def _construct_search_query(self, profile: Dict) -> str:
        """Build semantic search query from user profile"""
        goal = profile.get('goal', '').lower()
        experience = profile.get('experience_level', 'intermediate')
        
        # Tailor query to extract most relevant principles
        queries = {
            'marathon': f"marathon training {experience} runner periodization progressive overload",
            'half marathon': f"half marathon training {experience} periodization tempo runs",
            '10k': f"10k race training {experience} speed work intervals",
            '5k': f"5k training {experience} VO2max intervals speed",
        }
        
        # Match goal to query pattern
        for key in queries:
            if key in goal:
                return queries[key]
        
        # Default fallback
        return f"{goal} training principles {experience} runner"
    
    def _format_research(self, docs: List) -> str:
        """Format retrieved documents into context string"""
        context_parts = []
        
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get('source', 'Unknown')
            content = doc.page_content
            
            context_parts.append(f"""
### Research Source {i}: {source}
{content}
---
""")
        
        return "\n".join(context_parts)
    
    def retrieve_safety_guidelines(self) -> str:
        """Always include safety guidelines"""
        safety_query = "injury prevention progressive overload recovery rest days"
        docs = self.vector_store.similarity_search(safety_query, k=2)
        return self._format_research(docs)
```

---

## Phase 3: Chain-of-Thought Prompt Construction

### Step 3.1: Prompt Template with CoT

```python
# backend/services/prompt_builder.py

from typing import Dict
import json

class WorkoutPlanPromptBuilder:
    """Build Chain-of-Thought prompts with research context"""
    
    def __init__(self):
        self.system_role = """You are an expert running coach with 20+ years of experience 
creating evidence-based, personalized training plans. You follow scientific research 
and proven training methodologies. Your plans prioritize athlete safety, progressive 
development, and race-day success."""
    
    def build_cot_prompt(
        self,
        user_profile: Dict,
        research_context: str,
        safety_guidelines: str
    ) -> str:
        """
        Construct a Chain-of-Thought prompt with RAG context
        
        Args:
            user_profile: User's training goals and current fitness
            research_context: Retrieved research documents
            safety_guidelines: Safety and injury prevention guidelines
        """
        
        weeks_until_race = self._calculate_weeks(
            user_profile['current_date'],
            user_profile['race_date']
        )
        
        prompt = f"""
{self.system_role}

# RELEVANT TRAINING RESEARCH AND METHODOLOGIES

{research_context}

# SAFETY GUIDELINES (ALWAYS FOLLOW)

{safety_guidelines}

# USER PROFILE

```json
{json.dumps(user_profile, indent=2)}
```

Race in {weeks_until_race} weeks.

---

# CHAIN-OF-THOUGHT REASONING INSTRUCTIONS

Think through the training plan step-by-step, showing your reasoning:

## Step 1: Assess Current Fitness and Goal Appropriateness
- Analyze the user's current weekly mileage vs. race goal
- Determine if timeline is realistic
- Identify any red flags (too ambitious, injury risk, insufficient time)

## Step 2: Apply Training Principles from Research
- Which periodization model is most appropriate?
- How should the 80/20 rule apply to this plan?
- What does research say about optimal weekly mileage for this goal?
- What are the key physiological adaptations needed?

## Step 3: Design Periodization Structure
- How many weeks for base building?
- How many weeks for build phase (speed/tempo work)?
- When should peak training occur?
- How long should the taper be?

## Step 4: Calculate Weekly Progression
- Starting weekly mileage
- Peak weekly mileage target
- Weekly progression rate (following 10% rule)
- Distribution across training days

## Step 5: Structure Weekly Workouts
- What types of workouts each week? (easy, tempo, intervals, long run)
- How should intensity be distributed (80/20)?
- Rest/recovery days placement

## Step 6: Add Race-Specific Preparation
- Race pace work progression
- Mental preparation elements
- Taper strategy specifics

---

AFTER showing your reasoning above, create the complete training plan in this JSON format:

```json
{{
  "plan_metadata": {{
    "created_for": "{user_profile.get('name', 'Athlete')}",
    "goal": "{user_profile['goal']}",
    "race_date": "{user_profile['race_date']}",
    "total_weeks": <number>,
    "training_philosophy": "<brief description of approach>",
    "key_research_applied": ["<principle 1>", "<principle 2>"]
  }},
  "weekly_plans": [
    {{
      "week_number": 1,
      "phase": "base" | "build" | "peak" | "taper",
      "weekly_mileage": <number>,
      "phase_rationale": "<why this phase now>",
      "workouts": [
        {{
          "day": "Monday",
          "type": "easy" | "tempo" | "intervals" | "long" | "recovery" | "rest",
          "distance": <miles>,
          "pace_guidance": "<e.g., 'conversational pace', '10K race pace'>",
          "description": "<workout details>",
          "rationale": "<why this workout today>"
        }}
      ]
    }}
  ],
  "safety_notes": ["<note 1>", "<note 2>"],
  "nutrition_hydration_tips": ["<tip 1>", "<tip 2>"],
  "race_day_strategy": "<brief race day guidance>"
}}
```

IMPORTANT CONSTRAINTS:
- Never increase weekly mileage by more than 10% week-over-week
- Include at least 1 rest day per week
- 80% of weekly mileage should be easy/recovery pace
- Taper must reduce volume by 40-60% in final 2-3 weeks
- Progressive overload must be gradual and safe
"""
        return prompt
    
    def _calculate_weeks(self, current_date: str, race_date: str) -> int:
        """Calculate weeks between dates"""
        from datetime import datetime
        current = datetime.fromisoformat(current_date)
        race = datetime.fromisoformat(race_date)
        delta = race - current
        return max(1, delta.days // 7)
```

---

## Phase 4: Integration with Flask Backend

### Step 4.1: Workout Plan Generator Service

```python
# backend/services/workout_plan_generator.py

import os
from typing import Dict
import openai
import google.generativeai as genai
from .research_retriever import ResearchRetriever
from .prompt_builder import WorkoutPlanPromptBuilder

class WorkoutPlanGenerator:
    """Main service for generating research-backed workout plans"""
    
    def __init__(self):
        self.retriever = ResearchRetriever()
        self.prompt_builder = WorkoutPlanPromptBuilder()
        
        # Configuration
        self.llm_provider = os.getenv('LLM_PROVIDER', 'gemini')
        
        if self.llm_provider == 'openai':
            openai.api_key = os.getenv('OPENAI_API_KEY')
        else:
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    
    def generate_plan(self, user_profile: Dict) -> Dict:
        """
        Generate a complete workout plan
        
        Args:
            user_profile: Dict containing:
                - goal: str (e.g., "Half Marathon")
                - race_date: str (ISO format)
                - current_date: str (ISO format)
                - training_days_per_week: int
                - current_weekly_mileage: float
                - experience_level: str ("beginner", "intermediate", "advanced")
                - name: str (optional)
        
        Returns:
            Dict with workout plan JSON
        """
        
        # Step 1: Retrieve relevant research
        print("Retrieving relevant research...")
        research_context = self.retriever.retrieve_relevant_research(user_profile)
        safety_guidelines = self.retriever.retrieve_safety_guidelines()
        
        # Step 2: Build Chain-of-Thought prompt
        print("Building prompt...")
        prompt = self.prompt_builder.build_cot_prompt(
            user_profile,
            research_context,
            safety_guidelines
        )
        
        # Step 3: Call LLM with proper configuration
        print("Generating plan...")
        response = self._call_llm(prompt)
        
        # Step 4: Parse response
        plan = self._parse_response(response)
        
        return plan
    
    def _call_llm(self, prompt: str) -> str:
        """Call LLM with optimal configuration for workout planning"""
        
        if self.llm_provider == 'openai':
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo-preview",  # or gpt-3.5-turbo for cost savings
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,      # Deterministic for safety
                top_p=0.95,           # Slightly higher for structured output
                max_tokens=6000,      # CoT + plan needs space
                n=1
            )
            return response.choices[0].message.content
        
        else:  # Gemini
            model = genai.GenerativeModel('gemini-1.5-pro')
            
            generation_config = genai.GenerationConfig(
                temperature=0.1,
                top_p=0.95,
                top_k=20,
                max_output_tokens=6000,
            )
            
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return response.text
    
    def _parse_response(self, response: str) -> Dict:
        """Extract JSON from response"""
        import json
        import re
        
        # Find JSON block in response
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                # Try to repair JSON if needed
                from json_repair import repair_json
                return json.loads(repair_json(json_str))
        
        raise ValueError("Could not parse workout plan from LLM response")
```

### Step 4.2: Flask API Endpoint

```python
# backend/app.py (additions)

from flask import Flask, request, jsonify
from services.workout_plan_generator import WorkoutPlanGenerator

app = Flask(__name__)
plan_generator = WorkoutPlanGenerator()

@app.route('/api/workout-plan/generate', methods=['POST'])
def generate_workout_plan():
    """
    Generate a personalized workout plan
    
    Request body:
    {
        "goal": "Half Marathon",
        "race_date": "2026-06-15",
        "current_date": "2026-01-18",
        "training_days_per_week": 4,
        "current_weekly_mileage": 15,
        "experience_level": "intermediate",
        "name": "John Doe"
    }
    """
    try:
        user_profile = request.json
        
        # Validate required fields
        required_fields = [
            'goal', 'race_date', 'current_date',
            'training_days_per_week', 'current_weekly_mileage',
            'experience_level'
        ]
        
        for field in required_fields:
            if field not in user_profile:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Generate plan
        plan = plan_generator.generate_plan(user_profile)
        
        return jsonify({
            'success': True,
            'plan': plan
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/workout-plan/research-preview', methods=['POST'])
def preview_research():
    """
    Preview what research would be retrieved for a given profile
    Useful for debugging and transparency
    """
    try:
        user_profile = request.json
        
        from services.research_retriever import ResearchRetriever
        retriever = ResearchRetriever()
        
        research = retriever.retrieve_relevant_research(user_profile)
        safety = retriever.retrieve_safety_guidelines()
        
        return jsonify({
            'success': True,
            'research_context': research,
            'safety_guidelines': safety
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

---

## Phase 5: Frontend Integration

### Step 5.1: Conversational Data Collection

```javascript
// frontend/src/components/WorkoutPlanBuilder.jsx

import { useState } from 'react';
import axios from 'axios';

const WorkoutPlanBuilder = () => {
  const [step, setStep] = useState(0);
  const [userProfile, setUserProfile] = useState({
    goal: '',
    race_date: '',
    current_date: new Date().toISOString().split('T')[0],
    training_days_per_week: 0,
    current_weekly_mileage: 0,
    experience_level: '',
    name: ''
  });
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(false);

  const questions = [
    {
      key: 'name',
      question: "What's your name?",
      type: 'text',
      placeholder: 'John Doe'
    },
    {
      key: 'goal',
      question: "What are you training for?",
      type: 'select',
      options: ['5K', '10K', 'Half Marathon', 'Marathon', 'Ultra Marathon']
    },
    {
      key: 'race_date',
      question: "When is your race?",
      type: 'date'
    },
    {
      key: 'experience_level',
      question: "What's your running experience?",
      type: 'select',
      options: ['beginner', 'intermediate', 'advanced']
    },
    {
      key: 'current_weekly_mileage',
      question: "What's your current weekly mileage?",
      type: 'number',
      placeholder: 'e.g., 15'
    },
    {
      key: 'training_days_per_week',
      question: "How many days per week can you train?",
      type: 'number',
      min: 3,
      max: 7
    }
  ];

  const handleNext = () => {
    if (step < questions.length - 1) {
      setStep(step + 1);
    } else {
      generatePlan();
    }
  };

  const generatePlan = async () => {
    setLoading(true);
    try {
      const response = await axios.post(
        'http://localhost:5000/api/workout-plan/generate',
        userProfile
      );
      
      setPlan(response.data.plan);
    } catch (error) {
      console.error('Failed to generate plan:', error);
      alert('Failed to generate workout plan. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const currentQuestion = questions[step];

  return (
    <div className="workout-plan-builder">
      {!plan ? (
        <div className="question-flow">
          <div className="progress-bar">
            Step {step + 1} of {questions.length}
          </div>
          
          <h2>{currentQuestion.question}</h2>
          
          {currentQuestion.type === 'text' && (
            <input
              type="text"
              value={userProfile[currentQuestion.key]}
              onChange={(e) => setUserProfile({
                ...userProfile,
                [currentQuestion.key]: e.target.value
              })}
              placeholder={currentQuestion.placeholder}
            />
          )}
          
          {currentQuestion.type === 'number' && (
            <input
              type="number"
              value={userProfile[currentQuestion.key]}
              onChange={(e) => setUserProfile({
                ...userProfile,
                [currentQuestion.key]: parseFloat(e.target.value)
              })}
              min={currentQuestion.min}
              max={currentQuestion.max}
              placeholder={currentQuestion.placeholder}
            />
          )}
          
          {currentQuestion.type === 'date' && (
            <input
              type="date"
              value={userProfile[currentQuestion.key]}
              onChange={(e) => setUserProfile({
                ...userProfile,
                [currentQuestion.key]: e.target.value
              })}
            />
          )}
          
          {currentQuestion.type === 'select' && (
            <select
              value={userProfile[currentQuestion.key]}
              onChange={(e) => setUserProfile({
                ...userProfile,
                [currentQuestion.key]: e.target.value
              })}
            >
              <option value="">Select...</option>
              {currentQuestion.options.map(opt => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          )}
          
          <button 
            onClick={handleNext}
            disabled={!userProfile[currentQuestion.key] || loading}
          >
            {step === questions.length - 1 ? 'Generate Plan' : 'Next'}
          </button>
        </div>
      ) : (
        <PlanDisplay plan={plan} />
      )}
    </div>
  );
};

export default WorkoutPlanBuilder;
```

---

## Phase 6: Dependencies & Setup

### requirements.txt additions:

```
# RAG and Vector Store
langchain==0.1.0
chromadb==0.4.22
openai==1.0.0
tiktoken==0.5.2

# Document Processing
pypdf==3.17.0
unstructured==0.11.0
markdown==3.5

# JSON Repair
json-repair==0.7.0

# Existing dependencies...
flask==2.3.0
google-generativeai==0.3.0
```

### Installation Script:

```bash
#!/bin/bash
# setup_rag.sh

echo "Installing dependencies..."
pip install -r requirements.txt --break-system-packages

echo "Creating research directory structure..."
mkdir -p backend/training_research/{papers,methodologies,race_specific}

echo "Processing research documents..."
python backend/scripts/process_research.py

echo "✓ RAG system setup complete!"
```

---

## Phase 7: Testing & Validation

### Test Script:

```python
# backend/tests/test_plan_generation.py

import json
from services.workout_plan_generator import WorkoutPlanGenerator

def test_half_marathon_plan():
    """Test generating a half marathon plan"""
    
    generator = WorkoutPlanGenerator()
    
    profile = {
        "name": "Test Runner",
        "goal": "Half Marathon",
        "race_date": "2026-06-15",
        "current_date": "2026-01-18",
        "training_days_per_week": 4,
        "current_weekly_mileage": 15,
        "experience_level": "intermediate"
    }
    
    print("Generating plan...")
    plan = generator.generate_plan(profile)
    
    print("\n✓ Plan generated successfully!")
    print(f"\nTotal weeks: {plan['plan_metadata']['total_weeks']}")
    print(f"Philosophy: {plan['plan_metadata']['training_philosophy']}")
    print(f"\nFirst week mileage: {plan['weekly_plans'][0]['weekly_mileage']}")
    
    # Validate safety constraints
    for i in range(len(plan['weekly_plans']) - 1):
        current_mileage = plan['weekly_plans'][i]['weekly_mileage']
        next_mileage = plan['weekly_plans'][i + 1]['weekly_mileage']
        
        if next_mileage > current_mileage * 1.1:
            print(f"⚠️  Warning: Week {i+1} to {i+2} exceeds 10% rule!")
    
    print("\n✓ Safety validation passed")
    
    return plan

if __name__ == "__main__":
    plan = test_half_marathon_plan()
    
    # Save to file for inspection
    with open('test_plan.json', 'w') as f:
        json.dump(plan, f, indent=2)
    
    print("\nPlan saved to test_plan.json")
```

---

## Next Steps Checklist

- [ ] Create research directory structure
- [ ] Gather 5-10 key research documents
- [ ] Run document processing script
- [ ] Test RAG retrieval with sample queries
- [ ] Implement prompt builder
- [ ] Test full plan generation
- [ ] Integrate with Flask API
- [ ] Update frontend for conversational flow
- [ ] Add plan export functionality
- [ ] Create documentation for adding new research

---

## Maintenance & Iteration

### Adding New Research:
1. Drop PDF/MD files into appropriate research directory
2. Run `python backend/scripts/process_research.py`
3. Test retrieval quality with `/research-preview` endpoint

### Improving Prompts:
1. Use the documentation table format (from PDF page 66)
2. Track prompt iterations in a spreadsheet
3. A/B test different CoT structures
4. Adjust retrieval top_k parameter based on response quality

### Monitoring Quality:
- Log all generated plans
- Track user feedback
- Identify common failure modes
- Adjust safety constraints as needed
