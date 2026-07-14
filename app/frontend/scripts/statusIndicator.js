import { API_BASE } from "./config.js";

async function checkBackendHealth() {
    // Set up abort mechanism with 3-second timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000);
    
    try {
        console.log("Checking backend health");
        const response = await fetch(`${API_BASE}/api/health`, {
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        
        if (response.ok) {
            updateStatus('connected');
        } else {
            updateStatus('disconnected');
        }
    } catch (error) {
        console.log('Backend check failed:', error.name);
        updateStatus('disconnected');
    }
}


function updateStatus(status){
  const dot = document.getElementById('statusDot');
  const text = document.getElementById('statusText');

  // Remove all status classes
  dot.classList.remove('connected', 'disconnected');

  if (status === 'connected'){
    dot.classList.add('connected');
    text.textContent = 'Connected'
  }else if (status === 'disconnected'){
    dot.classList.add('disconnected');
    text.textContent = 'Disconnected'
  }
}


export function setupStatusIndicator() {
    // Check immediately on load
    checkBackendHealth();
    const timeoutId = setInterval(checkBackendHealth, 5000);
    
  
}