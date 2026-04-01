document.addEventListener("DOMContentLoaded", function () {

  const subtotalGeralEl  = document.getElementById("subtotal-geral");
  const totalGeralEl     = document.getElementById("total-geral");
  const freteValorEl     = document.getElementById("frete-valor");
  const freteResultadoEl = document.getElementById("frete-resultado");
  const cepInput         = document.getElementById("cep-input");
  const btnCalcularFrete = document.getElementById("btn-calcular-frete");

  let subtotalProdutos = parseFloat(subtotalGeralEl?.innerText.replace(",", ".")) || 0;
  let valorFrete       = parseFloat(freteValorEl?.innerText.replace(",", "."))    || 0;

  /* =========================
     FORMATAR MOEDA
  ========================= */
  function formatarMoeda(valor) {
    return valor
      .toFixed(2)
      .replace(".", ",")
      .replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  }

  function getCSRFToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";
  }

  function atualizarTotal() {
    const total = subtotalProdutos + valorFrete;
    if (subtotalGeralEl) subtotalGeralEl.innerText = formatarMoeda(subtotalProdutos);
    if (totalGeralEl)    totalGeralEl.innerText    = formatarMoeda(total);
  }

  function postJSON(url, callback) {
    fetch(url, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCSRFToken(),
        "X-Requested-With": "XMLHttpRequest"
      }
    }).then(r => r.json()).then(data => { if (callback) callback(data); });
  }

  // Helper: exibe mensagem de erro no container de frete
  function setFreteErro(container, mensagem) {
    container.innerHTML = "";
    const p = document.createElement("p");
    p.className   = "frete-erro";
    p.textContent = mensagem;
    container.appendChild(p);
    container.style.display = "block";
  }

  // Helper: monta as opções de frete via DOM
  function renderizarOpcoesFrete(opcoes, idSalvo) {
    freteResultadoEl.innerHTML = "";

    const wrapper = document.createElement("div");
    wrapper.className = "frete-opcoes";

    opcoes.forEach((opcao, index) => {
      const selecionada = idSalvo
        ? String(opcao.id) === String(idSalvo)
        : index === 0;

      const label = document.createElement("label");
      label.className = `frete-opcao${selecionada ? " selecionada" : ""}`;

      const radio = document.createElement("input");
      radio.type                    = "radio";
      radio.name                    = "frete-opcao";
      radio.value                   = opcao.id;
      radio.dataset.valor           = opcao.preco;
      radio.dataset.nome            = opcao.nome;
      radio.dataset.prazo           = opcao.prazo;
      radio.dataset.transportadora  = opcao.transportadora;
      if (selecionada) radio.checked = true;

      const info = document.createElement("div");
      info.className = "frete-opcao-info";

      const nomeSpan = document.createElement("span");
      nomeSpan.className   = "frete-opcao-nome";
      nomeSpan.textContent = `${opcao.transportadora} — ${opcao.nome}`;

      const prazoSpan = document.createElement("span");
      prazoSpan.className   = "frete-opcao-prazo";
      prazoSpan.textContent = `${opcao.prazo} dia(s) úteis`;

      info.appendChild(nomeSpan);
      info.appendChild(prazoSpan);

      const precoSpan = document.createElement("span");
      precoSpan.className   = "frete-opcao-preco";
      precoSpan.textContent = `R$ ${formatarMoeda(parseFloat(opcao.preco))}`;

      label.appendChild(radio);
      label.appendChild(info);
      label.appendChild(precoSpan);
      wrapper.appendChild(label);
    });

    freteResultadoEl.appendChild(wrapper);
    freteResultadoEl.style.display = "block";
  }

  atualizarTotal();

  // ==========================
  // CEP — MÁSCARA
  // ==========================
  if (cepInput) {
    const cepSalvo = sessionStorage.getItem("cep_digitado");
    if (cepSalvo && cepSalvo.length === 8) {
      cepInput.value = cepSalvo.slice(0, 5) + "-" + cepSalvo.slice(5);
    }

    cepInput.addEventListener("input", () => {
      let v = cepInput.value.replace(/\D/g, "").substring(0, 8);
      if (v.length > 5) v = v.slice(0, 5) + "-" + v.slice(5);
      cepInput.value = v;

      const cepLimpo = v.replace(/\D/g, "");
      sessionStorage.setItem("cep_digitado", cepLimpo);

      if (cepLimpo.length === 0) {
        sessionStorage.removeItem("cep_digitado");
        if (freteResultadoEl) freteResultadoEl.style.display = "none";
        valorFrete = 0;
        if (freteValorEl) freteValorEl.innerText = "0,00";
        atualizarTotal();

        fetch("/carrinho/frete/limpar/", {
          method: "POST",
          headers: {
            "X-CSRFToken": getCSRFToken(),
            "X-Requested-With": "XMLHttpRequest"
          }
        });
      }
    });

    cepInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") { e.preventDefault(); btnCalcularFrete?.click(); }
    });
  }

  // ==========================
  // QUANTIDADE
  // ==========================
  document.querySelectorAll(".btn-aumentar").forEach(btn => {
    btn.addEventListener("click", function () {
      postJSON(`/carrinho/aumentar/${encodeURIComponent(this.dataset.itemId)}/`, () => location.reload());
    });
  });

  document.querySelectorAll(".btn-diminuir").forEach(btn => {
    btn.addEventListener("click", function () {
      postJSON(`/carrinho/diminuir/${encodeURIComponent(this.dataset.itemId)}/`, () => location.reload());
    });
  });

  document.querySelectorAll(".form-remover").forEach(form => {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      postJSON(form.action, () => location.reload());
    });
  });

  // ==========================
  // CALCULAR FRETE
  // ==========================
  function calcularFrete(cep, idSelecionadoAntes) {
    if (!btnCalcularFrete || !cep || cep.length !== 8) return;

    btnCalcularFrete.disabled     = true;
    btnCalcularFrete.textContent  = "Calculando...";

    fetch("/carrinho/frete/calcular/", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": getCSRFToken(),
        "X-Requested-With": "XMLHttpRequest",
      },
      body: `cep=${encodeURIComponent(cep)}`
    })
      .then(r => r.json())
      .then(data => {
        btnCalcularFrete.disabled    = false;
        btnCalcularFrete.textContent = "Calcular";

        if (data.status === "erro") {
          if (freteResultadoEl) setFreteErro(freteResultadoEl, data.mensagem);
          return;
        }

        const idSalvo = idSelecionadoAntes || sessionStorage.getItem("frete_selecionado_id");

        if (freteResultadoEl) renderizarOpcoesFrete(data.opcoes, idSalvo);

        const opcaoSelecionada = idSalvo
          ? data.opcoes.find(o => String(o.id) === String(idSalvo)) || data.opcoes[0]
          : data.opcoes[0];

        valorFrete = parseFloat(opcaoSelecionada.preco) || 0;
        if (freteValorEl) freteValorEl.innerText = formatarMoeda(valorFrete);
        atualizarTotal();

        fetch("/carrinho/frete/selecionar/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
            "X-Requested-With": "XMLHttpRequest"
          },
          body: JSON.stringify({
            id:             opcaoSelecionada.id,
            valor:          opcaoSelecionada.preco,
            nome:           opcaoSelecionada.nome,
            prazo:          opcaoSelecionada.prazo,
            transportadora: opcaoSelecionada.transportadora,
            cep:            cep,
          })
        });

        document.querySelectorAll('input[name="frete-opcao"]').forEach(radio => {
          radio.addEventListener("change", function () {
            document.querySelectorAll(".frete-opcao").forEach(el => el.classList.remove("selecionada"));
            this.closest(".frete-opcao").classList.add("selecionada");

            sessionStorage.setItem("frete_selecionado_id", this.value);

            valorFrete = parseFloat(this.dataset.valor) || 0;
            if (freteValorEl) freteValorEl.innerText = formatarMoeda(valorFrete);
            atualizarTotal();

            fetch("/carrinho/frete/selecionar/", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
                "X-Requested-With": "XMLHttpRequest"
              },
              body: JSON.stringify({
                id:             this.value,
                valor:          this.dataset.valor,
                nome:           this.dataset.nome,
                prazo:          this.dataset.prazo,
                transportadora: this.dataset.transportadora,
                cep:            cep,
              })
            });
          });
        });
      });
  }

  btnCalcularFrete?.addEventListener("click", function () {
    const cep = cepInput.value.replace(/\D/g, "");
    if (cep.length !== 8) { alert("CEP inválido"); return; }
    sessionStorage.setItem("cep_digitado", cep);
    calcularFrete(cep, null);
  });

  const cepParaRecalcular = sessionStorage.getItem("cep_digitado");
  if (cepParaRecalcular && cepParaRecalcular.length === 8 && btnCalcularFrete) {
    if (cepInput) {
      cepInput.value = cepParaRecalcular.slice(0, 5) + "-" + cepParaRecalcular.slice(5);
    }
    setTimeout(() =>
      calcularFrete(
        cepParaRecalcular,
        sessionStorage.getItem("frete_selecionado_id")
      ),
      300
    );
  }
});