import os
import re
import glob
import time
import uuid
import json
import requests
import io
import pdfplumber
import docx
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, List, Any

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
    TEMPLATES_REGISTRY,
    BASE_LATEX_TEMPLATE, 
    BASE_LATEX_CODE, 
    DEFAULT_SUMMARY_LATEX,
    DEFAULT_SKILLS_LATEX,
    DEFAULT_PROJECTS_LATEX, 
    compile_tex_string
)

app = FastAPI(title="Underleaf - DeepSeek AI Resume Tailor & Multi-Template Studio")

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_pdfs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class TailorRequest(BaseModel):
    job_description: str
    template_id: Optional[str] = "jake_ryan"
    openrouter_api_key: Optional[str] = None
    model: Optional[str] = "deepseek/deepseek-chat"
    profile_data: Optional[Dict[str, Any]] = None

class ScratchRequest(BaseModel):
    template_id: Optional[str] = "jake_ryan"
    job_description: Optional[str] = ""
    openrouter_api_key: Optional[str] = None
    model: Optional[str] = "deepseek/deepseek-chat"
    profile_data: Dict[str, Any]

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
    return clean_latex_text(summary_str.strip())

def format_skills_to_latex(skills_dict: dict, template_id: str = "jake_ryan") -> str:
    if isinstance(skills_dict, str):
        return clean_latex_text(skills_dict)
        
    domains = clean_latex_text(skills_dict.get("domains", "Financial Risk Modeling, Predictive Analytics, NLP, LLMs"))
    languages = clean_latex_text(skills_dict.get("languages", "Python, R, SQL, SAS"))
    libraries = clean_latex_text(skills_dict.get("libraries", "Pandas, NumPy, Scikit-learn, TensorFlow, PyTorch, LangChain"))
    tools = clean_latex_text(skills_dict.get("tools", "Power BI, Tableau, AWS, Streamlit, Git"))
    
    if template_id == "jake_ryan":
        return f"\\textbf{{Domains:}} {{{domains}}} \\\\ \n\\textbf{{Languages:}} {{{languages}}} \\\\ \n\\textbf{{Libraries/Frameworks:}} {{{libraries}}} \\\\ \n\\textbf{{Tools:}} {{{tools}}}"
    elif template_id == "deedy_resume":
        return f"\\subsection*{{Domains}}\n{domains}\n\n\\subsection*{{Languages}}\n{languages}\n\n\\subsection*{{Libraries}}\n{libraries}\n\n\\subsection*{{Tools}}\n{tools}"
    else:
        return f"\\textbf{{Domains:}} {domains} \\\\\n\\textbf{{Languages:}} {languages} \\\\\n\\textbf{{Libraries:}} {libraries} \\\\\n\\textbf{{Tools:}} {tools}"

def format_experience_to_latex(exp_data: list, template_id: str = "jake_ryan") -> str:
    if not exp_data:
        return ""
    blocks = []
    for exp in exp_data:
        dates = clean_latex_text(exp.get("dates", "May 2026 -- Present"))
        role = clean_latex_text(exp.get("role", "AI Engineer"))
        company = clean_latex_text(exp.get("company", "PSS"))
        loc = clean_latex_text(exp.get("location", "Mumbai, IN"))
        bullets = exp.get("bullets", [])
        
        if template_id == "jake_ryan":
            bullet_tex = "\n".join([f"        \\resumeItem{{{clean_latex_text(b)}}}" for b in bullets])
            block = f"""    \\resumeSubheading
      {{{role}}}{{{dates}}}
      {{{company}}}{{{loc}}}
      \\resumeItemListStart
{bullet_tex}
      \\resumeItemListEnd"""
        elif template_id == "deedy_resume":
            bullet_tex = "\n".join([f"  \\item {clean_latex_text(b)}" for b in bullets])
            block = f"""\\subsection*{{{company} \\hfill \\normalfont\\footnotesize {loc}}}
\\textit{{{role}}} \\hfill {{\\footnotesize {dates}}}
\\begin{{itemize}}[leftmargin=*,itemsep=1pt,topsep=2pt]
{bullet_tex}
\\end{{itemize}}"""
        else:
            bullet_tex = "\n".join([f"            \\item {clean_latex_text(b)}" for b in bullets])
            block = f"""    \\textbf{{{role}}}, {company} \\hfill {{{dates}}}\\\\
    \\begin{{itemize}}[leftmargin=12pt, topsep=1pt, itemsep=1pt]
{bullet_tex}
    \\end{{itemize}}"""
        blocks.append(block)
    return "\n\n".join(blocks)

