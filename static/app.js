document.addEventListener('DOMContentLoaded', () => {
    // Page Elements
    const wizardPage1 = document.getElementById('wizardPage1');
    const wizardPage2 = document.getElementById('wizardPage2');
    const navLinkPage2 = document.getElementById('navLinkPage2');
    
    // Page 1 Navigation Buttons
    const btnLeftNext = document.getElementById('btnLeftNext');
    const btnLeftBack = document.getElementById('btnLeftBack');
    const btnBackToPage1 = document.getElementById('btnBackToPage1');
    const btnGetStarted = document.getElementById('btnGetStarted');
    const btnBuildAiHero = document.getElementById('btnBuildAiHero');
    
    // Character Counter
    const scratchSummary = document.getElementById('scratchSummary');
    const summaryCharCount = document.getElementById('summaryCharCount');
    
    if (scratchSummary && summaryCharCount) {
        scratchSummary.addEventListener('input', () => {
            summaryCharCount.textContent = scratchSummary.value.length;
        });
    }

    // Sub-tabs (Education vs Certifications)
    const subTabEdu = document.getElementById('subTabEdu');
    const subTabCerts = document.getElementById('subTabCerts');
    const subContentEdu = document.getElementById('subContentEdu');
    const subContentCerts = document.getElementById('subContentCerts');

    if (subTabEdu && subTabCerts) {
        subTabEdu.addEventListener('click', () => {
            subTabEdu.classList.add('active');
            subTabCerts.classList.remove('active');
            subContentEdu.classList.remove('hidden');
            subContentCerts.classList.add('hidden');
        });

        subTabCerts.addEventListener('click', () => {
            subTabCerts.classList.add('active');
            subTabEdu.classList.remove('active');
            subContentCerts.classList.remove('hidden');
            subContentEdu.classList.add('hidden');
        });
    }

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
    
    // Page 2 & Generate Buttons
    const templatesGrid = document.getElementById('templatesGrid');
    const activeTemplateName = document.getElementById('activeTemplateName');
    const modelSelect = document.getElementById('modelSelect');
    const jdInput = document.getElementById('jdInput');
    const btnGenerate = document.getElementById('btnGenerate');
    
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
    let parsedProfile = null;
    let allTemplates = [];

    // Page Switching (Wizard Navigation)
    function gotoPage(pageNum) {
        if (pageNum === 1) {
            wizardPage1.classList.remove('hidden');
            wizardPage2.classList.add('hidden');
            window.scrollTo({ top: 0, behavior: 'smooth' });
        } else if (pageNum === 2) {
            wizardPage1.classList.add('hidden');
            wizardPage2.classList.remove('hidden');
            window.scrollTo({ top: 0, behavior: 'smooth' });
            
            // Auto compile PDF when entering Page 2
            const currentProfile = collectProfileFromForm();
            compileAndDisplayPdf(currentProfile);
        }
    }

    if (btnLeftNext) btnLeftNext.addEventListener('click', () => gotoPage(2));
    if (btnLeftBack) btnLeftBack.addEventListener('click', () => gotoPage(1));
    if (btnBackToPage1) btnBackToPage1.addEventListener('click', () => gotoPage(1));
    if (navLinkPage2) navLinkPage2.addEventListener('click', (e) => { e.preventDefault(); gotoPage(2); });
    if (btnGetStarted) btnGetStarted.addEventListener('click', () => gotoPage(1));
    if (btnBuildAiHero) btnBuildAiHero.addEventListener('click', () => gotoPage(1));

    // Dynamic Card Helpers
    if (btnAddExp) btnAddExp.addEventListener('click', () => addExperienceCard({}));
    if (btnAddProject) btnAddProject.addEventListener('click', () => addProjectCard({}));
    if (btnAddEdu) btnAddEdu.addEventListener('click', () => addEducationCard({}));

    function addExperienceCard(data = {}) {
        const card = document.createElement('div');
        card.className = 'dynamic-card exp-card';
        const bulletsText = Array.isArray(data.bullets) ? data.bullets.join('\n') : (data.bullets || '');
        card.innerHTML = `
            <button type="button" class="card-remove-btn"><i class="fa-solid fa-xmark"></i></button>
            <div class="scratch-form-grid">
                <div class="form-field">
                    <label>Job Title *</label>
                    <input type="text" class="exp-role" value="${data.role || data.title || ''}" placeholder="e.g. Data Scientist">
                </div>
                <div class="form-field">
                    <label>Company Name *</label>
                    <input type="text" class="exp-company" value="${data.company || data.organization || ''}" placeholder="e.g. ABC Analytics Pvt. Ltd.">
                </div>
                <div class="form-field">
                    <label>Location</label>
                    <input type="text" class="exp-loc" value="${data.location || ''}" placeholder="e.g. Mumbai, India">
                </div>
                <div class="form-field">
                    <label>Duration *</label>
                    <input type="text" class="exp-dates" value="${data.dates || ''}" placeholder="e.g. MM/YYYY -- MM/YYYY">
                </div>
                <div class="form-field full-width">
                    <label>Key Responsibilities & Achievements *</label>
                    <textarea class="exp-bullets" rows="3" placeholder="Describe your key responsibilities and achievements. Use bullet points for best results.">${bulletsText}</textarea>
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
                    <label>Project Title *</label>
                    <input type="text" class="proj-title" value="${data.title || data.name || ''}" placeholder="e.g. Credit Risk Prediction Model">
                </div>
                <div class="form-field">
                    <label>Duration</label>
                    <input type="text" class="proj-year" value="${data.year || data.dates || ''}" placeholder="e.g. 2024">
                </div>
                <div class="form-field full-width">
                    <label>Description & Outcomes *</label>
                    <textarea class="proj-bullets" rows="3" placeholder="Describe the problem, your approach, key technologies used, and outcomes.">${bulletsText}</textarea>
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
                    <label>Degree / Course *</label>
                    <input type="text" class="edu-degree" value="${data.degree || data.title || ''}" placeholder="e.g. M.Sc. in Data Science">
                </div>
                <div class="form-field">
                    <label>Institute / University *</label>
                    <input type="text" class="edu-inst" value="${data.institution || data.school || ''}" placeholder="e.g. NMIMS, Mumbai">
                </div>
                <div class="form-field">
                    <label>Location</label>
                    <input type="text" class="edu-loc" value="${data.location || ''}" placeholder="e.g. Mumbai, India">
                </div>
                <div class="form-field">
                    <label>Graduation Year</label>
                    <input type="text" class="edu-year" value="${data.year || data.dates || ''}" placeholder="e.g. 2025">
                </div>
                <div class="form-field full-width">
                    <label>Grade / CGPA (Optional)</label>
                    <input type="text" class="edu-detail" value="${data.detail || data.gpa || ''}" placeholder="e.g. 8.5 / 10">
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
        if (p.summary) {
            document.getElementById('scratchSummary').value = p.summary;
            if (summaryCharCount) summaryCharCount.textContent = p.summary.length;
        }
        
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
        
        // Re-compile PDF if on Page 2
        if (!wizardPage2.classList.contains('hidden')) {
            compileAndDisplayPdf(collectProfileFromForm());
        }
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

            // Populate form fields
            populateFormFromProfile(parsedProfile);

            // Switch to Page 2 & compile PDF preview immediately
            gotoPage(2);

        } catch (err) {
            console.error(err);
            resumeFileInfo.textContent = `❌ Error: ${err.message}`;
            showToast(err.message, 'error');
        }
    }

    // Helper: Compile & Display PDF
    async function compileAndDisplayPdf(profileData) {
        btnGenerate.disabled = true;
        btnGenerate.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Compiling PDF...`;

        try {
            const jd = jdInput ? jdInput.value.trim() : '';
            let res, data;

            if (jd) {
                const payload = {
                    job_description: jd,
                    template_id: selectedTemplateId,
                    model: modelSelect ? modelSelect.value : 'deepseek/deepseek-chat',
                    profile_data: profileData
                };
                res = await fetch('/api/tailor-and-generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
            } else {
                const payload = {
                    template_id: selectedTemplateId,
                    profile_data: profileData
                };
                res = await fetch('/api/generate-from-scratch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
            }

            data = await res.json();
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
            btnGenerate.disabled = false;
            btnGenerate.innerHTML = `<i class="fa-solid fa-wand-magic-sparkles"></i> Compile & Render PDF`;
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

    // Page 2: Compile Button
    btnGenerate.addEventListener('click', () => {
        const currentProfile = collectProfileFromForm();
        compileAndDisplayPdf(currentProfile);
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

    // Initialize Default Cards & Templates
    addExperienceCard({});
    addProjectCard({});
    addEducationCard({});
    loadTemplates();
});
