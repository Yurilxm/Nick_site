document.addEventListener('DOMContentLoaded', function() {
  const container = document.getElementById('auth-container');
  const signInBtn = document.getElementById('login');
  const signUpBtn = document.getElementById('register');
  
  // Função para ativar a aba correta
  function setActiveTab(tab) {
    if (!container) return;
    
    if (tab === 'login') {
      container.classList.remove('active');
    } else if (tab === 'register') {
      container.classList.add('active');
    }
  }

  // Verificar se há erros no cadastro (formulário de registro)
  const registerForm = document.getElementById('register-form');
  const hasRegisterErrors = registerForm && registerForm.querySelector('.field-error');
  
  // Verificar se há erros no login
  const loginForm = document.getElementById('login-form');
  const hasLoginErrors = loginForm && loginForm.querySelector('.field-error');
  
  // Verificar qual aba deve estar ativa
  // Prioridade: 1. Erros no cadastro, 2. active_tab do Django, 3. data-active, 4. padrão
  if (hasRegisterErrors) {
    setActiveTab('register');
  } else if (hasLoginErrors) {
    setActiveTab('login');
  } else if (container && container.getAttribute('data-active') === 'register') {
    setActiveTab('register');
  } else if (typeof activeTab !== 'undefined' && activeTab === 'register') {
    setActiveTab('register');
  } else {
    setActiveTab('login');
  }

  // Eventos dos botões de toggle
  if (signInBtn) {
    signInBtn.addEventListener('click', function(e) {
      e.preventDefault();
      setActiveTab('login');
    });
  }

  if (signUpBtn) {
    signUpBtn.addEventListener('click', function(e) {
      e.preventDefault();
      setActiveTab('register');
    });
  }
});

// Toggle de senha
document.querySelectorAll('.toggle-password').forEach(toggleButton => {
    toggleButton.addEventListener('click', function(e) {
        e.stopPropagation(); // Evita propagação
        const passwordField = this.closest('.password-field');
        const input = passwordField ? passwordField.querySelector('input') : this.previousElementSibling;
        
        if (input && (input.type === 'password' || input.type === 'text')) {
            const isPassword = input.type === 'password';
            input.type = isPassword ? 'text' : 'password';
            this.className = isPassword
                ? 'ri-eye-fill toggle-password'
                : 'ri-eye-off-fill toggle-password';
        }
    });
});