import os
import re
import glob
import time
import uuid
import json
import requests
import io

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import docx
except ImportError:
    docx = None

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
    compile_tex_string
)

app = FastAPI(title="Texora - Universal AI Resume Converter & Multi-Template Studio")

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_pdfs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class TailorRequest(BaseModel):
    job_description: Optional[str] = ""
    template_id: Optional[str] = "suraj_template"
    openrouter_api_key: Optional[str] = None
    model: Optional[str] = "deepseek/deepseek-chat"
    profile_data: Optional[Dict[str, Any]] = None

class ScratchRequest(BaseModel):
    template_id: Optional[str] = "suraj_template"
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
    if text is None:
        return ""
    text = str(text)
    text = re.sub(r'(?<!\\)%', r'\%', text)
    text = re.sub(r'(?<!\\)&', r'\&', text)
    text = re.sub(r'(?<!\\)\$', r'\$', text)
    return text

def format_summary_to_latex(summary_str: str) -> str:
    if not summary_str:
        return ""
    return clean_latex_text(summary_str.strip())

def format_skills_to_latex(skills_dict: Any, template_id: str = "jake_ryan") -> str:
    if not skills_dict:
        return ""
    if isinstance(skills_dict, str):
        return clean_latex_text(skills_dict)
    if isinstance(skills_dict, list):
        return clean_latex_text(", ".join([str(s) for s in skills_dict]))
        
    lines = []
    if isinstance(skills_dict, dict):
        domains = clean_latex_text(skills_dict.get("domains", ""))
        languages = clean_latex_text(skills_dict.get("languages", ""))
        libraries = clean_latex_text(skills_dict.get("libraries", ""))
        tools = clean_latex_text(skills_dict.get("tools", ""))
        
        if domains: lines.append(f"\\textbf{{Core Competencies/Domains:}} {domains}")
        if languages: lines.append(f"\\textbf{{Languages/Skills:}} {languages}")
        if libraries: lines.append(f"\\textbf{{Frameworks/Methodologies:}} {libraries}")
        if tools: lines.append(f"\\textbf{{Tools/Software:}} {tools}")
        
        if not lines:
            for k, v in skills_dict.items():
                if v and str(v).strip():
                    lines.append(f"\\textbf{{{clean_latex_text(k.title())}:}} {clean_latex_text(str(v))}")
                    
    if not lines:
        return ""

    if template_id == "jake_ryan":
        return " \\\\ \n".join(lines)
    elif template_id == "deedy_resume":
        formatted_deedy = []
        for l in lines:
            parts = l.split(":", 1)
            title = parts[0].replace("\\textbf{", "").replace("}", "").strip()
            body = parts[1].strip() if len(parts) > 1 else ""
            formatted_deedy.append(f"\\subsection*{{{title}}}\n{body}")
        return "\n\n".join(formatted_deedy)
    else:
        return " \\\\\n".join(lines)

def format_experience_to_latex(exp_data: list, template_id: str = "jake_ryan") -> str:
    if not exp_data or not isinstance(exp_data, list):
        return ""
    blocks = []
    for exp in exp_data:
        if not isinstance(exp, dict):
            continue
        dates = clean_latex_text(exp.get("dates", ""))
        role = clean_latex_text(exp.get("role", exp.get("title", "")))
        company = clean_latex_text(exp.get("company", exp.get("organization", "")))
        loc = clean_latex_text(exp.get("location", ""))
        bullets = exp.get("bullets", exp.get("highlights", []))
        if isinstance(bullets, str):
            bullets = [bullets]
            
        if not role and not company:
            continue
            
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
        elif template_id == "classic_charter":
            bullet_tex = "\n".join([f"        \\small{{\\item {clean_latex_text(b)}}}" for b in bullets])
            block = f"""    \\charterSubheading
      {{{role}}}{{{dates}}}
      {{{company}}}{{{loc}}}
      \\begin{{itemize}}[leftmargin=12pt, topsep=1pt, itemsep=1pt]
{bullet_tex}
      \\end{{itemize}}"""
        elif template_id == "suraj_template":
            bullet_tex = "\n".join([f"            \\item {clean_latex_text(b)}" for b in bullets])
            block = f"""    \\begin{{twocolentry}}{{{dates}}}
        \\textbf{{{role}}}, {company}
    \\end{{twocolentry}}
    \\vspace{{0.03 cm}}
    \\begin{{onecolentry}}
        \\begin{{highlights}}
{bullet_tex}
        \\end{{highlights}}
    \\end{{onecolentry}}"""
        else:
            bullet_tex = "\n".join([f"            \\item {clean_latex_text(b)}" for b in bullets])
            block = f"""    \\textbf{{{role}}}, {company} \\hfill {{{dates}}}\\\\
    \\begin{{itemize}}[leftmargin=12pt, topsep=1pt, itemsep=1pt]
{bullet_tex}
    \\end{{itemize}}"""
        blocks.append(block)
    return "\n\n".join(blocks)

