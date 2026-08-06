import os
import re
import glob
import time
import uuid
import json
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

# Load local .env file if present
ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip("'\"")

from compile import (
    BASE_LATEX_TEMPLATE, 
    BASE_LATEX_CODE, 
    DEFAULT_SUMMARY_LATEX,
    DEFAULT_SKILLS_LATEX,
    DEFAULT_PROJECTS_LATEX, 
    compile_tex_string
)

app = FastAPI(title="DeepSeek OpenRouter Resume Tailor")

# Directory for generated outputs
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_pdfs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Mount static files directory
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class TailorRequest(BaseModel):
    job_description: str
    openrouter_api_key: Optional[str] = None
    model: Optional[str] = "deepseek/deepseek-chat"

def cleanup_old_pdfs(max_age_seconds: int = 600, max_files: int = 5):
    """Automatically purge old generated PDF and TEX files to keep disk usage near zero."""
    try:
        now = time.time()
        files = glob.glob(os.path.join(OUTPUT_DIR, "*"))
        files.sort(key=os.path.getmtime, reverse=True)
        
        for i, fpath in enumerate(files):
            file_age = now - os.path.getmtime(fpath)
            if i >= max_files or file_age > max_age_seconds:
                try:
                    os.remove(fpath)
                except OSError:
                    pass
    except Exception as e:
        print(f"Cleanup error: {e}")

def clean_latex_text(text: str) -> str:
    """Ensure percent signs and special chars in text are properly escaped for LaTeX."""
    text = str(text)
    text = re.sub(r'(?<!\\)%', r'\%', text)
    text = re.sub(r'(?<!\\)&', r'\&', text)
    text = re.sub(r'(?<!\\)\$', r'\$', text)
    return text

def format_summary_to_latex(summary_str: str) -> str:
    """Format summary string for LaTeX."""
    summary_clean = clean_latex_text(summary_str.strip())
    return f"        {summary_clean}"

def format_skills_to_latex(skills_dict: dict) -> str:
    """Format technical skills dict into LaTeX onecolentry blocks."""
    domains = clean_latex_text(skills_dict.get("domains", "Financial Risk Modeling, Predictive Analytics, NLP, LLMs, Quantitative Research, Credit Scoring, Time-Series Analysis."))
    languages = clean_latex_text(skills_dict.get("languages", "Python, R, SQL, SAS."))
    libraries = clean_latex_text(skills_dict.get("libraries", "Pandas, NumPy, Scikit-learn, TensorFlow, PyTorch, LangChain, Statsmodels, Hugging Face, Transformers."))
    tools = clean_latex_text(skills_dict.get("tools", "Power BI, Tableau, AWS, Streamlit, Git, RMS, AIR, CatRisk."))
    
    return f"""    \\begin{{onecolentry}}
        \\textbf{{Domains:}} {domains}
    \\end{{onecolentry}}
    \\vspace{{0.01 cm}}
    \\begin{{onecolentry}}
        \\textbf{{Languages:}} {languages}
    \\end{{onecolentry}}
    \\vspace{{0.01 cm}}
    \\begin{{onecolentry}}
        \\textbf{{Libraries:}} {libraries}
    \\end{{onecolentry}}
    \\vspace{{0.01 cm}}
    \\begin{{onecolentry}}
        \\textbf{{Tools:}} {tools}
    \\end{{onecolentry}}"""

