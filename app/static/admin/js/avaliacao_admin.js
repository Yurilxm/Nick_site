document.addEventListener("DOMContentLoaded", function () {

    // ── LIGHTBOX ─────────────────────────────────────────────
    function criarLightbox() {
        if (document.getElementById("admin-lightbox")) return;

        const lb = document.createElement("div");
        lb.id = "admin-lightbox";

        const overlay = document.createElement("div");
        overlay.id = "admin-lightbox-overlay";

        const btnFechar = document.createElement("button");
        btnFechar.id          = "admin-lightbox-fechar";
        btnFechar.textContent = "✕";

        const img = document.createElement("img");
        img.id  = "admin-lightbox-img";
        img.src = "";
        img.alt = "";

        overlay.appendChild(btnFechar);
        overlay.appendChild(img);
        lb.appendChild(overlay);
        document.body.appendChild(lb);

        lb.addEventListener("click", function (e) {
            if (e.target === lb || e.target.id === "admin-lightbox-fechar") fecharLightbox();
        });
        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape") fecharLightbox();
        });
    }

    function abrirLightbox(src) {
        const lb  = document.getElementById("admin-lightbox");
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
                previewContainer.innerHTML = "";

                const label = document.createElement("p");
                label.className   = "avaliacao-preview-label";
                label.textContent = "Nova foto selecionada:";

                const img = document.createElement("img");
                img.src       = e.target.result; // data URL gerada localmente pelo FileReader
                img.className = "avaliacao-foto-preview";
                img.alt       = "Preview";

                previewContainer.appendChild(label);
                previewContainer.appendChild(img);
                aplicarLightbox(img);
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
                previewContainer.innerHTML = "";

                const label = document.createElement("p");
                label.className   = "avaliacao-preview-label";
                label.textContent = "Nova imagem selecionada:";

                const img = document.createElement("img");
                img.src       = e.target.result; // data URL gerada localmente pelo FileReader
                img.className = "imagem-sobre-thumb";
                img.alt       = "Preview";

                previewContainer.appendChild(label);
                previewContainer.appendChild(img);
                aplicarLightbox(img);
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