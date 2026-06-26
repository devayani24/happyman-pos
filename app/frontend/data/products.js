import { API_BASE } from "../scripts/config.js";


export let products = []


export function getProductsById(productId){
  let matchingProduct;
  products.forEach((product)=>{
    if(product.id == productId){
      matchingProduct = product;
    }
  })
  return matchingProduct
}


export async function loadProducts(){
  try{ 
    const response = await fetch(`${API_BASE}/products`);
    if(!response.ok){
        throw new Error(`Failed to load products: ${response.status}`);
      }
    products = await response.json()
    console.log(`Loaded ${products.length} products`);
    // After fetching, render the buttons}
  }catch (error){
    console.error('Error loading products:', error);
  }
}

export function generateTapToAddMenuGrid(categoryId){


  let html = '';
  
  products.forEach((product)=>{
    if (product.categoryId === categoryId){
        html += 
      `
      <div class = "menu-box js-menu-box" data-product-id = ${product.id}>
        <div class = "menu-pic">
            <img class = image src=${product.image} alt="">
        </div>
        <div class = "menu-info">
            <div class = "menu-info-name-local">
                ${product.localName}
            </div>
            <div class="menu-info-name">
                ${product.name}
            </div>
            <div class = "menu-info-price">
                ₹${product.price} / ${product.priceUnit}${product.priceUnitType}
            </div>
        </div>
          
      </div>
      `
    }
  })


  document.querySelector('.tap-to-add-menu-grid').innerHTML = html
}