def format_projects_to_latex(projects_data: list) -> str:
    """Format a list of project dicts into valid LaTeX project entries."""
    latex_blocks = []
    for proj in projects_data[:3]:
        year = clean_latex_text(proj.get("year", "2024"))
        title = clean_latex_text(proj.get("title", "Data Science Project"))
        bullets = proj.get("bullets", [])
        
        bullet_items = []
        for i, b in enumerate(bullets):
            b_str = clean_latex_text(b)
            if b_str.lower().startswith("impact:"):
                b_str = b_str[7:].strip()
                bullet_items.append(f"            \\item \\textbf{{Impact:}} {b_str}")
            elif i == len(bullets) - 1 and not any("impact" in item.lower() for item in bullet_items):
                bullet_items.append(f"            \\item \\textbf{{Impact:}} {b_str}")
            else:
                bullet_items.append(f"            \\item {b_str}")
                
        bullets_tex = "\n".join(bullet_items)
        
        block = f"""    \\begin{{twocolentry}}{{{year}}}
        \\textbf{{{title}}}
    \\end{{twocolentry}}
    \\vspace{{0.01 cm}}
    \\begin{{onecolentry}}
        \\begin{{highlights}}
{bullets_tex}
        \\end{{highlights}}
    \\end{{onecolentry}}"""
        latex_blocks.append(block)
        
    return "\n\n    \\vspace{0.01 cm}\n\n".join(latex_blocks)

@app.get("/", response_class=HTMLResponse)
def read_root():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>DeepSeek Resume Tailor API Running</h1>"

@app.get("/api/base-template")
def get_base_template():
    return {"latex_code": BASE_LATEX_CODE}

