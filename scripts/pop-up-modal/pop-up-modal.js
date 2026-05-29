import { getProductsById } from "../../data/products.js";
import { popUpBox ,setupCounter,getCartValues} from "./container1.js";
import { renderQuickPickPanel,buildQuickPickButtons,setupQuickPickButton } from "./container2.js";

import { cart,updateCart, addItemToCart,renderCart,getCartItemByCartId} from "../cart.js";


export function renderPopUpModal(className) {
    document.querySelectorAll(className).forEach((element) => {
        element.addEventListener('click', () => {
            const productId = element.dataset.productId;
            const product = getProductsById(productId);
            const cartId = element.dataset.cartId;

            
            
            if (cartId) {
                openEditMode(product, cartId);
            } else {
                openAddMode(product);
            }
        });
    });
}

function openAddMode(product) {
    const html = buildModalHTML(product, 'add');
    const overlayElement = popUpBox(html, product);
    
    renderQuickPickPanel();
    setupDoneButton(overlayElement, product);
    setupPacketCounter();
}

function openEditMode(product, cartId) {
    const cartIndex = getCartItemByCartId(cartId);
    const cartItem = cart[cartIndex];
    
    const html = buildModalHTML(product, 'edit', cartItem);
    const overlayElement = popUpBox(html, product);
    
    renderQuickPickPanel();
    prefillFormFromCartItem(overlayElement, cartItem);
    setupUpdateButton(overlayElement, product, cartId);
    setupPacketCounter();
}

function buildModalHTML(product, mode, cartItem = null) {
    const isEdit = mode === 'edit';
    const packetValue = isEdit ? cartItem.cartPackets : 1;
    const actionButton = isEdit
        ? `<button class="btn-primary js-update-button">Update</button>`
        : `<button class="btn-primary js-done-button">Done</button>`;
    
    return `
        <div class="modal js-modal">
            <div class="modal__main">
                <button class="btn-close js-close-button">X</button>
                
                <div class="product-title-local">${product.localName}</div>
                <div class="product-title">${product.name}</div>
                <div class="product-price">
                    ₹${product.price}/<span class="product-price-unit">${product.priceUnit}${product.priceUnitType}</span>
                </div>
                <img class="product-image" src="${product.image}" alt="">

                <div class="form-row js-quantity-area" data-product-unit-type="${product.priceUnitType}">
                </div>

                <div class="form-field">
                    <label class="form-label">Number of packets</label>
                    <div class="counter">
                        <button class="counter-btn js-packet-decrement">-</button>
                        <input class="counter-value js-packet-count" type="number" value="${packetValue}" min="1">
                        <button class="counter-btn js-packet-increment">+</button>
                    </div>
                </div>

                ${actionButton}
            </div>

            <div class="modal__sidebar">
                <div class="sidebar-label">Quick Pick</div>
                <div class="quick-pick-grid js-quick-pick-grid"></div>
            </div>
        </div>
    `;
}

function prefillFormFromCartItem(overlayElement, cartItem) {
    overlayElement.querySelector('.js-unit-select').value = cartItem.cartUnit;
    
    if (cartItem.cartPieces) {
        overlayElement.querySelector('.js-piece-count').value = cartItem.cartPieces;
    } else {
        overlayElement.querySelector('.js-weight-input').value = cartItem.cartWeight;
    }
    
    overlayElement.querySelector('.js-quick-pick-grid').innerHTML = 
        buildQuickPickButtons(cartItem.cartUnit);
    setupQuickPickButton(); 
}

function setupPacketCounter() {
    setupCounter('.js-packet-count', '.js-packet-increment', '.js-packet-decrement');
}

function setupDoneButton(overlayElement, product) {
    document.querySelector('.js-done-button').addEventListener('click', () => {
        const { cartUnit, cartWeight, cartPieces, cartPackets } = getCartValues();
        addItemToCart(product, cartUnit, cartWeight, cartPieces, cartPackets);
        overlayElement.classList.remove('js-overlay-show');
        renderCart();
    });
}

function setupUpdateButton(overlayElement,product,cartId){
 
  const updateButton = document.querySelector('.js-update-button');
  updateButton.addEventListener('click',()=>{
    const { cartUnit, cartWeight, cartPieces, cartPackets } = getCartValues();
    
    updateCart(product,cartId,cartUnit, cartWeight, cartPieces, cartPackets);
    overlayElement.classList.remove('js-overlay-show');
    renderCart();
  
  })
  
  
}


