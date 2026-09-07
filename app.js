/**
 * CareerSync Interactive Application Engine
 * Team: Rasika Chinchalkar · Payal Koyare
 * Guided By: Prof. Mrunali Jadhav | TGPCET NAGPUR
 */

document.addEventListener('DOMContentLoaded', () => {
    initResumePreviewEngine();
    initSkillGapAnalyzer();
    initGoalRoadmapTracker();
    initAIAdvisorDrawer();
});

/* ================= 1. RESUME LIVE PREVIEW ENGINE ================= */
function initResumePreviewEngine() {
    const nameInput = document.getElementById('res_name');
    if (!nameInput) return; // Not on resume page

    const emailInput = document.getElementById('res_email');
    const phoneInput = document.getElementById('res_phone');
    const branchInput = document.getElementById('res_branch');
    const collegeInput = document.getElementById('res_college');
    const summaryInput = document.getElementById('res_summary');
    const skillsInput = document.getElementById('res_skills');
    const projectsInput = document.getElementById('res_projects');
    const certsInput = document.getElementById('res_certs');

    const previewPaper = document.getElementById('resume_paper');

    function updatePreview() {
        if (!previewPaper) return;

        document.getElementById('prev_name').innerText = nameInput.value || 'Student Name';
        document.getElementById('prev_contact').innerText = 
            `${emailInput.value || 'student@tgpcet.ac.in'} ${phoneInput.value ? ' | ' + phoneInput.value : ''}`;
        
        document.getElementById('prev_edu').innerText = 
            `${branchInput.value || 'B.Tech Computer Science & Engineering'} — ${collegeInput.value || 'TGPCET Nagpur'}`;

        document.getElementById('prev_summary').innerText = 
            summaryInput.value || 'Motivated CS student with strong foundations in software development, problem solving, and modern web tech.';

        // Skills tags
        const skillsArr = (skillsInput.value || 'HTML, CSS, JavaScript, Python, Flask, SQL, Git').split(',');
        const skillsContainer = document.getElementById('prev_skills_tags');
        skillsContainer.innerHTML = '';
        skillsArr.forEach(s => {
            if (s.trim()) {
                const span = document.createElement('span');
                span.className = 'resume-pill-tag';
                span.innerText = s.trim();
                skillsContainer.appendChild(span);
            }
        });

        // Projects
        const projectsVal = projectsInput.value || 'CareerSync Web App: Student career & skill management platform.\nPortfolio Website: Responsive personal website built with HTML/CSS.';
        const prevProjects = document.getElementById('prev_projects_list');
        prevProjects.innerHTML = '';
        projectsVal.split('\n').forEach(line => {
            if (line.trim()) {
                const li = document.createElement('li');
                li.style.marginBottom = '6px';
                li.innerText = line.trim();
                prevProjects.appendChild(li);
            }
        });

        // Certificates
        const certsVal = certsInput.value || 'AWS Certified Cloud Practitioner (2025)\nFull Stack Web Development Certification — Coursera';
        const prevCerts = document.getElementById('prev_certs_list');
        prevCerts.innerHTML = '';
        certsVal.split('\n').forEach(c => {
            if (c.trim()) {
                const p = document.createElement('p');
                p.style.marginBottom = '4px';
                p.innerText = '• ' + c.trim();
                prevCerts.appendChild(p);
            }
        });
    }

    // Attach listeners
    [nameInput, emailInput, phoneInput, branchInput, collegeInput, summaryInput, skillsInput, projectsInput, certsInput].forEach(inp => {
        if (inp) inp.addEventListener('input', updatePreview);
    });

    // Theme switcher buttons
    const themeBtns = document.querySelectorAll('.theme-btn');
    themeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            themeBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const themeClass = btn.getAttribute('data-theme');
            previewPaper.className = 'resume-paper ' + themeClass;
        });
    });

    // Initial run
    updatePreview();
}

