document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const apiKeyInput = document.getElementById('apiKey');
    const toggleKeyBtn = document.getElementById('toggleKeyBtn');
    const modeTailorBtn = document.getElementById('modeTailorBtn');
    const modeScratchBtn = document.getElementById('modeScratchBtn');
    const modeTailorView = document.getElementById('modeTailorView');
    const modeScratchView = document.getElementById('modeScratchView');
    const templateGrid = document.getElementById('templateGrid');
    const selectedTemplateBadge = document.getElementById('selectedTemplateBadge');
    
    // Upload Elements
    const resumeDropZone = document.getElementById('resumeDropZone');
    const resumeFileInput = document.getElementById('resumeFileInput');
    const resumeFileInfo = document.getElementById('resumeFileInfo');
    
    // Tailor Form Elements
    const modelSelect = document.getElementById('modelSelect');
    const jdInput = document.getElementById('jdInput');
    const btnGenerate = document.getElementById('btnGenerate');
    
    // Scratch Form Elements
    const scratchForm = document.getElementById('scratchForm');
    const btnGenerateScratch = document.getElementById('btnGenerateScratch');
    const scratchJdInput = document.getElementById('scratchJdInput');
    
    // Preview Elements
    const btnDownload = document.getElementById('btnDownload');
    const btnCopyCode = document.getElementById('btnCopyCode');
    const pipelineCard = document.getElementById('pipelineCard');
    const pdfPlaceholder = document.getElementById('pdfPlaceholder');
    const pdfFrame = document.getElementById('pdfFrame');
    const codeView = document.getElementById('codeView');
    const latexCodeEditor = document.getElementById('latexCodeEditor');
    const tabPreviewBtn = document.getElementById('tabPreviewBtn');
    const tabCodeBtn = document.getElementById('tabCodeBtn');
    const toast = document.getElementById('toast');
    const toastMsg = document.getElementById('toastMsg');

    // State Variables
    let selectedTemplateId = 'classic_executive';
    let currentMode = 'tailor'; // 'tailor' or 'scratch'
    let parsedProfile = null;

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
        apiKeyInput.type = apiKeyInput.type === 'password' ? 'text' : 'password';
    });

    // Mode Switching Logic
    modeTailorBtn.addEventListener('click', () => {
        currentMode = 'tailor';
        modeTailorBtn.classList.add('active');
        modeScratchBtn.classList.remove('active');
        modeTailorView.classList.remove('hidden');
        modeScratchView.classList.add('hidden');
    });

    modeScratchBtn.addEventListener('click', () => {
        currentMode = 'scratch';
        modeScratchBtn.classList.add('active');
        modeTailorBtn.classList.remove('active');
        modeScratchView.classList.remove('hidden');
        modeTailorView.classList.add('hidden');
    });

    // Scratch Form Tab Switching
    document.querySelectorAll('.form-tabs .tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            document.querySelectorAll('.form-tabs .tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            const targetId = btn.getAttribute('data-tab');
            document.getElementById(targetId).classList.add('active');
        });
    });

    // Load Template Gallery from Backend
    async function loadTemplates() {
        try {
            const res = await fetch('/api/templates');
            const data = await res.json();
            templateGrid.innerHTML = '';
            
            data.templates.forEach(tmpl => {
                const item = document.createElement('div');
                item.className = `template-item ${tmpl.id === selectedTemplateId ? 'selected' : ''}`;
                item.innerHTML = `
                    <div class="template-name">${tmpl.name}</div>
                    <div class="template-tag">${tmpl.tag}</div>
                `;
                item.addEventListener('click', () => {
                    document.querySelectorAll('.template-item').forEach(i => i.classList.remove('selected'));
                    item.classList.add('selected');
                    selectedTemplateId = tmpl.id;
                    selectedTemplateBadge.textContent = tmpl.name;
                    showToast(`Selected Template: ${tmpl.name}`, 'info');
                });
                templateGrid.appendChild(item);
            });
        } catch (err) {
            console.error('Failed to load templates:', err);
        }
    }
    loadTemplates();

    // Resume Upload Drag & Drop
    resumeDropZone.addEventListener('click', () => resumeFileInput.click());
    resumeDropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        resumeDropZone.classList.add('dragover');
    });
    resumeDropZone.addEventListener('dragleave', () => resumeDropZone.classList.remove('dragover'));
    resumeDropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        resumeDropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });
    resumeFileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFileUpload(e.target.files[0]);
        }
    });

    async function handleFileUpload(file) {
        resumeFileInfo.textContent = `Uploading & Parsing "${file.name}" via DeepSeek...`;
        showToast(`Parsing ${file.name}...`, 'info');
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('openrouter_api_key', apiKeyInput.value.trim());

        try {
            const res = await fetch('/api/upload-resume', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Failed to parse uploaded resume.');

            parsedProfile = data.profile;
            resumeFileInfo.textContent = `✓ Successfully Parsed "${file.name}"! (${data.profile.name || 'Candidate'})`;
            showToast(`Parsed ${file.name} successfully!`, 'success');

            // Pre-fill Scratch Form fields with parsed profile data
            if (parsedProfile.name) document.getElementById('scratchName').value = parsedProfile.name;
            if (parsedProfile.location) document.getElementById('scratchLoc').value = parsedProfile.location;
            if (parsedProfile.email) document.getElementById('scratchEmail').value = parsedProfile.email;
            if (parsedProfile.phone) document.getElementById('scratchPhone').value = parsedProfile.phone;
            if (parsedProfile.summary) document.getElementById('scratchSummary').value = parsedProfile.summary;

        } catch (err) {
            console.error('File Upload Error:', err);
            resumeFileInfo.textContent = `❌ Error: ${err.message}`;
            showToast(err.message, 'error');
        }
    }

    // Sample JDs
    const sampleJDs = {
        quant: `Quantitative Data Scientist / Risk Analyst Requirement:\n- Strong background in Statistics, Credit Risk Modeling, and Time-Series Analysis.\n- Proficiency in Python (Pandas, NumPy, Scikit-learn), SQL, and XGBoost/GLM loss estimation.\n- Experience predicting borrower default probabilities, SMOTE-ENN class imbalance, and portfolio risk management.`,
        genai: `Senior GenAI & LLM Engineer Requirement:\n- Hands-on experience building RAG architectures, LangChain, FAISS/Pinecone vector DBs.\n- Fine-tuning open-source LLMs (Ollama, Mistral-7B, Llama 3) for domain NLP-to-SQL tasks.\n- Optimization of GPU inference latency and multi-agent system workflows.`,
        datasci: `Senior Data Scientist Requirement:\n- Track record in predictive analytics, machine learning pipeline deployment, and customer LTV/churn forecasting.\n- Advanced expertise in Python, PyTorch, TensorFlow, and cloud platforms (AWS/Azure).\n- Ability to translate statistical findings into executive dashboards (Power BI / Tableau).`
    };

    document.querySelectorAll('.btn-chip').forEach(btn => {
        btn.addEventListener('click', () => {
            const type = btn.getAttribute('data-sample');
            if (sampleJDs[type]) {
                jdInput.value = sampleJDs[type];
                showToast(`Loaded ${btn.textContent} Job Description`, 'info');
            }
        });
    });

    // Helper: Step Progress Tracker
    function updateStep(stepId, state) {
        const step = document.getElementById(stepId);
        if (!step) return;
        step.className = `step ${state}`;
        const icon = step.querySelector('.step-icon i');
        if (state === 'active') {
            icon.className = 'fa-solid fa-circle-notch fa-spin';
        } else if (state === 'done') {
            icon.className = 'fa-solid fa-circle-check';
        } else {
            icon.className = 'fa-solid fa-circle';
        }
    }

    function sleep(ms) {
        return new Promise(r => setTimeout(r, ms));
    }

    // Mode 1: Tailor & Generate PDF
    btnGenerate.addEventListener('click', async () => {
        const jd = jdInput.value.strip ? jdInput.value.strip() : jdInput.value.trim();
        if (!jd) {
            showToast('Please enter a target Job Description!', 'error');
            return;
        }

        btnGenerate.disabled = true;
        pipelineCard.classList.remove('hidden');
        updateStep('step1', 'done');
        updateStep('step2', 'active');

        try {
            const payload = {
                job_description: jd,
                template_id: selectedTemplateId,
                openrouter_api_key: apiKeyInput.value.trim(),
                model: modelSelect.value,
                profile_data: parsedProfile
            };

            const res = await fetch('/api/tailor-and-generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Tailoring failed.');

            updateStep('step2', 'done');
            updateStep('step3', 'active');
            await sleep(400);

            // Render PDF
            const pdfUrl = `${data.pdf_url}?t=${Date.now()}`;
            pdfFrame.src = pdfUrl;
            pdfFrame.classList.remove('hidden');
            pdfPlaceholder.classList.add('hidden');

            latexCodeEditor.value = data.latex_code;
            btnDownload.href = pdfUrl;
            btnDownload.download = data.download_name || 'Tailored_Resume.pdf';
            btnDownload.classList.remove('disabled');

            updateStep('step3', 'done');
            updateStep('step4', 'done');
            showToast('Tailored Resume PDF Compiled Successfully!', 'success');

        } catch (err) {
            console.error('Tailor Error:', err);
            showToast(err.message, 'error');
            updateStep('step2', 'error');
        } finally {
            btnGenerate.disabled = false;
        }
    });

    // Mode 2: Generate Resume from Scratch
    btnGenerateScratch.addEventListener('click', async () => {
        btnGenerateScratch.disabled = true;
        pipelineCard.classList.remove('hidden');
        updateStep('step1', 'done');
        updateStep('step2', 'done');
        updateStep('step3', 'active');

        try {
            const profile = {
                name: document.getElementById('scratchName').value.trim(),
                location: document.getElementById('scratchLoc').value.trim(),
                email: document.getElementById('scratchEmail').value.trim(),
                phone: document.getElementById('scratchPhone').value.trim(),
                linkedin: document.getElementById('scratchLinkedin').value.trim(),
                github: document.getElementById('scratchGithub').value.trim(),
                summary: document.getElementById('scratchSummary').value.trim(),
                skills: {
                    domains: document.getElementById('scratchDomains').value.trim(),
                    languages: document.getElementById('scratchLanguages').value.trim(),
                    libraries: document.getElementById('scratchLibraries').value.trim(),
                    tools: document.getElementById('scratchTools').value.trim()
                },
                experience: [
                    {
                        dates: 'May 2026 -- Present',
                        role: 'AI Engineer',
                        company: 'PSS',
                        bullets: document.getElementById('scratchExpBullets1').value.split('\n').filter(b => b.trim())
                    }
                ],
                projects: [
                    {
                        year: '2024',
                        title: 'Credit Risk Modeling & Loan Default Prediction',
                        bullets: document.getElementById('scratchProjBullets1').value.split('\n').filter(b => b.trim())
                    }
                ],
                education: [
                    {
                        year: 'May 2025',
                        degree: 'M.Sc. Statistics & Data Science',
                        institution: 'NMIMS Mumbai',
                        detail: 'CGPA: 3.67 / 4.0'
                    }
                ],
                certifications: [
                    'Python with Data Science (Udemy)',
                    'Machine Learning Advanced (Udemy)',
                    'Deep Learning with TensorFlow (Udemy)'
                ]
            };

            const payload = {
                template_id: selectedTemplateId,
                job_description: scratchJdInput.value.trim(),
                openrouter_api_key: apiKeyInput.value.trim(),
                model: modelSelect.value,
                profile_data: profile
            };

            const res = await fetch('/api/generate-from-scratch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Build from scratch failed.');

            // Render PDF
            const pdfUrl = `${data.pdf_url}?t=${Date.now()}`;
            pdfFrame.src = pdfUrl;
            pdfFrame.classList.remove('hidden');
            pdfPlaceholder.classList.add('hidden');

            latexCodeEditor.value = data.latex_code;
            btnDownload.href = pdfUrl;
            btnDownload.download = data.download_name || 'Compiled_Resume.pdf';
            btnDownload.classList.remove('disabled');

            updateStep('step3', 'done');
            updateStep('step4', 'done');
            showToast('Resume PDF Built & Compiled Successfully!', 'success');

        } catch (err) {
            console.error('Scratch Error:', err);
            showToast(err.message, 'error');
        } finally {
            btnGenerateScratch.disabled = false;
        }
    });

    // Preview / Code View Tabs
    tabPreviewBtn.addEventListener('click', () => {
        tabPreviewBtn.classList.add('active');
        tabCodeBtn.classList.remove('active');
        if (pdfFrame.src) pdfFrame.classList.remove('hidden');
        else pdfPlaceholder.classList.remove('hidden');
        codeView.classList.add('hidden');
        btnCopyCode.classList.add('hidden');
    });

    tabCodeBtn.addEventListener('click', () => {
        tabCodeBtn.classList.add('active');
        tabPreviewBtn.classList.remove('active');
        pdfFrame.classList.add('hidden');
        pdfPlaceholder.classList.add('hidden');
        codeView.classList.remove('hidden');
        btnCopyCode.classList.remove('hidden');
    });

    // Copy Code Button
    btnCopyCode.addEventListener('click', () => {
        if (!latexCodeEditor.value) return;
        navigator.clipboard.writeText(latexCodeEditor.value);
        showToast('LaTeX Source Code Copied to Clipboard!', 'info');
    });

    // Helper: Toast Notifications
    function showToast(msg, type = 'info') {
        toastMsg.textContent = msg;
        toast.className = `toast ${type}`;
        setTimeout(() => toast.classList.add('hidden'), 4000);
    }
});
