// History Page Logic

const loadingSection = document.getElementById('loading-section');
const historySection = document.getElementById('history-section');
const emptySection = document.getElementById('empty-section');
const trendsSection = document.getElementById('trends-section');

let currentUrl = null;

// Load history on page load
window.addEventListener('load', loadHistory);

async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        const data = await response.json();
        
        if (data.urls.length === 0) {
            showSection(emptySection);
        } else {
            displayURLList(data.urls);
            showSection(historySection);
        }
    } catch (error) {
        console.error('Failed to load history:', error);
        showSection(emptySection);
    }
}

function showSection(section) {
    [loadingSection, historySection, emptySection].forEach(s => s.classList.add('hidden'));
    section.classList.remove('hidden');
}

function displayURLList(urls) {
    const container = document.getElementById('url-list');
    
    let html = '<div class="url-list-grid">';
    
    urls.forEach(item => {
        const date = new Date(item.timestamp).toLocaleDateString();
        
        html += `
            <div class="url-item" onclick="loadTrends('${item.url}')">
                <div class="url-item-header">
                    <div>
                        <div class="url-item-title">${item.title}</div>
                        <div class="url-item-url">${item.url}</div>
                    </div>
                    <div class="url-item-timestamp">${date}</div>
                </div>
                <div class="url-item-scores">
                    <span class="score-badge seo">SEO: ${item.seo_score}</span>
                    <span class="score-badge aeo">AEO: ${item.aeo_score}</span>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

async function loadTrends(url) {
    currentUrl = url;
    
    try {
        // Load trends
        const trendsResponse = await fetch(`/api/trends/${encodeURIComponent(url)}`);
        const trendsData = await trendsResponse.json();
        
        // Load full history
        const historyResponse = await fetch(`/api/history/${encodeURIComponent(url)}`);
        const historyData = await historyResponse.json();
        
        // Display trends
        displayTrends(trendsData.trends);
        
        // Display timeline
        displayTimeline(historyData.history);
        
        // Show trends section
        trendsSection.classList.remove('hidden');
        
        // Update selected URL display
        document.getElementById('selected-url').textContent = url;
        
        // Scroll to trends
        trendsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch (error) {
        console.error('Failed to load trends:', error);
        alert('Failed to load trends for this URL');
    }
}

function displayTrends(trends) {
    const container = document.getElementById('trend-charts');
    
    if (trends.trend === 'insufficient_data') {
        container.innerHTML = `<p>${trends.message}</p>`;
        return;
    }
    
    // Summary stats
    let html = '<div class="trend-summary">';
    
    // Current SEO
    html += `
        <div class="trend-stat">
            <div class="trend-stat-label">Current SEO Score</div>
            <div class="trend-stat-value">${trends.seo.current}</div>
            ${trends.seo.change !== 0 ? `
                <div class="trend-stat-change ${trends.seo.change > 0 ? 'positive' : 'negative'}">
                    ${trends.seo.change > 0 ? '▲' : '▼'} ${Math.abs(trends.seo.change)} pts
                </div>
            ` : '<div class="trend-stat-change neutral">No change</div>'}
        </div>
    `;
    
    // Current AEO
    html += `
        <div class="trend-stat">
            <div class="trend-stat-label">Current AEO Score</div>
            <div class="trend-stat-value">${trends.aeo.current}</div>
            ${trends.aeo.change !== 0 ? `
                <div class="trend-stat-change ${trends.aeo.change > 0 ? 'positive' : 'negative'}">
                    ${trends.aeo.change > 0 ? '▲' : '▼'} ${Math.abs(trends.aeo.change)} pts
                </div>
            ` : '<div class="trend-stat-change neutral">No change</div>'}
        </div>
    `;
    
    // Analyses count
    html += `
        <div class="trend-stat">
            <div class="trend-stat-label">Total Analyses</div>
            <div class="trend-stat-value">${trends.history_count}</div>
            <div class="trend-stat-change neutral">${trends.trend === 'improving' ? '📈 Improving' : '📉 Declining'}</div>
        </div>
    `;
    
    html += '</div>';
    
    // Score charts
    html += '<div class="score-chart">';
    html += '<div class="chart-title">SEO Score History</div>';
    html += '<div class="chart-bars">';
    
    trends.timestamps.forEach((timestamp, index) => {
        const date = new Date(timestamp).toLocaleDateString();
        const score = trends.seo.scores[index];
        
        html += `
            <div class="chart-bar">
                <div class="chart-bar-label">${date}</div>
                <div class="chart-bar-visual">
                    <div class="chart-bar-fill" style="width: ${score}%"></div>
                </div>
                <div class="chart-bar-value">${score}</div>
            </div>
        `;
    });
    
    html += '</div></div>';
    
    // AEO chart
    html += '<div class="score-chart">';
    html += '<div class="chart-title">AEO Score History</div>';
    html += '<div class="chart-bars">';
    
    trends.timestamps.forEach((timestamp, index) => {
        const date = new Date(timestamp).toLocaleDateString();
        const score = trends.aeo.scores[index];
        
        html += `
            <div class="chart-bar">
                <div class="chart-bar-label">${date}</div>
                <div class="chart-bar-visual">
                    <div class="chart-bar-fill" style="width: ${score}%; background: var(--success-color);"></div>
                </div>
                <div class="chart-bar-value">${score}</div>
            </div>
        `;
    });
    
    html += '</div></div>';
    
    container.innerHTML = html;
}

function displayTimeline(history) {
    const container = document.getElementById('history-timeline');
    
    let html = '<div class="history-timeline">';
    
    history.forEach(item => {
        const date = new Date(item.timestamp);
        const dateStr = date.toLocaleString();
        
        html += `
            <div class="timeline-item">
                <div class="timeline-item-header">
                    <div class="timeline-item-date">${dateStr}</div>
                    <div class="timeline-item-scores">
                        <span class="timeline-score seo">SEO: ${item.seo_score}</span>
                        <span class="timeline-score aeo">AEO: ${item.aeo_score}</span>
                    </div>
                </div>
                <div class="timeline-item-actions">
                    <button class="btn-small btn-view" onclick="viewAnalysis('${item.id}')">
                        View Details
                    </button>
                    <button class="btn-small btn-delete" onclick="deleteAnalysis('${item.id}')">
                        Delete
                    </button>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

function viewAnalysis(analysisId) {
    // Redirect to main page with analysis ID in URL
    window.location.href = `/?analysis=${analysisId}`;
}

async function deleteAnalysis(analysisId) {
    if (!confirm('Are you sure you want to delete this analysis?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/history/${analysisId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            // Reload trends for current URL
            if (currentUrl) {
                await loadTrends(currentUrl);
            }
            
            // Reload URL list
            await loadHistory();
        } else {
            alert('Failed to delete analysis');
        }
    } catch (error) {
        console.error('Failed to delete analysis:', error);
        alert('Failed to delete analysis');
    }
}
