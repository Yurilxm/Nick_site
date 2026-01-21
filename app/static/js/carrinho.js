document.addEventListener('DOMContentLoaded', () => {
    const botaoCarrinho = document.getElementById('btn-carrinho');
    const carrinho = document.getElementById('carrinho');
    const botaoFechar = document.getElementById('fechar-carrinho');

    // Abrir / fechar pelo ícone do menu
    botaoCarrinho.addEventListener('click', (e) => {
        e.preventDefault();
        carrinho.classList.toggle('aberto');
    });

    // Fechar pelo botão X
    botaoFechar.addEventListener('click', () => {
        carrinho.classList.remove('aberto');
    });
});

