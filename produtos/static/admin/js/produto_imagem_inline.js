document.addEventListener("DOMContentLoaded", function () {

    function atualizarOpcoesHover() {
        const selects = document.querySelectorAll("select[id$='-tipo']");
        let hoverSelecionado = false;

        selects.forEach(select => {
            if (select.value === "hover") {
                hoverSelecionado = true;
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

    function previewImagem(input) {
        const file = input.files[0];
        if (!file) return;

        const reader = new FileReader();

        reader.onload = function (e) {
            let previewContainer = input.closest(".form-row").querySelector(".preview-temp");

            if (!previewContainer) {
                previewContainer = document.createElement("div");
                previewContainer.classList.add("preview-temp");
                previewContainer.style.marginTop = "10px";

                const img = document.createElement("img");
                img.style.width = "140px";
                img.style.height = "140px";
                img.style.objectFit = "cover";
                img.style.borderRadius = "10px";
                img.style.border = "2px solid #e5e7eb";

                previewContainer.appendChild(img);
                input.closest(".form-row").appendChild(previewContainer);
            }

            previewContainer.querySelector("img").src = e.target.result;
        };

        reader.readAsDataURL(file);
    }

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
            setTimeout(atualizarOpcoesHover, 200);
        }
    });

    atualizarOpcoesHover();
});