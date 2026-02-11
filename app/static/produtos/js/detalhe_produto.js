document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    // ====================================
    // GALERIA DE IMAGENS - SIMPLES E FUNCIONAL
    // ====================================
    
    function initGaleria() {
        const imgPrincipal = document.getElementById('imagem-principal');
        const miniaturas = document.querySelectorAll('.miniaturas img');
        
        if (!imgPrincipal || miniaturas.length === 0) return;
        
        // Garante primeira miniatura ativa
        miniaturas.forEach(img => img.classList.remove('ativa'));
        miniaturas[0].classList.add('ativa');
        
        // Adiciona evento de clique
        miniaturas.forEach(miniatura => {
            miniatura.onclick = function(e) {
                e.preventDefault();
                imgPrincipal.src = this.src;
                miniaturas.forEach(m => m.classList.remove('ativa'));
                this.classList.add('ativa');
                return false;
            };
        });
        
        console.log('✅ Galeria OK');
    }

    // ====================================
    // CONTROLE DE QUANTIDADE - SÓ BOTÕES
    // ====================================
    
    function initQuantidade() {
        const inputQtd = document.getElementById('quantidade');
        const btnMenos = document.querySelector('.quantidade-btn.menos');
        const btnMais = document.querySelector('.quantidade-btn.mais');
        const inputHidden = document.getElementById('input-quantidade');
        
        if (!inputQtd || !btnMenos || !btnMais) return;
        
        // FORÇA READONLY (garantia)
        inputQtd.readOnly = true;
        
        const max = parseInt(inputQtd.max) || 99;
        
        function atualizar(valor) {
            valor = parseInt(valor) || 1;
            valor = Math.max(1, Math.min(valor, max));
            inputQtd.value = valor;
            if (inputHidden) inputHidden.value = valor;
        }
        
        btnMenos.onclick = () => atualizar(parseInt(inputQtd.value) - 1);
        btnMais.onclick = () => atualizar(parseInt(inputQtd.value) + 1);
        
        console.log('✅ Quantidade OK');
    }

    // ====================================
    // PERSONALIZAÇÃO
    // ====================================
    
    function initPersonalizacao() {
        const textarea = document.getElementById('personalizacao');
        const contador = document.querySelector('.caracteres-restantes');
        const inputHidden = document.getElementById('input-personalizacao');
        
        if (!textarea) return;
        
        textarea.oninput = function() {
            const max = 200;
            let texto = this.value;
            
            if (texto.length > max) {
                texto = texto.slice(0, max);
                this.value = texto;
            }
            
            if (inputHidden) inputHidden.value = texto;
            if (contador) contador.textContent = `${texto.length}/${max}`;
        };
        
        console.log('✅ Personalização OK');
    }

    // ====================================
    // CARRINHO
    // ====================================
    
    function initCarrinho() {
        const form = document.getElementById('form-carrinho');
        const btnComprar = document.getElementById('btn-comprar-agora');
        
        if (!form) return;
        
        // Atualiza quantidade antes de enviar
        form.onsubmit = function() {
            const qtd = document.getElementById('quantidade');
            const qtdHidden = document.getElementById('input-quantidade');
            if (qtdHidden && qtd) qtdHidden.value = qtd.value;
        };
        
        // Comprar agora
        if (btnComprar) {
            btnComprar.onclick = function(e) {
                e.preventDefault();
                const qtd = document.getElementById('quantidade');
                const qtdHidden = document.getElementById('input-quantidade');
                if (qtdHidden && qtd) qtdHidden.value = qtd.value;
                form.action = '/checkout/';
                form.submit();
            };
        }
        
        console.log('✅ Carrinho OK');
    }

    // ====================================
    // INICIALIZAR TUDO
    // ====================================
    
    console.log('🚀 Iniciando produto detalhe...');
    initGaleria();
    initQuantidade();
    initPersonalizacao();
    initCarrinho();
    console.log('✅ Produto detalhe pronto!');
});