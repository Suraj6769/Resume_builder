document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const templatesGrid = document.getElementById('templatesGrid');
    const activeTemplateName = document.getElementById('activeTemplateName');
    
    // Mode Switcher Pills
    const modeTailorBtn = document.getElementById('modeTailorBtn');
    const modeScratchBtn = document.getElementById('modeScratchBtn');
    const tailorInputCard = document.getElementById('tailorInputCard');
    const scratchInputCard = document.getElementById('scratchInputCard');
    
    // Upload Dropzone Elements
    const resumeDropZone = document.getElementById('resumeDropZone');
    const resumeFileInput = document.getElementById('resumeFileInput');
    const resumeFileInfo = document.getElementById('resumeFileInfo');
    
    // Input & Generate Buttons
    const modelSelect = document.getElementById('modelSelect');
    const jdInput = document.getElementById('jdInput');
    const btnGenerate = document.getElementById('btnGenerate');
    const btnGenerateScratch = document.getElementById('btnGenerateScratch');
    const btnGetStarted = document.getElementById('btnGetStarted');
    const btnBuildAiHero = document.getElementById('btnBuildAiHero');
    
    // Preview Elements
    const pdfPlaceholder = document.getElementById('pdfPlaceholder');
    const pdfFrame = document.getElementById('pdfFrame');
    const codeView = document.getElementById('codeView');
    const latexCodeEditor = document.getElementById('latexCodeEditor');
    const tabPdfBtn = document.getElementById('tabPdfBtn');
    const tabCodeBtn = document.getElementById('tabCodeBtn');
    const btnDownload = document.getElementById('btnDownload');
    const btnCopyCode = document.getElementById('btnCopyCode');
    const toast = document.getElementById('toast');
    const toastMsg = document.getElementById('toastMsg');

    // Application State
    let selectedTemplateId = 'suraj_template';
    let currentMode = 'tailor';
    let parsedProfile = null;
    let allTemplates = [];

    // Mode Switching
    modeTailorBtn.addEventListener('click', () => setMode('tailor'));
    modeScratchBtn.addEventListener('click', () => setMode('scratch'));
    
    btnGetStarted.addEventListener('click', () => {
        document.getElementById('templatesSection').scrollIntoView({ behavior: 'smooth' });
    });

    btnBuildAiHero.addEventListener('click', () => {
        setMode('tailor');
        document.getElementById('studioSection').scrollIntoView({ behavior: 'smooth' });
    });

    function setMode(mode) {
        currentMode = mode;
        if (mode === 'tailor') {
            modeTailorBtn.classList.add('active');
            modeScratchBtn.classList.remove('active');
            tailorInputCard.classList.remove('hidden');
            scratchInputCard.classList.add('hidden');
        } else {
            modeScratchBtn.classList.add('active');
            modeTailorBtn.classList.remove('active');
            scratchInputCard.classList.remove('hidden');
            tailorInputCard.classList.add('hidden');
        }
    }

    // Load Template Cards Grid from /api/templates
    async function loadTemplates() {
        try {
            const res = await fetch('/api/templates');
            const data = await res.json();
            allTemplates = data.templates;
            renderTemplateGrid(allTemplates);
        } catch (err) {
            console.error('Error loading templates:', err);
        }
    }

    function renderTemplateGrid(templates) {
        templatesGrid.innerHTML = '';
        templates.forEach(tmpl => {
            const card = document.createElement('div');
            const isSelected = tmpl.id === selectedTemplateId;
            card.className = `template-card ${isSelected ? 'active-selected' : ''}`;
            card.innerHTML = `
                <div class="card-preview-box">
                    <img src="${tmpl.preview_img}" alt="${tmpl.name}" class="card-preview-img" onerror="this.src='/static/charter_preview.png'">
                    ${isSelected ? '<div class="card-selected-check"><i class="fa-solid fa-check"></i></div>' : ''}
                    <span class="card-badge">${tmpl.badge || 'POPULAR'}</span>
                </div>
                <div class="card-info">
                    <div>
                        <div class="card-title-text">${tmpl.name}</div>
                        <div class="card-tag-text">${tmpl.tag}</div>
                        <div class="card-desc-text">${tmpl.description}</div>
                    </div>
                    <button class="btn-select-tmpl">${isSelected ? '✓ Selected Template' : 'Use This Template'}</button>
                </div>
            `;

            card.addEventListener('click', () => selectTemplate(tmpl));
            templatesGrid.appendChild(card);
        });
    }

    function selectTemplate(tmpl) {
        selectedTemplateId = tmpl.id;
        activeTemplateName.textContent = tmpl.name;
        document.querySelectorAll('.template-card').forEach(c => c.classList.remove('active-selected'));
        renderTemplateGrid(allTemplates);
        showToast(`Selected Template: ${tmpl.name}`, 'info');
        document.getElementById('studioSection').scrollIntoView({ behavior: 'smooth' });
    }

    // Texora Category Filter Pills
    document.querySelectorAll('.cat-pill').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.cat-pill').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const filter = btn.getAttribute('data-filter');
            
            if (filter === 'all') {
                renderTemplateGrid(allTemplates);
            } else if (filter === 'modern') {
                renderTemplateGrid(allTemplates.filter(t => t.id === 'modern_classic' || t.id === 'jake_ryan'));
            } else if (filter === 'classic') {
                renderTemplateGrid(allTemplates.filter(t => t.id === 'suraj_template' || t.id === 'classic_charter'));
            } else if (filter === 'minimal') {
                renderTemplateGrid(allTemplates.filter(t => t.id === 'jake_ryan'));
            } else if (filter === 'creative') {
                renderTemplateGrid(allTemplates.filter(t => t.id === 'deedy_resume' || t.id === 'modern_classic'));
            } else if (filter === 'academic') {
                renderTemplateGrid(allTemplates.filter(t => t.id === 'academic_cv'));
            } else if (filter === 'tech') {
                renderTemplateGrid(allTemplates.filter(t => t.id === 'suraj_template' || t.id === 'deedy_resume' || t.id === 'jake_ryan'));
            }
        });
    });

    // File Drag & Drop Uploading
    resumeDropZone.addEventListener('click', () => resumeFileInput.click());
    resumeDropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        resumeDropZone.classList.add('dragover');
    });
    resumeDropZone.addEventListener('dragleave', () => resumeDropZone.classList.remove('dragover'));
    resumeDropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        resumeDropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) handleFileUpload(e.dataTransfer.files[0]);
    });
    resumeFileInput.addEventListener('change', (e) => {
        if (e.target.files.length) handleFileUpload(e.target.files[0]);
    });

    async function handleFileUpload(file) {
        resumeFileInfo.textContent = `Extracting & Parsing "${file.name}" via DeepSeek...`;
        showToast(`Parsing ${file.name}...`, 'info');

        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await fetch('/api/upload-resume', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Resume parsing failed.');

            parsedProfile = data.profile;
            resumeFileInfo.textContent = `✓ Parsed "${file.name}" (${data.profile.name || 'Candidate'})`;
            showToast(`Resume text parsed successfully!`, 'success');

            if (parsedProfile.name) document.getElementById('scratchName').value = parsedProfile.name;
            if (parsedProfile.location) document.getElementById('scratchLoc').value = parsedProfile.location;
            if (parsedProfile.email) document.getElementById('scratchEmail').value = parsedProfile.email;
            if (parsedProfile.phone) document.getElementById('scratchPhone').value = parsedProfile.phone;
            if (parsedProfile.summary) document.getElementById('scratchSummary').value = parsedProfile.summary;

        } catch (err) {
            console.error(err);
            resumeFileInfo.textContent = `❌ Error: ${err.message}`;
            showToast(err.message, 'error');
        }
    }

    // Sample JDs
    const sampleJDs = {
        quant: `Quantitative Data Scientist / Risk Analyst:\n- Strong foundation in Statistics, Credit Risk Modeling, and Time-Series Analysis.\n- Proficiency in Python (Pandas, NumPy, Scikit-learn), SQL, and XGBoost/GLM loss estimation.\n- Experience predicting borrower default probabilities and SMOTE-ENN class imbalance.`,
        genai: `Senior GenAI & LLM Engineer:\n- Hands-on experience building RAG architectures, LangChain, FAISS/Pinecone vector DBs.\n- Fine-tuning open-source LLMs (Ollama, Mistral-7B, Llama 3) for domain NLP-to-SQL tasks.\n- Optimization of GPU inference latency and multi-agent system workflows.`,
        datasci: `Senior Data Scientist:\n- Track record in predictive analytics, machine learning pipeline deployment, and customer LTV/churn forecasting.\n- Advanced expertise in Python, PyTorch, TensorFlow, and cloud platforms (AWS/Azure).`
    };

    document.querySelectorAll('.sample-chip').forEach(btn => {
        btn.addEventListener('click', () => {
            const key = btn.getAttribute('data-sample');
            if (sampleJDs[key]) {
                jdInput.value = sampleJDs[key];
                showToast(`Loaded ${btn.textContent} JD`, 'info');
            }
        });
    });

    // Mode 1: Tailor & Generate PDF
    btnGenerate.addEventListener('click', async () => {
        const jd = jdInput.value.trim();
        if (!jd) {
            showToast('Please enter a target Job Description!', 'error');
            return;
        }

        btnGenerate.disabled = true;
        btnGenerate.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Tailoring & Compiling PDF...`;

        try {
            const payload = {
                job_description: jd,
                template_id: selectedTemplateId,
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

            const pdfUrl = `${data.pdf_url}?t=${Date.now()}`;
            pdfFrame.src = pdfUrl;
            pdfFrame.classList.remove('hidden');
            pdfPlaceholder.classList.add('hidden');

            latexCodeEditor.value = data.latex_code;
            btnDownload.href = pdfUrl;
            btnDownload.download = data.download_name || 'Tailored_Resume.pdf';
            btnDownload.classList.remove('disabled');

            showToast('Tailored 1-Page PDF Compiled Successfully!', 'success');

        } catch (err) {
            console.error('Generation Error:', err);
            showToast(err.message, 'error');
        } finally {
            btnGenerate.disabled = false;
            btnGenerate.innerHTML = `<i class="fa-solid fa-wand-magic-sparkles"></i> Generate & Compile PDF`;
        }
    });

    // Mode 2: Generate Scratch PDF
    btnGenerateScratch.addEventListener('click', async () => {
        btnGenerateScratch.disabled = true;
        btnGenerateScratch.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Compiling PDF...`;

        try {
            const profile = {
                name: document.getElementById('scratchName').value.trim(),
                location: document.getElementById('scratchLoc').value.trim(),
                email: document.getElementById('scratchEmail').value.trim(),
                phone: document.getElementById('scratchPhone').value.trim(),
                summary: document.getElementById('scratchSummary').value.trim(),
                skills: {
                    domains: 'Financial Risk Modeling, Predictive Analytics, NLP, LLMs',
                    languages: 'Python, R, SQL, SAS',
                    libraries: 'Pandas, NumPy, Scikit-learn, TensorFlow, PyTorch, LangChain',
                    tools: 'Power BI, Tableau, AWS, Streamlit, Git'
                },
                experience: [
                    {
                        dates: 'May 2026 -- Present',
                        role: 'AI Engineer',
                        company: 'PSS',
                        bullets: [
                            'Leveraged GenAI to optimize recruitment finance, reducing manual screening costs.',
                            'Built an LLM-based resume recommendation system improving hiring pipeline velocity by 20%.'
                        ]
                    }
                ],
                projects: [
                    {
                        year: '2024',
                        title: 'Credit Risk Modeling & Loan Default Prediction',
                        bullets: [
                            'Built an end-to-end ML pipeline (XGBoost, Random Forest) to predict borrower default probability.',
                            'Impact: Achieved 89% AUC-ROC, potential to reduce NPL ratios by 15%.'
                        ]
                    }
                ],
                education: [
                    {
                        year: 'May 2025',
                        degree: 'M.Sc. Statistics & Data Science',
                        institution: 'NMIMS Mumbai',
                        detail: 'CGPA: 3.67 / 4.0'
                    }
                ]
            };

            const payload = {
                template_id: selectedTemplateId,
                profile_data: profile
            };

            const res = await fetch('/api/generate-from-scratch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Build from scratch failed.');

            const pdfUrl = `${data.pdf_url}?t=${Date.now()}`;
            pdfFrame.src = pdfUrl;
            pdfFrame.classList.remove('hidden');
            pdfPlaceholder.classList.add('hidden');

            latexCodeEditor.value = data.latex_code;
            btnDownload.href = pdfUrl;
            btnDownload.download = data.download_name || 'Compiled_Resume.pdf';
            btnDownload.classList.remove('disabled');

            showToast('Resume PDF Compiled Successfully!', 'success');

        } catch (err) {
            console.error('Scratch Build Error:', err);
            showToast(err.message, 'error');
        } finally {
            btnGenerateScratch.disabled = false;
            btnGenerateScratch.innerHTML = `<i class="fa-solid fa-bolt-lightning"></i> Build & Compile PDF`;
        }
    });

    // Preview / Code Tabs
    tabPdfBtn.addEventListener('click', () => {
        tabPdfBtn.classList.add('active');
        tabCodeBtn.classList.remove('active');
        if (pdfFrame.src) pdfFrame.classList.remove('hidden');
        else pdfPlaceholder.classList.remove('hidden');
        codeView.classList.add('hidden');
        btnCopyCode.classList.add('hidden');
    });

    tabCodeBtn.addEventListener('click', () => {
        tabCodeBtn.classList.add('active');
        tabPdfBtn.classList.remove('active');
        pdfFrame.classList.add('hidden');
        pdfPlaceholder.classList.add('hidden');
        codeView.classList.remove('hidden');
        btnCopyCode.classList.remove('hidden');
    });

    btnCopyCode.addEventListener('click', () => {
        if (!latexCodeEditor.value) return;
        navigator.clipboard.writeText(latexCodeEditor.value);
        showToast('LaTeX Source Code Copied!', 'info');
    });

    function showToast(msg, type = 'info') {
        toastMsg.textContent = msg;
        toast.className = `toast ${type}`;
        setTimeout(() => toast.classList.add('hidden'), 3500);
    }

    // Initialize
    loadTemplates();
});
