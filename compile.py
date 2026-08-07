import os
import re
import shutil
import subprocess
import urllib.parse
import urllib.request
import uuid

# ==============================================================================
# TEMPLATE 1: CLASSIC EXECUTIVE (Single Column, Charter Font, Clean Divider Lines)
# ==============================================================================
TEMPLATE_CLASSIC_EXECUTIVE = r"""
\documentclass[9.5pt, letterpaper]{article}

\usepackage[
    ignoreheadfoot,
    top=0.65 cm,
    bottom=0.65 cm,
    left=1.0 cm,
    right=1.0 cm,
    footskip=0.3 cm,
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
    \input{glyphtounicode}
    \pdfgentounicode=1
    \usepackage[T1]{fontenc}
    \usepackage[utf8]{inputenc}
    \usepackage{lmodern}
\fi

\usepackage{charter}

\raggedright
\linespread{0.95}\selectfont
\AtBeginEnvironment{adjustwidth}{\partopsep0pt}
\pagestyle{empty}
\setcounter{secnumdepth}{0}
\setlength{\parindent}{0pt}
\setlength{\topskip}{0pt}
\setlength{\columnsep}{0.1cm}
\pagenumbering{gobble}

\titleformat{\section}{\needspace{2\baselineskip}\bfseries\large}{}{0pt}{}[\vspace{1pt}\titlerule]
\titlespacing{\section}{-1pt}{0.04 cm}{0.02 cm}

\renewcommand\labelitemi{$\vcenter{\hbox{\small$\bullet$}}$}
\newenvironment{highlights}{
    \begin{itemize}[
        topsep=0pt,
        parsep=0pt,
        partopsep=0pt,
        itemsep=0pt,
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
    \setlength{\topsep}{0pt}\par\kern\topsep\centering\linespread{1.1}
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
        \fontsize{19 pt}{19 pt}\selectfont {{NAME}}

        \vspace{1 pt}

        \normalsize
        {{CONTACT_LINE}}
    \end{header}

    \vspace{1 pt - 0.2 cm}

    \section{SUMMARY}
    \begin{onecolentry}
{{SUMMARY_SECTION}}
    \end{onecolentry}

    \section{TECHNICAL SKILLS}
{{SKILLS_SECTION}}

    \section{PROFESSIONAL EXPERIENCE}
{{EXPERIENCE_SECTION}}

    \section{ACADEMIC PROJECTS}
{{PROJECTS_SECTION}}

    \section{EDUCATION}
{{EDUCATION_SECTION}}

    \section{CERTIFICATIONS}
    \begin{onecolentry}
        \begin{highlights}
{{CERTIFICATIONS_SECTION}}
        \end{highlights}
    \end{onecolentry}

\end{document}
"""

# ==============================================================================
# TEMPLATE 2: MODERN MINIMALIST (Sleek Sans-Serif, Navy Accent Headers)
# ==============================================================================
TEMPLATE_MODERN_MINIMALIST = r"""
\documentclass[9.5pt, letterpaper]{article}

\usepackage[
    top=0.65 cm,
    bottom=0.65 cm,
    left=1.0 cm,
    right=1.0 cm,
]{geometry}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault}
\usepackage{xcolor}
\definecolor{navyAccent}{RGB}{15, 32, 67}
\definecolor{darkText}{RGB}{30, 30, 30}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{tabularx}
\usepackage{hyperref}
\hypersetup{colorlinks=true, urlcolor=navyAccent}

\pagestyle{empty}
\setlength{\parindent}{0pt}
\linespread{0.96}\selectfont

\titleformat{\section}{\color{navyAccent}\bfseries\large\uppercase}{}{0pt}{}[\vspace{1pt}\hrule height 1pt color navyAccent]
\titlespacing{\section}{0pt}{0.06 cm}{0.04 cm}

\newenvironment{customitem}{
    \begin{itemize}[topsep=0pt, parsep=0pt, itemsep=0.5pt, leftmargin=12pt]
}{
    \end{itemize}
}

\begin{document}

\begin{center}
    {\Huge \bfseries \color{navyAccent} {{NAME}}}\\[3pt]
    {\small \color{darkText} {{CONTACT_LINE}}}
\end{center}

\vspace{-0.1cm}

\section{Professional Summary}
{\small {{SUMMARY_SECTION}}}

\section{Technical Skills}
{{SKILLS_SECTION}}

\section{Professional Experience}
{{EXPERIENCE_SECTION}}

\section{Projects}
{{PROJECTS_SECTION}}

\section{Education}
{{EDUCATION_SECTION}}

\section{Certifications}
\begin{customitem}
{{CERTIFICATIONS_SECTION}}
\end{customitem}

\end{document}
"""

