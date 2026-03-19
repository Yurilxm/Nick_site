document.addEventListener("DOMContentLoaded", function () {

  const subtotalGeralEl = document.getElementById("subtotal-geral");
  const totalGeralEl = document.getElementById("total-geral");
  const freteValorEl = document.getElementById("frete-valor");
  const freteResultadoEl = document.getElementById("frete-resultado");
  const cepInput = document.getElementById("cep-input");
  const btnCalcularFrete = document.getElementById("btn-calcular-frete");

  sessionStorage.removeItem('frete_selecionado_id');

  // ==========================
  // VERIFICAR SE CEP FOI APAGADO
  // ==========================
  function verificarCepApagado() {
    const foiApagado = sessionStorage.getItem('cep_foi_apagado') === 'true';
    if (foiApagado) {
      // Limpa tudo e remove a flag
      [
        "cep_digitado",
        "endereco_cep",
        "endereco_rua",
        "endereco_numero",
        "endereco_complemento",
        "endereco_bairro",
        "endereco_cidade",
        "endereco_estado",
        "frete_selecionado_id"
      ].forEach(key => sessionStorage.removeItem(key));
      sessionStorage.removeItem('cep_foi_apagado');
      return true;
    }
    return false;
  }

  // Restaura CEP com máscara - SOMENTE se não tiver sido apagado
  if (cepInput) {
    // Verifica se foi apagado antes de restaurar
    const foiApagado = verificarCepApagado();
    
    if (!foiApagado) {
      const cepSalvo = sessionStorage.getItem('cep_digitado');
      if (cepSalvo) {
        cepInput.value = cepSalvo.length > 5
          ? cepSalvo.slice(0, 5) + "-" + cepSalvo.slice(5)
          : cepSalvo;
      }
    }

    // Máscara + salva CEP
    cepInput.addEventListener('input', () => {
      let v = cepInput.value.replace(/\D/g, "").substring(0, 8);
      if (v.length > 5) v = v.slice(0, 5) + "-" + v.slice(5);
      cepInput.value = v;

      const cepLimpo = v.replace(/\D/g, "");
      
      // Se o usuário está digitando, remove a flag de apagado
      if (cepLimpo.length > 0) {
        sessionStorage.removeItem('cep_foi_apagado');
      }
      
      sessionStorage.setItem('cep_digitado', cepLimpo);

      // Busca endereço automático quando CEP estiver completo
      if (cepLimpo.length === 8) {
        fetch(`https://viacep.com.br/ws/${cepLimpo}/json/`)
          .then(r => r.json())
          .then(data => {
            if (!data.erro) {
              // Salva no sessionStorage
              sessionStorage.setItem("endereco_rua", data.logradouro || "");
              sessionStorage.setItem("endereco_bairro", data.bairro || "");
              sessionStorage.setItem("endereco_cidade", data.localidade || "");
              sessionStorage.setItem("endereco_estado", data.uf || "");
              sessionStorage.setItem("endereco_numero", "");
              sessionStorage.setItem("endereco_complemento", "");
              
              // Salva no backend
              fetch("/carrinho/endereco/salvar/", {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                  "X-CSRFToken": getCSRFToken(),
                  "X-Requested-With": "XMLHttpRequest"
                },
                body: JSON.stringify({
                  cep: cepLimpo,
                  rua: data.logradouro || "",
                  bairro: data.bairro || "",
                  cidade: data.localidade || "",
                  estado: data.uf || "",
                  numero: "",
                  complemento: ""
                })
              });
            }
          });
      }

      // LIMPEZA COMPLETA quando apaga CEP
      if (cepLimpo.length === 0) {
          // Marca que foi apagado (para não restaurar depois)
          sessionStorage.setItem('cep_foi_apagado', 'true');
          
          // Limpa sessionStorage
          sessionStorage.removeItem('frete_selecionado_id');
          sessionStorage.removeItem('cep_digitado');
          [
              "endereco_cep",
              "endereco_rua",
              "endereco_numero",
              "endereco_complemento",
              "endereco_bairro",
              "endereco_cidade",
              "endereco_estado"
          ].forEach(key => sessionStorage.removeItem(key));

          // Limpa UI
          if (freteResultadoEl) freteResultadoEl.style.display = "none";
          valorFrete = 0;
          if (freteValorEl) freteValorEl.innerText = "0.00";
          atualizarTotal();

          // Limpa backend
          fetch("/carrinho/endereco/salvar/", {
              method: "POST",
              headers: {
                  "Content-Type": "application/json",
                  "X-CSRFToken": getCSRFToken(),
                  "X-Requested-With": "XMLHttpRequest"
              },
              body: JSON.stringify({
                  cep: "",
                  rua: "",
                  numero: "",
                  complemento: "",
                  bairro: "",
                  cidade: "",
                  estado: ""
              })
          });

          fetch("/carrinho/frete/limpar/", {
              method: "POST",
              headers: {
                  "X-CSRFToken": getCSRFToken(),
                  "X-Requested-With": "XMLHttpRequest"
              }
          });
      }
    });

    cepInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') { e.preventDefault(); btnCalcularFrete?.click(); }
    });
  }

  let subtotalProdutos = parseFloat(subtotalGeralEl?.innerText.replace(",", ".")) || 0;
  let valorFrete = parseFloat(freteValorEl?.innerText.replace(",", ".")) || 0;
  atualizarTotal();

  function atualizarTotal() {
    const total = subtotalProdutos + valorFrete;
    if (subtotalGeralEl) subtotalGeralEl.innerText = subtotalProdutos.toFixed(2);
    if (totalGeralEl) totalGeralEl.innerText = total.toFixed(2);
  }

  function getCSRFToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";
  }

  function postJSON(url, callback) {
    fetch(url, {
      method: "POST",
      headers: { "X-CSRFToken": getCSRFToken(), "X-Requested-With": "XMLHttpRequest" }
    }).then(r => r.json()).then(data => { if (callback) callback(data); });
  }

  document.querySelectorAll(".btn-aumentar").forEach(btn => {
    btn.addEventListener("click", function () {
      postJSON(`/carrinho/aumentar/${this.dataset.itemId}/`, () => {
        sessionStorage.removeItem('frete_selecionado_id');
        location.reload();
      });
    });
  });

  document.querySelectorAll(".btn-diminuir").forEach(btn => {
    btn.addEventListener("click", function () {
      postJSON(`/carrinho/diminuir/${this.dataset.itemId}/`, () => {
        sessionStorage.removeItem('frete_selecionado_id');
        location.reload();
      });
    });
  });

  document.querySelectorAll(".form-remover").forEach(form => {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      postJSON(form.action, () => {
        sessionStorage.removeItem('frete_selecionado_id');
        location.reload();
      });
    });
  });

  if (btnCalcularFrete) {
    btnCalcularFrete.addEventListener("click", function () {
      const cep = cepInput.value.replace(/\D/g, "");
      if (cep.length !== 8) { alert("CEP inválido"); return; }

      // Remove flag de apagado quando calcular novo CEP
      sessionStorage.removeItem('cep_foi_apagado');
      
      // Salva e busca endereço automaticamente para o checkout
      sessionStorage.setItem('cep_digitado', cep);
      fetch(`https://viacep.com.br/ws/${cep}/json/`)
        .then(r => r.json())
        .then(data => {
          if (!data.erro) {
            sessionStorage.setItem("endereco_rua", data.logradouro || "");
            sessionStorage.setItem("endereco_bairro", data.bairro || "");
            sessionStorage.setItem("endereco_cidade", data.localidade || "");
            sessionStorage.setItem("endereco_estado", data.uf || "");
            sessionStorage.setItem("endereco_numero", "");
            sessionStorage.setItem("endereco_complemento", "");

            // Salva na sessão do Django também
            fetch("/carrinho/endereco/salvar/", {
              method: "POST",
              headers: { "Content-Type": "application/json", "X-CSRFToken": getCSRFToken(), "X-Requested-With": "XMLHttpRequest" },
              body: JSON.stringify({
                cep: cep,
                rua: data.logradouro || "",
                bairro: data.bairro || "",
                cidade: data.localidade || "",
                estado: data.uf || "",
                numero: "",
                complemento: "",
              })
            });
          }
        });

      btnCalcularFrete.disabled = true;
      btnCalcularFrete.textContent = "Calculando...";

      fetch("/carrinho/frete/calcular/", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-CSRFToken": getCSRFToken(),
          "X-Requested-With": "XMLHttpRequest",
        },
        body: `cep=${cep}`
      })
        .then(r => r.json())
        .then(data => {
          btnCalcularFrete.disabled = false;
          btnCalcularFrete.textContent = "Calcular";

          if (data.status === "erro") {
            if (freteResultadoEl) {
              freteResultadoEl.innerHTML = `<p class="frete-erro">${data.mensagem}</p>`;
              freteResultadoEl.style.display = "block";
            }
            return;
          }

          const idSalvo = sessionStorage.getItem('frete_selecionado_id');
          let html = '<div class="frete-opcoes">';
          data.opcoes.forEach((opcao, index) => {
            const selecionada = idSalvo ? String(opcao.id) === String(idSalvo) : index === 0;
            html += `
              <label class="frete-opcao ${selecionada ? 'selecionada' : ''}">
                <input type="radio" name="frete-opcao" value="${opcao.id}"
                  data-valor="${opcao.preco}" data-nome="${opcao.nome}"
                  data-prazo="${opcao.prazo}" data-transportadora="${opcao.transportadora}"
                  ${selecionada ? 'checked' : ''}>
                <div class="frete-opcao-info">
                  <span class="frete-opcao-nome">${opcao.transportadora} — ${opcao.nome}</span>
                  <span class="frete-opcao-prazo">${opcao.prazo} dia(s) úteis</span>
                </div>
                <span class="frete-opcao-preco">R$ ${parseFloat(opcao.preco).toFixed(2).replace(".", ",")}</span>
              </label>`;
          });
          html += '</div>';

          if (freteResultadoEl) {
            freteResultadoEl.innerHTML = html;
            freteResultadoEl.style.display = "block";
          }

          const opcaoSelecionada = idSalvo
            ? data.opcoes.find(o => String(o.id) === String(idSalvo)) || data.opcoes[0]
            : data.opcoes[0];

          valorFrete = parseFloat(opcaoSelecionada.preco) || 0;
          if (freteValorEl) freteValorEl.innerText = valorFrete.toFixed(2).replace(".", ",");
          atualizarTotal();

          document.querySelectorAll('input[name="frete-opcao"]').forEach(radio => {
            radio.addEventListener("change", function () {
              document.querySelectorAll(".frete-opcao").forEach(el => el.classList.remove("selecionada"));
              this.closest(".frete-opcao").classList.add("selecionada");
              sessionStorage.setItem('frete_selecionado_id', this.value);
              valorFrete = parseFloat(this.dataset.valor) || 0;
              if (freteValorEl) freteValorEl.innerText = valorFrete.toFixed(2).replace(".", ",");
              atualizarTotal();

              fetch("/carrinho/frete/selecionar/", {
                method: "POST",
                headers: { "Content-Type": "application/json", "X-CSRFToken": getCSRFToken(), "X-Requested-With": "XMLHttpRequest" },
                body: JSON.stringify({
                  id: this.value, valor: this.dataset.valor, nome: this.dataset.nome,
                  prazo: this.dataset.prazo, transportadora: this.dataset.transportadora, cep: cep,
                })
              });
            });
          });
        });
    });
  }
});