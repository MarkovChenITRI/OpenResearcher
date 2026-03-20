"""
OpenResearcher Web Application
Flask-based interface for research question generation and management
Runs from project root directory for security
Uses folder-based document processing with real-time progress tracking
"""
import os
import json
import asyncio
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, Response
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import queue

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] if __name__ == '__main__':
    print("=" * 60)
    print("🚀 OpenResearcher Web Application")
    print("=" * 60)
    print("\n📝 Features:")
    print("  1. 📁 Folder-based document processing")
    print("  2. 🖼️  Image support (flowcharts, diagrams)")
    print("  3. 📊 Real-time progress tracking")
    print("  4. 🤖 Two-stage AI analysis (summary → questions)")
    print("  5. 🚀 Research execution with GPT-5.4")
    print("\n🤖 AI Models:")
    print("  • GPT-4o: Question generation (with vision)")
    print("  • GPT-5.4: Research execution")
    print("\n📄 Supported Files:")
    print("  • Text: .md, .txt, .py, .json, .csv, .html, .xml")
    print("  • Images: .png, .jpg, .jpeg, .gif, .bmp, .webp")
    print("\n🌐 URLs:")
    print("  • Main (Folder Mode): http://localhost:7080")
    print("  • Legacy (Upload Mode): http://localhost:7080/legacy")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=7080)fig['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
app.config['RESULTS_FOLDER'] = 'results'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# Global storage for research tasks and processing queues
research_tasks = {}
processing_progress = {}  # Track document processing progress

# Import Azure OpenAI
from utils.azure_openai_generator import AzureOpenAIAsyncGenerator


class ResearchTask:
    """Manages a single research task execution"""
    def __init__(self, task_id, questions, output_dir, time_limit=None):
        self.task_id = task_id
        self.questions = questions
        self.output_dir = output_dir
        self.time_limit = time_limit
        self.status = "pending"
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
            questions_file = os.path.join(self.output_dir, "questions.json")
            with open(questions_file, 'w', encoding='utf-8') as f:
                json.dump(self.questions, f, ensure_ascii=False, indent=2)
            
            # Simple and secure: deploy_agent.py is in current directory
            cmd = [
                "python", "deploy_agent.py",
                "--vllm_server_url", "AZURE_OPENAI",
                "--dataset_name", "custom",
                "--data_path", questions_file,
                "--browser_backend", "serper",
                "--output_dir", self.output_dir,
                "--model_name_or_path", os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5.4"),
                "--search_url", "NONE"
            ]
            
            with open(self.log_file, 'w', encoding='utf-8') as log:
                self.process = subprocess.Popen(
                    cmd,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                
                start = time.time()
                while self.process.poll() is None:
                    if self.time_limit and (time.time() - start) > self.time_limit:
                        self.stop()
                        break
                    
                    self._update_progress()
                    time.sleep(5)
                
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
            result_files = list(Path(self.output_dir).glob("*.jsonl"))
            if result_files:
                result_file = result_files[0]
                with open(result_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    completed = len(lines)
                    total = len(self.questions)
                    self.progress = int((completed / total) * 100) if total > 0 else 0
                    
                    if lines:
                        latest = json.loads(lines[-1])
                        self.current_question = latest.get('question', 'Unknown')
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


def extract_file_content(filepath):
    """Extract content from files - supports text and images"""
    ext = Path(filepath).suffix.lower()
    
    # Text files
    if ext in ['.md', '.txt']:
        with open(filepath, 'r', encoding='utf-8') as f:
            return {"type": "text", "content": f.read()}
    
    # Image files - return base64 for vision API
    elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
        import base64
        with open(filepath, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
            return {"type": "image", "content": image_data, "format": ext[1:]}
    
    else:
        return {"type": "text", "content": f"[{ext} file: {Path(filepath).name}]"}


def scan_folder_for_documents(folder_path):
    """Scan folder and return all supported documents"""
    supported_text = ['.md', '.txt', '.py', '.json', '.csv', '.html', '.xml']
    supported_images = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
    supported_exts = supported_text + supported_images
    
    documents = []
    folder = Path(folder_path)
    
    if not folder.exists() or not folder.is_dir():
        return []
    
    # Recursively find all supported files
    for file_path in folder.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in supported_exts:
            documents.append({
                'path': str(file_path),
                'filename': file_path.name,
                'relative_path': str(file_path.relative_to(folder)),
                'extension': file_path.suffix.lower()
            })
    
    return documents


async def process_documents_with_progress(documents, progress_id):
    """Process all documents and emit progress updates"""
    processed_docs = []
    total = len(documents)
    
    for idx, doc_info in enumerate(documents):
        # Update progress
        progress = {
            'status': 'processing',
            'current_file': doc_info['relative_path'],
            'processed': idx,
            'total': total,
            'percentage': int((idx / total) * 100) if total > 0 else 0
        }
        processing_progress[progress_id] = progress
        
        try:
            content_data = extract_file_content(doc_info['path'])
            processed_docs.append({
                'filename': doc_info['filename'],
                'relative_path': doc_info['relative_path'],
                **content_data
            })
            
            # Small delay to make progress visible
            await asyncio.sleep(0.1)
            
        except Exception as e:
            print(f"Error processing {doc_info['path']}: {e}")
            processed_docs.append({
                'filename': doc_info['filename'],
                'relative_path': doc_info['relative_path'],
                'type': 'text',
                'content': f"[Error reading file: {e}]"
            })
    
    # Final progress update
    processing_progress[progress_id] = {
        'status': 'completed',
        'current_file': 'All files processed',
        'processed': total,
        'total': total,
        'percentage': 100
    }
    
    return processed_docs


async def summarize_documents_before_questions(documents, context):
    """First pass: Summarize all documents to understand the full context"""
    
    # Separate by type
    text_docs = [doc for doc in documents if doc.get('type') == 'text']
    image_docs = [doc for doc in documents if doc.get('type') == 'image']
    
    # Build summary prompt
    docs_summary = "\n\n".join([
        f"File: {doc['relative_path']}\nContent preview: {doc['content'][:500]}..."
        for doc in text_docs[:20]  # Limit to first 20 text files for summary
    ])
    
    summary_prompt = f"""You are analyzing a research project folder. Please provide a concise summary of the research context based on these documents.

Research Context provided by user:
{context}

Documents found ({len(text_docs)} text files, {len(image_docs)} images):
{docs_summary}

Provide a 2-3 paragraph summary that captures:
1. Main research theme
2. Key methodologies or approaches mentioned
3. Important findings or hypotheses
4. Any gaps or areas needing further investigation

Return your summary in plain text."""

    async with AzureOpenAIAsyncGenerator(
        azure_endpoint=os.getenv("AZURE_OPENAI_4O_ENDPOINT"),
        deployment_name=os.getenv("AZURE_OPENAI_4O_DEPLOYMENT"),
        api_key=os.getenv("AZURE_OPENAI_4O_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_4O_API_VERSION"),
        use_native_tools=False
    ) as generator:
        response = await generator.chat_completion(
            messages=[{"role": "user", "content": summary_prompt}],
            max_tokens=1000,
            temperature=0.5
        )
        
        return response['choices'][0]['message']['content']


async def generate_questions_from_documents(documents, context, num_questions, document_summary=None):
    """Generate research questions using Azure OpenAI GPT-4o (with vision) based on context and optional documents
    
    Args:
        documents: List of processed documents
        context: User's research context
        num_questions: Number of questions to generate
        document_summary: Optional pre-generated summary of all documents
    """
    
    # Detect if any images are present
    has_images = any(doc.get('type') == 'image' for doc in documents)
    
    # Build messages for GPT-4o (supports both text and images)
    if documents:
        # Separate text and image documents
        text_docs = [doc for doc in documents if doc.get('type') == 'text']
        image_docs = [doc for doc in documents if doc.get('type') == 'image']
        
        # Build prompt with summary-first approach
        base_prompt = f"""You are a research question generator for the OpenResearcher platform. Based on the comprehensive analysis below, generate {num_questions} high-quality, specific research questions.

Research Context and Goals:
{context}

Document Summary:
{document_summary if document_summary else 'Processing individual documents...'}

Total Documents Analyzed: {len(text_docs)} text files, {len(image_docs)} images

"""

        # Add representative documents (not all, to avoid token limits)
        if text_docs:
            # Show up to 5 most relevant text documents
            representative_docs = text_docs[:5]
            docs_text = "\n\n".join([
                f"📄 {doc['relative_path']}\n{doc['content'][:1000]}"
                for doc in representative_docs
            ])
            base_prompt += f"""Key Document Samples:
{docs_text}

"""

        if image_docs:
            base_prompt += f"""Visual Information: {len(image_docs)} image(s) attached (flowcharts, diagrams, screenshots). Please analyze these for methodological insights.

"""

        base_prompt += f"""Generate {num_questions} research questions that:
1. Are specific and focused on the research context and documents
2. Require web search and browsing multiple sources to answer
3. Need analysis and synthesis of information
4. Have clear, verifiable answers
5. If images show flowcharts/diagrams, generate questions about the methodology or process
6. Consider ALL the documents analyzed (not just the samples shown)

Return ONLY a JSON array of questions in this format:
[
  {{"qid": "q1", "question": "Your question here", "answer": ""}}
]"""

        # Build message content with images (GPT-4o Vision API format)
        if has_images:
            message_content = [{"type": "text", "text": base_prompt}]
            # Limit to first 3 images to avoid token limits
            for img_doc in image_docs[:3]:
                message_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/{img_doc['format']};base64,{img_doc['content']}"
                    }
                })
            messages = [{"role": "user", "content": message_content}]
        else:
            messages = [{"role": "user", "content": base_prompt}]
        
    else:
        # No documents - generate based on context alone
        prompt = f"""Based on the following research context and goals, generate {num_questions} high-quality research questions suitable for deep research with OpenResearcher.

Research Context and Goals:
{context}

Generate {num_questions} research questions that:
1. Are specific and focused on the research context
2. Require web search and browsing multiple sources
3. Need analysis and synthesis of information
4. Have clear, verifiable answers

Return ONLY a JSON array of questions in this format:
[
  {{"qid": "q1", "question": "Your question here", "answer": ""}}
]"""
        messages = [{"role": "user", "content": prompt}]

    # Use GPT-4o for question generation (supports vision)
    async with AzureOpenAIAsyncGenerator(
        azure_endpoint=os.getenv("AZURE_OPENAI_4O_ENDPOINT"),
        deployment_name=os.getenv("AZURE_OPENAI_4O_DEPLOYMENT"),
        api_key=os.getenv("AZURE_OPENAI_4O_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_4O_API_VERSION"),
        use_native_tools=False
    ) as generator:
        response = await generator.chat_completion(
            messages=messages,
            max_tokens=2000,
            temperature=0.7
        )
        
        content = response['choices'][0]['message']['content']
        
        try:
            questions = json.loads(content)
        except:
            import re
            match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', content, re.DOTALL)
            if match:
                questions = json.loads(match.group(1))
            else:
                questions = [{"qid": f"q{i+1}", "question": f"Research question {i+1}", "answer": ""} for i in range(num_questions)]
        
        return questions


async def refine_questions_with_llm(questions, feedback):
    """Refine questions based on user feedback - using GPT-4o"""
    prompt = f"""You are helping refine research questions. Here are the current questions:

{json.dumps(questions, indent=2, ensure_ascii=False)}

User feedback: {feedback}

Please refine these questions based on the feedback. Maintain the same structure but improve the questions.

Return ONLY the updated JSON array."""

    # Use GPT-4o for refinement as well
    async with AzureOpenAIAsyncGenerator(
        azure_endpoint=os.getenv("AZURE_OPENAI_4O_ENDPOINT"),
        deployment_name=os.getenv("AZURE_OPENAI_4O_DEPLOYMENT"),
        api_key=os.getenv("AZURE_OPENAI_4O_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_4O_API_VERSION"),
        use_native_tools=False
    ) as generator:
        response = await generator.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.7
        )
        
        content = response['choices'][0]['message']['content']
        
        try:
            refined = json.loads(content)
        except:
            import re
            match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', content, re.DOTALL)
            if match:
                refined = json.loads(match.group(1))
            else:
                refined = questions
        
        return refined


