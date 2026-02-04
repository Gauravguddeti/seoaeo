// Competitor Comparison Logic
let comparisonData = null;

const inputSection = document.getElementById('input-section');
const loadingSection = document.getElementById('loading-section');
const resultsSection = document.getElementById('results-section');
const errorSection = document.getElementById('error-section');

document.getElementById('compare-btn').addEventListener('click', startComparison);
document.getElementById('compare-another-btn').addEventListener('click', () => {
    showSection(inputSection);
    clearInputs();
});
document.getElementById('try-again-btn').addEventListener('click', () => {
    showSection(inputSection);
});

function showSection(section) {
    [inputSection, loadingSection, resultsSection, errorSection].forEach(s => s.classList.add('hidden'));
    section.classList.remove('hidden');
}

function clearInputs() {
    document.querySelectorAll('.url-input').forEach(input => input.value = '');
}

async function startComparison() {
    // Collect URLs
    const urls = [];
    for (let i = 1; i <= 4; i++) {
        const url = document.getElementById(`url${i}`).value.trim();
        if (url) {
            urls.push(url);
        }
    }
    
    if (urls.length < 2) {
        alert('Please enter at least 2 URLs to compare');
        return;
    }
    
    // Show loading
    showSection(loadingSection);
    document.getElementById('progress-text').textContent = `Analyzing ${urls.length} websites...`;
    
    const progressContainer = document.getElementById('progress-status');
    progressContainer.innerHTML = '';
    
    try {
        // Start analyzing all URLs
        const analyses = await Promise.all(
            urls.map((url, index) => analyzeURL(url, index, progressContainer))
        );
        
        // Generate comparison
        comparisonData = generateComparison(analyses, urls);
        displayComparison(comparisonData);
        
        showSection(resultsSection);
    } catch (error) {
        showError(error.message);
    }
}

async function analyzeURL(url, index, progressContainer) {
    const progressItem = document.createElement('div');
    progressItem.className = 'progress-item';
    progressItem.textContent = `URL ${index + 1}: Analyzing...`;
    progressContainer.appendChild(progressItem);
    
    try {
        // Start analysis
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        
        if (!response.ok) {
            throw new Error(`Failed to analyze ${url}`);
        }
        
        const data = await response.json();
        const analysisId = data.analysis_id;
        
        // Poll for results
        let attempts = 0;
        const maxAttempts = 60;
        
        while (attempts < maxAttempts) {
            const statusResponse = await fetch(`/api/status/${analysisId}`);
            const statusData = await statusResponse.json();
            
            if (statusData.status === 'completed') {
                progressItem.textContent = `URL ${index + 1}: ✓ Complete`;
                progressItem.classList.add('complete');
                return statusData.result;
            } else if (statusData.status === 'failed') {
                throw new Error(statusData.error || `Analysis failed for ${url}`);
            }
            
            await new Promise(resolve => setTimeout(resolve, 1000));
            attempts++;
        }
        
        throw new Error(`Timeout analyzing ${url}`);
    } catch (error) {
        progressItem.textContent = `URL ${index + 1}: ✗ Failed`;
        throw error;
    }
}

function generateComparison(analyses, urls) {
    // Identify best/worst performers
    const seoScores = analyses.map(a => a.seo.score);
    const aeoScores = analyses.map(a => a.aeo.score);
    
    const bestSEOIndex = seoScores.indexOf(Math.max(...seoScores));
    const bestAEOIndex = aeoScores.indexOf(Math.max(...aeoScores));
    
    // Extract all keywords
    const allKeywords = analyses.map(a => new Set(a.keywords.top_keywords));
    
    // Find unique keywords for each site
    const keywordGaps = analyses.map((analysis, index) => {
        const thisKeywords = allKeywords[index];
        const otherKeywords = new Set();
        
        allKeywords.forEach((keywords, i) => {
            if (i !== index) {
                keywords.forEach(kw => otherKeywords.add(kw));
            }
        });
        
        const unique = [...thisKeywords].filter(kw => !otherKeywords.has(kw));
        const missing = [...otherKeywords].filter(kw => !thisKeywords.has(kw));
        
        return { unique, missing };
    });
    
    // SEO check comparison
    const seoCheckComparison = compareChecks(analyses, 'seo');
    const aeoCheckComparison = compareChecks(analyses, 'aeo');
    
    return {
        urls,
        analyses,
        bestSEOIndex,
        bestAEOIndex,
        keywordGaps,
        seoCheckComparison,
        aeoCheckComparison
    };
}

