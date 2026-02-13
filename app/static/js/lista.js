// Estado de la lista
let listaCompras = JSON.parse(localStorage.getItem('compri_lista')) || [];

document.addEventListener('DOMContentLoaded', () => {
    actualizarBadge();
    renderizarLista();
});

// Función para agregar producto
function agregarALista(producto) {
    // Evitar duplicados exactos (opcional)
    const existe = listaCompras.some(p => p.nombre === producto.nombre);
    if (existe) {
        alert("Este producto ya está en la lista");
        return;
    }

    listaCompras.push(producto);
    guardarLista();
    actualizarBadge();
    renderizarLista();
    
    // Feedback visual
    const btn = document.querySelector('.fab-btn');
    btn.style.transform = 'scale(1.2)';
    setTimeout(() => btn.style.transform = 'scale(1)', 200);
}

// Función para eliminar producto
function eliminarDeLista(index) {
    listaCompras.splice(index, 1);
    guardarLista();
    actualizarBadge();
    renderizarLista();
}

function vaciarLista() {
    if(confirm('¿Borrar toda la lista?')) {
        listaCompras = [];
        guardarLista();
        actualizarBadge();
        renderizarLista();
    }
}

function guardarLista() {
    localStorage.setItem('compri_lista', JSON.stringify(listaCompras));
}

function actualizarBadge() {
    const badge = document.getElementById('lista-count');
    if (badge) {
        badge.innerText = listaCompras.length;
        badge.style.display = listaCompras.length > 0 ? 'flex' : 'none';
    }
}

// Renderizar elementos en el modal
function renderizarLista() {
    const contenedor = document.getElementById('lista-items-container');
    const footer = document.getElementById('lista-footer');
    const emptyMsg = document.getElementById('lista-empty');
    
    if (!contenedor) return;

    contenedor.innerHTML = '';

    if (listaCompras.length === 0) {
        emptyMsg.style.display = 'block';
        footer.style.display = 'none';
        return;
    }

    emptyMsg.style.display = 'none';
    footer.style.display = 'flex';

    listaCompras.forEach((prod, index) => {
        const item = document.createElement('div');
        item.className = 'lista-item';
        item.innerHTML = `
            <div class="item-details">
                <h4>${prod.nombre}</h4>
                <p>${prod.ubicacion} • <strong>$${prod.precio}</strong></p>
            </div>
            <button class="btn-remove" onclick="eliminarDeLista(${index})">
                <span class="material-icons">delete</span>
            </button>
        `;
        contenedor.appendChild(item);
    });
}

// Abrir/Cerrar Modal
function toggleModal() {
    const modal = document.getElementById('modal-lista');
    const isOpen = modal.classList.contains('open');
    if (isOpen) {
        modal.classList.remove('open');
    } else {
        modal.classList.add('open');
        renderizarLista();
    }
}

// Generar PDF
async function descargarPDF() {
    if (listaCompras.length === 0) return;

    const btn = document.getElementById('btn-descargar-pdf');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="material-icons">sync</span> Generando...';
    btn.disabled = true;

    try {
        const response = await fetch('/api/generar_lista_pdf', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ productos: listaCompras })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = "Lista_CompriAyuda.pdf";
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
        } else {
            alert("Error al generar el PDF");
        }
    } catch (error) {
        console.error(error);
        alert("Error de conexión");
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}