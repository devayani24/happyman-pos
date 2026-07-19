import { closeSideHeader } from "./pop-up-modal/sideHeader.js";

const MODAL_ID = 'transactionHistoryModal';
const VISIBLE_CLASS = 'visible';

function openTransactionModal() {
    closeSideHeader();
    document.getElementById(MODAL_ID).classList.add(VISIBLE_CLASS);
}

function closeTransactionModal() {
    document.getElementById(MODAL_ID).classList.remove(VISIBLE_CLASS);
}

function setupCloseHandlers() {
    const closeSelectors = [
        '.js-transaction-back-arrow',
        '.js-close-transaction-modal'
    ];
    
    closeSelectors.forEach(selector => {
        const button = document.querySelector(selector);
        if (button) {
            button.addEventListener('click', closeTransactionModal);
        }
    });
}

function setupOpenHandler() {
    document.querySelector('.js-view-history-icon')
        .addEventListener('click', openTransactionModal);
}

export function renderViewTransaction() {
    setupOpenHandler();
    setupCloseHandlers();
}