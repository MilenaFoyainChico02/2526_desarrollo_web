let productos = [
  {
    nombre: "Base líquida",
    precio: 18,
    descripcion: "Base de maquillaje con acabado natural"
  },
  {
    nombre: "Labial mate",
    precio: 10,
    descripcion: "Labial de larga duración"
  },
  {
    nombre: "Máscara de pestañas",
    precio: 12,
    descripcion: "Define y alarga las pestañas"
  }
];

let lista = document.getElementById("listaProductos");

function renderizarProductos() {
  lista.innerHTML = "";

  productos.forEach(function (producto) {
    let item = document.createElement("li");
    item.textContent =
      producto.nombre + " - $" +
      producto.precio + " | " +
      producto.descripcion;

    lista.appendChild(item);
  });
}

// Carga automática
renderizarProductos();

// Agregar producto especificado por el usuario
document.getElementById("btnAgregar").addEventListener("click", function () {
  let nombre = document.getElementById("nombre").value;
  let precio = document.getElementById("precio").value;
  let descripcion = document.getElementById("descripcion").value;

  if (nombre === "" || precio === "" || descripcion === "") {
    alert("Por favor completa todos los campos");
    return;
  }

  let nuevoProducto = {
    nombre: nombre,
    precio: precio,
    descripcion: descripcion
  };

  productos.push(nuevoProducto);
  renderizarProductos();

  // Limpiar campos
  document.getElementById("nombre").value = "";
  document.getElementById("precio").value = "";
  document.getElementById("descripcion").value = "";
});