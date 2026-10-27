import { cart } from "./cart.js"
import { API_BASE , SHOP_ID} from "./config.js";



export let salesCart = JSON.parse(localStorage.getItem('sales') || '[]');



function saveSalesCart() {
    localStorage.setItem('sales', JSON.stringify(salesCart));
}

// ----- OPERATIONS -----

export async function addSaleToSalesCart(subtotal,paymentMethod,paymentReceived,change) {
    
    const sale = {
        items: cart.map(item => ({ ...item })),
        subtotal,
        paymentMethod,
        paymentReceived,
        change,
    };
    
    // Try backend FIRST — backend is source of truth
    const { bill_number, timestamp } = await sendSaleToBackend(sale);
    
    // Only save to localStorage after backend confirms
    sale.billNumber =`${SHOP_ID}-${bill_number}`;
    sale.timestamp = timestamp;
    salesCart.push(sale);
    saveSalesCart();
    
    return bill_number;
   
}

async function sendSaleToBackend(sale) {
    // Transform the JS shape into the Python shape
    const payload = {
        shop_id: SHOP_ID,     
        total_price: sale.subtotal,
        payment_mode: sale.paymentMethod,
        amount_received: sale.paymentReceived,
        amount_change: sale.change,
        items: sale.items.map(item => ({
            product_id: item.productId,
            cart_unit: item.cartUnit,
            cart_weight: item.cartWeight ? parseFloat(item.cartWeight) : null,
            cart_pieces: item.cartPieces ? parseInt(item.cartPieces) : null,
            cart_packets: parseInt(item.cartPackets),
            line_total: item.lineTotal,
        })),
    };
    
    const response = await fetch(`${API_BASE}/save-sale`,{
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });
    if (!response.ok) {
        const errorDetails = await response.json();
        throw new Error(`Backend returned ${response.status}: ${JSON.stringify(errorDetails)}`);
    }
    
    const result = await response.json();
    
    if (!result.bill_number || !result.timestamp) {
        throw new Error('Backend response missing valid bill_number or timestamp');
    }
    
    return result;
}