def format_projects_to_latex(projects_data: list, template_id: str = "jake_ryan") -> str:
    if not projects_data or not isinstance(projects_data, list):
        return ""
    blocks = []
    for proj in projects_data:
        if not isinstance(proj, dict):
            continue
        year = clean_latex_text(proj.get("year", proj.get("date", "")))
        title = clean_latex_text(proj.get("title", proj.get("name", "")))
        bullets = proj.get("bullets", proj.get("highlights", []))
        if isinstance(bullets, str):
            bullets = [bullets]
            
        if not title:
            continue
            
        if template_id == "jake_ryan":
            bullet_items = []
            for b in bullets:
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
        elif template_id == "classic_charter":
            bullet_items = [f"        \\small{{\\item {clean_latex_text(b)}}}" for b in bullets]
            bullets_tex = "\n".join(bullet_items)
            block = f"""    \\charterProjectHeading
      {{\\textbf{{{title}}}}}{{{year}}}
      \\begin{{itemize}}[leftmargin=12pt, topsep=1pt, itemsep=1pt]
{bullets_tex}
      \\end{{itemize}}"""
        elif template_id == "suraj_template":
            bullet_items = [f"            \\item {clean_latex_text(b)}" for b in bullets]
            bullets_tex = "\n".join(bullet_items)
            block = f"""    \\begin{{twocolentry}}{{{year}}}
        \\textbf{{{title}}}
    \\end{{twocolentry}}
    \\vspace{{0.03 cm}}
    \\begin{{onecolentry}}
        \\begin{{highlights}}
{bullets_tex}
        \\end{{highlights}}
    \\end{{onecolentry}}"""
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
    if not edu_data or not isinstance(edu_data, list):
        return ""
    blocks = []
    for edu in edu_data:
        if not isinstance(edu, dict):
            continue
        year = clean_latex_text(edu.get("year", edu.get("dates", "")))
        degree = clean_latex_text(edu.get("degree", edu.get("title", "")))
        inst = clean_latex_text(edu.get("institution", edu.get("school", "")))
        loc = clean_latex_text(edu.get("location", ""))
        detail = clean_latex_text(edu.get("detail", edu.get("gpa", "")))
        
        if not degree and not inst:
            continue
            
        if template_id == "jake_ryan":
            block = f"""    \\resumeSubheading
      {{{inst}}}{{{loc}}}
      {{{degree}}}{{{year}}}"""
        elif template_id == "deedy_resume":
            block = f"""\\subsection*{{{inst}}}
{degree} \\\\
{{\\footnotesize {detail}}} \\\\
{{\\footnotesize {year}}}"""
        elif template_id == "classic_charter":
            block = f"""    \\charterSubheading
      {{{inst}}}{{{loc}}}
      {{{degree}}}{{{year}}}"""
        elif template_id == "suraj_template":
            block = f"""    \\begin{{twocolentry}}{{{year}}}
        \\textbf{{{degree}}}, {inst}
    \\end{{twocolentry}}
    \\vspace{{0.03 cm}}
    \\begin{{onecolentry}}
        \\begin{{highlights}}
            \\item {detail}
        \\end{{highlights}}
    \\end{{onecolentry}}"""
        else:
            block = f"""    \\textbf{{{inst}}} \\hfill {{{year}}}\\\\
    \\textit{{{degree}}} -- {{{detail}}}"""
        blocks.append(block)
    return "\n\n".join(blocks)

def format_certifications_to_latex(certs_data: list) -> str:
    if not certs_data or not isinstance(certs_data, list):
        return ""
    return "\n".join([f"  \\item {clean_latex_text(c)}" for c in certs_data if str(c).strip()])

@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
def read_root():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Texora AI Resume Studio Running</h1>"

@app.api_route("/health", methods=["GET", "HEAD"])
def health_check():
    return {"status": "ok"}

@app.get("/api/templates")
def get_templates():
    return {"templates": list(TEMPLATES_REGISTRY.values())}

@app.get("/api/config")
def get_config():
    env_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    return {
        "has_env_key": bool(env_key),
        "masked_key": f"{env_key[:6]}...{env_key[-4:]}" if len(env_key) > 10 else ""
    }

@app.get("/api/base-template")
def get_base_template():
    return {"latex_code": BASE_LATEX_CODE}

