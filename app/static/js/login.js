
const togglePassword = document.getElementById('togglePassword');
const passwordInput = document.getElementById('password');

togglePassword.addEventListener('click', () => {
    const isPassword = passwordInput.type === 'password';
    passwordInput.type = isPassword ? 'text' : 'password';
    togglePassword.textContent = isPassword ? 'visibility' : 'visibility_off';
});


const loginForm = document.getElementById('loginForm');
const loginError = document.getElementById('loginError');
const errorText = document.getElementById('errorText');
const btnLogin = document.getElementById('btnLogin');

loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    

    loginError.classList.remove('show');
    

    btnLogin.disabled = true;
    btnLogin.classList.add('loading');
    btnLogin.innerHTML = '<span class="material-icons">sync</span> Verificando...';

    const usuario = document.getElementById('usuario').value.trim();
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ usuario, password })
        });

        const data = await response.json();

        if (data.success) {
            btnLogin.innerHTML = '<span class="material-icons">check_circle</span> Acceso concedido';
            btnLogin.style.background = '#4a8c5c';
            
            setTimeout(() => {
                window.location.href = '/admin';
            }, 600);
        } else {
            errorText.textContent = data.error || 'Credenciales incorrectas';
            loginError.classList.add('show');
            resetButton();
        }
    } catch (err) {
        errorText.textContent = 'Error de conexión con el servidor';
        loginError.classList.add('show');
        resetButton();
    }
});

function resetButton() {
    btnLogin.disabled = false;
    btnLogin.classList.remove('loading');
    btnLogin.innerHTML = '<span class="material-icons">login</span> Ingresar';
    btnLogin.style.background = '';
}


document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && document.activeElement.tagName !== 'BUTTON') {
        loginForm.dispatchEvent(new Event('submit'));
    }
});
