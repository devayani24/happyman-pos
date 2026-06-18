import { cart,clearCart,renderCart } from "./cart.js";
import { addSaleToSalesCart,salesCart } from "./sales.js";

// ----- MODULE-LEVEL STATE -----
let payamt = '';        // shared by all functions in this file

export function calculateGrandTotal(){
  let grandTotal = 0;

  cart.forEach((cartItem)=>{
    grandTotal += cartItem.lineTotal
  })

  document.querySelector('.js-grand-total').innerHTML = `₹${grandTotal}`
  return grandTotal
  
}

// ----- INIT: wire the Cash button to open the modal -----
export function setupCashButton() {
    const cashButton = document.querySelector('.js-pay-cash');
    
    cashButton.addEventListener('click', () => {
        if (cart.length === 0) return;
        openCashModal();
    });
}
function openCashModal(){
  const amountDue = calculateGrandTotal();
  document.querySelector('.js-checkout-payment-overlay').innerHTML = buildCashModalHTML(amountDue);

  wireDigitButtons();
  wireClearButton();
  wireBackspaceButton();
  wireDenominationButtons();
  wireTenderButton(amountDue);
  closeCheckOutModal();
}

function openGpayModal(){
  const amountDue = calculateGrandTotal();
  document.querySelector('.js-checkout-payment-overlay').innerHTML = buildGpayModalHTML(amountDue);
  wireGpayConfirm(amountDue);

  closeCheckOutModal();
}



// ----- HTML BUILDER -----
function buildCashModalHTML(amountDue) {
    return `
        <div class="side-header">
            <img class="back-arrow js-cancel-checkout" src="icons/back-arrow2.svg" alt="">
        </div>
        <div class="checkout-payment">
            
            <div class="cash-section cash-amount-due">
                <div class="cash-label">Amount Due</div>
                <div class="cash-amount-due-value js-amount-due">₹${amountDue}</div>
            </div>
            
            <div class="cash-section cash-payment-input">
                <div class="cash-label">Payment Amount</div>
                <div class="cash-payment-display js-payment-display">0</div>
                
                <div class="numpad">
                    <button class="numpad-btn js-digit" data-digit="7">7</button>
                    <button class="numpad-btn js-digit" data-digit="8">8</button>
                    <button class="numpad-btn js-digit" data-digit="9">9</button>
                    <button class="numpad-btn numpad-clear js-clear-button">C</button>
                    
                    <button class="numpad-btn js-digit" data-digit="4">4</button>
                    <button class="numpad-btn js-digit" data-digit="5">5</button>
                    <button class="numpad-btn js-digit" data-digit="6">6</button>
                    <button class="numpad-btn numpad-back js-backspace-button">⌫</button>
                    
                    <button class="numpad-btn js-digit" data-digit="1">1</button>
                    <button class="numpad-btn js-digit" data-digit="2">2</button>
                    <button class="numpad-btn js-digit" data-digit="3">3</button>
                    <button class="numpad-btn numpad-tender js-tender-button">✓</button>
                    
                    <button class="numpad-btn js-digit" data-digit="00">00</button>
                    <button class="numpad-btn js-digit" data-digit="0">0</button>
                    <button class="numpad-btn js-digit" data-digit="000">000</button>
                </div>
                
                <div class="cash-change">
                    <div class="cash-label">Change</div>
                    <div class="cash-change-value js-change">₹0</div>
                </div>
            </div>
            
            <div class="cash-section cash-denominations">
                <div class="cash-label">Denominations</div>
                <div class="denom-grid">
                    <button class="denom-btn js-denom" data-amount="10">₹10</button>
                    <button class="denom-btn js-denom" data-amount="20">₹20</button>
                    <button class="denom-btn js-denom" data-amount="50">₹50</button>
                    <button class="denom-btn js-denom" data-amount="100">₹100</button>
                    <button class="denom-btn js-denom" data-amount="200">₹200</button>
                    <button class="denom-btn js-denom" data-amount="500">₹500</button>
                    <button class="denom-btn js-denom" data-amount="2000">₹2000</button>
                    <button class="denom-btn denom-exact js-denom" data-amount="${amountDue}">EXACT</button>
                </div>
            </div>
        </div>
    `;
}

function buildGpayModalHTML(amountDue) {
    return `
        <div class="side-header">
            <img class="back-arrow js-cancel-checkout" src="icons/back-arrow2.svg" alt="">
        </div>
        <div class="gpay-checkout-payment">
            
        
            <div class="gpay-modal">
                
                <div class="gpay-header">
                    <span class="gpay-icon">📱</span>
                    <span class="gpay-title">UPI / GPay Payment</span>
                </div>
                
                <div class="gpay-body">
                    
                    <div class="gpay-instruction">
                        Customer scans the QR at the counter
                    </div>
                    
                    <div class="gpay-amount-section">
                        <div class="gpay-label">Amount Due</div>
                        <div class="gpay-amount js-gpay-amount">₹${amountDue}</div>
                    </div>
                    
                    <div class="gpay-verify-note">
                        ✓ Confirm only after payment shows in the customer's app
                    </div>
                    
                </div>
                
                <div class="gpay-footer">
                    <button class="gpay-btn gpay-btn--cancel js-cancel-checkout">Cancel</button>
                    <button class="gpay-btn gpay-btn--confirm js-gpay-confirm">
                        Payment Received ✓
                    </button>
                </div>
                
            </div>
        </div>
    `;
}

