import { products, getProductsById } from "../../data/products.js"




export function popUpBox(html, product){
 const overlayElement =  document.querySelector('.js-overlay-default')
 
  overlayElement.classList.add("js-overlay-show")
  overlayElement.innerHTML = html
    
  const closeELement = document.querySelector('.js-close-button')
  

  closeELement.addEventListener('click', ()=>{
    overlayElement.classList.remove("js-overlay-show")
  })
  

  overlayElement.addEventListener('click',(event)=>{
    if(event.target === overlayElement){
      overlayElement.classList.remove("js-overlay-show")
    }
  })
 


    return overlayElement
    
}



export function setupCounter(valueSelector, incrementSelector, decrementSelector) {
    const valueElement = document.querySelector(valueSelector);
    const incrementElement = document.querySelector(incrementSelector);
    const decrementElement = document.querySelector(decrementSelector);
    
    incrementElement.addEventListener('click', () => {
        const currentValue = parseInt(valueElement.value);
        valueElement.value = currentValue + 1;
    });
    
    decrementElement.addEventListener('click', () => {
        const currentValue = parseInt(valueElement.value);
        if (currentValue > 1) {
            valueElement.value = currentValue - 1;
        }
    });
}

export function getCartValues() {
    let cartWeight;
    let cartPieces;
    const cartUnit = document.querySelector('.js-unit-select').value;
    
    const weightElement = document.querySelector('.js-weight-input');
    const pieceElement = document.querySelector('.js-piece-count');
    
    if (weightElement) {
        cartWeight = parseFloat(weightElement.value) || 0;  
        cartPieces = null;
    } else if (pieceElement) {
        cartPieces = parseInt(pieceElement.value) || 0;            
        cartWeight = null;
    }
    
    const cartPackets = parseInt(document.querySelector('.js-packet-count').value) || 0;
    
    return { cartUnit, cartWeight, cartPieces, cartPackets };
}

