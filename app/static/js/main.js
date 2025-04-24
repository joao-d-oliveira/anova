document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const uploadForm = document.getElementById('upload-form');
    const uploadSection = document.getElementById('upload-section');
    const processingSection = document.getElementById('processing-section');
    const resultSection = document.getElementById('result-section');
    const errorSection = document.getElementById('error-section');
    const processingMessage = document.getElementById('processing-message');
    const resultMessage = document.getElementById('result-message');
    const errorMessage = document.getElementById('error-message');
    const downloadButton = document.getElementById('download-button');
    const downloadTeamButton = document.getElementById('download-team-button');
    const downloadOpponentButton = document.getElementById('download-opponent-button');
    const newAnalysisButton = document.getElementById('new-analysis-button');
    const tryAgainButton = document.getElementById('try-again-button');
    const teamFilesInput = document.getElementById('team_files');
    const opponentFilesInput = document.getElementById('opponent_files');
    
    // Current task ID
    let currentTaskId = null;
    
    // Add event listeners
    uploadForm.addEventListener('submit', handleFormSubmit);
    newAnalysisButton.addEventListener('click', resetForm);
    tryAgainButton.addEventListener('click', resetForm);
    
    /**
     * Handle form submission
     * @param {Event} event - Form submit event
     */
    async function handleFormSubmit(event) {
        event.preventDefault();
        
        // Show processing section
        uploadSection.style.display = 'none';
        processingSection.style.display = 'block';
        resultSection.style.display = 'none';
        errorSection.style.display = 'none';
        
        // Get form data
        const formData = new FormData(uploadForm);
        
        try {
            // Upload files
            const response = await fetch('/api/upload/', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            currentTaskId = data.task_id;
            
            // Start checking status
            checkStatus();
        } catch (error) {
            console.error('Error uploading files:', error);
            showError('An error occurred while uploading files. Please try again.');
        }
    }
    
    /**
     * Check processing status
     */
    async function checkStatus() {
        if (!currentTaskId) {
            return;
        }
        
        try {
            const response = await fetch(`/api/status/${currentTaskId}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'processing') {
                // Update progress bar and message
                updateProgressBar(data);
                
                // Still processing, check again in 2 seconds
                setTimeout(checkStatus, 2000);
            } else if (data.status === 'completed') {
                // Processing completed
                showResult(data);
            } else if (data.status === 'failed') {
                // Processing failed
                showError(data.error || 'An error occurred during processing.');
            }
        } catch (error) {
            console.error('Error checking status:', error);
            showError('An error occurred while checking processing status.');
        }
    }
    
    /**
     * Update progress bar based on current step
     * @param {Object} data - Status data from the server
     */
    function updateProgressBar(data) {
        const progressBar = document.querySelector('.progress-bar');
        const processingMessage = document.getElementById('processing-message');
        
        if (data.total_steps && data.current_step !== undefined) {
            // Calculate progress percentage
            const progressPercent = Math.round((data.current_step / (data.total_steps - 1)) * 100);
            
            // Update progress bar width
            progressBar.style.width = `${progressPercent}%`;
            progressBar.setAttribute('aria-valuenow', progressPercent);
            
            // Update processing message
            if (data.step_description) {
                processingMessage.textContent = `${data.step_description} (Step ${data.current_step + 1} of ${data.total_steps})...`;
            }
        } else {
            // Fallback to indeterminate progress
            progressBar.style.width = '100%';
            processingMessage.textContent = 'Your files are being processed. This may take a few minutes...';
        }
    }
    
    /**
     * Show result section
     * @param {Object} data - Result data
     */
    function showResult(data) {
        uploadSection.style.display = 'none';
        processingSection.style.display = 'none';
        resultSection.style.display = 'block';
        errorSection.style.display = 'none';
        
        // Clear any existing event listeners
        downloadButton.replaceWith(downloadButton.cloneNode(true));
        downloadTeamButton.replaceWith(downloadTeamButton.cloneNode(true));
        downloadOpponentButton.replaceWith(downloadOpponentButton.cloneNode(true));
        
        // Get fresh references to the buttons
        const downloadBtn = document.getElementById('download-button');
        const downloadTeamBtn = document.getElementById('download-team-button');
        const downloadOpponentBtn = document.getElementById('download-opponent-button');
        
        // Set download URLs
        const downloadUrl = `/api/download/${currentTaskId}`;
        const teamDownloadUrl = `/api/download-team-analysis/${currentTaskId}`;
        const opponentDownloadUrl = `/api/download-opponent-analysis/${currentTaskId}`;
        
        console.log('Setting download URLs:');
        console.log('Combined report:', downloadUrl);
        console.log('Team analysis:', teamDownloadUrl);
        console.log('Opponent analysis:', opponentDownloadUrl);
        
        // Add click event listeners
        downloadBtn.addEventListener('click', function() {
            console.log('Downloading combined report from:', downloadUrl);
            window.open(downloadUrl, '_blank');
        });
        
        downloadTeamBtn.addEventListener('click', function() {
            console.log('Downloading team analysis from:', teamDownloadUrl);
            window.open(teamDownloadUrl, '_blank');
        });
        
        downloadOpponentBtn.addEventListener('click', function() {
            console.log('Downloading opponent analysis from:', opponentDownloadUrl);
            window.open(opponentDownloadUrl, '_blank');
        });
        
        // Set result message
        const teamName = data.team_name || 'Team';
        const opponentName = data.opponent_name || 'Opponent';
        resultMessage.textContent = `Your analysis for ${teamName} vs ${opponentName} is ready for download!`;
    }
    
    /**
     * Show error section
     * @param {string} message - Error message
     */
    function showError(message) {
        uploadSection.style.display = 'none';
        processingSection.style.display = 'none';
        resultSection.style.display = 'none';
        errorSection.style.display = 'block';
        
        // Set error message
        errorMessage.textContent = message;
    }
    
    /**
     * Reset form and show upload section
     */
    function resetForm() {
        uploadForm.reset();
        currentTaskId = null;
        
        uploadSection.style.display = 'block';
        processingSection.style.display = 'none';
        resultSection.style.display = 'none';
        errorSection.style.display = 'none';
    }
});