def format_projects_to_latex(projects_data: list, template_id: str = "jake_ryan") -> str:
    if not projects_data:
        return ""
    blocks = []
    for proj in projects_data[:3]:
        year = clean_latex_text(proj.get("year", "2024"))
        title = clean_latex_text(proj.get("title", "Data Science Project"))
        bullets = proj.get("bullets", [])
        
        if template_id == "jake_ryan":
            bullet_items = []
            for i, b in enumerate(bullets):
                b_str = clean_latex_text(b)
                if b_str.lower().startswith("impact:"):
                    b_str = b_str[7:].strip()
                    bullet_items.append(f"        \\resumeItem{{\\textbf{{Impact:}} {b_str}}}")
                else:
                    bullet_items.append(f"        \\resumeItem{{{b_str}}}")
            bullets_tex = "\n".join(bullet_items)
            block = f"""    \\resumeProjectHeading
      {{\\textbf{{{title}}}}}{{{year}}}
      \\resumeItemListStart
{bullets_tex}
      \\resumeItemListEnd"""
        elif template_id == "deedy_resume":
            bullet_items = [f"  \\item {clean_latex_text(b)}" for b in bullets]
            bullets_tex = "\n".join(bullet_items)
            block = f"""\\subsection*{{{title} \\hfill \\normalfont\\footnotesize {year}}}
\\begin{{itemize}}[leftmargin=*,itemsep=1pt,topsep=2pt]
{bullets_tex}
\\end{{itemize}}"""
        else:
            bullet_items = [f"            \\item {clean_latex_text(b)}" for b in bullets]
            bullets_tex = "\n".join(bullet_items)
            block = f"""    \\textbf{{{title}}} \\hfill {{{year}}}\\\\
    \\begin{{itemize}}[leftmargin=12pt, topsep=1pt, itemsep=1pt]
{bullets_tex}
    \\end{{itemize}}"""
        blocks.append(block)
    return "\n\n".join(blocks)

def format_education_to_latex(edu_data: list, template_id: str = "jake_ryan") -> str:
    if not edu_data:
        return ""
    blocks = []
    for edu in edu_data:
        year = clean_latex_text(edu.get("year", "May 2025"))
        degree = clean_latex_text(edu.get("degree", "M.Sc. Statistics & Data Science"))
        inst = clean_latex_text(edu.get("institution", "NMIMS Mumbai"))
        loc = clean_latex_text(edu.get("location", "Mumbai, IN"))
        detail = clean_latex_text(edu.get("detail", "CGPA: 3.67 / 4.0"))
        
        if template_id == "jake_ryan":
            block = f"""    \\resumeSubheading
      {{{inst}}}{{{loc}}}
      {{{degree}}}{{{year}}}"""
        elif template_id == "deedy_resume":
            block = f"""\\subsection*{{{inst}}}
{degree} \\\\
{{\\footnotesize {detail}}} \\\\
{{\\footnotesize {year}}}"""
        else:
            block = f"""    \\textbf{{{inst}}} \\hfill {{{year}}}\\\\
    \\textit{{{degree}}} -- {{{detail}}}"""
        blocks.append(block)
    return "\n\n".join(blocks)

def format_certifications_to_latex(certs_data: list) -> str:
    if not certs_data:
        return ""
    return "\n".join([f"  \\item {clean_latex_text(c)}" for c in certs_data])

@app.get("/", response_class=HTMLResponse)
def read_root():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Underleaf AI Resume Studio Running</h1>"

@app.get("/api/templates")
def get_templates():
    return {"templates": list(TEMPLATES_REGISTRY.values())}

@app.get("/api/base-template")
def get_base_template():
    return {"latex_code": BASE_LATEX_CODE}

