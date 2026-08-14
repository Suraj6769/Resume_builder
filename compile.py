import os
import re
import shutil
import subprocess
import urllib.parse
import urllib.request
import uuid

# ==============================================================================
# TEMPLATE 1: JAKE RYAN (Jake Gutierrez ATS Resume - POPULAR)
# ==============================================================================
TEMPLATE_JAKE_RYAN = r"""
\documentclass[letterpaper,11pt]{article}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\input{glyphtounicode}

\pagestyle{fancy}
\fancyhf{}
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

\addtolength{\oddsidemargin}{-0.5in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1in}
\addtolength{\topmargin}{-.5in}
\addtolength{\textheight}{1.0in}

\urlstyle{same}

\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

\titleformat{\section}{
  \vspace{-4pt}\scshape\raggedright\large
}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

\pdfgentounicode=1

\newcommand{\resumeItem}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \small#1 & #2 \\
    \end{tabular*}\vspace{-7pt}
}

\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

\begin{document}

\begin{center}
    \textbf{\Huge \scshape {{NAME}}} \\ \vspace{1pt}
    \small {{CONTACT_LINE}}
\end{center}

\section{Summary}
\small{{{SUMMARY_SECTION}}}

\section{Education}
  \resumeSubHeadingListStart
{{EDUCATION_SECTION}}
  \resumeSubHeadingListEnd

\section{Experience}
  \resumeSubHeadingListStart
{{EXPERIENCE_SECTION}}
  \resumeSubHeadingListEnd

\section{Projects}
  \resumeSubHeadingListStart
{{PROJECTS_SECTION}}
  \resumeSubHeadingListEnd

\section{Technical Skills}
 \begin{itemize}[leftmargin=0.15in, label={}]
    \small{\item{
{{SKILLS_SECTION}}
    }}
 \end{itemize}

\end{document}
"""

# ==============================================================================
# TEMPLATE 2: DEEDY RESUME (Deedy OpenFont 2-Column Sidebar Layout)
# ==============================================================================
TEMPLATE_DEEDY_RESUME = r"""
\documentclass[10pt,letterpaper]{article}
\usepackage[top=0.5in,bottom=0.5in,left=0.65in,right=0.65in]{geometry}
\usepackage[T1]{fontenc}
\usepackage{titlesec}
\usepackage{xcolor}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{paracol}
\setlength{\parindent}{0pt}
\pagestyle{empty}

\definecolor{primary}{HTML}{2b2b2b}
\definecolor{headings}{HTML}{6A6A6A}
\definecolor{subheadings}{HTML}{333333}

\titleformat{\section}{\color{primary}\scshape\raggedright\large}{}{0em}{}
\titleformat{\subsection}{\color{subheadings}\bfseries\small}{}{0em}{}

\begin{document}

\centerline{\Huge\bfseries {{NAME}}}
\vspace{4pt}
\centerline{\small {{CONTACT_LINE}}}

\vspace{10pt}
\setcolumnwidth{0.32\textwidth, 0.65\textwidth}
\begin{paracol}{2}

\section*{Education}
{{EDUCATION_SIDEBAR}}

\vspace{4pt}
\section*{Skills}
{{SKILLS_SIDEBAR}}

\vspace{4pt}
\section*{Certifications}
{{CERTIFICATIONS_SIDEBAR}}

\switchcolumn

\section*{Summary}
{\small {{SUMMARY_SECTION}}}

\vspace{4pt}
\section*{Experience}
{{EXPERIENCE_SECTION}}

\vspace{4pt}
\section*{Projects}
{{PROJECTS_SECTION}}

\end{paracol}

\end{document}
"""

