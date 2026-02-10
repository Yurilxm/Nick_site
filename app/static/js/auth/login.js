const container = document.getElementById('auth-container');
const btnRegister = document.getElementById('register');
const btnLogin = document.getElementById('login');

if (btnRegister && btnLogin && container) {
    btnRegister.addEventListener('click', () => {
        container.classList.add('active');
    });

    btnLogin.addEventListener('click', () => {
        container.classList.remove('active');
    });
}

document.querySelectorAll('.toggle-password').forEach(toggleButton => {
    toggleButton.addEventListener('click', () => {
        const input = toggleButton.previousElementSibling;

        const isPassword = input.type === 'password';
        input.type = isPassword ? 'text' : 'password';

        toggleButton.className = isPassword
            ? 'ri-eye-fill toggle-password'
            : 'ri-eye-off-fill toggle-password';

        toggleButton.classList.toggle('active', isPassword);
    });
});