// ----- BUTTON WIRING -----
function wireDigitButtons() {
    document.querySelectorAll('.js-digit').forEach((digit) => {
        digit.addEventListener('click', () => {
            payamt += digit.dataset.digit;       // append to the SHARED variable
            updatePaymentDisplay();
            updateChangeDisplay(calculateGrandTotal());
        });
    });
}

function wireClearButton() {
    document.querySelector('.js-clear-button').addEventListener('click', () => {
        payamt = '';                              // reset SHARED variable
        updatePaymentDisplay();
        updateChangeDisplay(calculateGrandTotal());
    });
}

function wireBackspaceButton() {
    document.querySelector('.js-backspace-button').addEventListener('click', () => {
        payamt = payamt.slice(0, -1);            // remove last character
        updatePaymentDisplay();
        updateChangeDisplay(calculateGrandTotal());
    });
}

function wireDenominationButtons() {
    document.querySelectorAll('.js-denom').forEach((denom) => {
        denom.addEventListener('click', () => {
            payamt = denom.dataset.amount;
            updatePaymentDisplay();
            updateChangeDisplay(calculateGrandTotal());
        });
    });
}

function wireTenderButton(amountDue) {
    
    document.querySelector('.js-tender-button').addEventListener('click', async () => {
        
        const payment = parseFloat(payamt) || 0;
        if (payment < amountDue) {
            alert('Payment is less than amount due');
            return;
        }
        
         
        const bill =  await addSaleToSalesCart(amountDue,'cash',payment,payment-amountDue)
        
        payamt = '';
        
        document.querySelector('.js-checkout-payment-overlay').innerHTML = '';
        
        clearCart();
        renderCart();
        
        openChangeModal(bill,amountDue,payment);
        
        
        
        
    });
}

// ----- UI UPDATERS -----

function updatePaymentDisplay() {
    document.querySelector('.js-payment-display').innerHTML = payamt || '0';
}

function updateChangeDisplay(amountDue){
  const payment = parseFloat(payamt) || 0;
  const change = payment - amountDue;
  const display = change >= 0 ? `₹${change}` : `−₹${Math.abs(change)}`;
  document.querySelector('.js-change').innerHTML = display;
}

function closeCheckOutModal(){
  document.querySelectorAll('.js-cancel-checkout').forEach((element) => {
        element.addEventListener('click', () => {
            document.querySelector('.js-checkout-payment-overlay').innerHTML = '';
        });
    });
}


function buildChangeModalHTML(billNumber,amountDue,payment){
  return`
  <div class="change-modal-overlay">
    <div class="change-modal">
        
      <div class="change-modal__header">
          <div class="change-modal__title">Sale Complete</div>
          <div class="change-modal__subtitle">Bill #${billNumber}</div>
      </div>
      
      <div class="change-modal__body">
          
          <div class="change-modal__row">
              <span class="change-modal__label">Amount Due</span>
              <span class="change-modal__value js-amount-due">₹${amountDue}</span>
          </div>
          
          <div class="change-modal__row">
              <span class="change-modal__label">Payment Received</span>
              <span class="change-modal__value js-payment-received">₹${payment}</span>
          </div>
          
          <div class="change-modal__divider"></div>
          
          <div class="change-modal__row change-modal__row--highlight">
              <span class="change-modal__label-large">Change to Give</span>
              <span class="change-modal__value-large js-change-due">₹${payment-amountDue}</span>
          </div>
          
      </div>
      
      <div class="change-modal__footer">
          <button class="change-modal__btn change-modal__btn--secondary js-change-close">Close</button>
          <button class="change-modal__btn change-modal__btn--primary js-change-print">🖨 Print Receipt</button>
      </div>
        
    </div>
  </div>`
}

function openChangeModal(billNumber,amountDue,payment) {
  
    document.querySelector('.js-change-modal-overlay').innerHTML = buildChangeModalHTML(billNumber,amountDue,payment);
  
  closeChangeModal();
 
}

function closeChangeModal(){
  document.querySelector('.js-change-close').addEventListener('click',()=>{
    console.log('CLOSE BUTTON CLICKED — closing modal');
    document.querySelector('.js-change-modal-overlay').innerHTML = '';
  })
}

export function setupGpayButton() {
    document.querySelector('.js-pay-gpay').addEventListener('click', () => {
        if (cart.length === 0) return;
        openGpayModal();
    });
}

function wireGpayConfirm(amountDue) {
    document.querySelector('.js-gpay-confirm').addEventListener('click',async () => {
        // GPay: payment received = amount due, change = 0
        const billNumber = await addSaleToSalesCart(amountDue, 'gpay', amountDue, 0);
        console.log(salesCart)
        document.querySelector('.js-checkout-payment-overlay').innerHTML = '';
        clearCart();
        renderCart();
  
        openChangeModal(billNumber,amountDue, amountDue);   // change modal shows ₹0 change
    });
}