# ==============================================================================
# TEMPLATE 3: MODERN CLASSIC (Jan Küster Raleway Font Template)
# ==============================================================================
TEMPLATE_MODERN_CLASSIC = r"""
\documentclass[10pt,letterpaper]{article}
\usepackage[top=0.6 cm, bottom=0.6 cm, left=1.0 cm, right=1.0 cm]{geometry}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{xcolor}
\definecolor{primaryColor}{RGB}{30, 41, 59}
\definecolor{accentColor}{RGB}{37, 99, 235}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{tabularx}
\usepackage{hyperref}
\hypersetup{colorlinks=true, urlcolor=accentColor}

\pagestyle{empty}
\setlength{\parindent}{0pt}
\linespread{0.96}\selectfont

\titleformat{\section}{\color{primaryColor}\scshape\large\bfseries}{}{0pt}{}[\vspace{1pt}\hrule height 1pt color primaryColor]
\titlespacing{\section}{0pt}{0.06 cm}{0.04 cm}

\begin{document}

\begin{center}
    {\Huge \bfseries \color{primaryColor} {{NAME}}}\\[3pt]
    {\small \color{accentColor} {{CONTACT_LINE}}}
\end{center}

\vspace{-0.1cm}

\section{Summary}
{\small {{SUMMARY_SECTION}}}

\section{Technical Skills}
{{SKILLS_SECTION}}

\section{Professional Experience}
{{EXPERIENCE_SECTION}}

\section{Academic \& Personal Projects}
{{PROJECTS_SECTION}}

\section{Education}
{{EDUCATION_SECTION}}

\end{document}
"""

# ==============================================================================
# TEMPLATE 4: ACADEMIC CV (Zoe Kearney Formal Dossier Template)
# ==============================================================================
TEMPLATE_ACADEMIC_CV = r"""
\documentclass[a4paper,9pt]{extarticle}
\usepackage[utf8]{inputenc}
\usepackage{geometry}
\geometry{a4paper, margin=0.75in}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{changepage}

\setlist{noitemsep}
\titleformat{\section}{\large\bfseries}{\thesection}{1em}{}[\titlerule]
\titlespacing*{\section}{0pt}{0.6\baselineskip}{0.4\baselineskip}

\begin{document}

\begin{center}
    {\LARGE \bfseries {{NAME}}}\\[3pt]
    {\small {{CONTACT_LINE}}}
\end{center}

\section{Executive Summary}
{{SUMMARY_SECTION}}

\section{Education \& Qualifications}
{{EDUCATION_SECTION}}

\section{Professional Appointments \& Experience}
{{EXPERIENCE_SECTION}}

\section{Research Projects \& Innovations}
{{PROJECTS_SECTION}}

\section{Technical Skills \& Competencies}
{{SKILLS_SECTION}}

\end{document}
"""

# ==============================================================================
# TEMPLATE 5: EXECUTIVE CHARTER (Charter Font Single-Column)
# ==============================================================================
TEMPLATE_EXECUTIVE_CHARTER = r"""
\documentclass[letterpaper,10pt]{article}
\usepackage[top=0.6in,bottom=0.6in,left=0.65in,right=0.65in]{geometry}
\usepackage{titlesec}
\usepackage{tabularx}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{charter}
\usepackage{xcolor}

\pagestyle{empty}
\setlength{\parindent}{0pt}
\linespread{0.96}\selectfont

\titleformat{\section}{
  \vspace{-3pt}\scshape\raggedright\large\bfseries
}{}{0em}{}[\color{black}\titlerule \vspace{-4pt}]

\newcommand{\charterSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-6pt}
}

\newcommand{\charterProjectHeading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \small#1 & #2 \\
    \end{tabular*}\vspace{-6pt}
}

\begin{document}

\begin{center}
    {\Huge \scshape \bfseries {{NAME}}} \\[4pt]
    \small {{CONTACT_LINE}}
\end{center}

\vspace{-6pt}

\section{Professional Summary}
\small{{{SUMMARY_SECTION}}}

\section{Technical Skills}
\begin{itemize}[leftmargin=0.15in, label={}, itemsep=1pt, topsep=2pt]
    \small{\item{
{{SKILLS_SECTION}}
    }}
\end{itemize}

\section{Professional Experience}
\begin{itemize}[leftmargin=0.15in, label={}]
{{EXPERIENCE_SECTION}}
\end{itemize}

\section{Key Projects \& Impact}
\begin{itemize}[leftmargin=0.15in, label={}]
{{PROJECTS_SECTION}}
\end{itemize}

\section{Education}
\begin{itemize}[leftmargin=0.15in, label={}]
{{EDUCATION_SECTION}}
\end{itemize}

\end{document}
"""

