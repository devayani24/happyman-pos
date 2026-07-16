const overlay = document.getElementById("overlay");

function toggleSideHeader(event) {
  event.stopPropagation();

  const sideHeader = document.querySelector('.side-header');

  sideHeader.classList.toggle('visible');
  overlay.classList.toggle('active');
}

function closeSideHeader() {
  const sideHeader = document.querySelector('.side-header');

  sideHeader.classList.remove('visible');
  overlay.classList.remove('active');
}

export function renderSideHeader (){
  const sideHeader = document.querySelector('.side-header');
  const menuButton = document.querySelector('.js-menu-toggle');

  menuButton.addEventListener('click', toggleSideHeader);

  // Clicking the panel closes the sidebar
  overlay.addEventListener("click", closeSideHeader);

  // Prevent clicks inside the sidebar from closing it
  sideHeader.addEventListener('click', (event) => {
    event.stopPropagation();
  });

  
}
