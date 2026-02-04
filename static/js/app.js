// SEO + AEO Analyzer - Frontend Application

// DOM Elements
const inputSection = document.getElementById('input-section');
const loadingSection = document.getElementById('loading-section');
const resultsSection = document.getElementById('results-section');
const errorSection = document.getElementById('error-section');

const urlInput = document.getElementById('url-input');
const analyzeBtn = document.getElementById('analyze-btn');
const progressText = document.getElementById('progress-text');
const analyzeAnotherBtn = document.getElementById('analyze-another-btn');
const tryAgainBtn = document.getElementById('try-again-btn');

let currentAnalysisId = null;
let currentResults = null;
let charts = { score: null, status: null, keyword: null };

// Event Listeners
analyzeBtn.addEventListener('click', startAnalysis);
analyzeAnotherBtn.addEventListener('click', resetForm);
tryAgainBtn.addEventListener('click', resetForm);

// Visual mode toggle
document.getElementById('toggle-visual')?.addEventListener('click', () => setVisualMode(true));
document.getElementById('toggle-list')?.addEventListener('click', () => setVisualMode(false));

urlInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        startAnalysis();
    }
});

// Main Functions
async function startAnalysis() {
    const url = urlInput.value.trim();
    
    // Validation
    if (!url) {
        alert('Please enter a URL');
        return;
    }
    
    if (!isValidUrl(url)) {
        alert('Please enter a valid URL (must start with http:// or https://)');
        return;
    }
    
    // Show loading
    showSection(loadingSection);
    
    try {
        // Start analysis
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });
        
        if (!response.ok) {
            throw new Error('Failed to start analysis');
        }
        
        const data = await response.json();
        const analysisId = data.analysis_id;
        
        // Poll for results
        pollStatus(analysisId);
    } catch (error) {
        showError(error.message);
    }
}

async function pollStatus(analysisId) {
    const maxAttempts = 60; // 60 seconds max
    let attempts = 0;
    
    const interval = setInterval(async () => {
        attempts++;
        
        if (attempts > maxAttempts) {
            clearInterval(interval);
            showError('Analysis timed out. Please try again.');
            return;
        }
        
        try {
            const response = await fetch(`/api/status/${analysisId}`);
            const data = await response.json();
            
            // Update progress
            progressText.textContent = data.progress;
            
            // Check status
            if (data.status === 'completed') {
                clearInterval(interval);
                data.result.analysis_id = analysisId; // Store for export
                displayResults(data.result);
            } else if (data.status === 'failed') {
                clearInterval(interval);
                showError(data.error || 'Analysis failed');
            }
        } catch (error) {
            clearInterval(interval);
            showError('Failed to get analysis status');
        }
    }, 1000); // Poll every second
}

function displayResults(result) {
    // Store analysis ID for export
    currentAnalysisId = result.analysis_id || currentAnalysisId;
    
    // Page Info
    document.getElementById('page-title').textContent = result.metadata.title || 'Untitled Page';
    document.getElementById('analyzed-url').textContent = result.metadata.url;
    document.getElementById('word-count').textContent = result.metadata.word_count || 0;
    
    // SEO Score
    document.getElementById('seo-score').textContent = result.seo.score;
    const seoGrade = document.getElementById('seo-grade');
    seoGrade.textContent = result.seo.grade;
    seoGrade.className = `score-grade ${result.seo.grade}`;
    document.getElementById('seo-explanation').textContent = result.seo.explanation;
    
    // AEO Score
    document.getElementById('aeo-score').textContent = result.aeo.score;
    const aeoGrade = document.getElementById('aeo-grade');
    aeoGrade.textContent = result.aeo.grade;
    aeoGrade.className = `score-grade ${result.aeo.grade}`;
    document.getElementById('aeo-explanation').textContent = result.aeo.explanation;
    
    // Top Issues
    if (result.aeo.top_issues && result.aeo.top_issues.length > 0) {
        const topIssuesList = document.getElementById('top-issues-list');
        topIssuesList.innerHTML = result.aeo.top_issues.map(issue => `
            <div class="issue-item">
                <strong>${issue.name}</strong>
                <span>${issue.reason}</span>
            </div>
        `).join('');
    } else {
        document.getElementById('top-issues-container').style.display = 'none';
    }
    
    // Before/After Example
    if (result.before_after_example) {
        const example = result.before_after_example;
        document.getElementById('before-text').textContent = example.before;
        document.getElementById('after-text').textContent = example.after;
        document.getElementById('what-changed').textContent = `What changed: ${example.explanation}`;
    } else {
        document.getElementById('before-after-container').style.display = 'none';
    }
    
    // SEO Checks
    displayChecks(result.seo.checks, 'seo-checks');
    
    // AEO Checks
    displayChecks(result.aeo.checks, 'aeo-checks');
    
    // Keywords Section
    displayKeywords(result.keywords);
    
    // Action Checklist
    displayActionChecklist(result.action_checklist);
    
    // Store results for visual mode
    currentResults = result;
    
    // Initialize visual mode
    initVisualMode(result);
    
    // Show results
    showSection(resultsSection);
}

