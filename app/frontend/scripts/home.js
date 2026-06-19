import { generateCategoryButtons,categoryButtonEventListener } from "../data/categories.js";
import { generateTapToAddMenuGrid } from "../data/products.js";
import { renderCart,setupClearButton } from "./cart.js";
import { calculateGrandTotal,setupCashButton,setupGpayButton } from "./checkout.js";
import { cartActionMenu } from "./cart-actions/cartActionMenu.js";
import { renderPopUpModal } from "./pop-up-modal/pop-up-modal.js";
import { cart } from "./cart.js";


CurrentDateTime();
generateCategoryButtons();
generateTapToAddMenuGrid('1');
categoryButtonEventListener();

renderPopUpModal('.js-menu-box')
setupClearButton();
renderCart();
setupCashButton();
setupGpayButton();

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

