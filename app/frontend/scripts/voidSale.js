import { SHOP_ID } from "./config.js";

// Module-level state — shared across functions
let currentBillNumber = null;
let selectedReason = null;

function openVoidModal(billNumber) {
    currentBillNumber = billNumber;
    selectedReason = null;
    
    // Update bill number display
    document.querySelector('.js-void-bill-number').textContent = 
        `Bill #${SHOP_ID}-${billNumber}`;
    
    // Reset all reason buttons
    document.querySelectorAll('.js-void-reason').forEach(btn => {
        btn.classList.remove('selected');
    });
    
    // Disable confirm button
    document.querySelector('.js-void-confirm').disabled = true;
    
    // Show modal
    document.querySelector('.js-void-modal').style.display = 'flex';
}

export function setupVoidSale(){
    document.querySelector('.js-cancel-sale').addEventListener('click',()=>{
        const selectedRow = document.querySelector('.transaction-row.selected');
        if (!selectedRow) {
            alert('Please select a transaction first');
            return;
        }
        
        const billNumber = parseInt(selectedRow.dataset.billNumber);
        console.log(billNumber)
        openVoidModal(billNumber);
        
    })
    closeVoidSale();
    
}

function closeVoidSale(){
    document.querySelector('.js-void-close').addEventListener('click',()=>{
        document.querySelector('.js-void-modal').style.display = "none"
    })
}