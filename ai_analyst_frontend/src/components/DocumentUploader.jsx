import React, { useState } from 'react';

function DocumentUploader() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [teamStrength, setTeamStrength] = useState('');
  const [marketSize, setMarketSize] = useState('');
  const [founderBackground, setFounderBackground] = useState(''); // New state for Founder's Background
  const [uploadStatus, setUploadStatus] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setUploadStatus(''); // Clear previous status
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus({ type: 'error', message: 'Please select a file first.' });
      return;
    }

    setIsLoading(true);
    setUploadStatus({ type: 'info', message: 'Uploading...' });

    const formData = new FormData();
    formData.append('document', selectedFile);
    formData.append('teamStrength', teamStrength);
    formData.append('marketSize', marketSize);
    formData.append('founderBackground', founderBackground); // Append new field

    try {
      const response = await fetch('/api/v1/documents/upload-and-analyze', {
        method: 'POST',
        body: formData,
        // If your backend requires specific headers like Authorization, add them here:
        // headers: {
        //   'Authorization': 'Bearer YOUR_AUTH_TOKEN',
        // }
      });

      const data = await response.json();

      if (response.ok) {
        setUploadStatus({ type: 'success', message: data.message || 'Document uploaded successfully!' });
        console.log('Document ID:', data.documentId);
        setSelectedFile(null); // Clear selected file after successful upload
        setTeamStrength(''); // Clear team strength input
        setMarketSize(''); // Clear market size input
        setFounderBackground(''); // Clear founder background input
      } else {
        setUploadStatus({ type: 'error', message: data.message || 'Failed to upload document.' });
      }
    } catch (error) {
      setUploadStatus({ type: 'error', message: `Network error: ${error.message}` });
      console.error('Upload error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusClass = () => {
    if (typeof uploadStatus === 'string') return 'info'; // For initial 'Uploading...' string
    if (uploadStatus.type === 'success') return 'success';
    if (uploadStatus.type === 'error') return 'error';
    if (uploadStatus.type === 'info') return 'info';
    return '';
  };

  return (
    <div className="document-uploader-container">
      <h2>Upload Document for Analysis</h2>

      <div className="input-group">
        <label htmlFor="team-strength">Team Strength:</label>
        <input
          type="text"
          id="team-strength"
          className="text-input"
          value={teamStrength}
          onChange={(e) => setTeamStrength(e.target.value)}
          placeholder="e.g., 5 engineers, 2 designers"
          disabled={isLoading}
        />
      </div>

      <div className="input-group">
        <label htmlFor="market-size">Market Size:</label>
        <input
          type="text"
          id="market-size"
          className="text-input"
          value={marketSize}
          onChange={(e) => setMarketSize(e.target.value)}
          placeholder="e.g., $10B TAM, $500M SAM"
          disabled={isLoading}
        />
      </div>

      {/* New input field for Founder's Background */}
      <div className="input-group">
        <label htmlFor="founder-background">Founder's Background:</label>
        <input
          type="text"
          id="founder-background"
          className="text-input"
          value={founderBackground}
          onChange={(e) => setFounderBackground(e.target.value)}
          placeholder="e.g., Ex-Google, Serial Entrepreneur"
          disabled={isLoading}
        />
      </div>

      <div className="file-input-wrapper">
        <input
          type="file"
          id="file-upload"
          onChange={handleFileChange}
          disabled={isLoading}
        />
        <label htmlFor="file-upload" className="custom-button btn-outline">
          {selectedFile ? 'Change File' : 'Choose File'}
        </label>
        <button
          onClick={handleUpload}
          disabled={!selectedFile || isLoading}
          className="custom-button btn-primary"
        >
          {isLoading ? (
            <>
              <span className="loading-spinner"></span> Uploading...
            </>
          ) : (
            'Upload and Analyze'
          )}
        </button>
      </div>

      {selectedFile && !isLoading && (
        <p className="selected-file-name">Selected: {selectedFile.name}</p>
      )}

      {uploadStatus && (
        <p className={`status-message ${getStatusClass()}`}>
          {typeof uploadStatus === 'string' ? uploadStatus : uploadStatus.message}
        </p>
      )}
    </div>
  );
}

export default DocumentUploader;