# ==============================================================================
# TEMPLATE 6: SURAJ EXECUTIVE (Detailed Charter Dossier Template)
# ==============================================================================
TEMPLATE_SURAJ_EXECUTIVE = r"""
\documentclass[10pt, letterpaper]{article}

\usepackage[
    ignoreheadfoot,
    top=1.5 cm,
    bottom=1.5 cm,
    left=1.2 cm,
    right=1.2 cm,
    footskip=0.8 cm,
]{geometry}
\usepackage{titlesec}
\usepackage{tabularx}
\usepackage{array}
\usepackage[dvipsnames]{xcolor}
\definecolor{primaryColor}{RGB}{0, 0, 0}
\usepackage{enumitem}
\usepackage{fontawesome5}
\usepackage{amsmath}
\usepackage[
    pdftitle={{{NAME}} - Resume},
    pdfauthor={{{NAME}}},
    colorlinks=true,
    urlcolor=primaryColor
]{hyperref}
\usepackage[pscoord]{eso-pic}
\usepackage{calc}
\usepackage{bookmark}
\usepackage{lastpage}
\usepackage{changepage}
\usepackage{paracol}
\usepackage{ifthen}
\usepackage{needspace}
\usepackage{iftex}

\ifPDFTeX
    \InputIfFileExists{glyphtounicode.tex}{\pdfgentounicode=1}{}
    \usepackage[T1]{fontenc}
    \usepackage[utf8]{inputenc}
    \usepackage{lmodern}
\fi

\usepackage{charter}

\raggedright
\AtBeginEnvironment{adjustwidth}{\partopsep0pt}
\pagestyle{empty}
\setcounter{secnumdepth}{0}
\setlength{\parindent}{0pt}
\setlength{\topskip}{0pt}
\setlength{\columnsep}{0.1cm}
\pagenumbering{gobble}

\titleformat{\section}{\needspace{4\baselineskip}\bfseries\large}{}{0pt}{}[\vspace{1pt}\titlerule]

\titlespacing{\section}{-1pt}{0.2 cm}{0.15 cm}

\renewcommand\labelitemi{$\vcenter{\hbox{\small$\bullet$}}$}
\newenvironment{highlights}{
    \begin{itemize}[
        topsep=0.03 cm,
        parsep=0.02 cm,
        partopsep=0pt,
        itemsep=0.02 cm,
        leftmargin=0 cm + 8pt
    ]
}{
    \end{itemize}
}

\newenvironment{onecolentry}{
    \begin{adjustwidth}{0 cm + 0.00001 cm}{0 cm + 0.00001 cm}
}{
    \end{adjustwidth}
}

\newenvironment{twocolentry}[2][]{
    \onecolentry
    \def\secondColumn{#2}
    \setcolumnwidth{\fill, 3.5 cm}
    \begin{paracol}{2}
}{
    \switchcolumn \raggedleft \secondColumn
    \end{paracol}
    \endonecolentry
}

\newenvironment{header}{
    \setlength{\topsep}{0pt}\par\kern\topsep\centering\linespread{1.3}
}{
    \par\kern\topsep
}

\let\hrefWithoutArrow\href

\begin{document}
    \newcommand{\AND}{\unskip
        \cleaders\copy\ANDbox\hskip\wd\ANDbox
        \ignorespaces
    }
    \newsavebox\ANDbox
    \sbox\ANDbox{$|$}

    \begin{header}
        \fontsize{22 pt}{22 pt}\selectfont {{NAME}}

        \vspace{3 pt}

        \normalsize
        {{CONTACT_LINE}}
    \end{header}

    \vspace{-0.15 cm}

    \section{PROFESSIONAL SUMMARY}
    \begin{onecolentry}
{{SUMMARY_SECTION}}
    \end{onecolentry}

    \section{TECHNICAL SKILLS}
{{SKILLS_SECTION}}

    \section{PROFESSIONAL EXPERIENCE}
{{EXPERIENCE_SECTION}}

    \section{KEY PROJECTS \& IMPACT}
{{PROJECTS_SECTION}}

    \section{EDUCATION}
{{EDUCATION_SECTION}}

    \section{CERTIFICATIONS \& ACHIEVEMENTS}
    \begin{onecolentry}
        \begin{highlights}
{{CERTIFICATIONS_SECTION}}
        \end{highlights}
    \end{onecolentry}

\end{document}
"""

