import { API_BASE } from "./config.js";

async function exportReport(){
    console.log("Button clicked");
    
    const response = await fetch(`${API_BASE}/api/export-report`);
    console.log("Got response:", response);
    
    const data = await response.json();
    console.log("Data:", data);
    
    alert(data.message);
  }

export function setupExportReport(){
  document.querySelector('.js-export-report').addEventListener('click',exportReport)

  
}