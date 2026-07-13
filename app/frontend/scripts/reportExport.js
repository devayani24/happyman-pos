import { API_BASE } from "./config.js";

// Helper: show the "downloading" state
function showDownloadingState() {
    document.getElementById('exportModal').style.display = 'block';
    document.getElementById('downloadingState').style.display = 'block';
    document.getElementById('downloadedState').style.display = 'none';
}

// Helper: show the "downloaded" state
function showDownloadedState(filename) {
    document.getElementById('downloadingState').style.display = 'none';
    document.getElementById('downloadedState').style.display = 'block';
    document.querySelector('.js-filename').textContent = filename;
}

// Helper: close the modal completely
function closeModal() {
    document.getElementById('exportModal').style.display = 'none';
}

async function exportReport() {
    console.log("Button clicked");
    
    // Step 1: Show modal in "downloading" state
    showDownloadingState();
    
    try {
        // Step 2: Call backend
        const response = await fetch(`${API_BASE}/api/export-report`);
        
        // Step 3: Get file as blob
        const blob = await response.blob();
        console.log("Got blob:", blob);
        
        // Step 4: Trigger download
        const filename = 'HappyMan_Report.xlsx';
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.click();
        URL.revokeObjectURL(url);
        
        // Step 5: Update modal to "downloaded" state
        showDownloadedState(filename);
        
    } catch (error) {
        console.error('Export failed:', error);
        closeModal();
        alert('Export failed. Please try again.');
    }
}

export function setupExportReport() {
    document.querySelector('.js-export-report').addEventListener('click', exportReport);
    document.querySelector('.js-export-close-button').addEventListener('click', closeModal);
}