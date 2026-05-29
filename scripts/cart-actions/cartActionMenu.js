import { setupDelete } from "./deleteCartItem.js";
// import { setupEdit } from "./editCartItem.js";
import { renderPopUpModal } from "../pop-up-modal/pop-up-modal.js";

export function cartActionMenu(){
  
  document.querySelectorAll('.js-full-cart-item').forEach((cartItemElement)=>{
    
    cartItemElement.addEventListener('click',()=>{
      
      const cartActionElement = cartItemElement.querySelector('.js-cart-action')
      
      const wasOpen = cartActionElement.classList.contains('show-cart-action');
     
      // Close all rows
      document.querySelectorAll('.js-cart-action').forEach((el) => {
          el.classList.remove('show-cart-action');
      });
      
      // If this row wasn't already open, open it now
      if (!wasOpen) {
          cartActionElement.classList.add('show-cart-action');
      setupDelete(cartActionElement);
      renderPopUpModal('.js-btn-edit');
          
      }
    })
  })
}

