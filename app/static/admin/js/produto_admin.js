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

    // Carrega salvos
    getCustomSelosStored().forEach(val => addOptionToSelect(val));
    renderSavedList();

    // Select onChange
    select.addEventListener("change", function () {
      if (select.value) {
        setValue(select.value);
        directInput.value = "";
      }
    });

    // Input direto — só atualiza o valor, SEM salvar
    directInput.addEventListener("input", function () {
      const val = directInput.value.trim();
      setValue(val);
      if (val) select.value = "";
    });

    // Botão ✏️ — salva na lista
    addBtn.addEventListener("click", function () {
      const val = directInput.value.trim();
      if (!val) {
        directInput.focus();
        return;
      }
      saveCustomSelo(val);
      addOptionToSelect(val);
      setValue(val);
      renderSavedList();
    });

    // Botão limpar
    clearBtn.addEventListener("click", function () {
      setValue("");
      select.value = "";
      directInput.value = "";
    });

    // Estado inicial
    const initialValue = hiddenInput.value;
    if (initialValue) setValue(initialValue);

  });

});