document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const templatesGrid = document.getElementById('templatesGrid');
    const activeTemplateName = document.getElementById('activeTemplateName');

    // Mode Switcher Pills
    const modeTailorBtn = document.getElementById('modeTailorBtn');
    const modeScratchBtn = document.getElementById('modeScratchBtn');
    const tailorInputCard = document.getElementById('tailorInputCard');
    const scratchInputCard = document.getElementById('scratchInputCard');

    // Form Tabs Elements
    const formTabs = document.querySelectorAll('.form-tab');
    const formTabContents = document.querySelectorAll('.form-tab-content');

    // Dynamic Lists Containers
    const expContainer = document.getElementById('expContainer');
    const projectsContainer = document.getElementById('projectsContainer');
    const eduContainer = document.getElementById('eduContainer');
    const btnAddExp = document.getElementById('btnAddExp');
    const btnAddProject = document.getElementById('btnAddProject');
    const btnAddEdu = document.getElementById('btnAddEdu');

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
    let currentMode = 'scratch';
    let parsedProfile = null;
    let allTemplates = [];

    // Form Tab Switching
    formTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            formTabs.forEach(t => t.classList.remove('active'));
            formTabContents.forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            const targetId = tab.getAttribute('data-tab');
            document.getElementById(targetId).classList.add('active');
        });
    });

    // Dynamic Card Builders
    btnAddExp.addEventListener('click', () => addExperienceCard({}));
    btnAddProject.addEventListener('click', () => addProjectCard({}));
    btnAddEdu.addEventListener('click', () => addEducationCard({}));

    function addExperienceCard(data = {}) {
        const card = document.createElement('div');
        card.className = 'dynamic-card exp-card';
        const bulletsText = Array.isArray(data.bullets) ? data.bullets.join('\n') : (data.bullets || '');
        card.innerHTML = `
            <button type="button" class="card-remove-btn"><i class="fa-solid fa-xmark"></i></button>
            <div class="scratch-form-grid">
                <div class="form-field">
                    <label>Role / Job Title</label>
                    <input type="text" class="exp-role" value="${data.role || data.title || ''}" placeholder="e.g. Senior Software Engineer">
                </div>
                <div class="form-field">
                    <label>Company / Organization</label>
                    <input type="text" class="exp-company" value="${data.company || data.organization || ''}" placeholder="e.g. Google">
                </div>
                <div class="form-field">
                    <label>Location</label>
                    <input type="text" class="exp-loc" value="${data.location || ''}" placeholder="e.g. Mountain View, CA">
                </div>
                <div class="form-field">
                    <label>Dates</label>
                    <input type="text" class="exp-dates" value="${data.dates || ''}" placeholder="e.g. Jan 2022 -- Present">
                </div>
                <div class="form-field full-width">
                    <label>Key Bullet Points (One per line)</label>
                    <textarea class="exp-bullets" rows="3" placeholder="Led a team of 5 engineers...\nImproved system latency by 35%...">${bulletsText}</textarea>
                </div>
            </div>
        `;
        card.querySelector('.card-remove-btn').addEventListener('click', () => card.remove());
        expContainer.appendChild(card);
    }

    function addProjectCard(data = {}) {
        const card = document.createElement('div');
        card.className = 'dynamic-card proj-card';
        const bulletsText = Array.isArray(data.bullets) ? data.bullets.join('\n') : (data.bullets || '');
        card.innerHTML = `
            <button type="button" class="card-remove-btn"><i class="fa-solid fa-xmark"></i></button>
            <div class="scratch-form-grid">
                <div class="form-field">
                    <label>Project Title</label>
                    <input type="text" class="proj-title" value="${data.title || data.name || ''}" placeholder="e.g. Real-Time Analytics Pipeline">
                </div>
                <div class="form-field">
                    <label>Year / Dates</label>
                    <input type="text" class="proj-year" value="${data.year || data.dates || ''}" placeholder="e.g. 2024">
                </div>
                <div class="form-field full-width">
                    <label>Project Details / Impact (One per line)</label>
                    <textarea class="proj-bullets" rows="3" placeholder="Architected distributed Kafka pipeline...\nImpact: Processed 1M+ events/sec.">${bulletsText}</textarea>
                </div>
            </div>
        `;
        card.querySelector('.card-remove-btn').addEventListener('click', () => card.remove());
        projectsContainer.appendChild(card);
    }

    function addEducationCard(data = {}) {
        const card = document.createElement('div');
        card.className = 'dynamic-card edu-card';
        card.innerHTML = `
            <button type="button" class="card-remove-btn"><i class="fa-solid fa-xmark"></i></button>
            <div class="scratch-form-grid">
                <div class="form-field">
                    <label>Degree / Field of Study</label>
                    <input type="text" class="edu-degree" value="${data.degree || data.title || ''}" placeholder="e.g. B.S. in Computer Science">
                </div>
                <div class="form-field">
                    <label>University / Institution</label>
                    <input type="text" class="edu-inst" value="${data.institution || data.school || ''}" placeholder="e.g. Stanford University">
                </div>
                <div class="form-field">
                    <label>Location</label>
                    <input type="text" class="edu-loc" value="${data.location || ''}" placeholder="e.g. Stanford, CA">
                </div>
                <div class="form-field">
                    <label>Graduation Year</label>
                    <input type="text" class="edu-year" value="${data.year || data.dates || ''}" placeholder="e.g. 2023">
                </div>
                <div class="form-field full-width">
                    <label>Details / GPA / Coursework</label>
                    <input type="text" class="edu-detail" value="${data.detail || data.gpa || ''}" placeholder="e.g. GPA: 3.9 / 4.0, Honors">
                </div>
            </div>
        `;
        card.querySelector('.card-remove-btn').addEventListener('click', () => card.remove());
        eduContainer.appendChild(card);
    }

    // Populate Entire Form from Extracted JSON Profile
    function populateFormFromProfile(p) {
        if (!p) return;

        if (p.name) document.getElementById('scratchName').value = p.name;
        if (p.location) document.getElementById('scratchLoc').value = p.location;
        if (p.email) document.getElementById('scratchEmail').value = p.email;
        if (p.phone) document.getElementById('scratchPhone').value = p.phone;
        if (p.linkedin) document.getElementById('scratchLinkedin').value = p.linkedin;
        if (p.github) document.getElementById('scratchGithub').value = p.github;
        if (p.summary) document.getElementById('scratchSummary').value = p.summary;

        if (p.skills) {
            if (typeof p.skills === 'object') {
                document.getElementById('skillDomains').value = p.skills.domains || '';
                document.getElementById('skillLanguages').value = p.skills.languages || '';
                document.getElementById('skillLibraries').value = p.skills.libraries || '';
                document.getElementById('skillTools').value = p.skills.tools || '';
            } else {
                document.getElementById('skillDomains').value = String(p.skills);
            }
        }

        // Experience entries
        expContainer.innerHTML = '';
        if (Array.isArray(p.experience) && p.experience.length) {
            p.experience.forEach(exp => addExperienceCard(exp));
        } else {
            addExperienceCard({});
        }

        // Projects entries
        projectsContainer.innerHTML = '';
        if (Array.isArray(p.projects) && p.projects.length) {
            p.projects.forEach(proj => addProjectCard(proj));
        } else {
            addProjectCard({});
        }

        // Education entries
        eduContainer.innerHTML = '';
        if (Array.isArray(p.education) && p.education.length) {
            p.education.forEach(edu => addEducationCard(edu));
        } else {
            addEducationCard({});
        }

        // Certifications
        if (Array.isArray(p.certifications)) {
            document.getElementById('scratchCerts').value = p.certifications.join('\n');
        } else if (p.certifications) {
            document.getElementById('scratchCerts').value = String(p.certifications);
        }
    }

    // Collect Current Profile Data from Form
    function collectProfileFromForm() {
        const expItems = [];
        document.querySelectorAll('.exp-card').forEach(card => {
            const role = card.querySelector('.exp-role').value.trim();
            const company = card.querySelector('.exp-company').value.trim();
            const location = card.querySelector('.exp-loc').value.trim();
            const dates = card.querySelector('.exp-dates').value.trim();
            const bulletsRaw = card.querySelector('.exp-bullets').value.split('\n').map(b => b.trim()).filter(Boolean);
            if (role || company) {
                expItems.push({ role, company, location, dates, bullets: bulletsRaw });
            }
        });

        const projItems = [];
        document.querySelectorAll('.proj-card').forEach(card => {
            const title = card.querySelector('.proj-title').value.trim();
            const year = card.querySelector('.proj-year').value.trim();
            const bulletsRaw = card.querySelector('.proj-bullets').value.split('\n').map(b => b.trim()).filter(Boolean);
            if (title) {
                projItems.push({ title, year, bullets: bulletsRaw });
            }
        });

        const eduItems = [];
        document.querySelectorAll('.edu-card').forEach(card => {
            const degree = card.querySelector('.edu-degree').value.trim();
            const institution = card.querySelector('.edu-inst').value.trim();
            const location = card.querySelector('.edu-loc').value.trim();
            const year = card.querySelector('.edu-year').value.trim();
            const detail = card.querySelector('.edu-detail').value.trim();
            if (degree || institution) {
                eduItems.push({ degree, institution, location, year, detail });
            }
        });

        const certsRaw = document.getElementById('scratchCerts').value.split('\n').map(c => c.trim()).filter(Boolean);

        return {
            name: document.getElementById('scratchName').value.trim(),
            location: document.getElementById('scratchLoc').value.trim(),
            email: document.getElementById('scratchEmail').value.trim(),
            phone: document.getElementById('scratchPhone').value.trim(),
            linkedin: document.getElementById('scratchLinkedin').value.trim(),
            github: document.getElementById('scratchGithub').value.trim(),
            summary: document.getElementById('scratchSummary').value.trim(),
            skills: {
                domains: document.getElementById('skillDomains').value.trim(),
                languages: document.getElementById('skillLanguages').value.trim(),
                libraries: document.getElementById('skillLibraries').value.trim(),
                tools: document.getElementById('skillTools').value.trim()
            },
            experience: expItems,
            projects: projItems,
            education: eduItems,
            certifications: certsRaw
        };
    }

    // Mode Switching
    modeTailorBtn.addEventListener('click', () => setMode('tailor'));
    modeScratchBtn.addEventListener('click', () => setMode('scratch'));

    btnGetStarted.addEventListener('click', () => {
        document.getElementById('templatesSection').scrollIntoView({ behavior: 'smooth' });
    });

    btnBuildAiHero.addEventListener('click', () => {
        setMode('scratch');
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
            showToast(`Extracted all profile fields from ${file.name}!`, 'success');

            // Populate form fields & switch to profile builder tab
            populateFormFromProfile(parsedProfile);
            setMode('scratch');

            // Immediately compile & display the PDF preview for the uploaded candidate
            compileAndDisplayPdf(parsedProfile);

        } catch (err) {
            console.error(err);
            resumeFileInfo.textContent = `❌ Error: ${err.message}`;
            showToast(err.message, 'error');
        }
    }

    // Helper: Compile & Display PDF
    async function compileAndDisplayPdf(profileData) {
        btnGenerateScratch.disabled = true;
        btnGenerateScratch.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Compiling PDF...`;

        try {
            const payload = {
                template_id: selectedTemplateId,
                profile_data: profileData
            };

            const res = await fetch('/api/generate-from-scratch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Compilation failed.');

            const pdfUrl = `${data.pdf_url}?t=${Date.now()}`;
            pdfFrame.src = pdfUrl;
            pdfFrame.classList.remove('hidden');
            pdfPlaceholder.classList.add('hidden');

            latexCodeEditor.value = data.latex_code;
            btnDownload.href = pdfUrl;
            btnDownload.download = data.download_name || 'Resume.pdf';
            btnDownload.classList.remove('disabled');

            showToast('Resume PDF Compiled Successfully!', 'success');

        } catch (err) {
            console.error('Compilation Error:', err);
            showToast(err.message, 'error');
        } finally {
            btnGenerateScratch.disabled = false;
            btnGenerateScratch.innerHTML = `<i class="fa-solid fa-bolt-lightning"></i> Compile & Render PDF`;
        }
    }

    // Generate Scratch PDF button listener
    btnGenerateScratch.addEventListener('click', () => {
        const currentProfile = collectProfileFromForm();
        compileAndDisplayPdf(currentProfile);
    });

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

    // Mode 1: AI Tailor & Generate PDF
    btnGenerate.addEventListener('click', async () => {
        const jd = jdInput.value.trim();
        const currentProfile = collectProfileFromForm();

        btnGenerate.disabled = true;
        btnGenerate.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Tailoring & Compiling PDF...`;

        try {
            const payload = {
                job_description: jd,
                template_id: selectedTemplateId,
                model: modelSelect.value,
                profile_data: currentProfile
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
            btnGenerate.innerHTML = `<i class="fa-solid fa-wand-magic-sparkles"></i> AI Tailor & Compile PDF`;
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

    // Initialize Default Empty Cards
    addExperienceCard({});
    addProjectCard({});
    addEducationCard({});
    loadTemplates();
});