function displayChecks(checks, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = checks.map(check => `
        <div class="check-item ${check.status}">
            <div class="check-header">
                <span class="check-name">${check.name}</span>
                <span class="check-status ${check.status}">${check.status}</span>
            </div>
            <div class="check-explanation">${check.explanation}</div>
            <div class="check-recommendation">
                <strong>Recommendation:</strong> ${check.recommendation}
            </div>
        </div>
    `).join('');
}

function displayKeywords(keywords) {
    const container = document.getElementById('keywords-container');
    
    let html = `
        <div class="keyword-focus">
            <strong>Primary Focus:</strong> <span class="keyword-badge primary">${keywords.primary_focus}</span>
        </div>
        <div class="keyword-section">
            <h4>Top Keywords:</h4>
            <div class="keyword-tags">
                ${keywords.top_keywords.map(kw => `<span class="keyword-badge">${kw}</span>`).join('')}
            </div>
        </div>
        <div class="keyword-section">
            <h4>Keyword Placement:</h4>
            <table class="keyword-table">
                <thead>
                    <tr>
                        <th>Keyword</th>
                        <th>In Title</th>
                        <th>In H1</th>
                        <th>In First Paragraph</th>
                    </tr>
                </thead>
                <tbody>
                    ${Object.entries(keywords.keyword_placement).map(([kw, placement]) => `
                        <tr>
                            <td><strong>${kw}</strong></td>
                            <td>${placement.in_title ? '✅' : '❌'}</td>
                            <td>${placement.in_h1 ? '✅' : '❌'}</td>
                            <td>${placement.in_first_paragraph ? '✅' : '❌'}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
    
    if (keywords.suggested_keywords && keywords.suggested_keywords.length > 0) {
        html += `
            <div class="keyword-section">
                <h4>💡 Suggested Keywords to Add:</h4>
                <div class="keyword-tags">
                    ${keywords.suggested_keywords.map(kw => `<span class="keyword-badge suggested">${kw}</span>`).join('')}
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

function displayActionChecklist(checklist) {
    const container = document.getElementById('checklist-items');
    
    if (!checklist || checklist.length === 0) {
        container.innerHTML = '<p>No action items - your site is well-optimized!</p>';
        return;
    }
    
    // Parse checklist (it's an array of strings with headers and items)
    let html = '';
    let currentGroup = '';
    
    checklist.forEach(item => {
        if (item.includes('🔴') || item.includes('🟡')) {
            // Group header
            if (currentGroup) {
                html += '</div>'; // Close previous group
            }
            currentGroup = item;
            html += `<div class="checklist-group"><h4>${item}</h4>`;
        } else if (item.trim().startsWith('•')) {
            // Checklist item
            html += `<div class="checklist-item">${item}</div>`;
        }
    });
    
    if (currentGroup) {
        html += '</div>'; // Close last group
    }
    
    container.innerHTML = html;
}

function showError(message) {
    document.getElementById('error-message').textContent = message;
    showSection(errorSection);
}

function resetForm() {
    urlInput.value = '';
    showSection(inputSection);
}

function showSection(section) {
    // Hide all sections
    inputSection.classList.add('hidden');
    loadingSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
    errorSection.classList.add('hidden');
    
    // Show target section
    section.classList.remove('hidden');
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function isValidUrl(string) {
    try {
        const url = new URL(string);
        return url.protocol === 'http:' || url.protocol === 'https:';
    } catch (_) {
        return false;
    }
}

// Export functions
function exportJSON() {
    if (!currentAnalysisId) return;
    window.location.href = `/api/export/${currentAnalysisId}?format=json`;
}

function exportTXT() {
    if (!currentAnalysisId) return;
    window.location.href = `/api/export/${currentAnalysisId}?format=txt`;
}

// Visual Mode Functions
function setVisualMode(isVisual) {
    const visualPreview = document.getElementById('visual-preview');
    const checksSections = document.querySelectorAll('.checks-section, .action-checklist');
    const toggleVisual = document.getElementById('toggle-visual');
    const toggleList = document.getElementById('toggle-list');
    
    if (isVisual) {
        visualPreview.style.display = 'block';
        checksSections.forEach(el => el.style.display = 'none');
        toggleVisual?.classList.add('active');
        toggleList?.classList.remove('active');
    } else {
        visualPreview.style.display = 'none';
        checksSections.forEach(el => el.style.display = 'block');
        toggleVisual?.classList.remove('active');
        toggleList?.classList.add('active');
    }
}

function initVisualMode(result) {
    // Load page preview
    loadPagePreview(result.metadata.url);
    
    // Create issue markers
    createIssueMarkers(result);
    
    // Draw charts
    drawScoreChart(result);
    drawStatusChart(result);
    drawKeywordChart(result);
    drawContentMetrics(result);
}

function loadPagePreview(url) {
    const iframe = document.getElementById('page-preview');
    
    // Try to load the page (may fail due to CORS/X-Frame-Options)
    iframe.src = url;
    
    // Handle load errors
    iframe.onerror = () => {
        iframe.contentDocument.body.innerHTML = `
            <div style="padding: 40px; text-align: center; color: #666;">
                <h3>⚠️ Unable to preview this page</h3>
                <p>The website blocks embedding. This is common for security.</p>
                <a href="${url}" target="_blank" style="color: #4f46e5; text-decoration: underline;">
                    Open in new tab →
                </a>
            </div>
        `;
    };
}

function createIssueMarkers(result) {
    const container = document.getElementById('issue-markers');
    const allChecks = [...result.seo.checks, ...result.aeo.checks];
    
    // Filter failed and warning checks
    const issues = allChecks.filter(check => check.status === 'fail' || check.status === 'warning');
    
    let html = '';
    issues.forEach((issue, index) => {
        const severity = issue.status === 'fail' ? 'error' : 'warning';
        const icon = issue.status === 'fail' ? '❌' : '⚠️';
        
        html += `
            <div class="issue-marker ${severity}" data-issue="${index}">
                <div class="issue-marker-title">${icon} ${issue.name}</div>
                <div class="issue-marker-desc">${issue.explanation}</div>
            </div>
        `;
    });
    
    if (issues.length === 0) {
        html = '<p style="color: #10b981; text-align: center; padding: 20px;">✅ No major issues found!</p>';
    }
    
    container.innerHTML = html;
}

function drawScoreChart(result) {
    const ctx = document.getElementById('score-chart');
    if (!ctx) return;
    
    // Destroy existing chart
    if (charts.score) charts.score.destroy();
    
    charts.score = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['SEO Score', 'AEO Score'],
            datasets: [{
                label: 'Score',
                data: [result.seo.score, result.aeo.score],
                backgroundColor: [
                    'rgba(79, 70, 229, 0.8)',
                    'rgba(52, 211, 153, 0.8)'
                ],
                borderColor: [
                    'rgba(79, 70, 229, 1)',
                    'rgba(52, 211, 153, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

function drawStatusChart(result) {
    const ctx = document.getElementById('status-chart');
    if (!ctx) return;
    
    const allChecks = [...result.seo.checks, ...result.aeo.checks];
    const statusCount = {
        pass: allChecks.filter(c => c.status === 'pass').length,
        warning: allChecks.filter(c => c.status === 'warning').length,
        fail: allChecks.filter(c => c.status === 'fail').length
    };
    
    if (charts.status) charts.status.destroy();
    
    charts.status = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Pass', 'Warning', 'Fail'],
            datasets: [{
                data: [statusCount.pass, statusCount.warning, statusCount.fail],
                backgroundColor: [
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(251, 146, 60, 0.8)',
                    'rgba(239, 68, 68, 0.8)'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function drawKeywordChart(result) {
    const ctx = document.getElementById('keyword-chart');
    if (!ctx) return;
    
    const placement = result.keywords.keyword_placement;
    const keywords = Object.keys(placement).slice(0, 5); // Top 5
    
    const inTitle = keywords.map(kw => placement[kw].in_title ? 1 : 0);
    const inH1 = keywords.map(kw => placement[kw].in_h1 ? 1 : 0);
    const inFirst = keywords.map(kw => placement[kw].in_first_paragraph ? 1 : 0);
    
    if (charts.keyword) charts.keyword.destroy();
    
    charts.keyword = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: keywords,
            datasets: [
                {
                    label: 'In Title',
                    data: inTitle,
                    backgroundColor: 'rgba(79, 70, 229, 0.2)',
                    borderColor: 'rgba(79, 70, 229, 1)',
                    borderWidth: 2
                },
                {
                    label: 'In H1',
                    data: inH1,
                    backgroundColor: 'rgba(52, 211, 153, 0.2)',
                    borderColor: 'rgba(52, 211, 153, 1)',
                    borderWidth: 2
                },
                {
                    label: 'In First ¶',
                    data: inFirst,
                    backgroundColor: 'rgba(251, 146, 60, 0.2)',
                    borderColor: 'rgba(251, 146, 60, 1)',
                    borderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 1,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function drawContentMetrics(result) {
    const container = document.getElementById('content-metrics');
    if (!container) return;
    
    const metrics = [
        { label: 'Word Count', value: result.metadata.word_count || 0 },
        { label: 'Headings', value: result.metadata.headings || 0 },
        { label: 'Links', value: result.metadata.internal_links || 0 },
        { label: 'Keywords', value: result.keywords.top_keywords.length }
    ];
    
    let html = '';
    metrics.forEach(metric => {
        html += `
            <div class="mini-stat-item">
                <div class="mini-stat-label">${metric.label}</div>
                <div class="mini-stat-value">${metric.value}</div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// Initialize
showSection(inputSection);
