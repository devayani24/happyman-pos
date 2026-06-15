import { cart } from "./cart.js"
export let salesCart = JSON.parse(localStorage.getItem('sales') || '[]');



function saveSalesCart() {
    localStorage.setItem('sales', JSON.stringify(salesCart));
}

// ----- OPERATIONS -----

export async function addSaleToSalesCart(subtotal,paymentMethod,paymentReceived,change) {
    const nextBillNumber = salesCart.length > 0
        ? salesCart[salesCart.length - 1].billNumber + 1
        : 1;
    // 1. Build the sale object (existing logic)
    const sale = {
        billNumber: nextBillNumber,
        timestamp: new Date().toISOString(),
        items: cart.map(item => ({ ...item })),
        subtotal,
        paymentMethod,
        paymentReceived,
        change,
    };
    
    // 2. Save to localStorage immediately (fast, never fails)
    salesCart.push(sale);
    saveSalesCart();
    

    // 
    try {
        await sendSaleToBackend(sale);
        console.log('Sale saved to backend');
    } catch (error) {
        console.error('Failed to save to backend:', error);
        // localStorage still has it — the sale isn't lost
    }
   
}

async function sendSaleToBackend(sale) {
    // Transform the JS shape into the Python shape
    const payload = {
        shop_id: "HM1",                                    // hardcoded for now
        bill_number: `HM1-${sale.billNumber}`,             // formatted bill number
        timestamp: sale.timestamp,
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
    console.log('Payload being sent:', JSON.stringify(payload, null, 2));
    const response = await fetch('http://localhost:8000/save-sale',{
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });
    if (!response.ok) {
        const errorDetails = await response.json();
        console.error('Python rejected the request:', errorDetails);
        throw new Error(`Backend returned ${response.status}`);
    }
    
    return response.json();
}