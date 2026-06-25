import { setupCounter } from "./container1.js";

const UNIT_CONFIG = {
    g: {
        startValue: 50,
        increment: 50,
        buttonCount: 20,
        defaultWeight: '50',
        showWeightInput: true,
    },
    kg: {
        startValue: 1,
        increment: 0.5,
        buttonCount: 20,
        defaultWeight: '1',
        showWeightInput: true,
    },
    pc: {
        startValue: 5,
        increment: 5,
        buttonCount: 20,
        defaultWeight: '1',
        showWeightInput: false,    // pieces use counter, not weight input
    },
};

// ==============================================
// HTML BUILDERS — pure functions that return HTML strings
// ==============================================

export function buildQuickPickButtons(unit) {
    const config = UNIT_CONFIG[unit];
    let html = '';
    
    for (let i = 0; i < config.buttonCount; i++) {
        const value = config.startValue + (i * config.increment);
        html += `<button class="quick-pick js-quick-pick" data-quick-pick-value = "${value}">${value}${unit}</button>`;
    }
    
    return html;
}

 function buildQuantityInput(productUnitType) {
    // const config = UNIT_CONFIG[unit];
    
    if (productUnitType === 'kg') {
        return `
            <div class="form-field">
                <label class="form-label">Select unit</label>
                <select class="form-select js-unit-select">
                    <option value="g">g</option>
                    <option value="kg">kg</option>
                    
                </select>
            </div>

            <div class="form-field">
                <label class="form-label">Weight per packet: </label>
                <input class="form-select js-weight-input" type="number">
            </div>
        `;
    } else {
        return `
            <div class="form-field">
                <label class="form-label">Select unit</label>
                <select class="form-select js-unit-select">
                    <option value="pc">pc</option>
                    
                    
                </select>
            </div>

            <div class="form-field">
                <label class="form-label">Pieces per packet:</label>
                <div class="counter">
                    <button class="counter-btn js-piece-decrement">-</button>
                    <input class="counter-value js-piece-count" type="number" value="1" min="1">
                    <button class="counter-btn js-piece-increment">+</button>
                </div>
            </div>
        `;
    }
}


export function setupQuickPickButton(){

    const quickPickButtons = document.querySelectorAll('.js-quick-pick');
 
    const pieceCount = document.querySelector('.js-piece-count');

    const weightInput = document.querySelector('.js-weight-input');

    quickPickButtons.forEach( (quickPickButton)=>{
        quickPickButton.addEventListener('click',()=>{
            if (pieceCount){
                pieceCount.value = quickPickButton.dataset.quickPickValue
                
            }else {
                weightInput.value = quickPickButton.dataset.quickPickValue
            }
            
        })
        
    })
}

// ==============================================
// MAIN — wire up the modal's container 2
// ==============================================

export function renderQuickPickPanel() {
    

    // build the quantity input area()
    

    const quantityArea = document.querySelector('.js-quantity-area');
    quantityArea.innerHTML = buildQuantityInput( quantityArea.dataset.productUnitType);

    const quickPickGrid = document.querySelector('.js-quick-pick-grid');
    const unitSelect = document.querySelector('.js-unit-select');
    
    function refreshForUnit(unit) {
        
        
        
        
        quickPickGrid.innerHTML = buildQuickPickButtons(unit);
  
        const config = UNIT_CONFIG[unit];
        
        if (config.showWeightInput) {
            // Weight mode (g, kg) — set the weight input default
            const weightInput = document.querySelector('.js-weight-input');
            if (weightInput) {
                weightInput.value = config.defaultWeight;
            }
        } else {
            // Piece mode (pc) — wire up the +/- buttons
            setupCounter(
                '.js-piece-count',
                '.js-piece-increment',
                '.js-piece-decrement'
            );
        }
    }
    
    // Initial render — start with grams for product soldBy weight , pc for product soldBy pieces.
    let defaultUnit = '';
    if (quantityArea.dataset.productUnitType === 'kg'){
         defaultUnit = 'g'
    }else{
        defaultUnit = quantityArea.dataset.productUnitType;
    }

    
    refreshForUnit(defaultUnit);
    setupQuickPickButton();
    

    
    // Respond when the user changes the unit
    unitSelect.addEventListener('change', () => {
        refreshForUnit(unitSelect.value);
       
        setupQuickPickButton();
    });
    
}