import { API_BASE } from "./config.js";

async function exportReport(){
    console.log("Button clicked");
    
    // Step 1: Call backend
    const response = await fetch(`${API_BASE}/api/export-report`);
    
    // Step 2: Get the file as a Blob
    const blob = await response.blob();
    console.log("Got blob:", blob);
    
    // Step 3: Create a temporary URL for the blob
    const url = URL.createObjectURL(blob);
    
    // Step 4: Create a temporary link and click it (triggers download)
    const link = document.createElement('a');
    link.href = url;
    link.download = 'HappyMan_Report.xlsx';  // filename
    link.click();
    
    // Step 5: Clean up the temporary URL
    URL.revokeObjectURL(url);
    
    console.log("Download triggered");
  }

export function setupExportReport(){
  document.querySelector('.js-export-report').addEventListener('click',exportReport)

  
}