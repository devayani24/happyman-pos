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
  const banner = document.getElementById('offlineWarning');
  const cashBtn = document.querySelector('.js-pay-cash');
  const gpayBtn = document.querySelector('.js-pay-gpay');
  const gpayTenderBtn = document.querySelector('.js-gpay-confirm');
  const cashTenderBtn = document.querySelector('.js-tender-button');

  // Remove all status classes
  dot.classList.remove('connected', 'disconnected');

  if (status === 'connected'){
    // Update indicator
    dot.classList.add('connected');
    text.textContent = 'Connected';

    // Enable payment buttons
    cashBtn.disabled = false;
    gpayBtn.disabled = false;
    if (gpayTenderBtn) gpayTenderBtn.disabled = false;
    if (cashTenderBtn) cashTenderBtn.disabled = false;
    // Hide banner
    banner.style.display = 'none';
  }else if (status === 'disconnected'){
    // Update indicator
    dot.classList.add('disconnected');
    text.textContent = 'Disconnected';

    // Disable payment buttons
    cashBtn.disabled = true;
    gpayBtn.disabled = true;
    if (gpayTenderBtn) gpayTenderBtn.disabled = true;
    if (cashTenderBtn) cashTenderBtn.disabled = true;
    // Show banner
    banner.style.display = 'block';
  }
}


export function setupStatusIndicator() {
    // Check immediately on load
    checkBackendHealth();
    const timeoutId = setInterval(checkBackendHealth, 5000);
    
  
}