/* ================= 2. SKILL GAP ANALYZER ================= */
const CAREER_ROLE_DATA = {
    "Web Developer": {
        required: ["HTML", "CSS", "JavaScript", "Python", "Flask", "SQL", "Git", "REST APIs"],
        description: "Designs, builds, and maintains full-stack responsive web applications."
    },
    "AI/ML Engineer": {
        required: ["Python", "Machine Learning", "Data Structures", "Statistics", "NumPy", "Pandas", "PyTorch/TensorFlow", "SQL"],
        description: "Builds predictive models, neural networks, and AI pipelines."
    },
    "Data Analyst": {
        required: ["Python", "SQL", "Excel", "Statistics", "Data Visualization", "PowerBI/Tableau", "Pandas"],
        description: "Transforms raw data into actionable business intelligence and dashboards."
    },
    "Software Engineer": {
        required: ["Data Structures", "Algorithms", "Python", "Java", "Git", "OOP", "System Design", "SQL"],
        description: "Engineers scalable backend services and robust software architectures."
    },
    "Cloud & DevOps Engineer": {
        required: ["Linux", "Git", "Docker", "AWS/Azure", "CI/CD Pipelines", "Python", "Kubernetes", "Networking"],
        description: "Automates deployment pipelines, cloud infrastructure, and server reliability."
    },
    "Mobile App Developer": {
        required: ["Java", "Kotlin", "Flutter", "UI/UX", "Firebase", "REST APIs", "Git"],
        description: "Creates native and cross-platform mobile apps for Android and iOS."
    }
};

function initSkillGapAnalyzer() {
    const roleSelect = document.getElementById('role_analyzer_select');
    if (!roleSelect) return;

    roleSelect.addEventListener('change', runGapAnalysis);
    runGapAnalysis();
}

function runGapAnalysis() {
    const roleSelect = document.getElementById('role_analyzer_select');
    if (!roleSelect) return;

    const selectedRole = roleSelect.value;
    const roleInfo = CAREER_ROLE_DATA[selectedRole];
    if (!roleInfo) return;

    // Get acquired skills from DOM or session
    const acquiredSkillsElements = document.querySelectorAll('.user-skill-tag');
    let userSkills = [];
    acquiredSkillsElements.forEach(el => userSkills.push(el.getAttribute('data-skill-name') || el.innerText.trim()));

    if (userSkills.length === 0) {
        // Default sample user skills if none added
        userSkills = ["HTML", "CSS", "JavaScript", "Python", "SQL", "Git"];
    }

    const required = roleInfo.required;
    const matched = required.filter(r => userSkills.some(u => u.toLowerCase() === r.toLowerCase()));
    const missing = required.filter(r => !userSkills.some(u => u.toLowerCase() === r.toLowerCase()));

    const matchPct = Math.round((matched.length / required.length) * 100);

    // Update UI elements
    const scoreVal = document.getElementById('gap_match_score');
    if (scoreVal) scoreVal.innerText = `${matchPct}%`;

    const progressFill = document.getElementById('gap_progress_fill');
    if (progressFill) {
        progressFill.style.width = `${matchPct}%`;
        progressFill.innerText = `${matchPct}% Matched`;
    }

    const matchedContainer = document.getElementById('gap_matched_container');
    if (matchedContainer) {
        matchedContainer.innerHTML = '';
        if (matched.length === 0) {
            matchedContainer.innerHTML = '<span style="color:var(--text-muted); font-size:13px;">No skill matches yet.</span>';
        } else {
            matched.forEach(m => {
                const tag = document.createElement('span');
                tag.className = 'tag-pill matched';
                tag.innerHTML = `✓ ${m}`;
                matchedContainer.appendChild(tag);
            });
        }
    }

    const missingContainer = document.getElementById('gap_missing_container');
    if (missingContainer) {
        missingContainer.innerHTML = '';
        if (missing.length === 0) {
            missingContainer.innerHTML = '<span style="color:var(--emerald-light); font-size:14px; font-weight:700;">🎉 Perfect Match! You have all required skills.</span>';
        } else {
            missing.forEach(m => {
                const tag = document.createElement('span');
                tag.className = 'tag-pill missing';
                tag.innerHTML = `⚠ ${m}`;
                missingContainer.appendChild(tag);
            });
        }
    }
}

