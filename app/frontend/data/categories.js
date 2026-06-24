import { generateTapToAddMenuGrid } from "./products.js";
import { renderPopUpModal } from "../scripts/pop-up-modal/pop-up-modal.js";
import { API_BASE } from "../scripts/config.js";

export let categories = [];

export async function loadCategories() {
  try  {
    const response = await fetch(`${API_BASE}/categories`);

    if(!response.ok){
      throw new Error(`Failed to load categories: ${response.status}`);
    }
    categories = await response.json();
   
    console.log(`Loaded ${categories.length} categories`);
    // After fetching, render the buttons
    generateCategoryButtons();
    categoryButtonEventListener();
  } catch (error){
    console.error('Error loading categories:', error);
  }
}


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