# ==============================================================================
# TEMPLATE 3: TECH SIDEBAR (2-Column Layout with Skills Sidebar)
# ==============================================================================
TEMPLATE_TECH_SIDEBAR = r"""
\documentclass[9.5pt, letterpaper]{article}
\usepackage[top=0.6 cm, bottom=0.6 cm, left=0.8 cm, right=0.8 cm]{geometry}
\usepackage{paracol}
\usepackage{xcolor}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{hyperref}
\usepackage{lmodern}

\definecolor{sidebarBg}{RGB}{245, 247, 250}
\definecolor{techBlue}{RGB}{20, 80, 160}

\pagestyle{empty}
\setlength{\parindent}{0pt}
\linespread{0.95}\selectfont

\titleformat{\section}{\color{techBlue}\bfseries\large}{}{0pt}{}[\vspace{1pt}\hrule height 0.8pt color techBlue]
\titlespacing{\section}{0pt}{0.05 cm}{0.03 cm}

\setcolumnwidth{5.2 cm, \fill}
\setlength{\columnsep}{0.4 cm}

\begin{document}

\begin{paracol}{2}

% --- LEFT SIDEBAR ---
\begin{center}
    {\Large \bfseries \color{techBlue} {{NAME}}}\\[3pt]
    {\footnotesize {{CONTACT_SIDEBAR}}}
\end{center}

\vspace{0.1 cm}

\section{Skills}
{{SKILLS_SIDEBAR}}

\vspace{0.1 cm}

\section{Education}
{{EDUCATION_SIDEBAR}}

\vspace{0.1 cm}

\section{Certifications}
\begin{itemize}[leftmargin=8pt, topsep=0pt, itemsep=1pt]
{{CERTIFICATIONS_SECTION}}
\end{itemize}

% --- MAIN COLUMN ---
\switchcolumn

\section{Summary}
{\small {{SUMMARY_SECTION}}}

\section{Experience}
{{EXPERIENCE_SECTION}}

\section{Projects}
{{PROJECTS_SECTION}}

\end{paracol}

\end{document}
"""

# ==============================================================================
# TEMPLATE 4: ACADEMIC FORMAL (Serif, Classic Research Format)
# ==============================================================================
TEMPLATE_ACADEMIC_FORMAL = r"""
\documentclass[10pt, letterpaper]{article}

\usepackage[top=0.7 cm, bottom=0.7 cm, left=1.1 cm, right=1.1 cm]{geometry}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{mathptmx} % Times New Roman style font

\pagestyle{empty}
\setlength{\parindent}{0pt}
\linespread{0.98}\selectfont

\titleformat{\section}{\scshape\large\bfseries}{}{0pt}{}[\vspace{1pt}\hrule height 0.5pt]
\titlespacing{\section}{0pt}{0.08 cm}{0.04 cm}

\begin{document}

\begin{center}
    {\LARGE \scshape \bfseries {{NAME}}}\\[4pt]
    {\small {{CONTACT_LINE}}}
\end{center}

\section{Summary}
{{SUMMARY_SECTION}}

\section{Technical & Analytical Skills}
{{SKILLS_SECTION}}

\section{Professional Experience}
{{EXPERIENCE_SECTION}}

\section{Research & Academic Projects}
{{PROJECTS_SECTION}}

\section{Education}
{{EDUCATION_SECTION}}

\section{Certifications}
\begin{itemize}[topsep=0pt, itemsep=1pt, leftmargin=12pt]
{{CERTIFICATIONS_SECTION}}
\end{itemize}

\end{document}
"""

# Registry of Available Templates
TEMPLATES_REGISTRY = {
    "classic_executive": {
        "id": "classic_executive",
        "name": "Classic Executive",
        "tag": "Charter Serif / Official Standard",
        "description": "Clean single-column professional resume layout with elegant Charter font and subtle dividing lines.",
        "latex_template": TEMPLATE_CLASSIC_EXECUTIVE
    },
    "modern_minimalist": {
        "id": "modern_minimalist",
        "name": "Modern Minimalist",
        "tag": "Sans-Serif / Navy Accent",
        "description": "Ultra-sleek modern layout with bold navy headers, Helvetica typography, and high readability.",
        "latex_template": TEMPLATE_MODERN_MINIMALIST
    },
    "tech_sidebar": {
        "id": "tech_sidebar",
        "name": "Tech & Developer Sidebar",
        "tag": "2-Column Sidebar Layout",
        "description": "Distinctive 2-column format featuring a left sidebar for skills, contact, and education alongside a main project column.",
        "latex_template": TEMPLATE_TECH_SIDEBAR
    },
    "academic_formal": {
        "id": "academic_formal",
        "name": "Academic & Research Formal",
        "tag": "Times Serif / Publication Style",
        "description": "Classic academic research format utilizing Times font and small-cap section headers.",
        "latex_template": TEMPLATE_ACADEMIC_FORMAL
    }
}