function compareChecks(analyses, type) {
    const checksMap = {};
    
    // Group checks by name
    analyses.forEach((analysis, urlIndex) => {
        analysis[type].checks.forEach(check => {
            if (!checksMap[check.name]) {
                checksMap[check.name] = [];
            }
            checksMap[check.name][urlIndex] = check.status;
        });
    });
    
    return checksMap;
}

function displayComparison(data) {
    displayScoreComparison(data);
    displayFeatureComparison(data);
    displayKeywordGaps(data);
    displayWinnerAnalysis(data);
    displayRecommendations(data);
}

function displayScoreComparison(data) {
    const container = document.getElementById('score-comparison');
    
    let html = '<div class="score-bars">';
    
    // SEO Scores
    html += '<h4>SEO Scores</h4>';
    data.analyses.forEach((analysis, index) => {
        const shortUrl = new URL(data.urls[index]).hostname;
        html += `
            <div class="score-bar-item">
                <div class="score-bar-label">${shortUrl}</div>
                <div class="score-bar-container">
                    <div class="score-bar-fill grade-${analysis.seo.grade}" style="width: ${analysis.seo.score}%">
                        ${analysis.seo.score} (${analysis.seo.grade})
                    </div>
                </div>
            </div>
        `;
    });
    
    // AEO Scores
    html += '<h4 style="margin-top: 30px;">AEO Scores</h4>';
    data.analyses.forEach((analysis, index) => {
        const shortUrl = new URL(data.urls[index]).hostname;
        html += `
            <div class="score-bar-item">
                <div class="score-bar-label">${shortUrl}</div>
                <div class="score-bar-container">
                    <div class="score-bar-fill grade-${analysis.aeo.grade}" style="width: ${analysis.aeo.score}%">
                        ${analysis.aeo.score} (${analysis.aeo.grade})
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

function displayFeatureComparison(data) {
    const container = document.getElementById('feature-comparison');
    
    // Combine SEO and AEO checks
    const allChecks = { ...data.seoCheckComparison, ...data.aeoCheckComparison };
    
    let html = '<div style="overflow-x: auto;"><table class="feature-table"><thead><tr>';
    html += '<th>Feature</th>';
    
    data.urls.forEach(url => {
        const shortUrl = new URL(url).hostname;
        html += `<th>${shortUrl}</th>`;
    });
    
    html += '</tr></thead><tbody>';
    
    Object.entries(allChecks).forEach(([checkName, statuses]) => {
        html += `<tr><td>${checkName}</td>`;
        
        // Find best/worst status
        const statusValues = { 'pass': 2, 'warning': 1, 'fail': 0 };
        const scores = statuses.map(s => statusValues[s] || 0);
        const maxScore = Math.max(...scores);
        const minScore = Math.min(...scores);
        
        statuses.forEach((status, index) => {
            const score = statusValues[status] || 0;
            let cellClass = '';
            
            if (score === maxScore && maxScore > minScore) {
                cellClass = 'best';
            } else if (score === minScore && maxScore > minScore) {
                cellClass = 'worst';
            }
            
            const icon = status === 'pass' ? '✅' : status === 'warning' ? '⚠️' : '❌';
            html += `<td class="${cellClass}">${icon} ${status}</td>`;
        });
        
        html += '</tr>';
    });
    
    html += '</tbody></table></div>';
    container.innerHTML = html;
}

function displayKeywordGaps(data) {
    const container = document.getElementById('keyword-gaps');
    
    let html = '<div class="keyword-gap-grid">';
    
    data.analyses.forEach((analysis, index) => {
        const shortUrl = new URL(data.urls[index]).hostname;
        const gaps = data.keywordGaps[index];
        
        html += `
            <div class="keyword-gap-item">
                <h4>${shortUrl}</h4>
                <p><strong>Unique keywords (${gaps.unique.length}):</strong></p>
                <div class="unique-keywords">
                    ${gaps.unique.slice(0, 8).map(kw => `<span class="keyword-badge">${kw}</span>`).join('')}
                </div>
                ${gaps.missing.length > 0 ? `
                    <p style="margin-top: 10px;"><strong>Missing ${gaps.missing.length} keywords</strong> found in competitors</p>
                ` : ''}
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

function displayWinnerAnalysis(data) {
    const container = document.getElementById('winner-analysis');
    
    const bestSEO = data.analyses[data.bestSEOIndex];
    const bestAEO = data.analyses[data.bestAEOIndex];
    
    let html = '<div class="winner-grid">';
    
    // Best SEO
    html += `
        <div class="winner-item">
            <h4>🏆 Best SEO Score</h4>
            <p>Score: <strong>${bestSEO.seo.score}/100</strong> (${bestSEO.seo.grade})</p>
            <p class="winner-url">${data.urls[data.bestSEOIndex]}</p>
        </div>
    `;
    
    // Best AEO
    html += `
        <div class="winner-item">
            <h4>🏆 Best AEO Score</h4>
            <p>Score: <strong>${bestAEO.aeo.score}/100</strong> (${bestAEO.aeo.grade})</p>
            <p class="winner-url">${data.urls[data.bestAEOIndex]}</p>
        </div>
    `;
    
    // Best primary keyword
    const bestKeywordSite = data.analyses.reduce((best, analysis, index) => {
        const keywordCount = analysis.keywords.top_keywords.length;
        return keywordCount > best.count ? { index, count: keywordCount } : best;
    }, { index: 0, count: 0 });
    
    html += `
        <div class="winner-item">
            <h4>🏆 Most Keywords</h4>
            <p>Keywords: <strong>${bestKeywordSite.count}</strong></p>
            <p class="winner-url">${data.urls[bestKeywordSite.index]}</p>
        </div>
    `;
    
    html += '</div>';
    container.innerHTML = html;
}

function displayRecommendations(data) {
    const container = document.getElementById('comparison-recommendations');
    
    // Find common weaknesses
    const recommendations = [];
    
    // Check for common failing checks
    Object.entries(data.seoCheckComparison).forEach(([checkName, statuses]) => {
        const failCount = statuses.filter(s => s === 'fail').length;
        if (failCount > 1) {
            recommendations.push({
                title: `${checkName} - ${failCount}/${statuses.length} sites failing`,
                description: `Multiple sites need improvement on ${checkName}. This is a high-priority fix.`
            });
        }
    });
    
    // Keyword gaps
    const worstKeywordGap = data.keywordGaps.reduce((worst, gap, index) => {
        return gap.missing.length > worst.count ? { index, count: gap.missing.length } : worst;
    }, { index: 0, count: 0 });
    
    if (worstKeywordGap.count > 5) {
        recommendations.push({
            title: `Keyword Gap on ${new URL(data.urls[worstKeywordGap.index]).hostname}`,
            description: `This site is missing ${worstKeywordGap.count} keywords that competitors are using. Consider adding content targeting: ${data.keywordGaps[worstKeywordGap.index].missing.slice(0, 5).join(', ')}`
        });
    }
    
    let html = '<div class="recommendation-list">';
    
    if (recommendations.length === 0) {
        html += '<p>All sites are performing well! No major gaps identified.</p>';
    } else {
        recommendations.forEach(rec => {
            html += `
                <div class="recommendation-item">
                    <h4>${rec.title}</h4>
                    <p>${rec.description}</p>
                </div>
            `;
        });
    }
    
    html += '</div>';
    container.innerHTML = html;
}

function exportComparison() {
    if (!comparisonData) {
        alert('No comparison data to export');
        return;
    }
    
    const exportData = {
        timestamp: new Date().toISOString(),
        urls: comparisonData.urls,
        scores: comparisonData.analyses.map(a => ({
            seo: a.seo.score,
            aeo: a.aeo.score
        })),
        checks: {
            seo: comparisonData.seoCheckComparison,
            aeo: comparisonData.aeoCheckComparison
        },
        keywords: comparisonData.keywordGaps
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `comparison_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
}

function showError(message) {
    document.getElementById('error-message').textContent = message;
    showSection(errorSection);
}
