import { loadCategories } from "../data/categories.js";
import { loadProducts,generateTapToAddMenuGrid } from "../data/products.js";
import { renderCart,setupClearButton } from "./cart.js";
import { calculateGrandTotal,setupCashButton,setupGpayButton } from "./checkout.js";
import { cartActionMenu } from "./cart-actions/cartActionMenu.js";
import { renderPopUpModal } from "./pop-up-modal/pop-up-modal.js";
import { cart } from "./cart.js";
import { setupExportReport } from "./reportExport.js";
import { setupStatusIndicator } from "./statusIndicator.js";
import { renderSideHeader } from "./pop-up-modal/sideHeader.js";
import { renderViewTransaction } from "./viewTransaction.js";

async function init() {
  setupStatusIndicator()
    // Load both in parallel for speed
    await Promise.all([
        loadCategories(),
        loadProducts()
    ]);
    
    // Now render UI
    
    generateTapToAddMenuGrid(1);
    renderSideHeader();
    renderPopUpModal('.js-menu-box')
    setupClearButton();
    renderCart();
    setupCashButton();
    setupGpayButton();
    setupExportReport();
    renderViewTransaction();
}

init();

CurrentDateTime();





console.log(window.location.hostname)

function CurrentDateTime(){
  const date = new Date();
  const formattedDate = date.toLocaleDateString('en-GB', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  }).replace(/ /g, ' ').replace(',', ', '); // Ensures the specific comma spacing

  document.querySelector('.js-date-time').innerHTML = formattedDate;
}



