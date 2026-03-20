document.addEventListener("DOMContentLoaded", function () {

    // ── LIGHTBOX ─────────────────────────────────────────────
    function criarLightbox() {
        if (document.getElementById("admin-lightbox")) return;
        const lb = document.createElement("div");
        lb.id = "admin-lightbox";
        lb.innerHTML = `
      <div id="admin-lightbox-overlay">
        <button id="admin-lightbox-fechar">✕</button>
        <img id="admin-lightbox-img" src="" alt="">
      </div>`;
        document.body.appendChild(lb);
        lb.addEventListener("click", function (e) {
            if (e.target === lb || e.target.id === "admin-lightbox-fechar") fecharLightbox();
        });
        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape") fecharLightbox();
        });
    }

    function abrirLightbox(src) {
        const lb = document.getElementById("admin-lightbox");
        const img = document.getElementById("admin-lightbox-img");
        if (!lb || !img) return;
        img.src = src;
        lb.classList.add("ativo");
        document.body.style.overflow = "hidden";
    }

    function fecharLightbox() {
        const lb = document.getElementById("admin-lightbox");
        if (!lb) return;
        lb.classList.remove("ativo");
        document.body.style.overflow = "";
    }

    function aplicarLightbox(img) {
        if (!img || img.dataset.lightboxOk) return;
        img.dataset.lightboxOk = "1";
        img.style.cursor = "zoom-in";
        img.addEventListener("click", function () { abrirLightbox(this.src); });
    }

    // ── PREVIEW AVALIAÇÃO ─────────────────────────────────────
    // Lightbox nas fotos já salvas — tanto no field-foto quanto no field-foto_preview
    function iniciarPreviewAvaliacao() {
        document.querySelectorAll(".field-foto img, .field-foto_preview img").forEach(img => {
            img.classList.add("avaliacao-foto-preview");
            aplicarLightbox(img);
        });

        const fieldFoto = document.querySelector(".field-foto");
        if (!fieldFoto) return;

        let previewContainer = fieldFoto.querySelector(".avaliacao-preview-novo");
        if (!previewContainer) {
            previewContainer = document.createElement("div");
            previewContainer.className = "avaliacao-preview-novo";
            fieldFoto.appendChild(previewContainer);
        }

        const input = fieldFoto.querySelector("input[type='file']");
        if (!input) return;

        input.addEventListener("change", function () {
            const file = this.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = function (e) {
                previewContainer.innerHTML = `
          <p class="avaliacao-preview-label">Nova foto selecionada:</p>
          <img src="${e.target.result}" class="avaliacao-foto-preview" alt="Preview">`;
                aplicarLightbox(previewContainer.querySelector("img"));
            };
            reader.readAsDataURL(file);
        });
    }

    // ── PREVIEW IMAGEM SOBRE ──────────────────────────────────
    function iniciarPreviewImagemSobre() {
        document.querySelectorAll(
            ".field-imagem img, .field-imagem_preview img, .imagem-sobre-thumb, .admin-list-img"
        ).forEach(img => {
            img.classList.add("imagem-sobre-thumb");
            aplicarLightbox(img);
        });

        const fieldImagem = document.querySelector(".field-imagem");
        if (!fieldImagem) return;

        let previewContainer = fieldImagem.querySelector(".imagem-sobre-preview-novo");
        if (!previewContainer) {
            previewContainer = document.createElement("div");
            previewContainer.className = "imagem-sobre-preview-novo";
            fieldImagem.appendChild(previewContainer);
        }

        const inputImagem = fieldImagem.querySelector("input[type='file']");
        if (!inputImagem) return;

        inputImagem.addEventListener("change", function () {
            const file = this.files[0];
            if (!file) return;

            const fieldPreviewRow = document.querySelector(".field-imagem_preview");
            if (fieldPreviewRow) fieldPreviewRow.style.display = "none";

            const reader = new FileReader();
            reader.onload = function (e) {
                previewContainer.innerHTML = `
          <p class="avaliacao-preview-label">Nova imagem selecionada:</p>
          <img src="${e.target.result}" class="imagem-sobre-thumb" alt="Preview">`;
                aplicarLightbox(previewContainer.querySelector("img"));
            };
            reader.readAsDataURL(file);
        });
    }

    // ── INIT ─────────────────────────────────────────────────
    window.addEventListener("load", function () {
        criarLightbox();
        iniciarPreviewAvaliacao();
        iniciarPreviewImagemSobre();
    });

});