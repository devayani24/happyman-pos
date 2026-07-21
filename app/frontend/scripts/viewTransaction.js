import { closeSideHeader } from "./pop-up-modal/sideHeader.js";
import { API_BASE } from "./config.js";
import { formatTime } from "./utils.js";

const MODAL_ID = 'transactionHistoryModal';
const VISIBLE_CLASS = 'visible';
let salesLists = []


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
      <div class="transaction-row js-transaction-row ${isFirst ? 'selected' : ''}" data-bill-number =${sale.bill_number}>
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
        row.addEventListener('click', async () => {
            
            let billNumber = row.dataset.billNumber
            let items = await loadSalesItems(billNumber)
            generateSaleItemsList(items,billNumber)
            
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

async function loadSalesItems(billNumber) {
  let saleItemsLists = []
    try {
        const response = await fetch(`${API_BASE}/api/sales/${billNumber}/items`);
        if (!response.ok) {
            throw new Error(`Failed to load sale items: ${response.status}`);
        }
        saleItemsLists = await response.json()
        return saleItemsLists ;
    } catch (error) {
        console.error('Error loading sale items:', error);
        return saleItemsLists;
    }
} 

function generateSaleItemsList(items,billNumber){

  // Update details header
  const sale = salesLists.find(s => s.bill_number === parseInt(billNumber));
  
  updateDetailsHeader(sale);

  let html = '';

  items.forEach((item, index)=>{
    const isFirst = index === 0;

    html += 
      `
      <div class="detail-row">
          <div class="col-item-id">${index+1}</div>
          <div class="col-item-name">${item.product_local_name}(${item.product_name})</div>
          <div class="col-quantity">${item.cart_weight || item.cart_pieces}${item.cart_unit} * ${item.cart_packets}</div>
          <div class="col-price">₹${item.line_total}</div>
      </div>
      `
  })
  document.querySelector('.js-details-list').innerHTML = html;
}

function updateDetailsHeader(sale){


  const html = 
    `
    <span class="details-bill">Bill #${sale.bill_number}</span>
    <span class="details-separator">•</span>
    <span class="details-total">₹${sale.total_price}</span>
    `
  document.querySelector('.js-details-meta').innerHTML = html;
 
}