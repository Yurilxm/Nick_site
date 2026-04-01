document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("form-carrinho");
  if (!form) return;

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const url = form.action;

    const nome   = document.querySelector(".produto-titulo")?.innerText;
    const imagem = document.getElementById("imagem-principal")?.src;

    // Preço unitário
    const precoElemento = document.querySelector(".produto-preco");
    let precoUnitario = 0;

    if (precoElemento) {
      precoUnitario = parseFloat(
        precoElemento.innerText
          .replace("R$", "")
          .replace(",", ".")
          .trim()
      );
    }

    // Quantidade
    const quantidade = parseInt(document.getElementById("quantidade")?.value || 1);

    // Total
    const total = precoUnitario * quantidade;

    // Formatação BR
    const precoFormatado = precoUnitario.toFixed(2).replace(".", ",");
    const totalFormatado = total.toFixed(2).replace(".", ",");

    // Texto final
    let precoTexto = `R$ ${precoFormatado}`;
    if (quantidade > 1) {
      precoTexto = `${quantidade}x R$ ${precoFormatado} = R$ ${totalFormatado}`;
    }

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
        mostrarToast(nome, precoTexto, imagem);

        if (typeof window.atualizarMiniCarrinho === "function") {
          window.atualizarMiniCarrinho();
        } else {
          console.warn("Função atualizarMiniCarrinho não encontrada");
        }
      });
  });
});

function mostrarToast(nome, precoTexto, imagem) {
  const container = document.getElementById("toast-produto-container");

  // Remove toasts anteriores
  container.innerHTML = '';

  const toast = document.createElement("div");
  toast.className = "toast-produto";
  toast.style.cursor = "pointer";
  toast.setAttribute("role", "button");
  toast.setAttribute("aria-label", "Abrir carrinho");

  // Imagem
  const img = document.createElement("img");
  img.src = imagem;
  img.alt = nome;
  toast.appendChild(img);

  // Info
  const info = document.createElement("div");
  info.className = "toast-info";

  const strong = document.createElement("strong");
  strong.textContent = nome;
  info.appendChild(strong);

  const span = document.createElement("span");
  span.textContent = precoTexto;
  info.appendChild(span);

  const small = document.createElement("small");
  small.textContent = "Adicionado ao carrinho";
  info.appendChild(small);

  toast.appendChild(info);

  // Evento de clique
  toast.addEventListener("click", function (e) {
    e.preventDefault();
    e.stopPropagation();
    this.remove();
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