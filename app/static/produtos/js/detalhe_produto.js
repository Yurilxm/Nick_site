document.addEventListener('DOMContentLoaded', () => {

  const btnComprar = document.getElementsByClassName('adicionar-carrinho')[0];
  const inputPersonalizacao = document.getElementById('personalizacao');
  const radiosArame = document.querySelectorAll('input[name="arame"]');
  const botoesAcabamento = document.querySelectorAll('[data-acabamento]');
  const btnMais = document.getElementById('qtd-mais');
  const btnMenos = document.getElementById('qtd-menos');
  const spanQtd = document.getElementById('quantidade');

  const produtoSelecionado = {
    personalizacao: '',
    arame: '',
    acabamento: '',
    quantidade: 1
  };

  // ===============================
  // FUNÇÃO DE VALIDAÇÃO
  // ===============================
  function validarFormulario() {
    const valido =
      produtoSelecionado.personalizacao.trim() !== '' &&
      produtoSelecionado.arame !== '' &&
      produtoSelecionado.acabamento !== '' &&
      produtoSelecionado.quantidade >= 1;

    btnComprar.disabled = !valido;
  }

  // ===============================
  // PERSONALIZAÇÃO
  // ===============================
  inputPersonalizacao.addEventListener('input', () => {
    produtoSelecionado.personalizacao = inputPersonalizacao.value;
    validarFormulario();
  });

  // ===============================
  // ARAME
  // ===============================
  radiosArame.forEach(radio => {
    radio.addEventListener('change', () => {
      produtoSelecionado.arame = radio.value;
      validarFormulario();
    });
  });

  // ===============================
  // ACABAMENTO
  // ===============================
  botoesAcabamento.forEach(botao => {
    botao.addEventListener('click', () => {

      // remove seleção visual
      botoesAcabamento.forEach(b => b.classList.remove('ativo'));

      botao.classList.add('ativo');
      produtoSelecionado.acabamento = botao.dataset.acabamento;

      validarFormulario();
    });
  });

  // ===============================
  // QUANTIDADE
  // ===============================
  btnMais.addEventListener('click', () => {
    produtoSelecionado.quantidade++;
    spanQtd.textContent = produtoSelecionado.quantidade;
    validarFormulario();
  });

  btnMenos.addEventListener('click', () => {
    if (produtoSelecionado.quantidade > 1) {
      produtoSelecionado.quantidade--;
      spanQtd.textContent = produtoSelecionado.quantidade;
      validarFormulario();
    }
  });

  // ===============================
  // BOTÃO COMPRAR (ainda sem carrinho)
  // ===============================
  btnComprar.addEventListener('click', () => {
    console.log('Produto pronto para carrinho:', produtoSelecionado);
    alert('Produto pronto para adicionar ao carrinho!');
  });

});


document.addEventListener("DOMContentLoaded", function() {
  const imagemPrincipal = document.getElementById("imagem-principal");
  const miniaturas = document.querySelectorAll(".miniaturas img");

  miniaturas.forEach((miniatura) => {
    miniatura.addEventListener("click", function() {
      // Troca a imagem principal
      imagemPrincipal.src = this.src;

      // Remove a classe 'ativa' de todas
      miniaturas.forEach((img) => img.classList.remove("ativa"));

      // Marca a miniatura clicada como ativa
      this.classList.add("ativa");
    });
  });
});