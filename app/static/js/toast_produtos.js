document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("btn-add-carrinho");
  if (!btn) return;

  btn.addEventListener("click", () => {
    const url = btn.dataset.url;
    const nome = btn.dataset.nome;
    const preco = btn.dataset.preco;
    const imagem = btn.dataset.imagem;

    fetch(url, {
      method: "POST",
      headers: {
        "X-CSRFToken": document.querySelector(
          'meta[name="csrf-token"]'
        ).content,
        "X-Requested-With": "XMLHttpRequest",
      },
    })
      .then((res) => res.json())
      .then(() => {
        mostrarToast(nome, preco, imagem);

        // Atualiza badge + mini carrinho em background
        if (typeof atualizarMiniCarrinho === "function") {
          atualizarMiniCarrinho();
        }
      });
  });
});

function mostrarToast(nome, preco, imagem) {
  const container = document.getElementById("toast-produto-container");

  const toast = document.createElement("div");
  toast.className = "toast-produto";

  toast.innerHTML = `
    <img src="${imagem}" alt="${nome}">
    <div class="toast-info">
      <strong>${nome}</strong>
      <span>R$ ${preco}</span>
      <small>Adicionado ao carrinho</small>
    </div>
  `;

  container.appendChild(toast);

  requestAnimationFrame(() => toast.classList.add("show"));

  // Tempo automatico
  const timeoutId = setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 300);
  }, 3000);

  // Clique -> busca dados frescos, espera, e so entao abre o carrinho
  toast.addEventListener("click", () => {
    clearTimeout(timeoutId);

    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 150);

    // Busca dados frescos e SO DEPOIS abre o carrinho lateral
    if (typeof atualizarMiniCarrinho === "function") {
      atualizarMiniCarrinho().then(() => {
        if (typeof window.abrirCarrinho === "function") {
          window.abrirCarrinho();
        }
      });
    } else if (typeof window.abrirCarrinho === "function") {
      window.abrirCarrinho();
    }
  });
}