BASE_LATEX_TEMPLATE = TEMPLATE_CLASSIC_EXECUTIVE

DEFAULT_SUMMARY_LATEX = r"""        Quantitative Data Scientist with a strong foundation in Statistics and Financial Risk Modeling. Experienced in building predictive models for loss estimation, customer behavior, and generative AI systems. Proficient in Python, SQL, and cloud platforms. Skilled in translating complex financial data into actionable business insights to drive revenue growth and mitigate risk."""

DEFAULT_SKILLS_LATEX = r"""    \begin{onecolentry}
        \textbf{Domains:} Financial Risk Modeling, Predictive Analytics, NLP, LLMs, Quantitative Research, Credit Scoring, Time-Series Analysis.
    \end{onecolentry}
    \vspace{0.01 cm}
    \begin{onecolentry}
        \textbf{Languages:} Python, R, SQL, SAS.
    \end{onecolentry}
    \vspace{0.01 cm}
    \begin{onecolentry}
        \textbf{Libraries:} Pandas, NumPy, Scikit-learn, TensorFlow, PyTorch, LangChain, Statsmodels, Hugging Face, Transformers.
    \end{onecolentry}
    \vspace{0.01 cm}
    \begin{onecolentry}
        \textbf{Tools:} Power BI, Tableau, AWS, Streamlit, Git, RMS, AIR, CatRisk.
    \end{onecolentry}"""

DEFAULT_PROJECTS_LATEX = r"""    \begin{twocolentry}{2024}
        \textbf{Credit Risk Modeling \& Loan Default Prediction}
    \end{twocolentry}
    \vspace{0.01 cm}
    \begin{onecolentry}
        \begin{highlights}
            \item Built an end-to-end machine learning pipeline (XGBoost, Random Forest, Logistic Regression) to predict borrower default probability using synthetic banking datasets.
            \item Applied advanced feature engineering (debt-to-income ratios, credit utilization) and handled severe class imbalance using SMOTE-ENN to minimize false negatives, which carry high financial costs for lenders.
            \item \textbf{Impact:} Achieved an 89\% AUC-ROC, with the potential to reduce non-performing loan (NPL) ratios by 15\% through early identification of high-risk accounts.
        \end{highlights}
    \end{onecolentry}

    \vspace{0.01 cm}

    \begin{twocolentry}{2024}
        \textbf{Financial Time-Series Forecasting \& Volatility Modeling}
    \end{twocolentry}
    \vspace{0.01 cm}
    \begin{onecolentry}
        \begin{highlights}
            \item Developed a hybrid ARIMA-LSTM model to forecast stock price movements and market volatility using historical S\&P 500 and Forex data.
            \item Implemented GARCH models to statistically analyze volatility clustering and heteroskedasticity in asset returns, providing robust risk estimates for algorithmic trading strategies.
            \item \textbf{Impact:} Improved directional forecasting accuracy by 7\% over traditional econometric models, enabling better timing for portfolio rebalancing and hedging decisions.
        \end{highlights}
    \end{onecolentry}

    \vspace{0.01 cm}

    \begin{twocolentry}{2024}
        \textbf{Customer Lifetime Value (LTV) \& Churn Analytics (Banking)}
    \end{twocolentry}
    \vspace{0.01 cm}
    \begin{onecolentry}
        \begin{highlights}
            \item Engineered ensemble ML models (Gradient Boosting, SVM) to predict customer churn in the retail banking sector, focusing on high-net-worth individuals.
            \item Performed PCA for dimensionality reduction and integrated behavioral transaction data to generate personalized retention strategies.
            \item \textbf{Impact:} Achieved 91\% prediction accuracy; implementing the model could increase overall portfolio profitability by 6\% by proactively retaining at-risk, high-value clients with targeted offers.
        \end{highlights}
    \end{onecolentry}"""

BASE_LATEX_CODE = BASE_LATEX_TEMPLATE.replace("{{SUMMARY_SECTION}}", DEFAULT_SUMMARY_LATEX).replace("{{SKILLS_SECTION}}", DEFAULT_SKILLS_LATEX).replace("{{PROJECTS_SECTION}}", DEFAULT_PROJECTS_LATEX).replace("{{NAME}}", "Suraj Vishwakarma").replace("{{CONTACT_LINE}}", "Dombivli, Mumbai | svishwakarma9322@gmail.com | +91 9324316769 | LinkedIn | GitHub").replace("{{EXPERIENCE_SECTION}}", "").replace("{{EDUCATION_SECTION}}", "").replace("{{CERTIFICATIONS_SECTION}}", "")

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
