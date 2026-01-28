document.addEventListener('DOMContentLoaded', () => {
  const botaoCarrinho = document.getElementById('btn-carrinho');
  const carrinho = document.getElementById('carrinho');
  const botaoFechar = document.getElementById('fechar-carrinho');

  if (!botaoCarrinho || !carrinho || !botaoFechar) return;

  botaoCarrinho.addEventListener('click', (e) => {
    e.preventDefault();
    carrinho.classList.toggle('aberto');
  });

  botaoFechar.addEventListener('click', () => {
    carrinho.classList.remove('aberto');
  });

  atualizarMiniCarrinho(); // carrega ao abrir a página
});

function atualizarMiniCarrinho() {
  fetch("/carrinho/mini/")
    .then(res => res.json())
    .then(data => {

      const lista = document.getElementById("mini-carrinho-lista");
      const total = document.getElementById("mini-carrinho-total");

      if (!lista || !total) return;

      lista.innerHTML = "";

      if (data.itens.length === 0) {
        lista.innerHTML = "<p>Seu carrinho está vazio.</p>";
        total.innerText = "Total: R$ 0,00";
        return;
      }

      data.itens.forEach(item => {
        lista.innerHTML += `
          <li class="item-carrinho">
            ${item.imagem ? `<img src="${item.imagem}" width="50">` : ""}
            <div class="item-carrinho-info">
              <strong>${item.nome}</strong>
              <span>${item.quantidade} × R$ ${item.preco.toFixed(2)}</span>
            </div>
          </li>
        `;
      });

      total.innerText = `Total: R$ ${data.total.toFixed(2)}`;
    });
}