@app.post("/api/upload-resume")
async def upload_resume(file: UploadFile = File(...), openrouter_api_key: Optional[str] = Form(None)):
    filename = file.filename.lower()
    content_bytes = await file.read()
    extracted_text = ""
    
    if filename.endswith(".pdf"):
        try:
            with pdfplumber.open(io.BytesIO(content_bytes)) as pdf:
                for page in pdf.pages:
                    extracted_text += (page.extract_text() or "") + "\n"
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read PDF file: {str(e)}")
    elif filename.endswith(".docx") or filename.endswith(".doc"):
        try:
            doc = docx.Document(io.BytesIO(content_bytes))
            extracted_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read Word document: {str(e)}")
    elif filename.endswith(".tex") or filename.endswith(".txt"):
        try:
            extracted_text = content_bytes.decode("utf-8", errors="ignore")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read text file: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload a .pdf, .docx, or .tex file.")

    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from the uploaded file.")
        
    api_key = openrouter_api_key or os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="OpenRouter API Key is required for parsing uploaded resume.")

    prompt = (
        "Extract structured JSON profile information from the raw resume text below.\n"
        "OUTPUT FORMAT (STRICT JSON ONLY):\n"
        "{\n"
        '  "name": "Candidate Full Name",\n'
        '  "location": "City, Country",\n'
        '  "email": "email@example.com",\n'
        '  "phone": "+1234567890",\n'
        '  "linkedin": "https://linkedin.com/in/username",\n'
        '  "github": "https://github.com/username",\n'
        '  "summary": "Professional summary statement...",\n'
        '  "skills": {\n'
        '    "domains": "Domain 1, Domain 2",\n'
        '    "languages": "Python, SQL, R",\n'
        '    "libraries": "Pandas, PyTorch, Scikit-learn",\n'
        '    "tools": "AWS, Docker, Git"\n'
        '  },\n'
        '  "experience": [\n'
        '    {\n'
        '      "dates": "May 2023 -- Present",\n'
        '      "role": "Role Title",\n'
        '      "company": "Company Name",\n'
        '      "bullets": ["Achievement line 1", "Achievement line 2"]\n'
        '    }\n'
        '  ],\n'
        '  "projects": [\n'
        '    {\n'
        '      "year": "2024",\n'
        '      "title": "Project Title",\n'
        '      "bullets": ["Project bullet 1", "Impact: Achieved 90% accuracy"]\n'
        '    }\n'
        '  ],\n'
        '  "education": [\n'
        '    {\n'
        '      "year": "2023",\n'
        '      "degree": "Degree Title",\n'
        '      "institution": "University Name",\n'
        '      "detail": "CGPA: 3.8 / 4.0"\n'
        '    }\n'
        '  ],\n'
        '  "certifications": ["Certification 1", "Certification 2"]\n'
        "}\n\n"
        f"RAW RESUME TEXT:\n{extracted_text[:4000]}"
    )
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8050",
        "X-Title": "Underleaf Resume Tailor"
    }
    
    payload = {
        "model": "deepseek/deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 1600
    }
    
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=25)
        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=f"OpenRouter API Error: {res.text}")
        content = res.json()["choices"][0]["message"]["content"].strip()
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        profile_json = json.loads(json_match.group(0)) if json_match else json.loads(content)
        return {"status": "success", "profile": profile_json, "raw_text": extracted_text[:1000]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing resume: {str(e)}")

@app.post("/api/generate-from-scratch")
async def generate_from_scratch(req: ScratchRequest):
    cleanup_old_pdfs(max_age_seconds=300, max_files=3)
    
    template_id = req.template_id if req.template_id in TEMPLATES_REGISTRY else "jake_ryan"
    template_info = TEMPLATES_REGISTRY[template_id]
    latex_tmpl = template_info["latex_template"]
    
    p = req.profile_data
    name = clean_latex_text(p.get("name", "Suraj Vishwakarma"))
    loc = clean_latex_text(p.get("location", "Dombivli, Mumbai"))
    email = clean_latex_text(p.get("email", "svishwakarma9322@gmail.com"))
    phone = clean_latex_text(p.get("phone", "+91 9324316769"))
    linkedin = clean_latex_text(p.get("linkedin", "LinkedIn"))
    github = clean_latex_text(p.get("github", "GitHub"))
    
    contact_line = f"{phone} $|$ \\href{{mailto:{email}}}{{\\underline{{{email}}}}} $|$ \\href{{{linkedin}}}{{\\underline{{linkedin.com}}}} $|$ \\href{{{github}}}{{\\underline{{github.com}}}}"
    
    summary_tex = format_summary_to_latex(p.get("summary", DEFAULT_SUMMARY_LATEX))
    skills_tex = format_skills_to_latex(p.get("skills", {}), template_id)
    exp_tex = format_experience_to_latex(p.get("experience", []), template_id)
    projects_tex = format_projects_to_latex(p.get("projects", []), template_id)
    edu_tex = format_education_to_latex(p.get("education", []), template_id)
    certs_tex = format_certifications_to_latex(p.get("certifications", []))
    
    clean_latex = latex_tmpl \
        .replace("{{NAME}}", name) \
        .replace("{{CONTACT_LINE}}", contact_line) \
        .replace("{{SUMMARY_SECTION}}", summary_tex) \
        .replace("{{SKILLS_SECTION}}", skills_tex) \
        .replace("{{SKILLS_SIDEBAR}}", skills_tex) \
        .replace("{{EXPERIENCE_SECTION}}", exp_tex) \
        .replace("{{PROJECTS_SECTION}}", projects_tex) \
        .replace("{{EDUCATION_SECTION}}", edu_tex) \
        .replace("{{EDUCATION_SIDEBAR}}", edu_tex) \
        .replace("{{CERTIFICATIONS_SECTION}}", certs_tex) \
        .replace("{{CERTIFICATIONS_SIDEBAR}}", certs_tex)
        
    req_id = str(uuid.uuid4())[:8]
    pdf_filename = f"resume_{req_id}.pdf"
    pdf_path = os.path.join(OUTPUT_DIR, pdf_filename)
    tex_path = os.path.join(OUTPUT_DIR, f"resume_{req_id}.tex")
    
    print(f"Compiling scratch resume using template '{template_id}'...")
    success, log_or_path = compile_tex_string(clean_latex, pdf_path, tex_path)
    if not success or not os.path.exists(pdf_path):
        raise HTTPException(status_code=500, detail=f"LaTeX compilation error: {log_or_path}")
        
    return {
        "status": "success",
        "pdf_id": req_id,
        "pdf_url": f"/api/pdf/{req_id}",
        "download_name": f"{name.replace(' ', '_')}_Resume.pdf",
        "latex_code": clean_latex
    }

@app.post("/api/tailor-and-generate")
async def tailor_and_generate(req: TailorRequest):
    cleanup_old_pdfs(max_age_seconds=300, max_files=3)
    
    jd_text = req.job_description.strip()
    if not jd_text:
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")
        
    api_key = req.openrouter_api_key or os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="OpenRouter API Key is missing. Please enter key or set OPENROUTER_API_KEY in .env.")
        
    model_name = req.model or "deepseek/deepseek-chat"
    template_id = req.template_id if req.template_id in TEMPLATES_REGISTRY else "jake_ryan"
    template_info = TEMPLATES_REGISTRY[template_id]
    latex_tmpl = template_info["latex_template"]
    
    profile = req.profile_data or {}
    cand_name = profile.get("name", "Suraj Vishwakarma")
    
    system_prompt = (
        f"You are an expert Quantitative AI & Data Science Resume Specialist for {cand_name}.\n"
        "Given a target Job Description (JD), customize the candidate's resume in valid JSON format:\n"
        "1. 'tailored_summary': Fine-tune ~10% of the summary to highlight key domain focus requested by the JD.\n"
        "2. 'tailored_skills': Inject key skills/tools from the JD into domains, languages, libraries, and tools lists.\n"
        "3. 'tailored_projects': Generate EXACTLY 3 high-impact academic/personal projects built around the skills required in the JD.\n\n"
        "STRICT JSON OUTPUT FORMAT:\n"
        "{\n"
        "  \"tailored_summary\": \"Quantitative Data Scientist with a strong foundation in Statistics...\",\n"
        "  \"tailored_skills\": {\n"
        "    \"domains\": \"Financial Risk Modeling, Predictive Analytics, NLP, LLMs\",\n"
        "    \"languages\": \"Python, R, SQL, SAS\",\n"
        "    \"libraries\": \"Pandas, NumPy, Scikit-learn, TensorFlow, PyTorch, LangChain\",\n"
        "    \"tools\": \"Power BI, Tableau, AWS, Streamlit, Git\"\n"
        "  },\n"
        "  \"tailored_projects\": [\n"
        "    {\n"
        "      \"year\": \"2024\",\n"
        "      \"title\": \"Project Name Matching JD Requirements\",\n"
        "      \"bullets\": [\n"
        "        \"Developed ML/AI pipeline using PyTorch/XGBoost/SQL targeting key JD skills.\",\n"
        "        \"Applied quantitative techniques to process datasets.\",\n"
        "        \"Impact: Achieved 91% accuracy, reducing financial risk by 15%.\"\n"
        "      ]\n"
        "    }\n"
        "  ]\n"
        "}\n\n"
        "RULES:\n"
        "1. Ensure JSON output is 100% valid.\n"
        "2. Return ONLY the JSON object."
    )
    
    user_prompt = f"TARGET JOB DESCRIPTION:\n{jd_text}\n\nGenerate the JSON output now:"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8050",
        "X-Title": "Underleaf Resume Tailor"
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
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=25)
        if response.status_code != 200:
            err_msg = response.text
            try:
                err_msg = response.json().get("error", {}).get("message", response.text)
            except Exception:
                pass
            raise HTTPException(status_code=response.status_code, detail=f"OpenRouter API Error: {err_msg}")
            
        res_data = response.json()
        generated_content = res_data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"OpenRouter API Exception: {str(e)}")
        
    try:
        json_match = re.search(r"\{.*\}", generated_content, re.DOTALL)
        ai_data = json.loads(json_match.group(0)) if json_match else json.loads(generated_content)
        
        summary_tex = format_summary_to_latex(ai_data.get("tailored_summary", DEFAULT_SUMMARY_LATEX))
        skills_tex = format_skills_to_latex(ai_data.get("tailored_skills", {}), template_id)
        projects_tex = format_projects_to_latex(ai_data.get("tailored_projects", []), template_id)
    except Exception as parse_err:
        summary_tex = DEFAULT_SUMMARY_LATEX
        skills_tex = format_skills_to_latex({}, template_id)
        projects_tex = format_projects_to_latex([], template_id)
        
    name = clean_latex_text(profile.get("name", "Suraj Vishwakarma"))
    loc = clean_latex_text(profile.get("location", "Dombivli, Mumbai"))
    email = clean_latex_text(profile.get("email", "svishwakarma9322@gmail.com"))
    phone = clean_latex_text(profile.get("phone", "+91 9324316769"))
    linkedin = clean_latex_text(profile.get("linkedin", "LinkedIn"))
    github = clean_latex_text(profile.get("github", "GitHub"))
    
    contact_line = f"{phone} $|$ \\href{{mailto:{email}}}{{\\underline{{{email}}}}} $|$ \\href{{{linkedin}}}{{\\underline{{linkedin.com}}}} $|$ \\href{{{github}}}{{\\underline{{github.com}}}}"
    
    exp_tex = format_experience_to_latex(profile.get("experience", []), template_id)
    edu_tex = format_education_to_latex(profile.get("education", []), template_id)
    certs_tex = format_certifications_to_latex(profile.get("certifications", []))
    
    clean_latex = latex_tmpl \
        .replace("{{NAME}}", name) \
        .replace("{{CONTACT_LINE}}", contact_line) \
        .replace("{{SUMMARY_SECTION}}", summary_tex) \
        .replace("{{SKILLS_SECTION}}", skills_tex) \
        .replace("{{SKILLS_SIDEBAR}}", skills_tex) \
        .replace("{{EXPERIENCE_SECTION}}", exp_tex) \
        .replace("{{PROJECTS_SECTION}}", projects_tex) \
        .replace("{{EDUCATION_SECTION}}", edu_tex) \
        .replace("{{EDUCATION_SIDEBAR}}", edu_tex) \
        .replace("{{CERTIFICATIONS_SECTION}}", certs_tex) \
        .replace("{{CERTIFICATIONS_SIDEBAR}}", certs_tex)
    
    req_id = str(uuid.uuid4())[:8]
    pdf_filename = f"resume_{req_id}.pdf"
    pdf_path = os.path.join(OUTPUT_DIR, pdf_filename)
    tex_path = os.path.join(OUTPUT_DIR, f"resume_{req_id}.tex")
    
    print(f"Compiling tailored LaTeX using template '{template_id}'...")
    success, log_or_path = compile_tex_string(clean_latex, pdf_path, tex_path)
    
    if not success or not os.path.exists(pdf_path):
        fallback_latex = BASE_LATEX_TEMPLATE.replace("{{SUMMARY_SECTION}}", DEFAULT_SUMMARY_LATEX).replace("{{SKILLS_SECTION}}", DEFAULT_SKILLS_LATEX).replace("{{PROJECTS_SECTION}}", DEFAULT_PROJECTS_LATEX).replace("{{NAME}}", "Suraj Vishwakarma").replace("{{CONTACT_LINE}}", contact_line).replace("{{EXPERIENCE_SECTION}}", "").replace("{{EDUCATION_SECTION}}", "").replace("{{CERTIFICATIONS_SECTION}}", "")
        fallback_success, _ = compile_tex_string(fallback_latex, pdf_path, tex_path)
        if not fallback_success:
            raise HTTPException(status_code=500, detail=f"LaTeX compilation error: {log_or_path}")
            
    return {
        "status": "success",
        "pdf_id": req_id,
        "pdf_url": f"/api/pdf/{req_id}",
        "download_name": f"{name.replace(' ', '_')}_Tailored_Resume.pdf",
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
