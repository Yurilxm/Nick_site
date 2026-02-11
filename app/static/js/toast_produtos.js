document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("form-carrinho");
  if (!form) return;

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const url = form.action;

    const nome = document.querySelector(".produto-titulo")?.innerText;
    const preco = document.querySelector(".preco-valor")?.innerText.replace("R$ ", "");
    const imagem = document.getElementById("imagem-principal")?.src;

    fetch(url, {
      method: "POST",
      headers: {
        "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
        "X-Requested-With": "XMLHttpRequest",
      },
      body: new URLSearchParams(new FormData(form))
    })
      .then(res => res.json())
      .then(() => {
        // 1. MOSTRA O TOAST
        mostrarToast(nome, preco, imagem);
        
        // 2. ATUALIZA O MINI CARRINHO IMEDIATAMENTE
        if (typeof window.atualizarMiniCarrinho === "function") {
          window.atualizarMiniCarrinho();
        } else {
          console.warn("Função atualizarMiniCarrinho não encontrada");
        }
      });
  });
});

function mostrarToast(nome, preco, imagem) {
  const container = document.getElementById("toast-produto-container");

  // Remove toasts anteriores
  container.innerHTML = '';

  const toast = document.createElement("div");
  toast.className = "toast-produto";
  
  // 🔥 TORNA CLICÁVEL
  toast.style.cursor = "pointer";
  toast.setAttribute('role', 'button');
  toast.setAttribute('aria-label', 'Abrir carrinho');
  
  toast.innerHTML = `
    <img src="${imagem}" alt="${nome}">
    <div class="toast-info">
      <strong>${nome}</strong>
      <span>R$ ${preco}</span>
      <small>Adicionado ao carrinho</small>
    </div>
  `;

  // 🔥 EVENTO DE CLIQUE
  toast.addEventListener('click', function(e) {
    e.preventDefault();
    e.stopPropagation();
    
    // Remove o toast
    this.remove();
    
    // Abre o carrinho
    if (typeof window.abrirCarrinho === "function") {
      window.abrirCarrinho();
    }
  });

  container.appendChild(toast);

  // Animação de entrada
  requestAnimationFrame(() => toast.classList.add("show"));

  // Auto-remove após 3 segundos
  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => {
      if (toast.parentNode) toast.remove();
    }, 300);
  }, 3000);
}