# Registry of Available Templates
TEMPLATES_REGISTRY = {
    "suraj_template": {
        "id": "suraj_template",
        "name": "Suraj Executive (Detailed)",
        "tag": "EXECUTIVE • DETAILED #1",
        "badge": "NEW",
        "preview_img": "/static/suraj_preview.png",
        "description": "Comprehensive Executive Charter format built specifically for Data Scientists, ML Engineers, and Risk Analytics.",
        "latex_template": TEMPLATE_SURAJ_EXECUTIVE
    },
    "jake_ryan": {
        "id": "jake_ryan",
        "name": "Jake Ryan (ATS Standard)",
        "tag": "POPULAR • ATS #1 CHOICE",
        "badge": "MOST POPULAR",
        "preview_img": "/static/jake_preview.png",
        "description": "The world-famous Jake Gutierrez clean single-column ATS resume layout used by top FAANG software engineers.",
        "latex_template": TEMPLATE_JAKE_RYAN
    },
    "deedy_resume": {
        "id": "deedy_resume",
        "name": "Deedy Resume (2-Column)",
        "tag": "2-COLUMN TECH SIDEBAR",
        "badge": "TECH FAVORITE",
        "preview_img": "/static/deedy_preview.png",
        "description": "The iconic Deedy 2-column layout with left sidebar for education/skills and main column for experience.",
        "latex_template": TEMPLATE_DEEDY_RESUME
    },
    "modern_classic": {
        "id": "modern_classic",
        "name": "Modern Classic (Raleway)",
        "tag": "MODERN • BLUE ACCENT",
        "badge": "SLEEK",
        "preview_img": "/static/modern_classic_preview.png",
        "description": "Jan Küster clean modern layout with Raleway typography and blue accent dividing lines.",
        "latex_template": TEMPLATE_MODERN_CLASSIC
    },
    "academic_cv": {
        "id": "academic_cv",
        "name": "Academic & Research CV",
        "tag": "ACADEMIC • DOSSIER STYLE",
        "badge": "FORMAL",
        "preview_img": "/static/academic_preview.png",
        "description": "Zoe Kearney formal university dossier format ideal for research, statistics, and academic roles.",
        "latex_template": TEMPLATE_ACADEMIC_CV
    },
    "classic_charter": {
        "id": "classic_charter",
        "name": "Executive Charter",
        "tag": "CHARTER SERIF • OFFICIAL",
        "badge": "EXECUTIVE",
        "preview_img": "/static/charter_preview.png",
        "description": "Clean executive single-column layout with Charter font, paracol dates, and tight vertical geometry.",
        "latex_template": TEMPLATE_EXECUTIVE_CHARTER
    }
}

DEFAULT_SUMMARY_LATEX = r"""Quantitative Data Scientist with a strong foundation in Statistics and Financial Risk Modeling. Experienced in building predictive models for loss estimation, customer behavior, and generative AI systems."""

DEFAULT_SKILLS_LATEX = r"""\textbf{Domains:} Financial Risk Modeling, Predictive Analytics, NLP, LLMs \\
\textbf{Languages:} Python, R, SQL, SAS \\
\textbf{Libraries:} Pandas, NumPy, Scikit-learn, TensorFlow, PyTorch, LangChain \\
\textbf{Tools:} Power BI, Tableau, AWS, Streamlit, Git"""