/* ================= 3. GOAL ROADMAP TRACKER ================= */
function initGoalRoadmapTracker() {
    const checkboxes = document.querySelectorAll('.task-checkbox');
    if (checkboxes.length === 0) return;

    function updateGoalProgress() {
        let total = checkboxes.length;
        let checkedCount = 0;
        checkboxes.forEach(cb => {
            const parentStep = cb.closest('.roadmap-step');
            if (cb.checked) {
                checkedCount++;
            }
        });

        const overallPct = Math.round((checkedCount / total) * 100);

        const goalProgressFill = document.getElementById('overall_goal_progress_fill');
        const goalProgressText = document.getElementById('overall_goal_progress_text');

        if (goalProgressFill) goalProgressFill.style.width = `${overallPct}%`;
        if (goalProgressText) goalProgressText.innerText = `${overallPct}% Completed`;
    }

    checkboxes.forEach(cb => {
        cb.addEventListener('change', updateGoalProgress);
    });

    updateGoalProgress();
}

/* ================= 4. AI ADVISOR DRAWER ================= */
function initAIAdvisorDrawer() {
    const fabBtn = document.getElementById('ai_fab_btn');
    const drawer = document.getElementById('ai_chat_drawer');
    const closeBtn = document.getElementById('ai_close_btn');
    const sendBtn = document.getElementById('ai_send_btn');
    const chatInput = document.getElementById('ai_chat_input');
    const chatBody = document.getElementById('ai_chat_body');

    if (!fabBtn || !drawer) return;

    fabBtn.addEventListener('click', () => drawer.classList.toggle('open'));
    if (closeBtn) closeBtn.addEventListener('click', () => drawer.classList.remove('open'));

    function appendMessage(text, isUser = false) {
        const bubble = document.createElement('div');
        bubble.className = `chat-bubble ${isUser ? 'user' : 'bot'}`;
        bubble.innerText = text;
        chatBody.appendChild(bubble);
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    function handleUserSend() {
        const text = chatInput.value.trim();
        if (!text) return;

        appendMessage(text, true);
        chatInput.value = '';

        // Generate intelligent AI response
        setTimeout(() => {
            let response = "That's a great question for your career journey! CareerSync recommends focusing on building hands-on projects, tracking your skill gaps against market demand, and maintaining an updated ATS resume.";

            const query = text.toLowerCase();
            if (query.includes('resume') || query.includes('cv')) {
                response = "💡 Resume Tip: Quantify your achievements! Instead of 'built a web app', write 'Developed a full-stack CareerSync app reducing skill tracking time by 40% using Flask & SQL'.";
            } else if (query.includes('full stack') || query.includes('web')) {
                response = "🚀 Full-Stack Roadmap: 1) Master HTML/CSS & Modern JS. 2) Pick a backend framework like Flask or Node. 3) Learn SQL database design. 4) Deploy your app live!";
            } else if (query.includes('ai') || query.includes('machine learning')) {
                response = "🤖 AI Engineer Path: Focus on Python, NumPy, Pandas, Scikit-learn, and linear algebra. Start by building a classification model on real datasets.";
            } else if (query.includes('tgpcet') || query.includes('placement')) {
                response = "🎓 Campus Placement Advice: Complete your CareerSync Profile, highlight core CS subjects (DSA, OS, DBMS), and build 2 polished capstone projects.";
            }

            appendMessage(response, false);
        }, 600);
    }

    if (sendBtn) sendBtn.addEventListener('click', handleUserSend);
    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') handleUserSend();
        });
    }
}
