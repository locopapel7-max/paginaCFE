// ---------- Mostrar opciones de usuario ----------
function showUsers() {
    document.getElementById('userOptions').style.display = 'block';
    document.getElementById('formContainer').style.display = 'none';
}

// ---------- Mostrar formulario de usuarios ----------
function showForm(type) {
    let formHTML = '';

    if (type === 'comisionista') {
        formHTML = `
            <form action="/register_user" method="POST" enctype="multipart/form-data">
                <h2>Registro de Comisionista</h2>
                <label>RFC:</label><input type="text" name="rfc" required>
                <label>Nombre:</label><input type="text" name="name" required>
                <label>Correo electrónico:</label><input type="email" name="email" required>
                <label>Campo extra:</label><input type="text" name="extra">
                <label>Sube tu INE:</label><input type="file" name="ine" accept=".jpg,.png,.pdf" required>
                <button type="submit">Enviar</button>
            </form>
        `;
    } else if (type === 'agentes_comerciales') {
        formHTML = `
            <form action="/register_user" method="POST" enctype="multipart/form-data">
                <h2>Registro de Agente Comercial</h2>
                <label>RTT:</label><input type="text" name="rtt" required>
                <label>Nombre:</label><input type="text" name="name" required>
                <label>Correo electrónico:</label><input type="email" name="email" required>
                <label>Campo extra:</label><input type="text" name="extra">
                <label>Sube tu INE:</label><input type="file" name="ine" accept=".jpg,.png,.pdf" required>
                <button type="submit">Enviar</button>
            </form>
        `;
    }

    document.getElementById('formContainer').innerHTML = formHTML;
    document.getElementById('formContainer').style.display = 'block';
}

// ---------- Mostrar formulario de reembolso ----------
function showReembolso() {
    const reembolsoHTML = `
        <form id="reembolsoForm" enctype="multipart/form-data">
            <h2>Solicitud de Reembolso</h2>
            <label>Nombre:</label><input type="text" name="name" required>
            <label>Correo electrónico:</label><input type="email" name="email" required>
            <label>Copia de INE:</label><input type="file" name="ine_file" required>
            <label>Razones del reembolso:</label><textarea name="reason" rows="4" required></textarea>
            <label>Monto del reembolso:</label><input type="number" name="amount" required>
            <button type="submit">Enviar</button>
        </form>
    `;
    document.getElementById('formContainer').innerHTML = reembolsoHTML;
    document.getElementById('formContainer').style.display = 'block';

    // Evento submit con AJAX
    document.getElementById('reembolsoForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);

        fetch('/submit', {
            method: 'POST',
            body: formData
        })
        .then(resp => resp.json())
        .then(data => {
            if(data.success){
                alert(data.message);
                this.reset();
            } else {
                alert(data.message || 'Error al enviar el reembolso.');
            }
        })
        .catch(err => console.error('Error:', err));
    });
}

// ---------- Modal contraseña para autorizar ----------
function openPasswordForm(reembolsoId) {
    sessionStorage.setItem('reembolsoId', reembolsoId);
    document.getElementById('passwordModal').style.display = 'block';
}

function closePasswordForm() {
    document.getElementById('passwordModal').style.display = 'none';
}

function checkPassword() {
    const password = document.getElementById('password').value;
    const reembolsoId = sessionStorage.getItem('reembolsoId');

    fetch(`/authorize_reembolso/${reembolsoId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: password })
    })
    .then(response => response.json())
    .then(data => {
        if(data.success){
            alert('Reembolso autorizado correctamente.');
            closePasswordForm();
            location.reload(); // refresca la lista de reembolsos
        } else {
            alert(data.message || 'Error al autorizar.');
        }
    })
    .catch(err => console.error('Error:', err));
}
