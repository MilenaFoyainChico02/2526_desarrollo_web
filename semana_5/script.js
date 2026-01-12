// selección de elementos del dom usando getElementById 
const inputUrl = document.getElementById('imgUrl');
const addBtn = document.getElementById('addBtn');
const deleteBtn = document.getElementById('deleteBtn');
const gallery = document.getElementById('gallery');

//  Agrega imagenes
function addImage() {
    const url = inputUrl.value.trim();

    //  no permite vacíos
    if (url === "") {
        alert("Por favor, ingresa una URL válida.");
        return;
    }

    // Crea un nuevo elemento 'img' 
    const newImage = document.createElement('img');
    
    // Modifica atributos y clases 
    newImage.src = url;
    newImage.alt = "Mascota en adopción";
    newImage.classList.add('pet-image');

    // agrega evento click a la imagen nueva
    // esto permite seleccionarla apenas se crea
    newImage.addEventListener('click', function() {
        selectImage(newImage);
    });

    // inserta en el dom (dentro de la galería) 
    gallery.appendChild(newImage);

    // Limpiar el input
    inputUrl.value = "";
}

//  selecciona la imagen (solo una a la vez)
function selectImage(imageClicked) {
    // Primero: Quitamos la clase 'selected' de todas las imágenes actuales
    // Usamos querySelectorAll para buscar las que ya tengan la clase 
    const allImages = document.querySelectorAll('.pet-image');
    allImages.forEach(img => {
        img.classList.remove('selected');
    });

    // gregamos la clase 'selected' solo a la imagen clickeada
    imageClicked.classList.add('selected');
}

//  botón para agregar 
addBtn.addEventListener('click', addImage);

// tecla enter en el input  
inputUrl.addEventListener('keydown', (event) => {
    if (event.key === "Enter") {
        addImage();
    }
});

//  Botón eliminar
deleteBtn.addEventListener('click', () => {
    // Buscamos si existe alguna imagen con la clase 'selected'
    const selectedImage = document.querySelector('.selected');

    if (selectedImage) {
        // Si existe, la eliminamos del dom
        selectedImage.remove();
    } else {
        alert("Selecciona una mascota haciendo clic en su foto para eliminarla.");
    }
});