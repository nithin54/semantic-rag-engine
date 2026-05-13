import json
from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
from app.benchmark import benchmark
from app.retriever import ContextAwareRAGEngine
import threading

app = Flask(__name__)
CORS(app)

# Global state
engine = None
benchmark_results = None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Semantic RAG Engine - Assessment Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            background: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        header h1 {
            color: #667eea;
            margin-bottom: 10px;
        }
        
        header p {
            color: #666;
            font-size: 16px;
        }
        
        .controls {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        
        button {
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn-secondary {
            background: #764ba2;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #633a87;
            transform: translateY(-2px);
        }
        
        .btn-danger {
            background: #f56565;
            color: white;
        }

        input[type="text"] {
            width: 100%;
            max-width: 560px;
            padding: 14px 18px;
            border-radius: 10px;
            border: 1px solid #dfe3e8;
            margin-top: 20px;
            font-size: 16px;
            color: #1f2937;
            background: #f8fafc;
        }

        .control-row {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            align-items: center;
            margin-top: 20px;
        }

        .control-row button {
            flex: 1 1 auto;
            min-width: 180px;
        }

        .strategy-summary {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-top: 18px;
            padding: 16px;
            border-radius: 12px;
            background: #eef2ff;
            color: #2d3748;
        }

        .strategy-label {
            font-size: 14px;
            line-height: 1.6;
        }

        .status-details {
            margin-top: 15px;
            color: #444;
        }
        
        .btn-danger:hover {
            background: #e53e3e;
        }
        
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .content {
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
        }
        
        .card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .card h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 22px;
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            border-bottom: 2px solid #eee;
            margin-bottom: 20px;
        }
        
        .tab-btn {
            padding: 12px 20px;
            background: none;
            border: none;
            border-bottom: 3px solid transparent;
            color: #666;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .tab-btn.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .query-section {
            margin: 20px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        
        .query-section h3 {
            color: #333;
            margin-bottom: 15px;
            font-size: 18px;
        }
        
        .query-text {
            color: #667eea;
            font-weight: 600;
            margin-bottom: 15px;
            font-style: italic;
        }
        
        .strategy {
            margin: 15px 0;
            padding: 15px;
            background: white;
            border-radius: 6px;
            border: 1px solid #eee;
        }
        
        .strategy h4 {
            color: #764ba2;
            margin-bottom: 10px;
            font-size: 16px;
        }
        
        .result-item {
            padding: 10px;
            margin: 8px 0;
            background: #f0f4ff;
            border-left: 3px solid #667eea;
            border-radius: 4px;
        }
        
        .result-doc {
            color: #333;
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .result-score {
            color: #667eea;
            font-weight: bold;
            font-size: 14px;
        }
        
        .comparison-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        .comparison-table th,
        .comparison-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        
        .comparison-table th {
            background: #f8f9fa;
            font-weight: 600;
            color: #667eea;
        }
        
        .comparison-table tr:hover {
            background: #f0f4ff;
        }
        
        .score-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .score-high {
            background: #c6f6d5;
            color: #22543d;
        }
        
        .score-medium {
            background: #bee3f8;
            color: #2c5282;
        }
        
        .score-low {
            background: #fed7d7;
            color: #742a2a;
        }
        
        .status-message {
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
            font-weight: 500;
        }
        
        .status-success {
            background: #c6f6d5;
            color: #22543d;
            border-left: 4px solid #38a169;
        }
        
        .status-error {
            background: #fed7d7;
            color: #742a2a;
            border-left: 4px solid #f56565;
        }
        
        .status-loading {
            background: #bee3f8;
            color: #2c5282;
            border-left: 4px solid #3182ce;
        }
        
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .metric-card {
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
            text-align: center;
        }
        
        .metric-label {
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 10px;
        }
        
        .metric-value {
            font-size: 28px;
            font-weight: bold;
        }
        
        .footer {
            margin-top: 40px;
            text-align: center;
            color: white;
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 Semantic RAG Engine - Senior Gen AI Assessment</h1>
            <p>Benchmark comparison between Raw Vector Search (Strategy A) and AI-Enhanced Retrieval (Strategy B)</p>
            
            <div class="controls">
                <input type="text" id="queryInput" placeholder="Ask a technical RAG question, e.g. How does the system handle peak load?" />
                <div class="strategy-summary">
                    <div class="strategy-label">
                        <strong>Strategy A:</strong> Raw Vector Search uses direct query embeddings against the stored corpus.
                    </div>
                    <div class="strategy-label">
                        <strong>Strategy B:</strong> AI-Enhanced Retrieval rewrites or expands the query before searching.
                    </div>
                </div>
                <div class="control-row">
                    <button class="btn-primary" onclick="runQuery('a')" id="queryRawBtn">
                        🔎 Raw Search
                    </button>
                    <button class="btn-secondary" onclick="runQuery('b')" id="queryEnhancedBtn">
                        ✨ Enhanced Search
                    </button>
                    <button class="btn-secondary" onclick="compareQuery()" id="queryCompareBtn">
                        ⚖️ Compare Query
                    </button>
                </div>
                <div class="control-row">
                    <button class="btn-primary" onclick="runBenchmark()" id="benchmarkBtn">
                        ▶ Run Benchmark
                    </button>
                    <button class="btn-secondary" onclick="loadBenchmark()">
                        📊 Load Results
                    </button>
                    <button class="btn-danger" onclick="clearResults()">
                        🗑 Clear Results
                    </button>
                </div>
                <div class="status-details">Run benchmark to load the comparison report for 3 complex queries, or use Live Query for ad hoc retrieval testing.</div>
            </div>
        </header>
        
        <div class="content">
            <div class="card">
                <div id="statusMessage"></div>
                
                <div class="tabs">
                    <button class="tab-btn active" onclick="switchTab('overview', event)">📈 Overview</button>
                    <button class="tab-btn" onclick="switchTab('queries', event)">🔍 Query Details</button>
                    <button class="tab-btn" onclick="switchTab('comparison', event)">⚖️ Comparison</button>
                    <button class="tab-btn" onclick="switchTab('single', event)">💡 Live Query</button>
                    <button class="tab-btn" onclick="switchTab('raw', event)">📋 Raw JSON</button>
                </div>
                
                <!-- Overview Tab -->
                <div id="overview" class="tab-content active">
                    <h2>Benchmark Summary</h2>
                    <div style="background: #f0f4ff; padding: 16px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #667eea;">
                        <h3 style="color: #667eea; margin-bottom: 12px; font-size: 16px;">How It Works</h3>
                        <p style="margin: 8px 0; color: #2d3748; font-size: 14px;"><strong>Strategy A:</strong> Takes your query and directly embeds it using sentence-transformers, then searches the FAISS vector store for the top-k most similar documents.</p>
                        <p style="margin: 8px 0; color: #2d3748; font-size: 14px;"><strong>Strategy B:</strong> Rewrites your query using a mocked Vertex AI GenerativeModel to expand it with synonyms and related terms, then embeds and searches the same vector store.</p>
                        <p style="margin: 8px 0; color: #2d3748; font-size: 14px;"><strong>Comparison:</strong> By running both strategies on the same queries, we measure how query expansion can improve retrieval quality (relevance scores and document ranking).</p>
                    </div>
                    <div id="overviewContent"></div>
                    <p style="margin-top: 12px; color: #555; font-size: 14px;">The dashboard visualizes strategy comparisons, showing which retrieval path is stronger for each benchmark query.</p>
                </div>
                
                <!-- Queries Tab -->
                <div id="queries" class="tab-content">
                    <h2>Query Results</h2>
                    <div id="queriesContent"></div>
                </div>
                
                <!-- Comparison Tab -->
                <div id="comparison" class="tab-content">
                    <h2>Strategy Comparison Analysis</h2>
                    <table class="comparison-table">
                        <thead>
                            <tr>
                                <th>Query</th>
                                <th>Strategy A Score</th>
                                <th>Strategy B Score</th>
                                <th>Improvement</th>
                                <th>Recommendation</th>
                            </tr>
                        </thead>
                        <tbody id="comparisonTable">
                        </tbody>
                    </table>
                </div>
                
                <div id="single" class="tab-content">
                    <h2>Live Query Results</h2>
                    <div id="singleResult"></div>
                </div>
                
                <!-- Raw JSON Tab -->
                <div id="raw" class="tab-content">
                    <h2>Raw JSON Results</h2>
                    <pre id="rawContent" style="background: #f8f9fa; padding: 15px; border-radius: 6px; overflow-x: auto; max-height: 600px;"></pre>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>✅ Assessment Ready | Embeddings: sentence-transformers | Vector Store: FAISS | Similarity: Cosine</p>
        </div>
    </div>

    <script>
        function showStatus(message, type = 'loading') {
            const statusEl = document.getElementById('statusMessage');
            statusEl.className = `status-message status-${type}`;
            let icon = type === 'success' ? '✅' : type === 'error' ? '❌' : '⏳';
            statusEl.innerHTML = `${icon} ${message}`;
            statusEl.style.display = 'block';
        }
        
        function hideStatus() {
            document.getElementById('statusMessage').style.display = 'none';
        }
        
        function switchTab(tabName, event) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            if (event && event.target) {
                event.target.classList.add('active');
            }
        }
        
        async function runBenchmark() {
            const btn = document.getElementById('benchmarkBtn');
            btn.disabled = true;
            showStatus('Running benchmark... This may take a minute.');
            
            try {
                const response = await fetch('/api/benchmark', { method: 'POST' });
                const data = await response.json();
                
                if (data.success) {
                    displayResults(data.results);
                    showStatus('Benchmark completed successfully!', 'success');
                    setTimeout(hideStatus, 3000);
                } else {
                    showStatus('Error: ' + data.error, 'error');
                }
            } catch (error) {
                showStatus('Error: ' + error.message, 'error');
            } finally {
                btn.disabled = false;
            }
        }
        
        async function loadBenchmark() {
            showStatus('Loading results...');
            try {
                const response = await fetch('/api/results');
                const data = await response.json();
                
                if (data.results) {
                    displayResults(data.results);
                    showStatus('Results loaded successfully!', 'success');
                    setTimeout(hideStatus, 3000);
                } else {
                    showStatus('No results available. Run benchmark first.', 'error');
                }
            } catch (error) {
                showStatus('Error: ' + error.message, 'error');
            }
        }

        async function runQuery(strategy) {
            const query = document.getElementById('queryInput').value.trim();
            if (!query) {
                showStatus('Please enter a query first.', 'error');
                return;
            }
            const btn = strategy === 'a' ? document.getElementById('queryRawBtn') : document.getElementById('queryEnhancedBtn');
            btn.disabled = true;
            showStatus('Running query...');

            try {
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query, strategy })
                });
                const data = await response.json();
                if (data.success) {
                    displaySingleResult(data.result);
                    switchTab('single');
                    showStatus('Query executed successfully!', 'success');
                    setTimeout(hideStatus, 2500);
                } else {
                    showStatus('Error: ' + data.error, 'error');
                }
            } catch (error) {
                showStatus('Error: ' + error.message, 'error');
            } finally {
                btn.disabled = false;
            }
        }

        async function compareQuery() {
            const query = document.getElementById('queryInput').value.trim();
            if (!query) {
                showStatus('Please enter a query first.', 'error');
                return;
            }
            const btn = document.getElementById('queryCompareBtn');
            btn.disabled = true;
            showStatus('Comparing strategies...');

            try {
                const response = await fetch('/api/compare', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query })
                });
                const data = await response.json();
                if (data.success) {
                    displayCompareResult(data.result);
                    switchTab('single');
                    showStatus('Comparison completed successfully!', 'success');
                    setTimeout(hideStatus, 2500);
                } else {
                    showStatus('Error: ' + data.error, 'error');
                }
            } catch (error) {
                showStatus('Error: ' + error.message, 'error');
            } finally {
                btn.disabled = false;
            }
        }

        function displaySingleResult(data) {
            const html = `
                <div class="query-section">
                    <h3>Query</h3>
                    <div class="query-text">"${data.query}"</div>
                    <div class="strategy">
                        <h4>${data.strategy}</h4>
                        ${data.expanded_query ? `<p><strong>Expanded Query:</strong> ${data.expanded_query}</p>` : ''}
                        ${data.results.map((res, j) => `
                            <div class="result-item">
                                <div class="result-doc">Rank ${j+1}: ${res.document}</div>
                                <div class="result-score">Score: ${res.score.toFixed(4)}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
            document.getElementById('singleResult').innerHTML = html;
        }

        function displayCompareResult(data) {
            const html = `
                <div class="query-section">
                    <h3>Query Comparison</h3>
                    <div class="query-text">"${data.query}"</div>
                    <div class="strategy">
                        <h4>Strategy A: Raw Vector Search</h4>
                        ${data.strategy_a_raw_search.map((res, j) => `
                            <div class="result-item">
                                <div class="result-doc">Rank ${j+1}: ${res.document}</div>
                                <div class="result-score">Score: ${res.score.toFixed(4)}</div>
                            </div>
                        `).join('')}
                    </div>
                    <div class="strategy">
                        <h4>Strategy B: AI-Enhanced Retrieval</h4>
                        ${data.strategy_b_enhanced_search.map((res, j) => `
                            <div class="result-item">
                                <div class="result-doc">Rank ${j+1}: ${res.document}</div>
                                <div class="result-score">Score: ${res.score.toFixed(4)}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
            document.getElementById('singleResult').innerHTML = html;
        }

        function clearResults() {
            if (confirm('Clear all benchmark results?')) {
                document.getElementById('overviewContent').innerHTML = '';
                document.getElementById('queriesContent').innerHTML = '';
                document.getElementById('comparisonTable').innerHTML = '';
                document.getElementById('rawContent').innerHTML = '';
                document.getElementById('singleResult').innerHTML = '';
                showStatus('Results cleared.', 'success');
                setTimeout(hideStatus, 2000);
            }
        }
        
        function displayResults(results) {
            // Overview
            const overviewHtml = `
                <div class="metric-grid">
                    <div class="metric-card">
                        <div class="metric-label">Total Queries</div>
                        <div class="metric-value">${results.length}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Average Strategy A Score</div>
                        <div class="metric-value">${(results.reduce((sum, r) => sum + (r.strategy_a_raw_search[0]?.score || 0), 0) / results.length).toFixed(3)}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Average Strategy B Score</div>
                        <div class="metric-value">${(results.reduce((sum, r) => sum + (r.strategy_b_enhanced_search[0]?.score || 0), 0) / results.length).toFixed(3)}</div>
                    </div>
                </div>
            `;
            document.getElementById('overviewContent').innerHTML = overviewHtml;
            
            // Queries
            let queriesHtml = '';
            results.forEach((r, i) => {
                queriesHtml += `
                    <div class="query-section">
                        <h3>Query ${i+1}</h3>
                        <div class="query-text">"${r.query}"</div>
                        
                        <div class="strategy">
                            <h4>Strategy A: Raw Vector Search</h4>
                            ${r.strategy_a_raw_search.map((res, j) => `
                                <div class="result-item">
                                    <div class="result-doc">Rank ${j+1}: ${res.document.substring(0, 80)}...</div>
                                    <div class="result-score">Score: ${res.score.toFixed(4)}</div>
                                </div>
                            `).join('')}
                        </div>
                        
                        <div class="strategy">
                            <h4>Strategy B: AI-Enhanced Retrieval</h4>
                            ${r.strategy_b_enhanced_search.map((res, j) => `
                                <div class="result-item">
                                    <div class="result-doc">Rank ${j+1}: ${res.document.substring(0, 80)}...</div>
                                    <div class="result-score">Score: ${res.score.toFixed(4)}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            });
            document.getElementById('queriesContent').innerHTML = queriesHtml;
            
            // Comparison Table
            let comparisonHtml = '';
            results.forEach((r, i) => {
                const scoreA = r.strategy_a_raw_search[0]?.score || 0;
                const scoreB = r.strategy_b_enhanced_search[0]?.score || 0;
                const improvement = ((scoreB - scoreA) / scoreA * 100).toFixed(2);
                const winner = scoreB > scoreA ? 'Strategy B ✓' : 'Strategy A ✓';
                
                comparisonHtml += `
                    <tr>
                        <td>${r.query.substring(0, 40)}...</td>
                        <td><span class="score-badge score-${scoreA > 0.6 ? 'high' : scoreA > 0.3 ? 'medium' : 'low'}">${scoreA.toFixed(3)}</span></td>
                        <td><span class="score-badge score-${scoreB > 0.6 ? 'high' : scoreB > 0.3 ? 'medium' : 'low'}">${scoreB.toFixed(3)}</span></td>
                        <td>${improvement}%</td>
                        <td>${winner}</td>
                    </tr>
                `;
            });
            document.getElementById('comparisonTable').innerHTML = comparisonHtml;
            
            // Raw JSON
            document.getElementById('rawContent').textContent = JSON.stringify(results, null, 2);
        }
        
        // Load results on page load
        window.addEventListener('load', () => {
            loadBenchmark();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/benchmark', methods=['POST'])
def run_benchmark():
    global benchmark_results, engine
    try:
        if engine is None:
            engine = ContextAwareRAGEngine()

        results = []
        for query in [
            "How does the system handle peak load?",
            "How is performance improved?",
            "How is system reliability maintained?"
        ]:
            results.append(engine.compare(query))

        benchmark_results = results
        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/results', methods=['GET'])
def get_results():
    global benchmark_results
    if benchmark_results is None:
        return jsonify({"results": None})
    return jsonify({"results": benchmark_results})

@app.route('/api/search', methods=['POST'])
def search_query():
    global engine
    try:
        data = request.get_json() or {}
        query = data.get('query', '').strip()
        strategy = data.get('strategy', 'a')
        if not query:
            return jsonify({"success": False, "error": "Query is required."})

        if engine is None:
            engine = ContextAwareRAGEngine()

        result = engine.search(query, strategy=strategy)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/compare', methods=['POST'])
def compare_query():
    global engine
    try:
        data = request.get_json() or {}
        query = data.get('query', '').strip()
        if not query:
            return jsonify({"success": False, "error": "Query is required."})

        if engine is None:
            engine = ContextAwareRAGEngine()

        result = engine.compare(query)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "Semantic RAG Engine"})

def run_server(debug=False, port=5000):
    print(f"\n✅ Starting Semantic RAG Engine Dashboard on http://localhost:{port}")
    print(f"📊 Open your browser and navigate to: http://localhost:{port}")
    print(f"🛑 Press CTRL+C to stop the server\n")
    app.run(debug=debug, port=port, threaded=True)

if __name__ == "__main__":
    run_server()