@app.post("/api/tailor-and-generate")
async def tailor_and_generate(req: TailorRequest):
    # Auto-clean old generated PDFs
    cleanup_old_pdfs(max_age_seconds=300, max_files=3)
    
    jd_text = req.job_description.strip()
    if not jd_text:
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")
        
    api_key = req.openrouter_api_key or os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="OpenRouter API Key is missing. Please provide your API key in the UI or set OPENROUTER_API_KEY in .env.")
        
    model_name = req.model or "deepseek/deepseek-chat"
    
    system_prompt = (
        "You are an expert Quantitative AI & Data Science Resume Specialist for Suraj Vishwakarma.\n"
        "Given a target Job Description (JD), customize Suraj Vishwakarma's resume in valid JSON format:\n"
        "1. 'tailored_summary': Fine-tune ~10% of Suraj's summary to highlight key domain focus requested by the JD (keeping core title as Quantitative Data Scientist).\n"
        "2. 'tailored_skills': Inject key skills/tools from the JD into domains, languages, libraries, and tools lists while preserving core existing skills.\n"
        "3. 'tailored_projects': Generate EXACTLY 3 high-impact academic projects built around the skills required in the JD.\n\n"
        "STRICT JSON OUTPUT FORMAT:\n"
        "{\n"
        "  \"tailored_summary\": \"Quantitative Data Scientist with a strong foundation in Statistics and Financial Risk Modeling. Experienced in building predictive models for loss estimation, customer behavior, and generative AI systems...\",\n"
        "  \"tailored_skills\": {\n"
        "    \"domains\": \"Financial Risk Modeling, Predictive Analytics, NLP, LLMs, Quantitative Research, Credit Scoring, Time-Series Analysis, [JD Domain]\",\n"
        "    \"languages\": \"Python, R, SQL, SAS, [JD Language]\",\n"
        "    \"libraries\": \"Pandas, NumPy, Scikit-learn, TensorFlow, PyTorch, LangChain, Statsmodels, Hugging Face, Transformers, [JD Library]\",\n"
        "    \"tools\": \"Power BI, Tableau, AWS, Streamlit, Git, RMS, AIR, CatRisk, [JD Tool]\"\n"
        "  },\n"
        "  \"tailored_projects\": [\n"
        "    {\n"
        "      \"year\": \"2024\",\n"
        "      \"title\": \"Project Name Matching JD Requirements\",\n"
        "      \"bullets\": [\n"
        "        \"Developed ML/AI pipeline using PyTorch/XGBoost/SQL targeting key JD skills.\",\n"
        "        \"Applied quantitative techniques like time-series/NLP/risk modeling to process datasets.\",\n"
        "        \"Impact: Achieved 91% accuracy, reducing financial risk by 15%.\"\n"
        "      ]\n"
        "    },\n"
        "    ...\n"
        "  ]\n"
        "}\n\n"
        "RULES:\n"
        "1. Ensure JSON output is 100% valid and formatted cleanly.\n"
        "2. Return ONLY the JSON object. Do NOT include markdown text outside the JSON block."
    )
    
    user_prompt = f"TARGET JOB DESCRIPTION:\n{jd_text}\n\nGenerate the JSON output now:"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8050",
        "X-Title": "DeepSeek Resume Tailor"
    }
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 1600
    }
    
    try:
        print(f"Calling OpenRouter DeepSeek API with model {model_name}...")
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=25
        )
        if response.status_code != 200:
            err_msg = response.text
            try:
                err_msg = response.json().get("error", {}).get("message", response.text)
            except Exception:
                pass
            raise HTTPException(status_code=response.status_code, detail=f"OpenRouter API Error: {err_msg}")
            
        res_data = response.json()
        generated_content = res_data["choices"][0]["message"]["content"].strip()
        print("Received response from OpenRouter DeepSeek.")
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="OpenRouter API request timed out (25s). Please try DeepSeek Chat model.")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"OpenRouter API Exception: {str(e)}")
        
    try:
        json_match = re.search(r"\{.*\}", generated_content, re.DOTALL)
        if json_match:
            ai_data = json.loads(json_match.group(0))
        else:
            ai_data = json.loads(generated_content)
        
        summary_tex = format_summary_to_latex(ai_data.get("tailored_summary", DEFAULT_SUMMARY_LATEX))
        skills_tex = format_skills_to_latex(ai_data.get("tailored_skills", {}))
        projects_tex = format_projects_to_latex(ai_data.get("tailored_projects", []))
    except Exception as parse_err:
        print(f"JSON parsing error ({parse_err}), using default fallback.")
        summary_tex = DEFAULT_SUMMARY_LATEX
        skills_tex = DEFAULT_SKILLS_LATEX
        projects_tex = DEFAULT_PROJECTS_LATEX
        
    clean_latex = BASE_LATEX_TEMPLATE.replace("{{SUMMARY_SECTION}}", summary_tex).replace("{{SKILLS_SECTION}}", skills_tex).replace("{{PROJECTS_SECTION}}", projects_tex)
    
    req_id = str(uuid.uuid4())[:8]
    pdf_filename = f"resume_{req_id}.pdf"
    pdf_path = os.path.join(OUTPUT_DIR, pdf_filename)
    tex_path = os.path.join(OUTPUT_DIR, f"resume_{req_id}.tex")
    
    print("Compiling tailored LaTeX to PDF...")
    success, log_or_path = compile_tex_string(clean_latex, pdf_path, tex_path)
    
    if not success or not os.path.exists(pdf_path):
        print("Primary compilation failed, compiling default fallback...")
        fallback_latex = BASE_LATEX_TEMPLATE.replace("{{SUMMARY_SECTION}}", DEFAULT_SUMMARY_LATEX).replace("{{SKILLS_SECTION}}", DEFAULT_SKILLS_LATEX).replace("{{PROJECTS_SECTION}}", DEFAULT_PROJECTS_LATEX)
        fallback_success, _ = compile_tex_string(fallback_latex, pdf_path, tex_path)
        if not fallback_success:
            raise HTTPException(status_code=500, detail=f"LaTeX compilation error: {log_or_path}")
            
    return {
        "status": "success",
        "pdf_id": req_id,
        "pdf_url": f"/api/pdf/{req_id}",
        "download_name": "Suraj_Vishwakarma_Tailored_Resume.pdf",
        "latex_code": clean_latex
    }

@app.get("/api/pdf/{pdf_id}")
def serve_pdf(pdf_id: str):
    pdf_path = os.path.join(OUTPUT_DIR, f"resume_{pdf_id}.pdf")
    if os.path.exists(pdf_path):
        return FileResponse(
            pdf_path, 
            media_type="application/pdf", 
            filename="Suraj_Vishwakarma_Resume.pdf",
            headers={"Content-Disposition": "inline; filename=Suraj_Vishwakarma_Resume.pdf"}
        )
    raise HTTPException(status_code=404, detail="PDF not found.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8050)
