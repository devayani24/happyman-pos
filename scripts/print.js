export function updateReprintButton() {
    const reprintBtn = document.querySelector('.js-reprint-last');
    reprintBtn.classList.toggle('is-disabled', salesCart.length === 0);
}

export function reprint(){
  document.querySelector('.js-reprint-last').addEventListener('click', () => {
    if (salesCart.length === 0) return;
    const lastSale = salesCart[salesCart.length - 1];
    // TODO: await fetch('http://localhost:8000/print', { method: 'POST', body: JSON.stringify(lastSale) });
    console.log('Reprint requested for bill:', lastSale.billNumber);
});
}

