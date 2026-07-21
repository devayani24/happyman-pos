import { closeSideHeader } from "./pop-up-modal/sideHeader.js";
import { API_BASE } from "./config.js";
import { formatTime } from "./utils.js";

const MODAL_ID = 'transactionHistoryModal';
const VISIBLE_CLASS = 'visible';
let salesLists = []
let salesItemsLists = []

async function openTransactionModal() {

    closeSideHeader();
    await loadSalesList()
    document.querySelector('.js-transaction-list').innerHTML = generateSalesListHTML();
    
    document.getElementById(MODAL_ID).classList.add(VISIBLE_CLASS);
    setupTransactionRowClicks();
}

function closeTransactionModal() {
    document.getElementById(MODAL_ID).classList.remove(VISIBLE_CLASS);
}

function setupCloseHandlers() {
    const closeSelectors = [
        '.js-transaction-back-arrow',
        '.js-close-transaction-modal'
    ];
    
    closeSelectors.forEach(selector => {
        const button = document.querySelector(selector);
        if (button) {
            button.addEventListener('click', closeTransactionModal);
        }
    });
}

function setupOpenHandler() {
    
    document.querySelector('.js-view-history-icon')
        .addEventListener('click', openTransactionModal);
}

export function renderViewTransaction() {
    
    setupOpenHandler();
    
    setupCloseHandlers();
    
}

async function loadSalesList() {
    try {
        const response = await fetch(`${API_BASE}/api/show-sales`);
        if (!response.ok) {
            throw new Error(`Failed to load sales: ${response.status}`);
        }
        salesLists = await response.json();
    } catch (error) {
        console.error('Error loading sales:', error);
        salesLists = [];
    }
}

function generateSalesListHTML(){
  let html = '';

  salesLists.forEach((sale, index)=>{
    const isFirst = index === 0;

    html += 
      `
      <div class="transaction-row js-transaction-row ${isFirst ? 'selected' : ''}" data-bill-number = ${isFirst ? `${sale.bill_number}` : ''}>
        <div class="col-checkbox">
            <input type="checkbox" ${isFirst ? 'checked' : ''}>
        </div>
        <div class="col-date">
            <div class="date-main">${sale.date} ${formatTime(sale.time)}</div>
            <div class="date-sub">Bill #${sale.bill_number}</div>
        </div>
        <div class="col-type">${sale.payment_mode}</div>
        <div class="col-receipt">${sale.transaction_type}</div>
        <div class="col-total">₹${sale.total_price}</div>
    </div>
      `
  })

  return html
}

function setupTransactionRowClicks() {
    document.querySelectorAll('.transaction-row').forEach(row => {
        row.addEventListener('click', () => {
            console.log('clicked');
            
            // Step 1: Deselect ALL rows (remove selected class and uncheck)
            document.querySelectorAll('.transaction-row').forEach(r => {
                r.classList.remove('selected');
                const checkbox = r.querySelector('input[type="checkbox"]');
                if (checkbox) checkbox.checked = false;
            });
            
            // Step 2: Select THIS row (add selected class and check)
            row.classList.add('selected');
            const clickedCheckbox = row.querySelector('input[type="checkbox"]');
            if (clickedCheckbox) clickedCheckbox.checked = true;
        });
    });
}