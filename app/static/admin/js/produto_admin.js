document.addEventListener("DOMContentLoaded", function () {

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

    function previewImagem(input) {
        const file = input.files[0];
        if (!file) return;

        const reader = new FileReader();

        reader.onload = function (e) {
            const inline = input.closest(".inline-related");
            const previewField = inline.querySelector(".field-preview");

            if (!previewField) return;

            previewField.innerHTML = `
                <img src="${e.target.result}" class="admin-preview-img admin-lightbox-trigger">
            `;

            // Aplica lightbox na nova imagem
            aplicarLightboxNaImagem(previewField.querySelector("img"));
        };

        reader.readAsDataURL(file);
    }

    function iniciarPreviewImagemPrincipal() {
        // Campo de imagem principal fica em .field-imagem
        const fieldImagem = document.querySelector(".field-imagem");
        if (!fieldImagem) return;

        const input = fieldImagem.querySelector("input[type='file']");
        if (!input) return;

        // Cria o container de preview se não existir
        let previewContainer = fieldImagem.querySelector(".admin-preview-principal");
        if (!previewContainer) {
            previewContainer = document.createElement("div");
            previewContainer.className = "admin-preview-principal";
            // Insere depois do widget de arquivo
            const widget = fieldImagem.querySelector(".file-upload");
            if (widget) {
                widget.after(previewContainer);
            } else {
                fieldImagem.appendChild(previewContainer);
            }
        }

        // Se já tem imagem salva, envolve ela no lightbox
        const imgExistente = fieldImagem.querySelector("a img, .readonly img");
        if (imgExistente) {
            imgExistente.classList.add("admin-lightbox-trigger");
            aplicarLightboxNaImagem(imgExistente);
        }

        // Preview ao selecionar novo arquivo
        input.addEventListener("change", function () {
            const file = this.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = function (e) {
                previewContainer.innerHTML = `
                    <img src="${e.target.result}"
                         class="admin-preview-img-principal admin-lightbox-trigger"
                         alt="Preview">
                `;
                aplicarLightboxNaImagem(previewContainer.querySelector("img"));
            };
            reader.readAsDataURL(file);
        });
    }

    function criarLightbox() {
        if (document.getElementById("admin-lightbox")) return;

        const lb = document.createElement("div");
        lb.id = "admin-lightbox";
        lb.innerHTML = `
            <div id="admin-lightbox-overlay">
                <button id="admin-lightbox-fechar">✕</button>
                <img id="admin-lightbox-img" src="" alt="">
            </div>
        `;
        document.body.appendChild(lb);

        // Fecha ao clicar no fundo ou no X
        lb.addEventListener("click", function (e) {
            if (e.target === lb || e.target.id === "admin-lightbox-fechar") {
                fecharLightbox();
            }
        });

        // Fecha com ESC
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

    function aplicarLightboxNaImagem(img) {
        if (!img) return;
        img.style.cursor = "zoom-in";
        img.addEventListener("click", function () {
            abrirLightbox(this.src);
        });
    }

    function aplicarLightboxEmTodas() {
        document.querySelectorAll(".admin-preview-img, .admin-list-img, .admin-preview-img-principal").forEach(img => {
            if (!img.dataset.lightboxOk) {
                img.dataset.lightboxOk = "1";
                aplicarLightboxNaImagem(img);
            }
        });
    }

    function aplicarLixeiraInline() {
        document.querySelectorAll(".inline-related").forEach(function (inline) {
            const deleteCheckbox = inline.querySelector("input[type='checkbox'][name$='-DELETE']");
            const titulo = inline.querySelector("h3");
            const changeLink = inline.querySelector(".inlinechangelink");

            if (!titulo) return;

            let actionContainer = inline.querySelector(".inline-actions");
            if (!actionContainer) {
                actionContainer = document.createElement("div");
                actionContainer.className = "inline-actions";
                titulo.appendChild(actionContainer);
            }

            if (changeLink && !changeLink.classList.contains("iconified")) {
                changeLink.textContent = "✏️";
                changeLink.classList.add("iconified");
                actionContainer.appendChild(changeLink);
            }

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

    document.addEventListener("change", function (e) {
        if (e.target.matches("select[id$='-tipo']")) {
            atualizarOpcoesHover();
        }

        if (e.target.matches("input[type='file']")) {
            // Inline images
            if (e.target.closest(".inline-related")) {
                previewImagem(e.target);
            }
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

    window.addEventListener("load", function () {
        criarLightbox();
        atualizarOpcoesHover();
        aplicarLixeiraInline();
        iniciarPreviewImagemPrincipal();
        aplicarLightboxEmTodas();
    });

});


// ==========================================
// SELOS
// ==========================================
document.addEventListener("DOMContentLoaded", function () {

  const STORAGE_KEY = "selo_custom_options";

  function getCustomSelosStored() {
    try {
      return JSON.parse(sessionStorage.getItem(STORAGE_KEY) || "[]");
    } catch { return []; }
  }

  function saveCustomSelo(value) {
    const list = getCustomSelosStored();
    if (!list.includes(value)) {
      list.push(value);
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(list));
    }
  }

  function removeCustomSelo(value) {
    const list = getCustomSelosStored().filter(s => s !== value);
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(list));
  }

  document.querySelectorAll(".selo-widget-wrapper").forEach(function (wrapper) {

    const id          = wrapper.id.replace("selo-wrapper-", "");
    const hiddenInput = document.getElementById(id);
    const select      = wrapper.querySelector(".selo-select");
    const directInput = document.getElementById(`selo-direct-${id}`);
    const clearBtn    = document.getElementById(`selo-clear-btn-${id}`);
    const addBtn      = document.getElementById(`selo-add-btn-${id}`);
    const savedList   = document.getElementById(`selo-saved-list-${id}`);

    if (!hiddenInput || !select) return;

    function renderSavedList() {
      const stored = getCustomSelosStored();
      savedList.innerHTML = "";

      if (stored.length === 0) return;

      const label = document.createElement("span");
      label.className = "selo-saved-label";
      label.textContent = "Salvos:";
      savedList.appendChild(label);

      stored.forEach(function (val) {
        const tag = document.createElement("span");
        tag.className = "selo-saved-tag";
        tag.dataset.value = val;

        const text = document.createElement("span");
        text.className = "selo-saved-tag-text";
        text.textContent = val;

        const del = document.createElement("button");
        del.type = "button";
        del.className = "selo-saved-tag-del";
        del.title = "Remover";
        del.textContent = "✖";

        text.addEventListener("click", function () {
          setValue(val);
          addOptionToSelect(val);
          select.value = val;
          directInput.value = "";
        });

        del.addEventListener("click", function () {
          removeCustomSelo(val);
          const opt = select.querySelector(`option[value="${val}"]`);
          if (opt) opt.remove();
          if (hiddenInput.value === val) {
            setValue("");
            select.value = "";
          }
          renderSavedList();
        });

        tag.appendChild(text);
        tag.appendChild(del);
        savedList.appendChild(tag);
      });
    }

    function setValue(val) {
      hiddenInput.value = val;
      savedList.querySelectorAll(".selo-saved-tag").forEach(t => {
        t.classList.toggle("active", t.dataset.value === val);
      });
    }

    function addOptionToSelect(value) {
      const exists = Array.from(select.options).some(o => o.value === value);
      if (!exists) {
        const opt = new Option(value, value, true, true);
        select.appendChild(opt);
      }
      select.value = value;
    }

    getCustomSelosStored().forEach(val => addOptionToSelect(val));
    renderSavedList();

    select.addEventListener("change", function () {
      if (select.value) {
        setValue(select.value);
        directInput.value = "";
      }
    });

    directInput.addEventListener("input", function () {
      const val = directInput.value.trim();
      setValue(val);
      if (val) select.value = "";
    });

    addBtn.addEventListener("click", function () {
      const val = directInput.value.trim();
      if (!val) { directInput.focus(); return; }
      saveCustomSelo(val);
      addOptionToSelect(val);
      setValue(val);
      renderSavedList();
    });

    clearBtn.addEventListener("click", function () {
      setValue("");
      select.value = "";
      directInput.value = "";
    });

    const initialValue = hiddenInput.value;
    if (initialValue) setValue(initialValue);
  });
});