@app.route('/')
def index():
    """Main dashboard - folder mode"""
    return render_template('folder_mode.html')


@app.route('/legacy')
def legacy():
    """Legacy upload mode"""
    return render_template('index.html')


@app.route('/api/analyze_documents', methods=['POST'])
def analyze_documents():
    """Generate research questions based on context and folder of documents"""
    try:
        data = request.json
        folder_path = data.get('folder_path', '')
        context = data.get('context', '')
        num_questions = int(data.get('num_questions', 3))
        
        # Context is required
        if not context:
            return jsonify({"error": "Research context is required"}), 400
        
        # Folder path is required
        if not folder_path:
            return jsonify({"error": "Folder path is required"}), 400
        
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            return jsonify({"error": "Invalid folder path"}), 400
        
        # Generate unique progress ID
        progress_id = f"progress_{int(time.time())}"
        
        # Scan folder for documents
        document_files = scan_folder_for_documents(folder_path)
        
        if not document_files:
            return jsonify({"error": "No supported documents found in folder"}), 400
        
        # Process documents with progress tracking
        async def process_and_generate():
            # Step 1: Process all documents
            processing_progress[progress_id] = {
                'status': 'scanning',
                'current_file': 'Scanning folder...',
                'processed': 0,
                'total': len(document_files),
                'percentage': 0
            }
            
            processed_docs = await process_documents_with_progress(document_files, progress_id)
            
            # Step 2: Generate summary
            processing_progress[progress_id] = {
                'status': 'summarizing',
                'current_file': 'Analyzing all documents...',
                'processed': len(processed_docs),
                'total': len(processed_docs),
                'percentage': 50
            }
            
            summary = await summarize_documents_before_questions(processed_docs, context)
            
            # Step 3: Generate questions
            processing_progress[progress_id] = {
                'status': 'generating',
                'current_file': 'Generating research questions...',
                'processed': len(processed_docs),
                'total': len(processed_docs),
                'percentage': 75
            }
            
            questions = await generate_questions_from_documents(
                processed_docs, context, num_questions, summary
            )
            
            # Complete
            processing_progress[progress_id] = {
                'status': 'done',
                'current_file': 'Completed!',
                'processed': len(processed_docs),
                'total': len(processed_docs),
                'percentage': 100
            }
            
            return questions, processed_docs, summary
        
        questions, processed_docs, summary = asyncio.run(process_and_generate())
        
        return jsonify({
            "success": True,
            "questions": questions,
            "documents_processed": len(processed_docs),
            "document_list": [doc['relative_path'] for doc in processed_docs],
            "summary": summary,
            "has_images": any(doc.get('type') == 'image' for doc in processed_docs),
            "model_used": "gpt-4o (vision-capable)",
            "progress_id": progress_id
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/progress/<progress_id>')
def get_progress(progress_id):
    """Get progress of document processing"""
    if progress_id in processing_progress:
        return jsonify(processing_progress[progress_id])
    else:
        return jsonify({"error": "Progress ID not found"}), 404


@app.route('/api/scan_folder', methods=['POST'])
def scan_folder():
    """Scan a folder and return document count"""
    try:
        data = request.json
        folder_path = data.get('folder_path', '')
        
        if not folder_path or not os.path.exists(folder_path):
            return jsonify({"error": "Invalid folder path"}), 400
        
        documents = scan_folder_for_documents(folder_path)
        
        # Group by type
        text_files = [d for d in documents if d['extension'] in ['.md', '.txt', '.py', '.json', '.csv', '.html', '.xml']]
        image_files = [d for d in documents if d['extension'] in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']]
        
        return jsonify({
            "success": True,
            "total_files": len(documents),
            "text_files": len(text_files),
            "image_files": len(image_files),
            "file_list": [d['relative_path'] for d in documents]
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
        
        refined = asyncio.run(refine_questions_with_llm(questions, feedback))
        
        return jsonify({"success": True, "questions": refined})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/start_research', methods=['POST'])
def start_research():
    """Start a research task"""
    try:
        data = request.json
        questions = data.get('questions', [])
        time_limit = data.get('time_limit')
        
        if not questions:
            return jsonify({"error": "No questions provided"}), 400
        
        task_id = f"task_{int(time.time())}"
        output_dir = os.path.join(app.config['RESULTS_FOLDER'], task_id)
        os.makedirs(output_dir, exist_ok=True)
        
        task = ResearchTask(task_id, questions, output_dir, time_limit)
        research_tasks[task_id] = task
        task.start()
        
        return jsonify({"success": True, "task_id": task_id, "message": "Research started"})
    
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


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 OpenResearcher Web Application")
    print("=" * 60)
    print("\n📝 Features:")
    print("  1. 📁 Document analysis & question generation")
    print("  2. �️  Image support (flowcharts, diagrams)")
    print("  3. �📝 Visual question management")
    print("  4. 🚀 Real-time research execution")
    print("  5. 📊 Results tracking & export")
    print("\n🤖 AI Models:")
    print("  • GPT-4o: Question generation (with vision)")
    print("  • GPT-5.4: Research execution")
    print("\n📄 Supported Files:")
    print("  • Text: .md, .txt")
    print("  • Images: .png, .jpg, .jpeg, .gif, .bmp, .webp")
    print("\n🌐 Starting server at http://localhost:7080")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=7080)
