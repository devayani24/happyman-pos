import {cart, renderCart,removeItemFromCart } from "../cart.js"


export function setupDelete(cartActionElement){
  const deleteButton = cartActionElement.querySelector('.js-btn-delete')
   deleteButton.addEventListener('click',()=>{
    const cartId = cartActionElement.dataset.cartId
    removeItemFromCart(cartId)
    
    renderCart()
   })
  
}

