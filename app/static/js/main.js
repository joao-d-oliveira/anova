document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');
    
    // Function to check if all required DOM elements are present
    function checkRequiredElements() {
        const requiredElements = {
            // Upload form elements
            'team_files': document.getElementById('team_files'),
            'opponent_files': document.getElementById('opponent_files'),
            'team-upload-btn': document.getElementById('team-upload-btn'),
            'opponent-upload-btn': document.getElementById('opponent-upload-btn'),
            'team-upload-box': document.getElementById('team-upload-box'),
            'opponent-upload-box': document.getElementById('opponent-upload-box'),
            'team-selected-file': document.getElementById('team-selected-file'),
            'opponent-selected-file': document.getElementById('opponent-selected-file'),
            'submit-btn': document.getElementById('submit-btn'),
            'use_local_simulation': document.getElementById('use_local_simulation'),
            'team_name': document.getElementById('team_name'),
            'opponent_name': document.getElementById('opponent_name'),
            
            // Sections
            'processing-section': document.getElementById('processing-section'),
            'result-section': document.getElementById('result-section'),
            'error-section': document.getElementById('error-section'),
            'previous-reports-section': document.getElementById('previous-reports-section'),
            'reports-list': document.getElementById('reports-list'),
            
            // Messages and buttons
            'processing-message': document.getElementById('processing-message'),
            'result-message': document.getElementById('result-message'),
            'error-message': document.getElementById('error-message'),
            'download-button': document.getElementById('download-button'),
            'download-team-button': document.getElementById('download-team-button'),
            'download-opponent-button': document.getElementById('download-opponent-button'),
            'new-analysis-button': document.getElementById('new-analysis-button'),
            'try-again-button': document.getElementById('try-again-button')
        };
        
        let allPresent = true;
        for (const [name, element] of Object.entries(requiredElements)) {
            if (!element) {
                console.error(`Required element not found: ${name}`);
                allPresent = false;
            }
        }
        
        return allPresent;
    }
    
    // Check if all required elements are present
    const allElementsPresent = checkRequiredElements();
    if (!allElementsPresent) {
        console.error('Some required elements are missing. The application may not function correctly.');
    }
    
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
    if (downloadButton) {
        downloadButton.addEventListener('click', function() {
            if (currentTaskId) {
                // Get root path from a meta tag that we'll add to the templates
                const rootPath = document.querySelector('meta[name="root-path"]')?.getAttribute('content') || '';
                window.location.href = `${rootPath}/api/download/${currentTaskId}`;
            }
        });
    }
    
    if (downloadTeamButton) {
        downloadTeamButton.addEventListener('click', function() {
            if (currentTaskId) {
                const rootPath = document.querySelector('meta[name="root-path"]')?.getAttribute('content') || '';
                window.location.href = `${rootPath}/api/download-team-analysis/${currentTaskId}`;
            }
        });
    }
    
    if (downloadOpponentButton) {
        downloadOpponentButton.addEventListener('click', function() {
            if (currentTaskId) {
                const rootPath = document.querySelector('meta[name="root-path"]')?.getAttribute('content') || '';
                window.location.href = `${rootPath}/api/download-opponent-analysis/${currentTaskId}`;
            }
        });
    }
    
    newAnalysisButton.addEventListener('click', resetForm);
    tryAgainButton.addEventListener('click', resetForm);
    
    // Add event listener for start again button
    const startAgainBtn = document.getElementById('start-again-btn');
    if (startAgainBtn) {
        startAgainBtn.addEventListener('click', function() {
            const rootPath = document.querySelector('meta[name="root-path"]')?.getAttribute('content') || '';
            window.location.href = `${rootPath}/app`;
        });
    }
    
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
        console.log('Submit button clicked');
        
        // Validate form
        if (!teamFileInput || !teamFileInput.files || !teamFileInput.files.length) {
            alert('Please select a team file.');
            return;
        }
        
        if (!opponentFileInput || !opponentFileInput.files || !opponentFileInput.files.length) {
            alert('Please select an opponent file.');
            return;
        }
        
        try {
            console.log('Form validation passed, proceeding with submission');
            
            // Show processing section - with null checks
            hideAllSections();
            if (processingSection) {
                processingSection.style.display = 'block';
                console.log('Processing section displayed');
            } else {
                console.error('Processing section element not found');
            }
            
            // Set initial message - with null check
            if (processingMessage) {
                processingMessage.textContent = 'Uploading files...';
                console.log('Processing message updated');
            } else {
                console.error('Processing message element not found');
            }
            
            // Create form data directly - no need for an extra form element
            const formData = new FormData();
            
            console.log('Team file:', teamFileInput.files[0].name, 'size:', teamFileInput.files[0].size);
            console.log('Opponent file:', opponentFileInput.files[0].name, 'size:', opponentFileInput.files[0].size);
            
            formData.append('team_files', teamFileInput.files[0]);
            formData.append('opponent_files', opponentFileInput.files[0]);
            
            if (teamNameInput) {
                formData.append('team_name', teamNameInput.value);
                console.log('Team name added:', teamNameInput.value);
            }
            
            if (opponentNameInput) {
                formData.append('opponent_name', opponentNameInput.value);
                console.log('Opponent name added:', opponentNameInput.value);
            }
            
            if (useLocalSimulation) {
                formData.append('use_local_simulation', useLocalSimulation.checked);
                console.log('Use local simulation added:', useLocalSimulation.checked);
            }
            
            console.log('FormData created, sending request to /api/upload/');
            
            // Log FormData contents for debugging
            console.log('FormData contents:');
            for (let pair of formData.entries()) {
                console.log(pair[0] + ': ' + (pair[1] instanceof File ? pair[1].name : pair[1]));
            }
            
            // Upload files with credentials and proper headers
            const rootPath = document.querySelector('meta[name="root-path"]')?.getAttribute('content') || '';
            const response = await fetch(`${rootPath}/api/upload/`, {
                method: 'POST',
                body: formData,
                credentials: 'same-origin',
                headers: {
                    // Don't set Content-Type header when using FormData
                    // The browser will set it automatically with the correct boundary
                    'Accept': 'application/json'
                }
            });
            
            console.log('Response received:', response.status, response.statusText);
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Response data:', data);
            
            currentTaskId = data.task_id;
            console.log('Task ID received:', currentTaskId);
            
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
            console.error('No task ID available for status check');
            return;
        }
        
        try {
            console.log('Checking status for task:', currentTaskId);
            const rootPath = document.querySelector('meta[name="root-path"]')?.getAttribute('content') || '';
            const response = await fetch(`${rootPath}/api/status/${currentTaskId}`, {
                method: 'GET',
                credentials: 'same-origin',
                headers: {
                    'Accept': 'application/json'
                }
            });
            
            console.log('Status response received:', response.status, response.statusText);
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Status data:', data);
            
            if (data.status === 'processing') {
                // Update processing message if we have step information
                if (processingMessage) {
                    if (data.step_description) {
                        processingMessage.textContent = `${data.step_description} (Step ${data.current_step + 1} of ${data.total_steps})`;
                        console.log('Updated processing message with step info');
                    } else {
                        processingMessage.textContent = 'Your files are being processed. This may take a few minutes...';
                        console.log('Updated processing message with generic info');
                    }
                } else {
                    console.error('Processing message element not found');
                }
                
                // Check again in 2 seconds
                console.log('Scheduling next status check in 2 seconds');
                setTimeout(checkStatus, 2000);
            } else if (data.status === 'completed') {
                // Processing completed
                console.log('Processing completed, showing result');
                showResult(data);
            } else if (data.status === 'failed') {
                // Processing failed
                console.error('Processing failed:', data.error);
                showError(data.error || 'An error occurred during processing.');
            } else {
                console.warn('Unknown status received:', data.status);
            }
        } catch (error) {
            console.error('Error checking status:', error);
            showError('An error occurred while checking processing status.');
        }
    }
    
    /**
     * Show result section or redirect to report view
     * @param {Object} data - Result data
     */
    function showResult(data) {
        // Get the report ID from the data
        const reportId = data.report_id || currentTaskId;
        
        console.log('Redirecting to report view with ID:', reportId);
        
        // Redirect to the report view page
        const rootPath = document.querySelector('meta[name="root-path"]')?.getAttribute('content') || '';
        window.location.href = `${rootPath}/report/${reportId}`;
    }
    
    /**
     * Show error section
     * @param {string} message - Error message
     */
    function showError(message) {
        console.error('Error occurred:', message);
        
        try {
            hideAllSections();
            
            // Check if error section exists before trying to display it
            if (errorSection) {
                errorSection.style.display = 'block';
                console.log('Error section displayed');
                
                // Set error message if element exists
                if (errorMessage) {
                    errorMessage.textContent = message;
                    console.log('Error message set');
                } else {
                    console.error('Error message element not found');
                }
            } else {
                console.error('Error section element not found');
                // Fallback to alert if error section doesn't exist
                alert('Error: ' + message);
            }
        } catch (error) {
            console.error('Error in showError function:', error);
            // Fallback to alert if there's an error
            alert('Error: ' + message);
        }
    }
    
    /**
     * Reset form and show upload section
     */
    function resetForm() {
        console.log('Resetting form');
        
        try {
            // Clear form inputs with null checks
            if (teamFileInput) {
                teamFileInput.value = '';
                console.log('Team file input cleared');
            }
            
            if (opponentFileInput) {
                opponentFileInput.value = '';
                console.log('Opponent file input cleared');
            }
            
            if (teamNameInput) {
                teamNameInput.value = '';
                console.log('Team name input cleared');
            }
            
            if (opponentNameInput) {
                opponentNameInput.value = '';
                console.log('Opponent name input cleared');
            }
            
            if (useLocalSimulation) {
                useLocalSimulation.checked = false;
                console.log('Use local simulation checkbox unchecked');
            }
            
            // Clear selected files with null checks
            if (teamSelectedFile) {
                teamSelectedFile.innerHTML = '';
                console.log('Team selected file cleared');
            }
            
            if (opponentSelectedFile) {
                opponentSelectedFile.innerHTML = '';
                console.log('Opponent selected file cleared');
            }
            
            // Reset task ID
            currentTaskId = null;
            console.log('Task ID reset');
            
            // Show upload section and previous reports
            hideAllSections();
            
            const uploadContainer = document.querySelector('.upload-container');
            if (uploadContainer) {
                uploadContainer.style.display = 'block';
                console.log('Upload container displayed');
            } else {
                console.error('Upload container element not found');
            }
            
            if (previousReportsSection) {
                previousReportsSection.style.display = 'block';
                console.log('Previous reports section displayed');
            } else {
                console.error('Previous reports section element not found');
            }
        } catch (error) {
            console.error('Error in resetForm function:', error);
        }
    }
    
    /**
     * Hide all sections
     */
    function hideAllSections() {
        try {
            console.log('Hiding all sections');
            
            // Check if elements exist before trying to access their style property
            const uploadContainer = document.querySelector('.upload-container');
            console.log('Upload container found:', !!uploadContainer);
            if (uploadContainer) {
                uploadContainer.style.display = 'none';
            }
            
            console.log('Processing section found:', !!processingSection);
            if (processingSection) {
                processingSection.style.display = 'none';
            }
            
            console.log('Result section found:', !!resultSection);
            if (resultSection) {
                resultSection.style.display = 'none';
            }
            
            console.log('Error section found:', !!errorSection);
            if (errorSection) {
                errorSection.style.display = 'none';
            }
            
            console.log('Previous reports section found:', !!previousReportsSection);
            if (previousReportsSection) {
                previousReportsSection.style.display = 'none';
            }
        } catch (error) {
            console.error('Error hiding sections:', error);
        }
    }
    
    /**
     * Load previous reports
     */
    async function loadPreviousReports() {
        try {
            console.log('Loading previous reports');
            const rootPath = document.querySelector('meta[name="root-path"]')?.getAttribute('content') || '';
            const response = await fetch(`${rootPath}/api/analyses`, {
                method: 'GET',
                credentials: 'same-origin',
                headers: {
                    'Accept': 'text/html'
                }
            });
            
            console.log('Previous reports response:', response.status, response.statusText);
            
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
                    
                    // Get report ID from the card
                    const reportId = card.getAttribute('data-report-id');
                    
                    // View Report button
                    const viewButton = document.createElement('button');
                    viewButton.className = 'btn-view';
                    viewButton.textContent = 'View Report';
                    viewButton.addEventListener('click', function() {
                        const rootPath = document.querySelector('meta[name="root-path"]')?.getAttribute('content') || '';
                        window.location.href = `${rootPath}/report/${reportId}`;
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
                        const rootPath = document.querySelector('meta[name="root-path"]')?.getAttribute('content') || '';
                        window.location.href = `${rootPath}/api/download/${reportId}`;
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
