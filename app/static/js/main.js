document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements - Upload form elements
    const teamFileInput = document.getElementById('team_files');
    const opponentFileInput = document.getElementById('opponent_files');
    const teamUploadBtn = document.getElementById('team-upload-btn');
    const opponentUploadBtn = document.getElementById('opponent-upload-btn');
    const teamUploadBox = document.getElementById('team-upload-box');
    const opponentUploadBox = document.getElementById('opponent-upload-box');
    const teamSelectedFile = document.getElementById('team-selected-file');
    const opponentSelectedFile = document.getElementById('opponent-selected-file');
    const submitBtn = document.getElementById('submit-btn');
    const useLocalSimulation = document.getElementById('use_local_simulation');
    const teamNameInput = document.getElementById('team_name');
    const opponentNameInput = document.getElementById('opponent_name');
    
    // Get DOM elements - Sections
    const processingSection = document.getElementById('processing-section');
    const resultSection = document.getElementById('result-section');
    const errorSection = document.getElementById('error-section');
    const previousReportsSection = document.getElementById('previous-reports-section');
    const reportsList = document.getElementById('reports-list');
    
    // Get DOM elements - Messages and buttons
    const processingMessage = document.getElementById('processing-message');
    const resultMessage = document.getElementById('result-message');
    const errorMessage = document.getElementById('error-message');
    const downloadButton = document.getElementById('download-button');
    const downloadTeamButton = document.getElementById('download-team-button');
    const downloadOpponentButton = document.getElementById('download-opponent-button');
    const newAnalysisButton = document.getElementById('new-analysis-button');
    const tryAgainButton = document.getElementById('try-again-button');
    
    // Current task ID
    let currentTaskId = null;
    
    // Add event listeners for file upload buttons
    teamUploadBtn.addEventListener('click', function() {
        teamFileInput.click();
    });
    
    opponentUploadBtn.addEventListener('click', function() {
        opponentFileInput.click();
    });
    
    // Handle file selection for team files
    teamFileInput.addEventListener('change', function(event) {
        handleFileSelection(event, teamSelectedFile);
    });
    
    // Handle file selection for opponent files
    opponentFileInput.addEventListener('change', function(event) {
        handleFileSelection(event, opponentSelectedFile);
    });
    
    // Handle drag and drop for team upload box
    setupDragAndDrop(teamUploadBox, teamFileInput, teamSelectedFile);
    
    // Handle drag and drop for opponent upload box
    setupDragAndDrop(opponentUploadBox, opponentFileInput, opponentSelectedFile);
    
    // Add event listener for submit button
    submitBtn.addEventListener('click', handleSubmit);
    
    // Add event listeners for result buttons
    newAnalysisButton.addEventListener('click', resetForm);
    tryAgainButton.addEventListener('click', resetForm);
    
    // Add event listener for start again button
    document.getElementById('start-again-btn').addEventListener('click', resetForm);
    
    // Load previous reports and ensure upload container is visible
    loadPreviousReports();
    document.querySelector('.upload-container').style.display = 'block';
    
    /**
     * Handle file selection
     * @param {Event} event - Change event
     * @param {HTMLElement} selectedFileElement - Element to display selected file
     */
    function handleFileSelection(event, selectedFileElement) {
        const files = event.target.files;
        
        if (files.length > 0) {
            const file = files[0];
            
            // Display selected file
            selectedFileElement.innerHTML = `
                <div class="file-name">${file.name}</div>
                <button type="button" class="remove-file">&times;</button>
            `;
            
            // Add event listener to remove button
            const removeButton = selectedFileElement.querySelector('.remove-file');
            removeButton.addEventListener('click', function() {
                event.target.value = '';
                selectedFileElement.innerHTML = '';
            });
        }
    }
    
    /**
     * Set up drag and drop functionality
     * @param {HTMLElement} dropZone - Drop zone element
     * @param {HTMLElement} fileInput - File input element
     * @param {HTMLElement} selectedFileElement - Element to display selected file
     */
    function setupDragAndDrop(dropZone, fileInput, selectedFileElement) {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });
        
        // Highlight drop zone when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });
        
        // Remove highlight when item is dragged out or dropped
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });
        
        // Handle dropped files
        dropZone.addEventListener('drop', function(event) {
            const dt = event.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                // Update file input
                fileInput.files = files;
                
                // Trigger change event
                const changeEvent = new Event('change', { bubbles: true });
                fileInput.dispatchEvent(changeEvent);
            }
        }, false);
        
        function preventDefaults(event) {
            event.preventDefault();
            event.stopPropagation();
        }
        
        function highlight() {
            dropZone.classList.add('highlight');
        }
        
        function unhighlight() {
            dropZone.classList.remove('highlight');
        }
    }
    
    /**
     * Handle form submission
     */
    async function handleSubmit() {
        // Validate form
        if (!teamFileInput.files.length) {
            alert('Please select a team file.');
            return;
        }
        
        if (!opponentFileInput.files.length) {
            alert('Please select an opponent file.');
            return;
        }
        
        // Show processing section
        hideAllSections();
        processingSection.style.display = 'block';
        
        // Create a form element
        const form = document.createElement('form');
        form.style.display = 'none';
        form.method = 'post';
        form.enctype = 'multipart/form-data';
        document.body.appendChild(form);
        
        // Create form data
        const formData = new FormData();
        formData.append('team_files', teamFileInput.files[0]);
        formData.append('opponent_files', opponentFileInput.files[0]);
        formData.append('team_name', teamNameInput.value);
        formData.append('opponent_name', opponentNameInput.value);
        formData.append('use_local_simulation', useLocalSimulation.checked);
        
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
        hideAllSections();
        resultSection.style.display = 'block';
        
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
        
        // Add click event listeners
        downloadBtn.addEventListener('click', function() {
            window.open(downloadUrl, '_blank');
        });
        
        downloadTeamBtn.addEventListener('click', function() {
            window.open(teamDownloadUrl, '_blank');
        });
        
        downloadOpponentBtn.addEventListener('click', function() {
            window.open(opponentDownloadUrl, '_blank');
        });
        
        // Set result message
        const teamName = data.team_name || 'Team';
        const opponentName = data.opponent_name || 'Opponent';
        resultMessage.textContent = `Your analysis for ${teamName} vs ${opponentName} is ready for download!`;
        
        // Reload previous reports
        loadPreviousReports();
    }
    
    /**
     * Show error section
     * @param {string} message - Error message
     */
    function showError(message) {
        hideAllSections();
        errorSection.style.display = 'block';
        
        // Set error message
        errorMessage.textContent = message;
    }
    
    /**
     * Reset form and show upload section
     */
    function resetForm() {
        // Clear form inputs
        teamFileInput.value = '';
        opponentFileInput.value = '';
        teamNameInput.value = '';
        opponentNameInput.value = '';
        useLocalSimulation.checked = false;
        
        // Clear selected files
        teamSelectedFile.innerHTML = '';
        opponentSelectedFile.innerHTML = '';
        
        // Reset task ID
        currentTaskId = null;
        
        // Show upload section and previous reports
        hideAllSections();
        document.querySelector('.upload-container').style.display = 'block';
        previousReportsSection.style.display = 'block';
    }
    
    /**
     * Hide all sections
     */
    function hideAllSections() {
        document.querySelector('.upload-container').style.display = 'none';
        processingSection.style.display = 'none';
        resultSection.style.display = 'none';
        errorSection.style.display = 'none';
    }
    
    /**
     * Load previous reports
     */
    async function loadPreviousReports() {
        try {
            const response = await fetch('/api/analyses');
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            
            // Extract analyses from the HTML
            const analysisCards = doc.querySelectorAll('.analysis-card');
            
            if (analysisCards.length > 0) {
                // Clear reports list
                reportsList.innerHTML = '';
                
                // Add each analysis to the reports list
                analysisCards.forEach(card => {
                    const teamNames = card.querySelector('.team-names').textContent;
                    const timestamp = card.querySelector('.timestamp').textContent;
                    const downloadButtons = card.querySelectorAll('.download-button');
                    
                    const reportItem = document.createElement('div');
                    reportItem.className = 'report-item';
                    
                    const reportInfo = document.createElement('div');
                    reportInfo.className = 'report-info';
                    
                    const reportTitle = document.createElement('div');
                    reportTitle.className = 'report-title';
                    reportTitle.textContent = teamNames;
                    
                    const reportDate = document.createElement('div');
                    reportDate.className = 'report-date';
                    reportDate.textContent = timestamp;
                    
                    reportInfo.appendChild(reportTitle);
                    reportInfo.appendChild(reportDate);
                    
                    const reportActions = document.createElement('div');
                    reportActions.className = 'report-actions';
                    
                    // View Report button
                    const viewButton = document.createElement('button');
                    viewButton.className = 'btn-view';
                    viewButton.textContent = 'View Report';
                    viewButton.addEventListener('click', function() {
                        if (downloadButtons.length > 0) {
                            window.open(downloadButtons[0].href, '_blank');
                        }
                    });
                    
                    // Download Report button
                    const downloadButton = document.createElement('button');
                    downloadButton.className = 'btn-download';
                    downloadButton.innerHTML = `
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-download" viewBox="0 0 16 16">
                            <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/>
                            <path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"/>
                        </svg>
                        Download Report
                    `;
                    downloadButton.addEventListener('click', function() {
                        if (downloadButtons.length > 0) {
                            window.open(downloadButtons[0].href, '_blank');
                        }
                    });
                    
                    reportActions.appendChild(viewButton);
                    reportActions.appendChild(downloadButton);
                    
                    reportItem.appendChild(reportInfo);
                    reportItem.appendChild(reportActions);
                    
                    reportsList.appendChild(reportItem);
                });
            } else {
                // No analyses found
                reportsList.innerHTML = `
                    <div class="no-reports">
                        <p>No previous reports found.</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error loading previous reports:', error);
            reportsList.innerHTML = `
                <div class="no-reports">
                    <p>Error loading previous reports.</p>
                </div>
            `;
        }
    }
});
