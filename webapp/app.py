"""
OpenResearcher Web Application
Flask-based web interface for research question generation and management
"""
import os
import json
import asyncio
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
import markdown
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['RESULTS_FOLDER'] = 'results'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# Global storage for research tasks
research_tasks = {}

# Import Azure OpenAI for question generation
from utils.azure_openai_generator import AzureOpenAIAsyncGenerator


class ResearchTask:
    """Manages a single research task execution"""
    def __init__(self, task_id, questions, output_dir, time_limit=None):
        self.task_id = task_id
        self.questions = questions
        self.output_dir = output_dir
        self.time_limit = time_limit
        self.status = "pending"  # pending, running, completed, stopped, error
        self.progress = 0
        self.current_question = None
        self.results = []
        self.process = None
        self.start_time = None
        self.end_time = None
        self.log_file = os.path.join(output_dir, "research.log")
        self.thread = None
    
    def start(self):
        """Start the research task in a background thread"""
        self.status = "running"
        self.start_time = datetime.now()
        self.thread = threading.Thread(target=self._run_research)
        self.thread.daemon = True
        self.thread.start()
    
    def _run_research(self):
        """Execute the research using deploy_agent.py"""
        try:
            # Create questions file
            questions_file = os.path.join(self.output_dir, "questions.json")
            with open(questions_file, 'w', encoding='utf-8') as f:
                json.dump(self.questions, f, ensure_ascii=False, indent=2)
            
            # Get path to deploy_agent.py (in parent directory)
            webapp_dir = Path(__file__).parent
            project_root = webapp_dir.parent
            deploy_agent_path = project_root / "deploy_agent.py"
            
            if not deploy_agent_path.exists():
                raise FileNotFoundError(f"deploy_agent.py not found at {deploy_agent_path}")
            
            # Build command - use absolute paths
            cmd = [
                "python", str(deploy_agent_path),
                "--vllm_server_url", "AZURE_OPENAI",
                "--dataset_name", "custom",
                "--data_path", str(Path(questions_file).absolute()),
                "--browser_backend", "serper",
                "--output_dir", str(Path(self.output_dir).absolute()),
                "--model_name_or_path", os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5.4"),
                "--search_url", "NONE"  # Required parameter
            ]
            
            # Start process with output capture
            # Set working directory to project root for proper imports
            with open(self.log_file, 'w', encoding='utf-8') as log:
                self.process = subprocess.Popen(
                    cmd,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    text=True,
                    cwd=str(project_root)  # Run from project root
                )
                
                # Monitor process with timeout
                start = time.time()
                while self.process.poll() is None:
                    # Check time limit
                    if self.time_limit and (time.time() - start) > self.time_limit:
                        self.stop()
                        break
                    
                    # Update progress by parsing log
                    self._update_progress()
                    time.sleep(5)
                
                # Final progress update
                self._update_progress()
                
                if self.process.returncode == 0:
                    self.status = "completed"
                else:
                    self.status = "error"
        
        except Exception as e:
            self.status = "error"
            print(f"Research task {self.task_id} error: {e}")
        
        finally:
            self.end_time = datetime.now()
    
    def stop(self):
        """Stop the research task"""
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process.wait(timeout=10)
            self.status = "stopped"
    
    def _update_progress(self):
        """Update progress by parsing results"""
        try:
            # Look for output JSONL file
            result_files = list(Path(self.output_dir).glob("*.jsonl"))
            if result_files:
                result_file = result_files[0]
                with open(result_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    completed = len(lines)
                    total = len(self.questions)
                    self.progress = int((completed / total) * 100) if total > 0 else 0
                    
                    # Parse latest result
                    if lines:
                        latest = json.loads(lines[-1])
                        self.current_question = latest.get('question', 'Unknown')
                        
                        # Store results
                        self.results = [json.loads(line) for line in lines]
        except Exception as e:
            print(f"Error updating progress: {e}")
    
    def get_status(self):
        """Get current status as dict"""
        return {
            "task_id": self.task_id,
            "status": self.status,
            "progress": self.progress,
            "current_question": self.current_question,
            "total_questions": len(self.questions),
            "completed_questions": len(self.results),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "time_limit": self.time_limit,
            "elapsed_time": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        }


@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')


@app.route('/api/analyze_documents', methods=['POST'])
def analyze_documents():
    """Analyze uploaded documents and generate research questions using LLM"""
    try:
        # Get uploaded files
        files = request.files.getlist('files')
        context = request.form.get('context', '')
        num_questions = int(request.form.get('num_questions', 3))
        
        if not files:
            return jsonify({"error": "No files uploaded"}), 400
        
        # Process files
        documents_content = []
        for file in files:
            if file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Extract content based on file type
                content = extract_file_content(filepath)
                documents_content.append({
                    "filename": filename,
                    "content": content
                })
        
        # Generate questions using LLM
        questions = asyncio.run(generate_questions_from_documents(
            documents_content, context, num_questions
        ))
        
        return jsonify({
            "success": True,
            "questions": questions,
            "documents": [doc["filename"] for doc in documents_content]
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/refine_questions', methods=['POST'])
def refine_questions():
    """Refine questions using conversational feedback"""
    try:
        data = request.json
        questions = data.get('questions', [])
        feedback = data.get('feedback', '')
        
        if not questions or not feedback:
            return jsonify({"error": "Questions and feedback required"}), 400
        
        # Use LLM to refine questions
        refined = asyncio.run(refine_questions_with_llm(questions, feedback))
        
        return jsonify({
            "success": True,
            "questions": refined
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/start_research', methods=['POST'])
def start_research():
    """Start a research task"""
    try:
        data = request.json
        questions = data.get('questions', [])
        time_limit = data.get('time_limit')  # seconds or None for unlimited
        
        if not questions:
            return jsonify({"error": "No questions provided"}), 400
        
        # Create task
        task_id = f"task_{int(time.time())}"
        output_dir = os.path.join(app.config['RESULTS_FOLDER'], task_id)
        os.makedirs(output_dir, exist_ok=True)
        
        task = ResearchTask(task_id, questions, output_dir, time_limit)
        research_tasks[task_id] = task
        
        # Start task
        task.start()
        
        return jsonify({
            "success": True,
            "task_id": task_id,
            "message": "Research started"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/task_status/<task_id>')
def task_status(task_id):
    """Get status of a research task"""
    task = research_tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    return jsonify(task.get_status())


@app.route('/api/stop_research/<task_id>', methods=['POST'])
def stop_research(task_id):
    """Stop a running research task"""
    task = research_tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    task.stop()
    return jsonify({"success": True, "message": "Task stopped"})


@app.route('/api/task_results/<task_id>')
def task_results(task_id):
    """Get results of a research task"""
    task = research_tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    return jsonify({
        "success": True,
        "task_id": task_id,
        "status": task.status,
        "results": task.results,
        "total_questions": len(task.questions),
        "completed": len(task.results)
    })


@app.route('/api/task_logs/<task_id>')
def task_logs(task_id):
    """Get logs of a research task"""
    task = research_tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    try:
        if os.path.exists(task.log_file):
            with open(task.log_file, 'r', encoding='utf-8') as f:
                logs = f.read()
            return jsonify({"success": True, "logs": logs})
        else:
            return jsonify({"success": True, "logs": "No logs yet"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/export_results/<task_id>')
def export_results(task_id):
    """Export results as JSON"""
    task = research_tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    export_path = os.path.join(task.output_dir, f"{task_id}_export.json")
    with open(export_path, 'w', encoding='utf-8') as f:
        json.dump({
            "task_id": task_id,
            "questions": task.questions,
            "results": task.results,
            "metadata": task.get_status()
        }, f, ensure_ascii=False, indent=2)
    
    return send_file(export_path, as_attachment=True)


@app.route('/api/list_tasks')
def list_tasks():
    """List all research tasks"""
    tasks_list = []
    for task_id, task in research_tasks.items():
        tasks_list.append(task.get_status())
    
    return jsonify({"success": True, "tasks": tasks_list})


# Import file utilities
from file_utils import extract_file_content

# Helper functions
# (extract_file_content is now imported from file_utils.py)


async def generate_questions_from_documents(documents, context, num_questions):
    """Generate research questions using Azure OpenAI"""
    # Build prompt
    docs_text = "\n\n".join([
        f"Document: {doc['filename']}\n{doc['content'][:2000]}"
        for doc in documents
    ])
    
    prompt = f"""Based on the following documents and context, generate {num_questions} high-quality research questions suitable for deep research with OpenResearcher.

Context: {context}

Documents:
{docs_text}

Generate {num_questions} research questions that:
1. Are specific and focused
2. Require web search and browsing multiple sources
3. Need analysis and synthesis of information
4. Have clear, verifiable answers

Return ONLY a JSON array of questions in this format:
[
  {{
    "qid": "q1",
    "question": "Your question here",
    "answer": ""
  }}
]"""

    async with AzureOpenAIAsyncGenerator(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        use_native_tools=False
    ) as generator:
        response = await generator.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.7
        )
        
        content = response['choices'][0]['message']['content']
        
        # Extract JSON from response
        try:
            # Try direct parse
            questions = json.loads(content)
        except:
            # Try to find JSON in markdown code block
            import re
            match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', content, re.DOTALL)
            if match:
                questions = json.loads(match.group(1))
            else:
                # Fallback: create default questions
                questions = [
                    {
                        "qid": f"q{i+1}",
                        "question": f"Research question {i+1} based on documents",
                        "answer": ""
                    }
                    for i in range(num_questions)
                ]
        
        return questions


async def refine_questions_with_llm(questions, feedback):
    """Refine questions based on user feedback"""
    prompt = f"""You are helping refine research questions. Here are the current questions:

{json.dumps(questions, indent=2, ensure_ascii=False)}

User feedback: {feedback}

Please refine these questions based on the feedback. Maintain the same structure but improve the questions.

Return ONLY the updated JSON array."""

    async with AzureOpenAIAsyncGenerator(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        use_native_tools=False
    ) as generator:
        response = await generator.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.7
        )
        
        content = response['choices'][0]['message']['content']
        
        # Extract JSON
        try:
            refined = json.loads(content)
        except:
            import re
            match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', content, re.DOTALL)
            if match:
                refined = json.loads(match.group(1))
            else:
                refined = questions  # Return original if parsing fails
        
        return refined


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 OpenResearcher Web Application")
    print("=" * 60)
    print("\n📝 Features:")
    print("  1. Document analysis & question generation")
    print("  2. Visual question management")
    print("  3. Real-time research execution")
    print("  4. Results tracking & export")
    print("\n🌐 Starting server at http://localhost:5000")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
