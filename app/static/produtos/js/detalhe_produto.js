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
    // MODAL GALERIA (ZOOM DAS IMAGENS)
    // ====================================

    function initModalGaleria(){

        const modal = document.getElementById("modal-galeria");
        const imagemPrincipal = document.getElementById("imagem-principal");
        const modalImg = document.getElementById("modal-imagem");
        const fechar = document.querySelector(".modal-fechar");

        const setaEsq = document.querySelector(".modal-seta.esquerda");
        const setaDir = document.querySelector(".modal-seta.direita");

        const miniaturas = document.querySelectorAll(".miniaturas img");

        if(!modal || miniaturas.length === 0 || !imagemPrincipal) return;

        const imagens = Array.from(miniaturas).map(img => img.src);

        let indiceAtual = 0;

        let startX = 0;

        imagemPrincipal.addEventListener("touchstart", (e)=>{

            startX = e.touches[0].clientX;

        });

        imagemPrincipal.addEventListener("touchend", (e)=>{

            let endX = e.changedTouches[0].clientX;

            let diff = startX - endX;

            if(Math.abs(diff) > 50){

                if(diff > 0){
                    proximaImagem();
                }else{
                    imagemAnterior();
                }

            }

        });

    // =============================
    // TROCAR IMAGEM PRINCIPAL
    // =============================

    function trocarImagem(index){

        indiceAtual = index;

        imagemPrincipal.src = imagens[indiceAtual];

        atualizarMiniatura();

    }

    function atualizarMiniatura(){

        miniaturas.forEach(m => m.classList.remove("ativa"));

        miniaturas[indiceAtual].classList.add("ativa");

    }

    // =============================
    // MINIATURAS
    // =============================

    miniaturas.forEach((miniatura, index)=>{

        miniatura.addEventListener("click", ()=>{

            trocarImagem(index);

        });

        miniatura.addEventListener("mouseenter", ()=>{

            trocarImagem(index);

        });

    });

    // =============================
    // ABRIR MODAL
    // =============================

    imagemPrincipal.addEventListener("click", ()=>{

        modal.style.display = "flex";

        modalImg.src = imagens[indiceAtual];

    });

    // =============================
    // FECHAR MODAL
    // =============================

    fechar.onclick = ()=> modal.style.display = "none";

    modal.onclick = (e)=>{

        if(e.target === modal){
            modal.style.display = "none";
        }

    };

    // =============================
    // NAVEGAÇÃO
    // =============================

    function proximaImagem(){

        indiceAtual++;

        if(indiceAtual >= imagens.length){
            indiceAtual = 0;
        }

        modalImg.src = imagens[indiceAtual];
        trocarImagem(indiceAtual);

    }

    function imagemAnterior(){

        indiceAtual--;

        if(indiceAtual < 0){
            indiceAtual = imagens.length - 1;
        }

        modalImg.src = imagens[indiceAtual];
        trocarImagem(indiceAtual);

    }

    setaDir.onclick = proximaImagem;
    setaEsq.onclick = imagemAnterior;

    // =============================
    // TECLADO
    // =============================

    document.addEventListener("keydown", (e)=>{

        if(modal.style.display === "flex"){

            if(e.key === "ArrowRight"){
                proximaImagem();
            }

            if(e.key === "ArrowLeft"){
                imagemAnterior();
            }

            if(e.key === "Escape"){
                modal.style.display = "none";
            }

        }

    });

    // =============================
    // ZOOM PROFISSIONAL
    // =============================

    const zoomContainer = document.querySelector(".zoom-container");

    if(zoomContainer){

        zoomContainer.addEventListener("mousemove",(e)=>{

            const rect = zoomContainer.getBoundingClientRect();

            const x = (e.clientX - rect.left) / rect.width * 100;
            const y = (e.clientY - rect.top) / rect.height * 100;

            imagemPrincipal.style.transformOrigin = `${x}% ${y}%`;
            imagemPrincipal.style.transform = "scale(1.5)";

        });

        zoomContainer.addEventListener("mouseleave",()=>{

            imagemPrincipal.style.transform = "scale(1)";

        });

    }

    console.log("✅ Modal Galeria OK");

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
        
        const max = 999;
        
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

    // Garante que quantidade sempre esteja sincronizada
    form.addEventListener('submit', function () {
        const qtd = document.getElementById('quantidade');
        const qtdHidden = document.getElementById('input-quantidade');
        if (qtdHidden && qtd) {
            qtdHidden.value = qtd.value;
        }
    });

    // Comprar Agora
    if (btnComprar) {
        btnComprar.addEventListener('click', function () {
            const finalizarUrl = this.dataset.finalizarUrl;
            const qtd = document.getElementById('quantidade');
            const qtdHidden = document.getElementById('input-quantidade');

            if (qtdHidden && qtd) {
                qtdHidden.value = qtd.value;
            }

            // Primeiro adiciona ao carrinho
            fetch(form.action, {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: new URLSearchParams(new FormData(form))
            })
            .then(() => {
                // Depois redireciona para finalizar
                window.location.href = finalizarUrl;
            });
        });
    }

    console.log('✅ Carrinho OK');
}

    // ====================================
    // INICIALIZAR TUDO
    // ====================================
    
    console.log('🚀 Iniciando produto detalhe...');
    initGaleria();
    initModalGaleria();
    initQuantidade();
    initPersonalizacao();
    initCarrinho();
    console.log('✅ Produto detalhe pronto!');
});