document.addEventListener("DOMContentLoaded", function () {

    const cepEnderecoInput = document.getElementById("endereco-cep");
    const btnBuscarCep = document.getElementById("btn-buscar-cep");
    const btnConfirmar = document.getElementById("btn-confirmar");
    const linhafretePendente = document.getElementById("linha-frete-pendente");
    const linhaFreteAtual = document.getElementById("linha-frete-atual");
    const totalEl = document.getElementById("total-geral-checkout");
    const btnAlterar = document.getElementById("btn-alterar-frete");
    const freteBox = document.getElementById("frete-box-checkout");

    // Campos de frete do resumo (podem não existir se frete já está calculado e box está oculto)
    const cepFreteInput = document.getElementById("cep-input-checkout");
    const btnCalcularFrete = document.getElementById("btn-calcular-frete-checkout");
    const freteResultado = document.getElementById("frete-resultado-checkout");

    function getCSRFToken() {
        return document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";
    }

    // ==========================
    // BOTÃO ALTERAR FRETE
    // ==========================
    btnAlterar?.addEventListener("click", function () {
        freteBox.style.display = "block";
        this.style.display = "none";
        const cepSalvo = sessionStorage.getItem('cep_digitado');
        if (cepSalvo && cepSalvo.length === 8 && cepFreteInput) {
            // ✅ Com máscara
            cepFreteInput.value = cepSalvo.slice(0, 5) + "-" + cepSalvo.slice(5);
        }
    });

    // ==========================
    // VALIDAÇÃO DO BOTÃO CONFIRMAR
    // ==========================
    function validarEndereco() {
        const cep = cepEnderecoInput?.value.replace(/\D/g, "");
        const rua = document.getElementById("endereco-rua")?.value.trim();
        const numero = document.getElementById("endereco-numero")?.value.trim();
        const bairro = document.getElementById("endereco-bairro")?.value.trim();
        const cidade = document.getElementById("endereco-cidade")?.value.trim();
        const estado = document.getElementById("endereco-estado")?.value.trim();
        return cep?.length === 8 && rua && numero && bairro && cidade && estado;
    }

    function atualizarBotaoConfirmar() {
        if (!btnConfirmar) return;
        // Se tem linha-frete-pendente ainda com classe pendente, frete não foi calculado
        const fretePendente = linhafretePendente?.classList.contains("frete-pendente");
        const enderecoOk = validarEndereco();
        const ok = enderecoOk && !fretePendente;

        btnConfirmar.disabled = !ok;
        btnConfirmar.style.opacity = ok ? "1" : "0.5";
        btnConfirmar.style.cursor = ok ? "pointer" : "not-allowed";
    }

    ["endereco-cep", "endereco-rua", "endereco-numero",
        "endereco-complemento", "endereco-bairro", "endereco-cidade", "endereco-estado"
    ].forEach(id => {
        document.getElementById(id)?.addEventListener("input", atualizarBotaoConfirmar);
    });

    // ==========================
    // BUSCA CEP VIA VIACEP
    // ==========================
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

        fetch(`https://viacep.com.br/ws/${cep}/json/`)
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

                document.getElementById("endereco-rua").value = data.logradouro || "";
                document.getElementById("endereco-bairro").value = data.bairro || "";
                document.getElementById("endereco-cidade").value = data.localidade || "";
                document.getElementById("endereco-estado").value = data.uf || "";

                // Espelha CEP no campo de frete
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

    btnBuscarCep?.addEventListener("click", () => buscarCep(false));

    // ==========================
    // MÁSCARA + AUTOCOMPLETE CEP ENDEREÇO
    // ==========================
    cepEnderecoInput?.addEventListener("input", (e) => {
        let v = e.target.value.replace(/\D/g, "").substring(0, 8);
        if (v.length > 5) v = v.slice(0, 5) + "-" + v.slice(5);
        e.target.value = v;

        const cepLimpo = v.replace(/\D/g, "");

        // Espelha no campo de frete
        if (cepFreteInput) cepFreteInput.value = v;

        // CEP completo → busca endereço automaticamente
        if (cepLimpo.length === 8) {
            clearTimeout(window.cepEnderecoTimeout);
            window.cepEnderecoTimeout = setTimeout(() => {
                buscarCep(true);
                // Se ainda não tem frete calculado, calcula automaticamente
                if (linhafretePendente?.classList.contains("frete-pendente")) {
                    setTimeout(() => btnCalcularFrete?.click(), 400);
                }
            }, 500);
        }

        // CEP apagado → limpa campos
        if (cepLimpo.length === 0) {
            document.getElementById("endereco-rua").value = "";
            document.getElementById("endereco-bairro").value = "";
            document.getElementById("endereco-cidade").value = "";
            document.getElementById("endereco-estado").value = "";
            if (cepFreteInput) cepFreteInput.value = "";
        }

        atualizarBotaoConfirmar();
    });

    cepEnderecoInput?.addEventListener("keydown", (e) => {
        if (e.key === "Enter") { e.preventDefault(); buscarCep(false); }
    });

    // ==========================
    // MÁSCARA + SYNC CEP FRETE → ENDEREÇO
    // ==========================
    cepFreteInput?.addEventListener("input", () => {
        let v = cepFreteInput.value.replace(/\D/g, "").substring(0, 8);
        if (v.length > 5) v = v.slice(0, 5) + "-" + v.slice(5);
        cepFreteInput.value = v;

        // Espelha no campo de endereço
        if (cepEnderecoInput) cepEnderecoInput.value = v;

        const cepLimpo = v.replace(/\D/g, "");

        // CEP completo → busca endereço automaticamente
        if (cepLimpo.length === 8) {
            clearTimeout(window.cepFreteTimeout);
            window.cepFreteTimeout = setTimeout(() => buscarCep(true), 500);
        }

        if (cepLimpo.length === 0) {
            // Some as opções
            if (freteResultado) {
                freteResultado.innerHTML = "";
                freteResultado.style.display = "none";
            }

            // Limpa endereço
            document.getElementById("endereco-rua").value = "";
            document.getElementById("endereco-bairro").value = "";
            document.getElementById("endereco-cidade").value = "";
            document.getElementById("endereco-estado").value = "";
            if (cepEnderecoInput) cepEnderecoInput.value = "";

            // Limpa frete na sessão Django
            fetch("/carrinho/frete/limpar/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                    "X-Requested-With": "XMLHttpRequest"
                }
            });

            // Volta linha de frete para pendente
            if (linhafretePendente) {
                linhafretePendente.innerHTML = `<span>Frete</span><span>A calcular</span>`;
                linhafretePendente.classList.add("frete-pendente");
            }
            if (linhaFreteAtual) {
                linhaFreteAtual.innerHTML = `<span>Frete</span><span>A calcular</span>`;
            }

            sessionStorage.removeItem('cep_digitado');
            atualizarBotaoConfirmar();
        }
    });

    cepFreteInput?.addEventListener("keydown", (e) => {
        if (e.key === "Enter") { e.preventDefault(); btnCalcularFrete?.click(); }
    });

    // ==========================
    // CALCULAR FRETE
    // ==========================
    btnCalcularFrete?.addEventListener("click", function () {
        const cep = cepFreteInput?.value.replace(/\D/g, "");
        if (!cep || cep.length !== 8) { alert("CEP inválido"); return; }

        // Garante que CEP de endereço também está preenchido
        if (cepEnderecoInput) {
            cepEnderecoInput.value = cep.slice(0, 5) + "-" + cep.slice(5);
        }

        sessionStorage.setItem('cep_digitado', cep);

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
                    if (freteResultado) {
                        freteResultado.innerHTML = `<p class="frete-erro">${data.mensagem}</p>`;
                        freteResultado.style.display = "block";
                    }
                    return;
                }

                let html = '<div class="frete-opcoes">';
                data.opcoes.forEach((opcao, index) => {
                    html += `
                        <label class="frete-opcao ${index === 0 ? 'selecionada' : ''}">
                            <input type="radio" name="frete-opcao-checkout" value="${opcao.id}"
                                data-valor="${opcao.preco}" data-nome="${opcao.nome}"
                                data-prazo="${opcao.prazo}" data-transportadora="${opcao.transportadora}"
                                ${index === 0 ? 'checked' : ''}>
                            <div class="frete-opcao-info">
                                <span class="frete-opcao-nome">${opcao.transportadora} — ${opcao.nome}</span>
                                <span class="frete-opcao-prazo">${opcao.prazo} dia(s) úteis</span>
                            </div>
                            <span class="frete-opcao-preco">R$ ${parseFloat(opcao.preco).toFixed(2).replace(".", ",")}</span>
                        </label>`;
                });
                html += '</div>';

                if (freteResultado) {
                    freteResultado.innerHTML = html;
                    freteResultado.style.display = "block";
                }

                selecionarOpcao(data.opcoes[0], cep);

                const ruaAtual = document.getElementById("endereco-rua")?.value.trim();
                if (!ruaAtual) {
                    setTimeout(() => buscarCep(true), 200);
                }

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

    // ==========================
    // SELECIONAR OPÇÃO DE FRETE
    // ==========================
    function selecionarOpcao(opcao, cep) {
        sessionStorage.setItem('frete_selecionado_id', String(opcao.id));

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

            if (totalEl) totalEl.innerText = `R$ ${(subtotal + frete).toFixed(2).replace(".", ",")}`;

            // Atualiza linha de frete pendente → calculado
            if (linhafretePendente) {
                linhafretePendente.innerHTML = `
                    <span>Frete (${opcao.transportadora} — ${opcao.nome})</span>
                    <span>R$ ${parseFloat(opcao.preco).toFixed(2).replace(".", ",")}</span>
                `;
                linhafretePendente.classList.remove("frete-pendente");
            }

            // Atualiza linha de frete já existente (caso "Alterar")
            if (linhaFreteAtual) {
                linhaFreteAtual.innerHTML = `
                    <span>Frete (${opcao.nome})</span>
                    <span>R$ ${parseFloat(opcao.preco).toFixed(2).replace(".", ",")}</span>
                `;
            }

            atualizarBotaoConfirmar();
        });
    }

    // ==========================
    // ESTADO INICIAL
    // ==========================
    atualizarBotaoConfirmar();
});