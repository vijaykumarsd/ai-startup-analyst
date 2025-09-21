import React, { useState } from 'react';
import './App.css';

//const API_BASE_URL = 'http://127.0.0.1:8000'; // Ensure this matches your backend URL
const API_BASE_URL = 'https://ai-analyst-backend-750412531100.us-central1.run.app'; // Ensure this matches your backend URL

function App() {
    const [selectedFile, setSelectedFile] = useState(null);
    const [customWeights, setCustomWeights] = useState({ team: 0.5, market_size: 0.5 });
    const [analysisResult, setAnalysisResult] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const handleFileChange = (event) => {
        setSelectedFile(event.target.files[0]);
        setAnalysisResult(null); // Clear previous results
        setError('');
    };

    const handleWeightChange = (event) => {
        const { name, value } = event.target;
        setCustomWeights(prev => ({ ...prev, [name]: parseFloat(value) }));
    };

    const handleUploadAndAnalyze = async () => {
        if (!selectedFile) {
            setError('Please select a file first.');
            return;
        }

        setIsLoading(true);
        setError('');
        setAnalysisResult(null);

        // Create a FormData object to send the file and weights
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('team_weight', customWeights.team);
        formData.append('market_size_weight', customWeights.market_size);

        try {
            // Call the new, combined endpoint
            const response = await fetch(`${API_BASE_URL}/api/v1/documents/upload-and-analyze`, {
                method: 'POST',
                body: formData, // No 'Content-Type' header needed, browser sets it for FormData
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Upload and analysis failed.');
            }

            const data = await response.json();
            setAnalysisResult(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="App">
            <header className="App-header">
                <h1>AI Analyst for Startup Evaluation</h1>
            </header>
            <main>
                <div className="card">
                    <h2>1. Select Pitch Deck & Set Weights</h2>
                    <input type="file" onChange={handleFileChange} accept=".pdf" />

                    <div className="weights-container">
                        <label>
                            Team Strength:
                            <input
                                type="range"
                                name="team"
                                min="0"
                                max="1"
                                step="0.1"
                                value={customWeights.team}
                                onChange={handleWeightChange}
                            />
                            {customWeights.team}
                        </label>
                        <label>
                            Market Size:
                            <input
                                type="range"
                                name="market_size"
                                min="0"
                                max="1"
                                step="0.1"
                                value={customWeights.market_size}
                                onChange={handleWeightChange}
                            />
                            {customWeights.market_size}
                        </label>
                    </div>

                    <button onClick={handleUploadAndAnalyze} disabled={isLoading || !selectedFile}>
                        {isLoading ? 'Uploading & Analyzing...' : 'Upload & Analyze'}
                    </button>
                </div>

                {error && <div className="error-message">{error}</div>}

                {isLoading && <div className="loader"></div>}

                {analysisResult && (
                    <div className="card result-card">
                        <h2>Analysis Results for: {analysisResult.file_name}</h2>

                        <div className="result-section">
                            <h3>Investment Recommendation</h3>
                            <p>{analysisResult.investment_recommendation}</p>
                        </div>

                        <div className="result-section">
                            <h3>Growth Summary</h3>
                            <p>{analysisResult.growth_summary}</p>
                        </div>

                        <div className="result-section">
                            <h3>Risk Analysis</h3>
                            <ul>
                                {analysisResult.risk_analysis.map((risk, index) => (
                                    <li key={index}>{risk}</li>
                                ))}
                            </ul>
                        </div>

                        <div className="result-section">
                            <h3>Peer Benchmarks (SaaS)</h3>
                            <p>Average Team Size: {analysisResult.peer_benchmarks.avg_team_size}</p>
                            <p>Average Seed Round: ${Number(analysisResult.peer_benchmarks.avg_seed_round).toLocaleString()}</p>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}

export default App;