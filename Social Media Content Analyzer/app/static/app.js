/**
 * Social Media Content Analyzer - Frontend JavaScript
 * Handles file upload, drag-drop, and UI interactions
 */

// DOM Elements
const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const loadingSpinner = document.getElementById('loadingSpinner');
const resultsSection = document.getElementById('resultsSection');
const errorMessage = document.getElementById('errorMessage');
const extractedTextDiv = document.getElementById('extractedText');
const suggestionsListDiv = document.getElementById('suggestionsList');
const fileNameSpan = document.getElementById('fileName');
const textStatsSpan = document.getElementById('textStats');

// Button Elements
const copyBtn = document.getElementById('copyBtn');
const newFileBtn = document.getElementById('newFileBtn');
const downloadBtn = document.getElementById('downloadBtn');

// State
let currentExtractedText = '';
let currentFileName = '';

// ============================================================================
// Event Listeners - File Upload
// ============================================================================

/**
 * Upload zone click handler
 */
uploadZone.addEventListener('click', () => {
    fileInput.click();
});

/**
 * File input change handler
 */
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        handleFileUpload(file);
    }
});

/**
 * Drag and drop handlers
 */
uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    e.stopPropagation();
    uploadZone.classList.add('dragover');
});

uploadZone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    e.stopPropagation();
    uploadZone.classList.remove('dragover');
});

uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    e.stopPropagation();
    uploadZone.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        handleFileUpload(file);
    }
});

// ============================================================================
// Event Listeners - Action Buttons
// ============================================================================

copyBtn.addEventListener('click', () => {
    if (currentExtractedText) {
        navigator.clipboard.writeText(currentExtractedText).then(() => {
            showNotification('✅ Text copied to clipboard!', 'success');
        }).catch(() => {
            showNotification('❌ Failed to copy text', 'error');
        });
    }
});

newFileBtn.addEventListener('click', () => {
    resetUI();
});

downloadBtn.addEventListener('click', () => {
    downloadResults();
});

// ============================================================================
// File Upload Handler
// ============================================================================

/**
 * Handle file upload and send to backend
 */
async function handleFileUpload(file) {
    // Validate file type
    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/tiff'];
    if (!allowedTypes.includes(file.type)) {
        showError('❌ Invalid file type. Please upload a PDF or image file.');
        return;
    }
    
    // Validate file size (50MB)
    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
        showError('❌ File too large. Maximum size is 50MB.');
        return;
    }
    
    currentFileName = file.name;
    
    // Show loading state
    hideError();
    resultsSection.style.display = 'none';
    loadingSpinner.style.display = 'block';
    uploadZone.style.opacity = '0.5';
    uploadZone.style.pointerEvents = 'none';
    
    try {
        // Create FormData and send to backend
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/extract', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to extract text');
        }
        
        // Handle successful extraction
        handleExtractionSuccess(data);
        
    } catch (error) {
        showError(`❌ Error: ${error.message}`);
    } finally {
        // Hide loading state
        loadingSpinner.style.display = 'none';
        uploadZone.style.opacity = '1';
        uploadZone.style.pointerEvents = 'auto';
    }
}

/**
 * Handle successful text extraction
 */
function handleExtractionSuccess(data) {
    currentExtractedText = data.extracted_text;
    
    // Update file info
    fileNameSpan.textContent = `📄 ${data.filename}`;
    textStatsSpan.textContent = `${data.word_count} words • ${data.text_length} characters`;
    
    // Display extracted text
    displayExtractedText(data.extracted_text);
    
    // Display suggestions
    displaySuggestions(data.suggestions);
    
    // Show results section
    resultsSection.style.display = 'block';
    
    // Smooth scroll to results
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

// ============================================================================
// Display Functions
// ============================================================================

/**
 * Display extracted text in results section
 */
function displayExtractedText(text) {
    // Escape HTML and preserve line breaks
    const escapedText = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .split('\n')
        .map(line => `<p>${line}</p>`)
        .join('');
    
    extractedTextDiv.innerHTML = escapedText;
}

/**
 * Display engagement suggestions
 */
function displaySuggestions(suggestions) {
    suggestionsListDiv.innerHTML = '';
    
    suggestions.forEach((suggestion, index) => {
        const suggestionEl = document.createElement('div');
        suggestionEl.className = 'suggestion-item';
        suggestionEl.innerHTML = suggestion;
        suggestionEl.style.animationDelay = `${index * 0.1}s`;
        suggestionsListDiv.appendChild(suggestionEl);
    });
}

/**
 * Show error message
 */
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

/**
 * Hide error message
 */
function hideError() {
    errorMessage.style.display = 'none';
    errorMessage.textContent = '';
}

/**
 * Show notification toast
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// ============================================================================
// Download & Reset Functions
// ============================================================================

/**
 * Download results as text file
 */
function downloadResults() {
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(currentExtractedText));
    element.setAttribute('download', `${currentFileName}_extracted.txt`);
    element.style.display = 'none';
    
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    
    showNotification('📥 Results downloaded!', 'success');
}

/**
 * Reset UI for new upload
 */
function resetUI() {
    fileInput.value = '';
    fileNameSpan.textContent = '';
    textStatsSpan.textContent = '';
    extractedTextDiv.innerHTML = '';
    suggestionsListDiv.innerHTML = '';
    resultsSection.style.display = 'none';
    hideError();
    currentExtractedText = '';
    currentFileName = '';
    
    // Scroll to top
    uploadZone.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ============================================================================
// Initialize
// ============================================================================

console.log('✅ Social Media Content Analyzer loaded');
