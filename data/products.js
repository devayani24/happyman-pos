export function getProductsById(productId){
  let matchingProduct;
  products.forEach((product)=>{
    if(product.id == productId){
      matchingProduct = product;
    }
  })
  return matchingProduct
}


export const products = [
  {
    id: 'p00001',
    name: 'Wheat Halwa',
    localName: 'கோதுமை அல்வா',
    categoryId: '1',
    soldBy: 'weight',
    price: 100,
    priceUnit: 50,
    priceUnitType: 'g',
    image: 'menu-pics/halwa2.jpg',
    isActive: true

  },
  {
    id: 'p00002',
    name: 'Cashew Halwa',
    localName: 'முந்திரி அல்வா',
    categoryId: '1',
    soldBy: 'weight',
    price: 60,
    priceUnit: 50,
    priceUnitType: 'g',
    image: 'menu-pics/cashew-halwa.png',
    isActive: true

  },
  {
    id: 'p00003',
    name: 'Paal Halwa',
    localName: 'பால் அல்வா',
    categoryId: '1',
    soldBy: 'weight',
    price: 50,
    priceUnit: 50,
    priceUnitType: 'g',
    image: 'menu-pics/Paal-Halwa.jpg',
    isActive: true

  },
  {
    id: 'p00004',
    name: 'Paal Kova',
    localName: 'பால்கோவா',
    categoryId: '1',
    soldBy: 'weight',
    price: 40,
    priceUnit: 50,
    priceUnitType: 'g',
    image: 'menu-pics/paalKova.jpg',
    isActive: true

  },
  {
    id: 'p00005',
    name: 'Mysore pak',
    localName: 'மைசூர் பாக்',
    categoryId: '2',
    soldBy: 'pieces',
    price: 40,
    priceUnit: 1,
    priceUnitType: 'pc',
    image: 'menu-pics/mysore-pak.jpg',
    isActive: true

  },
  {
    id: 'p00006',
    name: 'Soan Papdi',
    localName: 'சோன் பப்டி',
    categoryId: '2',
    soldBy: 'pieces',
    price: 50,
    priceUnit: 1,
    priceUnitType: 'pc',
    image: 'menu-pics/soan-papdi.jpg',
    isActive: true

  },
  {
    id: 'p00007',
    name: 'Kaju Katli',
    localName: 'காஜு கத்லி',
    categoryId: '2',
    soldBy: 'pieces',
    price: 50,
    priceUnit: 1,
    priceUnitType: 'pc',
    image: 'menu-pics/kaju-katli.avif',
    isActive: true

  },
  {
    id: 'p00008',
    name: 'Coconut Burfi',
    localName: 'தேங்காய் பர்பி',
    categoryId: '2',
    soldBy: 'pieces',
    price: 50,
    priceUnit: 1,
    priceUnitType: 'pc',
    image: 'menu-pics/ThengaiBurfi.webp',
    isActive: true

  },
  {
    id: 'p00009',
    name: 'Jalebi',
    localName: 'ஜிலேபி',
    categoryId: '3',
    soldBy: 'pieces',
    price: 50,
    priceUnit: 1,
    priceUnitType: 'pc',
    image: 'menu-pics/jalebi.jpg',
    isActive: true

  },
  {
    id: 'p00010',
    name: 'Adhirasam',
    localName: 'அதிரசம்',
    categoryId: '3',
    soldBy: 'pieces',
    price: 50,
    priceUnit: 1,
    priceUnitType: 'pc',
    image: 'menu-pics/adhirasam.jpg',
    isActive: true

  },
  
  {
    id: 'p00011',
    name: 'Badusha',
    localName: 'பாதுஷா',
    categoryId: '3',
    soldBy: 'pieces',
    price: 50,
    priceUnit: 1,
    priceUnitType: 'pc',
    image: 'menu-pics/badhusa.jpg',
    isActive: true

  },
  {
    id: 'p00012',
    name: 'Chandrakala',
    localName: 'சந்திரகலா ',
    categoryId: '3',
    soldBy: 'pieces',
    price: 50,
    priceUnit: 1,
    priceUnitType: 'pc',
    image: 'menu-pics/chandrakala.webp',
    isActive: true

  },
  {
    id: 'p00013',
    name: 'Sooriyakala',
    localName: 'சூரியகலா',
    categoryId: '3',
    soldBy: 'pieces',
    price: 50,
    priceUnit: 1,
    priceUnitType: 'pc',
    image: 'menu-pics/sooriyakala.jpg',
    isActive: true

  },
  {
    id: 'p00014',
    name: 'Boondi Laddu',
    localName: 'பூந்தி லட்டு',
    categoryId: '4',
    soldBy: 'pieces',
    price: 50,
    priceUnit: 1,
    priceUnitType: 'pc',
    image: 'menu-pics/boondi-laddu.webp',
    isActive: true

  },
  {
    id: 'p00015',
    name: 'Rava Ladoo',
    localName: 'ரவா லட்டு',
    categoryId: '4',
    soldBy: 'pieces',
    price: 50,
    priceUnit: 1,
    priceUnitType: 'pc',
    image: 'menu-pics/ravaLaddu.jpg',
    isActive: true

  },
  {
    id: 'p00016',
    name: 'Dry Fruit Ladoo',
    localName: 'உலர் பழ லட்டு',
    categoryId: '4',
    soldBy: 'pieces',
    price: 50,
    priceUnit: 1,
    priceUnitType: 'pc',
    image: 'menu-pics/DryFruitLaddu.jpg',
    isActive: true

  },
  {
    id: 'p00017',
    name: 'Mixture',
    localName: 'மிக்ஸர்',
    categoryId: '5',
    soldBy: 'weight',
    price: 50,
    priceUnit: 50,
    priceUnitType: 'g',
    image: 'menu-pics/mixture.jpg',
    isActive: true

  },
  {
    id: 'p00018',
    name: 'Special Mixture',
    localName: 'ஸ்பெஷல் மிக்ஸர்',
    categoryId: '5',
    soldBy: 'weight',
    price: 50,
    priceUnit: 50,
    priceUnitType: 'g',
    image: 'menu-pics/specialMixture.png',
    isActive: true

  },
  
  {
    id: 'p00019',
    name: 'Thattai',
    localName: 'தட்டை',
    categoryId: '6',
    soldBy: 'pieces',
    price: 50,
    priceUnit: 1,
    priceUnitType: 'pc',
    image: 'menu-pics/thattai.webp',
    isActive: true

  },
  
  {
    id: 'p00020',
    name: 'Kai Murukku',
    localName: 'கை முறுக்கு',
    categoryId: '6',
    soldBy: 'pieces',
    price: 50,
    priceUnit: 1,
    priceUnitType: 'pc',
    image: 'menu-pics/kaiMurukku.webp',
    isActive: true

  },
  {
    id: 'p00021',
    name: 'Kara Boondhi',
    localName: 'காரா பூந்தி',
    categoryId: '5',
    soldBy: 'weight',
    price: 50,
    priceUnit: 50,
    priceUnitType: 'g',
    image: 'menu-pics/karaBoondi.webp',
    isActive: true

  },
  {
    id: 'p00022',
    name: 'Kara Sevu',
    localName: 'காரா சேவ்',
    categoryId: '5',
    soldBy: 'weight',
    price: 50,
    priceUnit: 50,
    priceUnitType: 'g',
    image: 'menu-pics/karaSevu.jpg',
    isActive: true

  },
  
  {
    id: 'p00023',
    name: 'Seedai',
    localName: 'சீடை',
    categoryId: '3',
    soldBy: 'weight',
    price: 60,
    priceUnit: 50,
    priceUnitType: 'g',
    image: 'menu-pics/seedai.jpg',
    isActive: true

  },
  {
    id: 'p00024',
    name: 'Omapodi',
    localName: 'ஓமப்பொடி',
    categoryId: '5',
    soldBy: 'weight',
    price: 50,
    priceUnit: 50,
    priceUnitType: 'g',
    image: 'menu-pics/omapodi.jpg',
    isActive: true

  },
  {
    id: 'p00025',
    name: 'Thenkuzhal Murukku',
    localName: 'தேன்குழல் முறுக்கு',
    categoryId: '6',
    soldBy: 'pieces',
    price: 50,
    priceUnit: 1,
    priceUnitType: 'pc',
    image: 'menu-pics/thenkuzhalMuruku.webp',
    isActive: true

  },
  {
    id: 'p00026',
    name: 'Melagu Sevu',
    localName: 'மிளகு சேவ்',
    categoryId: '5',
    soldBy: 'weight',
    price: 50,
    priceUnit: 50,
    priceUnitType: 'g',
    image: 'menu-pics/melaguSevu.jpg',
    isActive: true

  },
 
]

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
                ₹${product.price} / ${product.priceUnit}
            </div>
        </div>
          
      </div>
      `
    }
  })


  document.querySelector('.tap-to-add-menu-grid').innerHTML = html
}

