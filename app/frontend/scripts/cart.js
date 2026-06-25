

import { getProductsById } from "../data/products.js";
import { getCartValues } from "./pop-up-modal/container1.js";
import { cartActionMenu } from "./cart-actions/cartActionMenu.js";
import { calculateGrandTotal } from "./checkout.js";

// ----- PERSISTENCE -----

function loadCart() {
    try {
        const stored = localStorage.getItem('cart');
        return stored ? JSON.parse(stored) : [];
    } catch (error) {
        console.error('Failed to load cart from localStorage:', error);
        return [];
    }
}

function saveCart() {
    localStorage.setItem('cart', JSON.stringify(cart));
}


// ----- STATE -----

export let cart = loadCart();

let nextCartId = cart.length > 0 
    ? Math.max(...cart.map(item => item.id)) + 1 
    : 1;


// ----- OPERATIONS -----

export function addItemToCart(product, cartUnit, cartWeight, cartPieces, cartPackets) {
    const lineTotal = calculateLineTotal(product, cartUnit, cartWeight, cartPieces, cartPackets);
    cart.push({
        id: nextCartId++,
        productId: product.id,
        cartUnit,
        cartWeight,
        cartPieces,
        cartPackets,
        lineTotal,
    });
    saveCart();
}

export function updateCart(product, cartId, cartUnit, cartWeight, cartPieces, cartPackets) {
    const cartIndex = getCartItemByCartId(cartId);
    const lineTotal = calculateLineTotal(product, cartUnit, cartWeight, cartPieces, cartPackets);
    
    cart[cartIndex].cartUnit = cartUnit;
    cart[cartIndex].cartWeight = cartWeight;
    cart[cartIndex].cartPieces = cartPieces;
    cart[cartIndex].cartPackets = cartPackets;
    cart[cartIndex].lineTotal = lineTotal;
    
    saveCart();
}

export function removeItemFromCart(cartId) {
    const index = getCartItemByCartId(cartId);
    if (index !== -1) {
        cart.splice(index, 1);
        saveCart();
    }
}

export function clearCart() {
    cart.length = 0;       // empties the array in place (preserves the reference)
    saveCart();
}

export function getCartItemByCartId(cartId) {
    return cart.findIndex(item => item.id === parseInt(cartId));
}

// ----- PURE CALCULATIONS -----

function getPricePerGram(product) {
    if (product.priceUnitType === 'kg') {
        return product.price / (product.priceUnit * 1000);
    } else if (product.priceUnitType === 'g') {
        return product.price / product.priceUnit;
    }
    throw new Error(`Cannot get gram price for unit type: ${product.priceUnitType}`);
}

function getPricePerPiece(product) {
    if (product.priceUnitType === 'pc') {
        return product.price / product.priceUnit;
    }
    throw new Error(`Cannot get piece price for unit type: ${product.priceUnitType}`);
}

function calculateLineTotal(product, cartUnit, cartWeight, cartPieces, cartPackets) {
    let lineTotal;
    
    if (cartUnit === 'g' || cartUnit === 'kg') {
        const pricePerGram = getPricePerGram(product);
        const grams = cartUnit === 'kg' 
            ? parseFloat(cartWeight) * 1000 
            : parseFloat(cartWeight);
        lineTotal = pricePerGram * grams;
    } else if (cartUnit === 'pc') {
        const pricePerPiece = getPricePerPiece(product);
        lineTotal = pricePerPiece * parseInt(cartPieces);
    }

    
    
    return lineTotal * parseInt(cartPackets);
}

// ----- RENDERING (depends on DOM) -----

export function renderCart() {
    
    const clearButton = document.querySelector('.js-button-clear');
    
    const cartElement = document.querySelector('.js-cart');
    
    if (cart.length === 0) {
        cartElement.innerHTML = `<div class="empty-cart">Select products from tap to add</div>`;
        clearButton.classList.add('is-hidden');
    } else {
        clearButton.classList.remove('is-hidden');
        cartElement.innerHTML = cart.map(buildCartRowHTML).join('');
    }
    
    // Re-wire interactions and update derived UI
    
    cartActionMenu();
    calculateGrandTotal();
    
    
}

function buildCartRowHTML(item) {
    const product = getProductsById(item.productId);
    const weightOrPieces = (item.cartWeight ? item.cartWeight : item.cartPieces) + item.cartUnit;
    
    return `
        <div class="full-cart js-full-cart-item">
            <div class="cart-item">
                <div class="cart-product-name">
                    <div class="local-title">${product.localName}</div>
                    <div class="title">
                        (${product.name}) - 
                        <span class="base-price">₹${product.price}/<span class="base-UnitType">${product.priceUnit}${product.priceUnitType}</span></span>
                    </div>
                </div>
                <div class="cart-product-weight-pieces">${weightOrPieces}</div>
                <div class="cart-product-packets">${item.cartPackets}</div>
                <div class="cart-product-total-price">${item.lineTotal}</div>
            </div>
            <div class="cart-action js-cart-action" data-cart-id="${item.id}">
                <button class="btn-edit js-btn-edit" data-product-id="${item.productId}" data-cart-id="${item.id}">✏ EDIT</button>
                <button class="btn-delete js-btn-delete">🗑 DELETE</button>
            </div>
        </div>
    `;
}

export function setupClearButton(){
    document.querySelector('.js-button-clear').addEventListener('click',()=>{
        clearCart();
        renderCart();
    })
}