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
        mostrarToast(nome, preco, imagem);

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

  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}