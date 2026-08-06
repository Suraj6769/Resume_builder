document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const apiKeyInput = document.getElementById('apiKey');
    const toggleKeyBtn = document.getElementById('toggleKeyBtn');
    const modelSelect = document.getElementById('modelSelect');
    const jdInput = document.getElementById('jdInput');
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const btnGenerate = document.getElementById('btnGenerate');
    const btnDownload = document.getElementById('btnDownload');
    const btnCopyCode = document.getElementById('btnCopyCode');
    const pipelineCard = document.getElementById('pipelineCard');
    const pdfPlaceholder = document.getElementById('pdfPlaceholder');
    const pdfFrame = document.getElementById('pdfFrame');
    const latexCodeEditor = document.getElementById('latexCodeEditor');
    const toast = document.getElementById('toast');

    // Load saved API key from localStorage
    const savedKey = localStorage.getItem('openrouter_api_key');
    if (savedKey) {
        apiKeyInput.value = savedKey;
    }

    apiKeyInput.addEventListener('input', () => {
        localStorage.setItem('openrouter_api_key', apiKeyInput.value.trim());
    });

    // Toggle API Key visibility
    toggleKeyBtn.addEventListener('click', () => {
        const type = apiKeyInput.type === 'password' ? 'text' : 'password';
        apiKeyInput.type = type;
        toggleKeyBtn.querySelector('i').className = type === 'password' ? 'fa-solid fa-eye' : 'fa-solid fa-eye-slash';
    });

    // Sample Job Descriptions
    const SAMPLES = {
        quant: `Role: Senior Quantitative Data Scientist
Key Responsibilities:
- Build high-frequency statistical models and time-series forecasting algorithms (ARIMA, GARCH, LSTM, Transformers) for risk and asset pricing.
- Design portfolio optimization pipelines and credit scoring risk models using XGBoost, Random Forest, and SMOTE for financial default probability estimation.
- Apply PCA, Monte Carlo simulation, and econometrics to analyze market volatility and liquidity risk.
Requirements: Python, SQL, PyTorch, Statsmodels, Scikit-learn, Financial Risk Analytics, Portfolio Optimization.`,

        genai: `Role: Generative AI & Agentic Workflow Engineer
Key Responsibilities:
- Architect LLM-based intelligent agentic workflows using LangChain, Hugging Face Transformers, and OpenAI/Gemini/DeepSeek APIs.
- Fine-tune domain-specific LLMs (Ollama, Stable Diffusion) and build NLP-to-SQL data querying pipelines for automated enterprise analytics.
- Deploy low-latency RAG (Retrieval-Augmented Generation) systems with vector databases for automated document extraction and candidate shortlisting.
Requirements: Python, PyTorch, LangChain, Transformers, Ollama, Vector DBs, FastAPI, Agentic AI.`,

        risk: `Role: Financial Risk Modeling Analyst
Key Responsibilities:
- Develop predictive loss cost models (XGBoost, GLM) to quantify catastrophe and credit risks across large commercial underwriting portfolios.
- Process and standardize large-scale financial exposure datasets using Pandas and SQL.
- Create interactive executive dashboards in Power BI/Tableau to visualize AAL, PML, OEP, and AEP risk distributions for reinsurance decision-making.
Requirements: Python, SQL, Power BI, RMS/AIR CatRisk Models, Loss Estimation, Time-Series Analysis.`
    };

    document.querySelectorAll('.chip').forEach(btn => {
        btn.addEventListener('click', () => {
            const key = btn.getAttribute('data-sample');
            if (SAMPLES[key]) {
                jdInput.value = SAMPLES[key];
                showToast(`Loaded ${btn.textContent} sample JD!`);
            }
        });
    });

    // File Upload handling
    dropZone.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    function handleFile(file) {
        const reader = new FileReader();
        reader.onload = (event) => {
            jdInput.value = event.target.result;
            showToast(`Loaded file: ${file.name}`);
        };
        reader.readAsText(file);
    }

    // Tab Switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
            
            btn.classList.add('active');
            const target = btn.getAttribute('data-tab');
            document.getElementById(target).classList.add('active');
        });
    });

    // Generate PDF Action
    btnGenerate.addEventListener('click', async () => {
        const jdText = jdInput.value.trim();
        if (!jdText) {
            showToast('Please enter or upload a Job Description.', 'error');
            return;
        }

        const apiKey = apiKeyInput.value.trim();
        if (!apiKey) {
            showToast('Please enter your OpenRouter API Key in the top header.', 'error');
            apiKeyInput.focus();
            return;
        }

        // Show Pipeline Progress
        btnGenerate.disabled = true;
        pipelineCard.style.display = 'flex';
        resetSteps();

        // Step 1: Parsing
        updateStep('step1', 'active');
        await sleep(400);
        updateStep('step1', 'done');

        // Step 2: DeepSeek AI Call
        updateStep('step2', 'active');
        
        try {
            const response = await fetch('/api/tailor-and-generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    job_description: jdText,
                    openrouter_api_key: apiKey,
                    model: modelSelect.value
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to generate tailored resume.');
            }

            updateStep('step2', 'done');

            // Step 3: LaTeX Compilation
            updateStep('step3', 'active');
            await sleep(500);
            updateStep('step3', 'done');

            // Step 4: Ready
            updateStep('step4', 'done');
            showToast('Tailored Resume PDF Generated Successfully!', 'success');

            // Render PDF & LaTeX Code
            pdfPlaceholder.style.display = 'none';
            pdfFrame.style.display = 'block';
            pdfFrame.src = data.pdf_url + '?t=' + Date.now();

            btnDownload.classList.remove('disabled');
            btnDownload.href = data.pdf_url;
            btnDownload.download = data.download_name || 'Suraj_Vishwakarma_Tailored_Resume.pdf';

            latexCodeEditor.value = data.latex_code;

        } catch (err) {
            showToast(err.message, 'error');
            resetSteps();
        } finally {
            btnGenerate.disabled = false;
        }
    });

    // Copy Code Button
    btnCopyCode.addEventListener('click', () => {
        if (!latexCodeEditor.value) return;
        navigator.clipboard.writeText(latexCodeEditor.value);
        showToast('LaTeX code copied to clipboard!');
    });

    // Helper functions
    function updateStep(stepId, state) {
        const el = document.getElementById(stepId);
        if (!el) return;
        el.className = `step ${state}`;
        const icon = el.querySelector('i');
        if (state === 'done') {
            icon.className = 'fa-solid fa-circle-check';
        } else if (state === 'active') {
            icon.className = 'fa-solid fa-spinner fa-spin';
        } else {
            icon.className = 'fa-regular fa-circle-check';
        }
    }

    function resetSteps() {
        ['step1', 'step2', 'step3', 'step4'].forEach(id => updateStep(id, 'waiting'));
    }

    function showToast(msg, type = 'info') {
        toast.textContent = msg;
        toast.style.borderColor = type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : 'rgba(255, 255, 255, 0.1)';
        toast.style.display = 'block';
        setTimeout(() => { toast.style.display = 'none'; }, 4000);
    }

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
});
