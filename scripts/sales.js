import { cart } from "./cart.js"
export let salesCart = JSON.parse(localStorage.getItem('sales') || '[]');



function saveSalesCart() {
    localStorage.setItem('sales', JSON.stringify(salesCart));
}

// ----- OPERATIONS -----

export function addSaleToSalesCart(subtotal,paymentMethod,paymentReceived,change) {
    const nextBillNumber = salesCart.length > 0
        ? salesCart[salesCart.length - 1].billNumber + 1
        : 1;
    salesCart.push({
        billNumber: nextBillNumber,
        timestamp: new Date().toISOString(),
        items: cart.map(item => ({ ...item })),
        subtotal,
        paymentMethod,
        paymentReceived,
        change,
    });
    saveSalesCart();
   
}