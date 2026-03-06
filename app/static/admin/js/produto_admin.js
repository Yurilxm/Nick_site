document.addEventListener("DOMContentLoaded", function () {

    // ==========================================
    // 1️⃣ CONTROLE IMAGEM HOVER
    // ==========================================
    function atualizarOpcoesHover() {
        const selects = document.querySelectorAll("select[id$='-tipo']");
        let hoverSelecionado = false;

        selects.forEach(select => {
            const inline = select.closest(".inline-related");
            const ordemField = inline.querySelector(".field-ordem");

            if (select.value === "hover") {
                hoverSelecionado = true;
                if (ordemField) ordemField.style.display = "none";
            } else {
                if (ordemField) ordemField.style.display = "block";
            }
        });

        selects.forEach(select => {
            const optionHover = select.querySelector("option[value='hover']");
            if (!optionHover) return;

            if (hoverSelecionado && select.value !== "hover") {
                optionHover.disabled = true;
            } else {
                optionHover.disabled = false;
            }
        });
    }

    // ==========================================
    // 2️⃣ PREVIEW NO CAMPO CORRETO
    // ==========================================
    function previewImagem(input) {
        const file = input.files[0];
        if (!file) return;

        const reader = new FileReader();

        reader.onload = function (e) {
            const inline = input.closest(".inline-related");
            const previewField = inline.querySelector(".field-preview");

            if (!previewField) return;

            previewField.innerHTML = `
                <img src="${e.target.result}"
                     class="admin-preview-img">
            `;
        };

        reader.readAsDataURL(file);
    }

    // ==========================================
    // 3️⃣ LIXEIRA INLINE
    // ==========================================
    function aplicarLixeiraInline() {

        document.querySelectorAll(".inline-related").forEach(function (inline) {

            const deleteCheckbox = inline.querySelector("input[type='checkbox'][name$='-DELETE']");
            const titulo = inline.querySelector("h3");
            const changeLink = inline.querySelector(".inlinechangelink");

            if (!titulo) return;

            // ============================
            // Criar container de ações
            // ============================
            let actionContainer = inline.querySelector(".inline-actions");

            if (!actionContainer) {
                actionContainer = document.createElement("div");
                actionContainer.className = "inline-actions";
                titulo.appendChild(actionContainer);
            }

            // ============================
            // Ajustar botão editar
            // ============================
            if (changeLink && !changeLink.classList.contains("iconified")) {

                changeLink.textContent = "✏️";
                changeLink.classList.add("iconified");

                actionContainer.appendChild(changeLink);
            }

            // ============================
            // Criar botão lixeira
            // ============================
            if (deleteCheckbox && !inline.querySelector(".inline-delete-btn")) {

                deleteCheckbox.style.display = "none";

                const btn = document.createElement("button");
                btn.innerHTML = "🗑️";
                btn.className = "inline-delete-btn";

                btn.addEventListener("click", function (e) {
                    e.preventDefault();
                    deleteCheckbox.checked = true;
                    inline.style.display = "none";
                });

                actionContainer.appendChild(btn);
            }

        });

    }
    // ==========================================
    // EVENTOS
    // ==========================================
    document.addEventListener("change", function (e) {

        if (e.target.matches("select[id$='-tipo']")) {
            atualizarOpcoesHover();
        }

        if (e.target.matches("input[type='file']")) {
            previewImagem(e.target);
        }
    });

    document.addEventListener("click", function (e) {
        if (e.target.matches(".add-row a")) {
            setTimeout(() => {
                atualizarOpcoesHover();
                aplicarLixeiraInline();
            }, 200);
        }
    });

    // IMPORTANTE: roda depois que tudo carregou
    window.addEventListener("load", function () {
        atualizarOpcoesHover();
        aplicarLixeiraInline();
    });

});