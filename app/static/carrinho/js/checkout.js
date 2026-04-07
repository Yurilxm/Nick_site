'use strict';

document.addEventListener("DOMContentLoaded", function () {

    // ================================================================
    // ELEMENTOS — TOGGLE ENTREGA / RETIRADA
    // ================================================================
    const radioEntrega = document.getElementById("radio-entrega");
    const radioRetirada = document.getElementById("radio-retirada");
    const labelEntrega = document.getElementById("label-entrega");
    const labelRetirada = document.getElementById("label-retirada");
    const blocoEntrega = document.getElementById("bloco-entrega");
    const blocoRetirada = document.getElementById("bloco-retirada");
    const formCheckout = document.getElementById("form-checkout");
    const tipoInicial = document.getElementById("tipo-entrega-inicial")?.value || "entrega";

    // ================================================================
    // ELEMENTOS — ENDEREÇO + FRETE (originais)
    // ================================================================
    const cepEnderecoInput = document.getElementById("endereco-cep");
    const btnBuscarCep = document.getElementById("btn-buscar-cep");
    const btnConfirmar = document.getElementById("btn-confirmar");
    const linhafretePendente = document.getElementById("linha-frete-pendente");
    const linhaFreteAtual = document.getElementById("linha-frete-atual");
    const totalEl = document.getElementById("total-geral-checkout");
    const btnAlterar = document.getElementById("btn-alterar-frete");
    const freteBox = document.getElementById("frete-box-checkout");
    const cepFreteInput = document.getElementById("cep-input-checkout");
    const btnCalcularFrete = document.getElementById("btn-calcular-frete-checkout");
    const freteResultado = document.getElementById("frete-resultado-checkout");
    const nomeCompletoInput = document.getElementById("endereco-nome");

    function getCSRFToken() {
        return document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";
    }

    // ================================================================
    // HELPERS FRETE
    // ================================================================
    function setLinhaFrete(el, texto, valor) {
        if (!el) return;
        el.innerHTML = "";
        const s1 = document.createElement("span");
        s1.textContent = texto;
        const s2 = document.createElement("span");
        s2.textContent = valor;
        el.appendChild(s1);
        el.appendChild(s2);
    }

    function setFreteErro(container, mensagem) {
        container.innerHTML = "";
        const p = document.createElement("p");
        p.className = "frete-erro";
        p.textContent = mensagem;
        container.appendChild(p);
        container.style.display = "block";
    }

    // ================================================================
    // TOGGLE ENTREGA / RETIRADA
    // ================================================================

    // Campos obrigatórios apenas na entrega
    const camposEntrega = [
        "endereco-nome", "endereco-cep", "endereco-rua", "endereco-numero",
        "endereco-bairro", "endereco-cidade", "endereco-estado"
    ].map(id => document.getElementById(id)).filter(Boolean);

    function ativarEntrega() {
        if (blocoEntrega) blocoEntrega.style.display = "block";
        if (blocoRetirada) blocoRetirada.style.display = "none";
        if (labelEntrega) labelEntrega.classList.add("ativa");
        if (labelRetirada) labelRetirada.classList.remove("ativa");

        camposEntrega.forEach(el => { if (el) el.required = true; });

        const wpp = document.getElementById("retirada-whatsapp");
        if (wpp) wpp.required = false;
        const nomeRet = document.getElementById("retirada-nome");
        if (nomeRet) nomeRet.required = false;

        atualizarBotaoConfirmar();
    }

    function ativarRetirada() {
        if (blocoEntrega) blocoEntrega.style.display = "none";
        if (blocoRetirada) blocoRetirada.style.display = "block";
        if (labelRetirada) labelRetirada.classList.add("ativa");
        if (labelEntrega) labelEntrega.classList.remove("ativa");

        camposEntrega.forEach(el => { if (el) el.required = false; });

        const wpp = document.getElementById("retirada-whatsapp");
        if (wpp) wpp.required = true;
        const nomeRet = document.getElementById("retirada-nome");
        if (nomeRet) nomeRet.required = true;

        atualizarBotaoConfirmar();
    }

    // Restaura estado da sessão ao carregar
    if (tipoInicial === "retirada") {
        if (radioRetirada) radioRetirada.checked = true;
        ativarRetirada();
    } else {
        if (radioEntrega) radioEntrega.checked = true;
        ativarEntrega();
    }

    if (radioEntrega) {
        radioEntrega.addEventListener("change", () => { if (radioEntrega.checked) ativarEntrega(); });
    }
    if (radioRetirada) {
        radioRetirada.addEventListener("change", () => { if (radioRetirada.checked) ativarRetirada(); });
    }

    // ================================================================
    // MÁSCARA WHATSAPP (retirada)
    // ================================================================
    const wppInput = document.getElementById("retirada-whatsapp");
    if (wppInput) {
        wppInput.addEventListener("input", function () {
            let v = this.value.replace(/\D/g, "").substring(0, 11);
            if (v.length > 7) v = `(${v.slice(0, 2)}) ${v.slice(2, 7)}-${v.slice(7)}`;
            else if (v.length > 2) v = `(${v.slice(0, 2)}) ${v.slice(2)}`;
            else if (v.length > 0) v = `(${v}`;
            this.value = v;
            atualizarBotaoConfirmar();
        });
    }

    // ================================================================
    // SINCRONIZAR NOME (entrega ↔ retirada)
    // ================================================================
    const nomeRetirada = document.getElementById("retirada-nome");
    if (nomeCompletoInput && nomeRetirada) {
        nomeCompletoInput.addEventListener("input", () => {
            if (!nomeRetirada.value) nomeRetirada.value = nomeCompletoInput.value;
        });
        nomeRetirada.addEventListener("input", () => {
            if (!nomeCompletoInput.value) nomeCompletoInput.value = nomeRetirada.value;
        });
    }

    // ================================================================
    // BOTÃO ALTERAR FRETE
    // ================================================================
    if (btnAlterar) {
        btnAlterar.addEventListener("click", function () {
            if (freteBox) freteBox.style.display = "block";
            this.style.display = "none";
            const cepSalvo = sessionStorage.getItem("cep_digitado");
            if (cepSalvo && cepSalvo.length === 8 && cepFreteInput) {
                cepFreteInput.value = cepSalvo.slice(0, 5) + "-" + cepSalvo.slice(5);
            }
        });
    }

    // ================================================================
    // VALIDAÇÃO DO BOTÃO CONFIRMAR
    // ================================================================
    function validarEndereco() {
        const isRetirada = radioRetirada?.checked;

        if (isRetirada) {
            // Para retirada: só precisa de nome e WhatsApp
            const nome = document.getElementById("retirada-nome")?.value.trim();
            const wpp = document.getElementById("retirada-whatsapp")?.value.replace(/\D/g, "") || "";
            return !!(nome && wpp.length >= 10);
        }

        // Para entrega: validação completa do endereço
        const nome = nomeCompletoInput?.value.trim();
        const cep = cepEnderecoInput?.value.replace(/\D/g, "");
        const rua = document.getElementById("endereco-rua")?.value.trim();
        const numero = document.getElementById("endereco-numero")?.value.trim();
        const bairro = document.getElementById("endereco-bairro")?.value.trim();
        const cidade = document.getElementById("endereco-cidade")?.value.trim();
        const estado = document.getElementById("endereco-estado")?.value.trim();
        return !!(nome && cep?.length === 8 && rua && numero && bairro && cidade && estado);
    }

    function atualizarBotaoConfirmar() {
        if (!btnConfirmar) return;
        const isRetirada = radioRetirada?.checked;
        const fretePendente = !isRetirada && linhafretePendente?.classList.contains("frete-pendente");
        const enderecoOk = validarEndereco();
        const ok = enderecoOk && !fretePendente;

        btnConfirmar.disabled = !ok;
        btnConfirmar.style.opacity = ok ? "1" : "0.5";
        btnConfirmar.style.cursor = ok ? "pointer" : "not-allowed";
    }

    // Escuta inputs de endereço para atualizar botão
    ["endereco-nome", "endereco-cep", "endereco-rua", "endereco-numero",
        "endereco-complemento", "endereco-bairro", "endereco-cidade", "endereco-estado"
    ].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener("input", atualizarBotaoConfirmar);
    });

    // ================================================================
    // BUSCA CEP VIA VIACEP
    // ================================================================
    function buscarCep(silencioso = false) {
        const cep = cepEnderecoInput?.value.replace(/\D/g, "");
        if (!cep || cep.length !== 8) {
            if (!silencioso) alert("Digite um CEP válido");
            return;
        }

        if (btnBuscarCep) {
            btnBuscarCep.textContent = "Buscando...";
            btnBuscarCep.disabled = true;
        }

        fetch(`/ajax/cep/?cep=${encodeURIComponent(cep)}`)
            .then(r => r.json())
            .then(data => {
                if (btnBuscarCep) {
                    btnBuscarCep.textContent = "Buscar";
                    btnBuscarCep.disabled = false;
                }
                if (data.erro) {
                    if (!silencioso) alert("CEP não encontrado.");
                    return;
                }

                const ruaInput = document.getElementById("endereco-rua");
                const bairroInput = document.getElementById("endereco-bairro");
                const cidadeInput = document.getElementById("endereco-cidade");
                const estadoInput = document.getElementById("endereco-estado");
                if (ruaInput) ruaInput.value = data.logradouro || "";
                if (bairroInput) bairroInput.value = data.bairro || "";
                if (cidadeInput) cidadeInput.value = data.localidade || "";
                if (estadoInput) estadoInput.value = data.uf || "";

                if (cepFreteInput) {
                    cepFreteInput.value = cep.slice(0, 5) + "-" + cep.slice(5);
                }

                if (!silencioso) document.getElementById("endereco-numero")?.focus();
                atualizarBotaoConfirmar();
            })
            .catch(() => {
                if (btnBuscarCep) {
                    btnBuscarCep.textContent = "Buscar";
                    btnBuscarCep.disabled = false;
                }
                if (!silencioso) alert("Erro ao buscar CEP.");
            });
    }

    if (btnBuscarCep) {
        btnBuscarCep.addEventListener("click", () => buscarCep(false));
    }

    // ================================================================
    // FRETE PENDENTE
    // ================================================================
    function marcarFretePendente() {
        setLinhaFrete(linhafretePendente, "Frete", "A calcular");
        if (linhafretePendente) linhafretePendente.classList.add("frete-pendente");
        setLinhaFrete(linhaFreteAtual, "Frete", "A calcular");
    }

    function triggerFreteCalculationIfNeeded(cep) {
        if (!cep || cep.length !== 8) return;
        const lastCep = sessionStorage.getItem("cep_digitado");
        if (lastCep !== cep) {
            marcarFretePendente();
            if (btnCalcularFrete) btnCalcularFrete.click();
        }
    }

    function handleCepComplete(cep) {
        if (cep.length !== 8) return;
        clearTimeout(window.cepEnderecoTimeout);
        window.cepEnderecoTimeout = setTimeout(() => buscarCep(true), 500);
        triggerFreteCalculationIfNeeded(cep);
    }

    // ================================================================
    // MÁSCARA + AUTOCOMPLETE CEP ENDEREÇO
    // ================================================================
    if (cepEnderecoInput) {
        cepEnderecoInput.addEventListener("input", (e) => {
            let v = e.target.value.replace(/\D/g, "").substring(0, 8);
            if (v.length > 5) v = v.slice(0, 5) + "-" + v.slice(5);
            e.target.value = v;

            const cepLimpo = v.replace(/\D/g, "");

            if (cepFreteInput) cepFreteInput.value = v;

            if (cepLimpo.length === 8) handleCepComplete(cepLimpo);

            if (cepLimpo.length === 0) {
                const rua = document.getElementById("endereco-rua");
                const bairro = document.getElementById("endereco-bairro");
                const cidade = document.getElementById("endereco-cidade");
                const estado = document.getElementById("endereco-estado");
                if (rua) rua.value = "";
                if (bairro) bairro.value = "";
                if (cidade) cidade.value = "";
                if (estado) estado.value = "";
                if (cepFreteInput) cepFreteInput.value = "";
                marcarFretePendente();
                sessionStorage.removeItem("cep_digitado");
            }

            atualizarBotaoConfirmar();
        });

        cepEnderecoInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter") { e.preventDefault(); buscarCep(false); }
        });
    }

    // ================================================================
    // MÁSCARA + SYNC CEP FRETE → ENDEREÇO
    // ================================================================
    if (cepFreteInput) {
        cepFreteInput.addEventListener("input", () => {
            let v = cepFreteInput.value.replace(/\D/g, "").substring(0, 8);
            if (v.length > 5) v = v.slice(0, 5) + "-" + v.slice(5);
            cepFreteInput.value = v;

            if (cepEnderecoInput) cepEnderecoInput.value = v;

            const cepLimpo = v.replace(/\D/g, "");

            if (cepLimpo.length === 8) handleCepComplete(cepLimpo);

            if (cepLimpo.length === 0) {
                if (freteResultado) {
                    freteResultado.innerHTML = "";
                    freteResultado.style.display = "none";
                }
                const rua = document.getElementById("endereco-rua");
                const bairro = document.getElementById("endereco-bairro");
                const cidade = document.getElementById("endereco-cidade");
                const estado = document.getElementById("endereco-estado");
                if (rua) rua.value = "";
                if (bairro) bairro.value = "";
                if (cidade) cidade.value = "";
                if (estado) estado.value = "";
                if (cepEnderecoInput) cepEnderecoInput.value = "";

                fetch("/carrinho/frete/limpar/", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCSRFToken(),
                        "X-Requested-With": "XMLHttpRequest"
                    }
                });

                marcarFretePendente();
                sessionStorage.removeItem("cep_digitado");
                atualizarBotaoConfirmar();
            }
        });

        cepFreteInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter") { e.preventDefault(); btnCalcularFrete?.click(); }
        });
    }

    // ================================================================
    // CALCULAR FRETE
    // ================================================================
    if (btnCalcularFrete) {
        btnCalcularFrete.addEventListener("click", function () {
            const cep = cepFreteInput?.value.replace(/\D/g, "");
            if (!cep || cep.length !== 8) { alert("CEP inválido"); return; }

            if (cepEnderecoInput) {
                cepEnderecoInput.value = cep.slice(0, 5) + "-" + cep.slice(5);
            }

            sessionStorage.setItem("cep_digitado", cep);

            btnCalcularFrete.disabled = true;
            btnCalcularFrete.textContent = "Calculando...";

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
                    btnCalcularFrete.disabled = false;
                    btnCalcularFrete.textContent = "Calcular";

                    if (data.status === "erro") {
                        if (freteResultado) setFreteErro(freteResultado, data.mensagem);
                        return;
                    }

                    if (freteResultado) {
                        freteResultado.innerHTML = "";
                        const wrapper = document.createElement("div");
                        wrapper.className = "frete-opcoes";

                        data.opcoes.forEach((opcao, index) => {
                            const label = document.createElement("label");
                            label.className = `frete-opcao${index === 0 ? " selecionada" : ""}`;

                            const radio = document.createElement("input");
                            radio.type = "radio";
                            radio.name = "frete-opcao-checkout";
                            radio.value = opcao.id;
                            radio.dataset.valor = opcao.preco;
                            radio.dataset.nome = opcao.nome;
                            radio.dataset.prazo = opcao.prazo;
                            radio.dataset.transportadora = opcao.transportadora;
                            if (index === 0) radio.checked = true;

                            const info = document.createElement("div");
                            info.className = "frete-opcao-info";

                            const nomeSpan = document.createElement("span");
                            nomeSpan.className = "frete-opcao-nome";
                            nomeSpan.textContent = `${opcao.transportadora} — ${opcao.nome}`;

                            const prazoSpan = document.createElement("span");
                            prazoSpan.className = "frete-opcao-prazo";
                            prazoSpan.textContent = `${opcao.prazo} dia(s) úteis`;

                            info.appendChild(nomeSpan);
                            info.appendChild(prazoSpan);

                            const precoSpan = document.createElement("span");
                            precoSpan.className = "frete-opcao-preco";
                            precoSpan.textContent = `R$ ${parseFloat(opcao.preco).toFixed(2).replace(".", ",")}`;

                            label.appendChild(radio);
                            label.appendChild(info);
                            label.appendChild(precoSpan);
                            wrapper.appendChild(label);
                        });

                        freteResultado.appendChild(wrapper);
                        freteResultado.style.display = "block";
                    }

                    selecionarOpcao(data.opcoes[0], cep);

                    const ruaAtual = document.getElementById("endereco-rua")?.value.trim();
                    if (!ruaAtual) setTimeout(() => buscarCep(true), 200);

                    document.querySelectorAll('input[name="frete-opcao-checkout"]').forEach(radio => {
                        radio.addEventListener("change", function () {
                            document.querySelectorAll(".frete-opcao").forEach(el => el.classList.remove("selecionada"));
                            this.closest(".frete-opcao").classList.add("selecionada");
                            selecionarOpcao({
                                id: this.value,
                                preco: this.dataset.valor,
                                nome: this.dataset.nome,
                                prazo: this.dataset.prazo,
                                transportadora: this.dataset.transportadora,
                            }, cep);
                        });
                    });
                });
        });
    }

    // ================================================================
    // SELECIONAR OPÇÃO DE FRETE
    // ================================================================
    function selecionarOpcao(opcao, cep) {
        sessionStorage.setItem("frete_selecionado_id", String(opcao.id));

        fetch("/carrinho/frete/selecionar/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
                "X-Requested-With": "XMLHttpRequest"
            },
            body: JSON.stringify({
                id: opcao.id,
                valor: opcao.preco,
                nome: opcao.nome,
                prazo: opcao.prazo,
                transportadora: opcao.transportadora,
                cep: cep,
            })
        }).then(() => {
            const subtotalEl = document.querySelector(".checkout-linha span:last-child");
            const subtotal = parseFloat(subtotalEl?.innerText.replace("R$", "").replace(",", ".").trim() || 0);
            const frete = parseFloat(opcao.preco) || 0;

            if (totalEl) {
                totalEl.textContent = `R$ ${(subtotal + frete).toFixed(2).replace(".", ",")}`;
            }

            setLinhaFrete(
                linhafretePendente,
                `Frete (${opcao.transportadora} — ${opcao.nome})`,
                `R$ ${parseFloat(opcao.preco).toFixed(2).replace(".", ",")}`
            );
            if (linhafretePendente) linhafretePendente.classList.remove("frete-pendente");

            setLinhaFrete(
                linhaFreteAtual,
                `Frete (${opcao.nome})`,
                `R$ ${parseFloat(opcao.preco).toFixed(2).replace(".", ",")}`
            );

            atualizarBotaoConfirmar();
        });
    }

    // ================================================================
    // SUBMIT — garante nome_completo correto e valida WhatsApp
    // ================================================================
    if (formCheckout) {
        formCheckout.addEventListener("submit", function (e) {
            const isRetirada = radioRetirada?.checked;

            if (isRetirada) {
                // Copia nome do campo de retirada para o campo principal
                const nomeRet = document.getElementById("retirada-nome");
                const nomeEnt = document.getElementById("endereco-nome");
                if (nomeRet && nomeEnt) nomeEnt.value = nomeRet.value;

                // Valida WhatsApp
                const wpp = document.getElementById("retirada-whatsapp");
                const wppLimpo = wpp?.value.replace(/\D/g, "") || "";
                if (wppLimpo.length < 10) {
                    e.preventDefault();
                    alert("Por favor, informe seu WhatsApp para combinarmos a retirada.");
                    wpp?.focus();
                    return;
                }
            }
        });
    }

    // ================================================================
    // ESTADO INICIAL
    // ================================================================
    atualizarBotaoConfirmar();
});