@app.post("/api/upload-resume")
async def upload_resume(file: UploadFile = File(...), openrouter_api_key: Optional[str] = Form(None)):
    filename = file.filename.lower()
    content_bytes = await file.read()
    extracted_text = ""
    
    if filename.endswith(".pdf"):
        if pdfplumber is None:
            raise HTTPException(status_code=500, detail="pdfplumber library is not installed.")
        try:
            with pdfplumber.open(io.BytesIO(content_bytes)) as pdf:
                for page in pdf.pages:
                    extracted_text += (page.extract_text() or "") + "\n"
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read PDF file: {str(e)}")
    elif filename.endswith(".docx") or filename.endswith(".doc"):
        if docx is None:
            raise HTTPException(status_code=500, detail="python-docx library is not installed.")
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
        "You are a Universal Resume Parser. Extract structured candidate profile information from the raw resume text below.\n"
        "This resume can belong to ANY candidate profession (Software Engineer, Data Scientist, Accountant, Nurse, Marketing Specialist, Civil Engineer, Manager, Designer, Lawyer, Tradesperson, etc.).\n"
        "PRESERVE candidate's exact profession, true job titles, actual experience bullet points, achievements, project details, education, and keywords.\n\n"
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
        '    "domains": "Domain 1, Core Competencies",\n'
        '    "languages": "Languages or Core Technical Skills",\n'
        '    "libraries": "Frameworks, Methodologies, Systems",\n'
        '    "tools": "Software, Cloud, Tools, Platforms"\n'
        '  },\n'
        '  "experience": [\n'
        '    {\n'
        '      "dates": "Start Date -- End Date",\n'
        '      "role": "Exact Job Title",\n'
        '      "company": "Company Name",\n'
        '      "location": "City, State/Country",\n'
        '      "bullets": ["Achievement bullet point 1", "Achievement bullet point 2"]\n'
        '    }\n'
        '  ],\n'
        '  "projects": [\n'
        '    {\n'
        '      "year": "Year",\n'
        '      "title": "Project Title / Accomplishment",\n'
        '      "bullets": ["Project detail 1", "Project impact 2"]\n'
        '    }\n'
        '  ],\n'
        '  "education": [\n'
        '    {\n'
        '      "year": "Graduation Year",\n'
        '      "degree": "Degree / Qualification Title",\n'
        '      "institution": "University / Institution Name",\n'
        '      "location": "City, Country",\n'
        '      "detail": "Honors / GPA / Key Coursework"\n'
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
        "X-Title": "Texora Resume Parser"
    }
    
    payload = {
        "model": "deepseek/deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 1800
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
    
    template_id = req.template_id if req.template_id in TEMPLATES_REGISTRY else "suraj_template"
    template_info = TEMPLATES_REGISTRY[template_id]
    latex_tmpl = template_info["latex_template"]
    
    p = req.profile_data or {}
    name = clean_latex_text(p.get("name") or "Candidate Name")
    loc = clean_latex_text(p.get("location") or "")
    email = clean_latex_text(p.get("email") or "")
    phone = clean_latex_text(p.get("phone") or "")
    linkedin = clean_latex_text(p.get("linkedin") or "")
    github = clean_latex_text(p.get("github") or "")
    
    contact_parts = []
    if loc: contact_parts.append(loc)
    if email: contact_parts.append(f"\\href{{mailto:{email}}}{{\\underline{{{email}}}}}")
    if phone: contact_parts.append(phone)
    if linkedin: contact_parts.append(f"\\href{{{linkedin}}}{{\\underline{{LinkedIn}}}}")
    if github: contact_parts.append(f"\\href{{{github}}}{{\\underline{{GitHub}}}}")
    
    contact_line = " $|$ ".join(contact_parts) if contact_parts else "contact@example.com"
    
    summary_tex = format_summary_to_latex(p.get("summary") or "")
    skills_tex = format_skills_to_latex(p.get("skills"), template_id)
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
    
    print(f"Compiling resume for '{name}' using template '{template_id}'...")
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
    
    jd_text = (req.job_description or "").strip()
    api_key = req.openrouter_api_key or os.environ.get("OPENROUTER_API_KEY", "").strip()
    model_name = req.model or "deepseek/deepseek-chat"
    template_id = req.template_id if req.template_id in TEMPLATES_REGISTRY else "suraj_template"
    template_info = TEMPLATES_REGISTRY[template_id]
    latex_tmpl = template_info["latex_template"]
    
    profile = req.profile_data or {}
    cand_name = clean_latex_text(profile.get("name") or "Candidate Name")
    
    # AI Tailoring if JD and API Key are present
    if jd_text and api_key:
        system_prompt = (
            f"You are a Universal Resume Tailor for candidate '{cand_name}'.\n"
            "Given the candidate's actual current profile and a target Job Description (JD), optimize their resume in valid JSON:\n"
            "1. 'tailored_summary': Refine candidate's professional summary to incorporate relevant target JD keywords.\n"
            "2. 'tailored_skills': Retain candidate's actual skills and inject matching keywords from the JD.\n"
            "3. 'tailored_experience': Refine candidate's actual work experience bullets to highlight achievements relevant to the JD.\n"
            "4. 'tailored_projects': Refine candidate's actual projects or generate key project bullets matching candidate's background + JD requirements.\n\n"
            "STRICT JSON OUTPUT FORMAT:\n"
            "{\n"
            "  \"tailored_summary\": \"...\",\n"
            "  \"tailored_skills\": {\n"
            "    \"domains\": \"...\",\n"
            "    \"languages\": \"...\",\n"
            "    \"libraries\": \"...\",\n"
            "    \"tools\": \"...\"\n"
            "  },\n"
            "  \"tailored_experience\": [\n"
            "    {\n"
            "      \"dates\": \"...\",\n"
            "      \"role\": \"...\",\n"
            "      \"company\": \"...\",\n"
            "      \"location\": \"...\",\n"
            "      \"bullets\": [\"...\"]\n"
            "    }\n"
            "  ],\n"
            "  \"tailored_projects\": [\n"
            "    {\n"
            "      \"year\": \"...\",\n"
            "      \"title\": \"...\",\n"
            "      \"bullets\": [\"...\"]\n"
            "    }\n"
            "  ]\n"
            "}\n\n"
            "RULES:\n"
            "1. DO NOT change candidate's core profession or invent false titles.\n"
            "2. Return ONLY valid JSON."
        )
        
        user_prompt = f"CANDIDATE PROFILE:\n{json.dumps(profile, indent=2)}\n\nTARGET JOB DESCRIPTION:\n{jd_text}\n\nGenerate tailored JSON output:"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8050",
            "X-Title": "Texora Resume Tailor"
        }
        
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 1800
        }
        
        try:
            print(f"Calling OpenRouter DeepSeek API to tailor resume for '{cand_name}'...")
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=25)
            if response.status_code == 200:
                res_data = response.json()
                generated_content = res_data["choices"][0]["message"]["content"].strip()
                json_match = re.search(r"\{.*\}", generated_content, re.DOTALL)
                ai_data = json.loads(json_match.group(0)) if json_match else json.loads(generated_content)
                
                if "tailored_summary" in ai_data:
                    profile["summary"] = ai_data["tailored_summary"]
                if "tailored_skills" in ai_data and ai_data["tailored_skills"]:
                    profile["skills"] = ai_data["tailored_skills"]
                if "tailored_experience" in ai_data and ai_data["tailored_experience"]:
                    profile["experience"] = ai_data["tailored_experience"]
                if "tailored_projects" in ai_data and ai_data["tailored_projects"]:
                    profile["projects"] = ai_data["tailored_projects"]
        except Exception as e:
            print(f"Tailoring note: {e}")

    # Generate LaTeX using candidate's profile (either AI-tailored or directly extracted)
    name = clean_latex_text(profile.get("name") or "Candidate Name")
    loc = clean_latex_text(profile.get("location") or "")
    email = clean_latex_text(profile.get("email") or "")
    phone = clean_latex_text(profile.get("phone") or "")
    linkedin = clean_latex_text(profile.get("linkedin") or "")
    github = clean_latex_text(profile.get("github") or "")
    
    contact_parts = []
    if loc: contact_parts.append(loc)
    if email: contact_parts.append(f"\\href{{mailto:{email}}}{{\\underline{{{email}}}}}")
    if phone: contact_parts.append(phone)
    if linkedin: contact_parts.append(f"\\href{{{linkedin}}}{{\\underline{{LinkedIn}}}}")
    if github: contact_parts.append(f"\\href{{{github}}}{{\\underline{{GitHub}}}}")
    
    contact_line = " $|$ ".join(contact_parts) if contact_parts else "contact@example.com"
    
    summary_tex = format_summary_to_latex(profile.get("summary") or "")
    skills_tex = format_skills_to_latex(profile.get("skills"), template_id)
    exp_tex = format_experience_to_latex(profile.get("experience", []), template_id)
    projects_tex = format_projects_to_latex(profile.get("projects", []), template_id)
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
    
    print(f"Compiling resume for '{name}' using template '{template_id}'...")
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

@app.get("/api/pdf/{pdf_id}")
def serve_pdf(pdf_id: str):
    pdf_path = os.path.join(OUTPUT_DIR, f"resume_{pdf_id}.pdf")
    if os.path.exists(pdf_path):
        return FileResponse(
            pdf_path, 
            media_type="application/pdf", 
            filename="Resume.pdf",
            headers={"Content-Disposition": "inline; filename=Resume.pdf"}
        )
    raise HTTPException(status_code=404, detail="PDF not found.")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8050))
    uvicorn.run(app, host="0.0.0.0", port=port)
