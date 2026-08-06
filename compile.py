import os
import shutil
import subprocess
import urllib.parse
import urllib.request
import uuid

# Base LaTeX Resume Template with placeholders for SUMMARY, SKILLS, and PROJECTS
BASE_LATEX_TEMPLATE = r"""
\documentclass[9.5pt, letterpaper]{article}

% Packages:
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
    pdftitle={Suraj Vishwakarma - Quantitative Data Scientist Resume},
    pdfauthor={Suraj Vishwakarma},
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
        \fontsize{19 pt}{19 pt}\selectfont Suraj Vishwakarma

        \vspace{1 pt}

        \normalsize
        \mbox{Dombivli, Mumbai}%
        \kern 4.0 pt%
        \AND%
        \kern 4.0 pt%
        \mbox{\hrefWithoutArrow{mailto:svishwakarma9322@gmail.com}{svishwakarma9322@gmail.com}}%
        \kern 4.0 pt%
        \AND%
        \kern 4.0 pt%
        \mbox{\hrefWithoutArrow{tel:+91-9324316769}{+91 9324316769}}%
        \kern 4.0 pt%
        \AND%
        \kern 4.0 pt%
        \mbox{\hrefWithoutArrow{https://linkedin.com/in/surajvishwakarma11}{LinkedIn}}%
        \kern 4.0 pt%
        \AND%
        \kern 4.0 pt%
        \mbox{\hrefWithoutArrow{https://github.com/Suraj6769}{GitHub}}%
    \end{header}

    \vspace{1 pt - 0.2 cm}

    \section{SUMMARY}
    \begin{onecolentry}
{{SUMMARY_SECTION}}
    \end{onecolentry}

    \section{TECHNICAL SKILLS}
{{SKILLS_SECTION}}

    \section{PROFESSIONAL EXPERIENCE}

    \begin{twocolentry}{May 2026 -- Present}
        \textbf{AI Engineer}, PSS
    \end{twocolentry}
    \vspace{0.01 cm}
    \begin{onecolentry}
        \begin{highlights}
            \item Leveraged GenAI to optimize recruitment finance, reducing manual screening costs by automating candidate shortlisting and data collection via robotic calls.
            \item Built an LLM-based resume recommendation system, integrating internal databases with external Google results to source top-tier talent, improving hiring pipeline velocity by 20\%.
            \item Developed an Agentic AI workflow to automate communication (Email/WhatsApp) and data collection, streamlining the end-to-end recruitment cycle and reducing administrative overhead by 30\%.
            \item Integrated APIs (ChatGPT, Gemini, Claude) to generate structured reports and screening criteria, standardizing candidate evaluation metrics.
        \end{highlights}
    \end{onecolentry}

    \vspace{0.01 cm}

    \begin{twocolentry}{Feb 2025 -- Apr 2026}
        \textbf{Risk Modeling Analyst}, Marsh McLennan (Internship)
    \end{twocolentry}
    \vspace{0.01 cm}
    \begin{onecolentry}
        \begin{highlights}
            \item Architected end-to-end data science pipelines in Python (Pandas, NumPy) to automate the ingestion, cleaning, and standardization of exposure data for 125+ accounts, eliminating manual Excel workflows and boosting team productivity by 40\%.
            \item Developed predictive machine learning models (XGBoost, GLM) to forecast aggregate loss costs, validating outputs against traditional RMS/AIR models to improve the accuracy of financial risk assessments by 12\% for underwriting portfolios.
            \item Designed and deployed interactive dashboards (Power BI) to visualize critical financial risk metrics (AAL, PML, OEP, AEP), enabling senior stakeholders to monitor portfolio concentration and make data-driven reinsurance purchasing decisions 30\% faster.
            \item Applied statistical modeling (Time-Series \& Regression) on historical claims data to identify emerging catastrophe risk drivers, directly influencing premium pricing strategies and optimizing capital allocation for the firm.
        \end{highlights}
    \end{onecolentry}

    \vspace{0.01 cm}

    \begin{twocolentry}{Jan 2025 -- Feb 2025}
        \textbf{Junior GenAI Engineer}, Visulon Inc.
    \end{twocolentry}
    \vspace{0.01 cm}
    \begin{onecolentry}
        \begin{highlights}
            \item Designed an NLP-to-SQL pipeline using Ollama LLMs, enabling business stakeholders to query financial databases using natural language, reducing reliance on technical teams and improving reporting speed by 40\%.
            \item Fine-tuned and deployed Stable Diffusion models for rapid prototyping, optimizing GPU inference latency for real-time applications.
        \end{highlights}
    \end{onecolentry}

    \section{ACADEMIC PROJECTS}

{{PROJECTS_SECTION}}

    \section{EDUCATION}
    \begin{twocolentry}{May 2025}
        \textbf{M.Sc. Statistics \& Data Science}, NMIMS Mumbai
    \end{twocolentry}
    \vspace{0.01 cm}
    \begin{onecolentry}
        \begin{highlights}
            \item CGPA: 3.67 / 4.0
        \end{highlights}
    \end{onecolentry}
    \vspace{0.01 cm}
    \begin{twocolentry}{2023}
        \textbf{B.Sc. Statistics}, B.N. Bandodkar College, Mumbai
    \end{twocolentry}
    \vspace{0.01 cm}
    \begin{onecolentry}
        \begin{highlights}
            \item CGPA: 9.7 / 10.0
        \end{highlights}
    \end{onecolentry}

    \section{CERTIFICATIONS}
    \begin{onecolentry}
        \begin{highlights}
            \item Python with Data Science (Udemy)
            \item Machine Learning Advanced (Udemy)
            \item Deep Learning with TensorFlow (Udemy)
        \end{highlights}
    \end{onecolentry}

\end{document}
"""

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

BASE_LATEX_CODE = BASE_LATEX_TEMPLATE.replace("{{SUMMARY_SECTION}}", DEFAULT_SUMMARY_LATEX).replace("{{SKILLS_SECTION}}", DEFAULT_SKILLS_LATEX).replace("{{PROJECTS_SECTION}}", DEFAULT_PROJECTS_LATEX)

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

