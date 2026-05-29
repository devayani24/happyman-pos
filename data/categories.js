import { generateTapToAddMenuGrid } from "./products.js";
import { renderPopUpModal } from "../scripts/pop-up-modal/pop-up-modal.js";

export const categories = [
  {
    id: '1',
    type: 'HALWA',
    localTypeName: 'அல்வா'
  },
  {
    id: '2',
    type: 'MILK SWEETS',
    localTypeName: 'பால் இனிப்பு'
  },
  {
    id: '3',
    type: 'FRIED SWEETS',
    localTypeName: 'வறுத்த இனிப்பு'
  },
  {
    id: '4',
    type: 'DRY SWEETS',
    localTypeName: 'உலர் இனிப்பு'
  },
  {
    id: '5',
    type: 'SAVOURIES',
    localTypeName: 'கார வகைகள்'
  },
  {
    id: '6',
    type: 'KARA VARIETIES',
    localTypeName: 'கார வகைகள்'
  },
]


export function generateCategoryButtons(){
  let html = '';

  categories.forEach((category)=>{
    

    html += 
      `
        <button class = "category-button js-category-button"
        data-category-id = ${category.id}>
          ${category.type}
        </button>
      `
    
  })
  const categoryElement = document.querySelector('.js-categories-buttons')
  categoryElement.innerHTML = html
}

export function categoryButtonEventListener(){
  document.querySelectorAll('.js-category-button').forEach((catogoryButtonElement)=>{
    
    catogoryButtonElement.addEventListener('click', ()=>{
      let id = catogoryButtonElement.dataset.categoryId;
      
      generateTapToAddMenuGrid(id);
      
      catogoryButtonElement.classList.add('is-categoryClicked');
      removeClass(id)
      // renderPopUpModal();
      renderPopUpModal('.js-menu-box');
    })
  
  
})
}

function removeClass(categoryId){
  document.querySelectorAll('.js-category-button').forEach((catogoryButtonElement)=>{
    if (catogoryButtonElement.dataset.categoryId !== categoryId){
      catogoryButtonElement.classList.remove('is-categoryClicked')
    }
    
  })
}





