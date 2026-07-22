export function setupVoidSale(){
    document.querySelector('.js-cancel-sale').addEventListener('click',()=>{
        document.getElementById('voidModal').style.display = "flex"
    })
    closeVoidSale()
}

function closeVoidSale(){
    document.querySelector('.js-void-close').addEventListener('click',()=>{
        document.getElementById('voidModal').style.display = "none"
    })
}