import { SHOP_ID, API_BASE } from "./config.js";
import { refreshTransactionList } from "./viewTransaction.js";

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

function closeVoidModal() {
    document.querySelector('.js-void-modal').style.display = 'none';
    currentBillNumber = null;
    selectedReason = null;
}

function selectReason(button) {
    // Deselect all
    document.querySelectorAll('.js-void-reason').forEach(btn => {
        btn.classList.remove('selected');
    });
    
    // Select this one
    button.classList.add('selected');
    selectedReason = button.dataset.reason;
    
    // Enable confirm button
    document.querySelector('.js-void-confirm').disabled = false;
}

async function confirmVoid() {
    if (!currentBillNumber || !selectedReason) {
        return;
    }
    
    const confirmBtn = document.querySelector('.js-void-confirm');
    const originalText = confirmBtn.textContent;
    
    try {
        // Show loading state
        confirmBtn.disabled = true;
        confirmBtn.textContent = 'Cancelling...';
        
        // Send void request
        const response = await fetch(
            `${API_BASE}/api/sales/${currentBillNumber}/${selectedReason}/void`,
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ reason: selectedReason })
            }
        );
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to cancel sale');
        }
        
        const result = await response.json();
        
        // Success — close modal and refresh transaction list
        alert(`Sale #${currentBillNumber} has been cancelled successfully.`);
        closeVoidModal();
        // Refresh the transaction history
        await refreshTransactionList();
        
       
    } catch (error) {
        alert(`Error: ${error.message}`);
        confirmBtn.disabled = false;
        confirmBtn.textContent = originalText;
    }
}


export function setupVoidSale(){
    // Reason button clicks
    document.querySelectorAll('.js-void-reason').forEach(btn => {
        btn.addEventListener('click', () => selectReason(btn));
    });

    // Close button
    document.querySelector('.js-void-close').addEventListener('click', closeVoidModal);

    // Confirm button
    document.querySelector('.js-void-confirm').addEventListener('click', confirmVoid);

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
}

