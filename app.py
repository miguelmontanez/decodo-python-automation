"""
FastAPI Web Application for Training Data Bot
"""
import os
import tempfile
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from bot import TrainingDataBot
from models import TaskType, ExportFormat
from storage import upload_to_supabase

app = FastAPI(title="Training Data Bot API", version="0.1.0")

# CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads and outputs directories
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the web interface"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Training Data Bot</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
                font-size: 2.5em;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
                font-size: 1.1em;
            }
            .form-group {
                margin-bottom: 25px;
            }
            label {
                display: block;
                margin-bottom: 8px;
                color: #333;
                font-weight: 600;
            }
            input[type="file"], input[type="text"], select {
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-size: 16px;
                transition: border-color 0.3s;
            }
            input[type="file"] {
                padding: 10px;
                cursor: pointer;
            }
            input:focus, select:focus {
                outline: none;
                border-color: #667eea;
            }
            .checkbox-group {
                display: flex;
                flex-wrap: wrap;
                gap: 15px;
                margin-top: 10px;
            }
            .checkbox-item {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .checkbox-item input[type="checkbox"] {
                width: auto;
                cursor: pointer;
            }
            button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 6px;
                font-size: 18px;
                font-weight: 600;
                cursor: pointer;
                width: 100%;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            button:active {
                transform: translateY(0);
            }
            button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            .status {
                margin-top: 20px;
                padding: 15px;
                border-radius: 6px;
                display: none;
            }
            .status.success {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .status.error {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            .status.info {
                background: #d1ecf1;
                color: #0c5460;
                border: 1px solid #bee5eb;
            }
            .progress {
                width: 100%;
                height: 6px;
                background: #e0e0e0;
                border-radius: 3px;
                overflow: hidden;
                margin-top: 10px;
                display: none;
            }
            .progress-bar {
                height: 100%;
                background: linear-gradient(90deg, #667eea, #764ba2);
                width: 0%;
                transition: width 0.3s;
            }
            .download-link {
                display: inline-block;
                margin-top: 15px;
                padding: 12px 24px;
                background: #28a745;
                color: white;
                text-decoration: none;
                border-radius: 6px;
                font-weight: 600;
            }
            .download-link:hover {
                background: #218838;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Training Data Bot</h1>
            <p class="subtitle">Transform documents into AI training datasets</p>
            
            <form id="processForm" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="files">Upload Documents (PDF, TXT, DOCX, etc.)</label>
                    <input type="file" id="files" name="files" multiple accept=".pdf,.txt,.docx,.md,.html,.json,.csv">
                    <small style="color: #666;">You can select multiple files</small>
                </div>
                
                <div class="form-group">
                    <label for="urls">Or Enter URLs (one per line)</label>
                    <textarea id="urls" name="urls" rows="3" style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 6px; font-size: 16px;" placeholder="https://example.com/page1&#10;https://example.com/page2"></textarea>
                </div>
                
                <div class="form-group">
                    <label>Task Types</label>
                    <div class="checkbox-group">
                        <div class="checkbox-item">
                            <input type="checkbox" id="qa" name="task_types" value="qa_generation" checked>
                            <label for="qa" style="font-weight: normal;">Q&A Generation</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="classification" name="task_types" value="classification">
                            <label for="classification" style="font-weight: normal;">Classification</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="summarization" name="task_types" value="summarization" checked>
                            <label for="summarization" style="font-weight: normal;">Summarization</label>
                        </div>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="format">Export Format</label>
                    <select id="format" name="format">
                        <option value="jsonl" selected>JSONL (Recommended)</option>
                        <option value="json">JSON</option>
                    </select>
                </div>
                
                <button type="submit" id="submitBtn">🚀 Generate Training Data</button>
                
                <div class="progress" id="progress">
                    <div class="progress-bar" id="progressBar"></div>
                </div>
                
                <div class="status" id="status"></div>
            </form>
        </div>
        
        <script>
            const form = document.getElementById('processForm');
            const statusDiv = document.getElementById('status');
            const progressDiv = document.getElementById('progress');
            const progressBar = document.getElementById('progressBar');
            const submitBtn = document.getElementById('submitBtn');
            
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = new FormData();
                const fileInput = document.getElementById('files');
                const urlsInput = document.getElementById('urls');
                const formatInput = document.getElementById('format');
                
                // Add files
                if (fileInput.files.length > 0) {
                    for (let file of fileInput.files) {
                        formData.append('files', file);
                    }
                }
                
                // Add URLs
                const urls = urlsInput.value.trim().split('\\n').filter(url => url.trim());
                if (urls.length > 0) {
                    formData.append('urls', JSON.stringify(urls));
                }
                
                // Add task types
                const checkboxes = document.querySelectorAll('input[name="task_types"]:checked');
                const taskTypes = Array.from(checkboxes).map(cb => cb.value);
                formData.append('task_types', JSON.stringify(taskTypes));
                
                // Add format
                formData.append('format', formatInput.value);
                
                // Validate
                if (fileInput.files.length === 0 && urls.length === 0) {
                    showStatus('Please upload files or enter URLs', 'error');
                    return;
                }
                
                if (taskTypes.length === 0) {
                    showStatus('Please select at least one task type', 'error');
                    return;
                }
                
                // Submit
                submitBtn.disabled = true;
                progressDiv.style.display = 'block';
                progressBar.style.width = '30%';
                showStatus('Processing documents...', 'info');
                
                try {
                    const response = await fetch('/api/process', {
                        method: 'POST',
                        body: formData
                    });
                    
                    progressBar.style.width = '80%';
                    
                    if (!response.ok) {
                        const error = await response.json();
                        throw new Error(error.detail || 'Processing failed');
                    }
                    
                    const result = await response.json();
                    progressBar.style.width = '100%';
                    
                    setTimeout(() => {
                        showStatus(`✅ Success! Generated ${result.examples_count} training examples. <a href="${result.download_url}" class="download-link" download>Download Dataset</a>`, 'success');
                        progressDiv.style.display = 'none';
                        submitBtn.disabled = false;
                    }, 500);
                    
                } catch (error) {
                    showStatus(`❌ Error: ${error.message}`, 'error');
                    progressDiv.style.display = 'none';
                    submitBtn.disabled = false;
                }
            });
            
            function showStatus(message, type) {
                statusDiv.textContent = '';
                statusDiv.innerHTML = message;
                statusDiv.className = `status ${type}`;
                statusDiv.style.display = 'block';
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/process")
async def process_documents(
    files: Optional[List[UploadFile]] = File(None),
    urls: Optional[str] = Form(None),
    task_types: str = Form("[]"),
    format: str = Form("jsonl")
):
    """Process uploaded files and/or URLs into training data"""
    try:
        import json
        from uuid import uuid4
        
        task_types_list = json.loads(task_types)
        task_type_enums = []
        for tt in task_types_list:
            if tt == "qa_generation":
                task_type_enums.append(TaskType.QA_GENERATION)
            elif tt == "classification":
                task_type_enums.append(TaskType.CLASSIFICATION)
            elif tt == "summarization":
                task_type_enums.append(TaskType.SUMMARIZATION)
        
        if not task_type_enums:
            raise HTTPException(status_code=400, detail="No task types selected")
        
        # Prepare sources
        sources = []
        
        # Save uploaded files
        if files:
            for file in files:
                file_path = UPLOAD_DIR / f"{uuid4()}_{file.filename}"
                with open(file_path, "wb") as f:
                    content = await file.read()
                    f.write(content)
                sources.append(str(file_path))
        
        # Add URLs
        if urls:
            url_list = json.loads(urls)
            sources.extend(url_list)
        
        if not sources:
            raise HTTPException(status_code=400, detail="No files or URLs provided")
        
        # Process with bot
        async with TrainingDataBot() as bot:
            documents = await bot.load_documents(sources)
            dataset = await bot.process_documents(
                documents=documents,
                task_types=task_type_enums
            )
            
            # Export
            export_format = ExportFormat.JSONL if format == "jsonl" else ExportFormat.JSON
            output_filename = f"dataset_{uuid4().hex[:8]}.{format}"
            output_path = OUTPUT_DIR / output_filename
            
            await bot.export_dataset(dataset, output_path, format=export_format)
            # Optional: upload to Supabase Storage and include a URL
            public_url = upload_to_supabase(output_path)

            return JSONResponse({
                "status": "success",
                "examples_count": len(dataset.examples),
                "download_url": f"/api/download/{output_filename}",
                "output_filename": output_filename,
                "supabase_url": public_url
            })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """Download generated dataset"""
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/octet-stream"
    )

@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "training-data-bot"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