DEFAULT_PROJECTS_LATEX = r"""\textbf{Credit Risk Modeling \& Loan Default Prediction} \hfill 2024\\
Built an end-to-end machine learning pipeline (XGBoost, Random Forest) to predict borrower default probability."""

BASE_LATEX_TEMPLATE = TEMPLATE_JAKE_RYAN
BASE_LATEX_CODE = TEMPLATE_JAKE_RYAN.replace("{{SUMMARY_SECTION}}", DEFAULT_SUMMARY_LATEX).replace("{{SKILLS_SECTION}}", DEFAULT_SKILLS_LATEX).replace("{{PROJECTS_SECTION}}", DEFAULT_PROJECTS_LATEX).replace("{{NAME}}", "Suraj Vishwakarma").replace("{{CONTACT_LINE}}", "Dombivli, Mumbai $|$ ABS@gmail.com $|$ +91 12345 $|$ LinkedIn $|$ GitHub").replace("{{EDUCATION_SECTION}}", "").replace("{{EXPERIENCE_SECTION}}", "")

def find_latex_compiler():
    """Look for local LaTeX compilers in PATH and common installation directories."""
    compilers = ["pdflatex", "xelatex", "lualatex", "tectonic"]
    for comp in compilers:
        found = shutil.which(comp)
        if found:
            return found
            
    local_appdata = os.environ.get("LOCALAPPDATA", "")
    program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
    program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
    
    possible_paths = [
        os.path.join(program_files, "MiKTeX", "miktex", "bin", "x64", "pdflatex.exe"),
        os.path.join(program_files_x86, "MiKTeX", "miktex", "bin", "pdflatex.exe"),
        os.path.join(local_appdata, "Programs", "MiKTeX", "miktex", "bin", "x64", "pdflatex.exe"),
        r"C:\texlive\2024\bin\windows\pdflatex.exe",
        r"C:\texlive\2023\bin\windows\pdflatex.exe",
        r"C:\texlive\2022\bin\win32\pdflatex.exe",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
            
    return None

def compile_tex_string(latex_code_content, output_pdf_path="document.pdf", tex_filename="document.tex"):
    """Compile LaTeX string content to PDF file path."""
    out_dir = os.path.dirname(os.path.abspath(output_pdf_path))
    os.makedirs(out_dir, exist_ok=True)
    
    with open(tex_filename, "w", encoding="utf-8") as f:
        f.write(latex_code_content.strip() + "\n")
        
    compiler = find_latex_compiler()
    
    if compiler:
        print(f"Found local LaTeX engine: {compiler}")
        try:
            cmd = [
                compiler,
                "-interaction=nonstopmode",
                "--enable-installer",
                f"-output-directory={out_dir}",
                tex_filename
            ]
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=45
            )
            
            if os.path.exists(output_pdf_path):
                print(f"Success! PDF generated at: {os.path.abspath(output_pdf_path)}")
                for ext in [".log", ".aux", ".fls", ".fdb_latexmk", ".synctex.gz", ".out"]:
                    helper_file = os.path.join(out_dir, os.path.basename(tex_filename).replace(".tex", ext))
                    if os.path.exists(helper_file):
                        try:
                            os.remove(helper_file)
                        except OSError:
                            pass
                return True, os.path.abspath(output_pdf_path)
            else:
                print("Local compilation log snippet:")
                print(result.stdout[-500:])
        except subprocess.TimeoutExpired:
            print("Local compilation timed out.")
        except Exception as e:
            print(f"Error running local compiler: {e}")
            
    return False, "Failed to compile LaTeX to PDF."

if __name__ == "__main__":
    print("Reading base LaTeX template and compiling document.pdf...")
    success, result = compile_tex_string(BASE_LATEX_CODE, "document.pdf", "document.tex")
    if success:
        print(f"Success! PDF created at: {result}")
    else:
        print(f"Compilation failed: {result}")
