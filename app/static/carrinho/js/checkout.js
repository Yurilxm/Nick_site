document.addEventListener("DOMContentLoaded", function () {

    const cepInput = document.getElementById("cep-input-checkout");
    const btnCalcular = document.getElementById("btn-calcular-frete-checkout");
    const freteResultado = document.getElementById("frete-resultado-checkout");
    const btnConfirmar = document.getElementById("btn-confirmar");
    const totalEl = document.getElementById("total-geral-checkout");
    const linhafretePendente = document.getElementById("linha-frete-pendente");
    const cepEnderecoInput = document.getElementById("endereco-cep");
    const btnBuscarCep = document.getElementById("btn-buscar-cep");

    if (!btnCalcular) return;

    function getCSRFToken() {
        return document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";
    }

    // ==========================
    // VERIFICAR SE CEP FOI APAGADO NO CARRINHO
    // ==========================
    function verificarCepApagado() {
        const foiApagado = sessionStorage.getItem('cep_foi_apagado') === 'true';
        const cepBackend = document.getElementById("endereco-cep")?.value.replace(/\D/g, "");

        // Se foi apagado no carrinho OU backend está vazio, limpa tudo
        if (foiApagado || !cepBackend || cepBackend.length === 0) {
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

            // Limpa os campos do formulário também
            [
                "endereco-cep",
                "endereco-rua",
                "endereco-numero",
                "endereco-complemento",
                "endereco-bairro",
                "endereco-cidade",
                "endereco-estado"
            ].forEach(id => {
                const el = document.getElementById(id);
                if (el) el.value = "";
            });

            sessionStorage.removeItem('cep_foi_apagado');
            return true;
        }
        return false;
    }

    // ==========================
    // SALVAR ENDEREÇO
    // ==========================
    function salvarEndereco() {
        const endereco = {
            cep: document.getElementById("endereco-cep")?.value.replace(/\D/g, "") || "",
            rua: document.getElementById("endereco-rua")?.value || "",
            numero: document.getElementById("endereco-numero")?.value || "",
            complemento: document.getElementById("endereco-complemento")?.value || "",
            bairro: document.getElementById("endereco-bairro")?.value || "",
            cidade: document.getElementById("endereco-cidade")?.value || "",
            estado: document.getElementById("endereco-estado")?.value || "",
        };

        // Salva no sessionStorage
        Object.entries(endereco).forEach(([key, val]) => {
            sessionStorage.setItem(`endereco_${key}`, val);
        });

        // Salva na sessão do Django
        fetch("/carrinho/endereco/salvar/", {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-CSRFToken": getCSRFToken(), "X-Requested-With": "XMLHttpRequest" },
            body: JSON.stringify(endereco)
        });
    }

    function restaurarEndereco() {
        // Primeiro: verifica se o CEP foi apagado no carrinho
        if (verificarCepApagado()) {
            return;
        }

        // Só tenta restaurar do sessionStorage se tiver dados
        const campos = {
            "endereco-rua": sessionStorage.getItem("endereco_rua"),
            "endereco-numero": sessionStorage.getItem("endereco_numero"),
            "endereco-complemento": sessionStorage.getItem("endereco_complemento"),
            "endereco-bairro": sessionStorage.getItem("endereco_bairro"),
            "endereco-cidade": sessionStorage.getItem("endereco_cidade"),
            "endereco-estado": sessionStorage.getItem("endereco_estado"),
        };

        let preencheuAlgo = false;
        Object.entries(campos).forEach(([id, valor]) => {
            if (valor) {
                const el = document.getElementById(id);
                if (el) {
                    el.value = valor;
                    preencheuAlgo = true;
                }
            }
        });

        if (!preencheuAlgo) {
            const cepBackend = document.getElementById("endereco-cep")?.value.replace(/\D/g, "");
            if (cepBackend && cepBackend.length === 8) {
                setTimeout(() => buscarCep(true), 200);
            }
        }
    }

    // ==========================
    // VALIDAÇÃO BOTÃO CONFIRMAR
    // ==========================
    function validarEndereco() {
        const cep = document.getElementById("endereco-cep")?.value.replace(/\D/g, "");
        const rua = document.getElementById("endereco-rua")?.value.trim();
        const numero = document.getElementById("endereco-numero")?.value.trim();
        const bairro = document.getElementById("endereco-bairro")?.value.trim();
        const cidade = document.getElementById("endereco-cidade")?.value.trim();
        const estado = document.getElementById("endereco-estado")?.value.trim();
        return cep?.length === 8 && rua && numero && bairro && cidade && estado;
    }

    function atualizarBotaoConfirmar() {
        if (!btnConfirmar) return;
        const temFrete = linhafretePendente
            ? !linhafretePendente.classList.contains("frete-pendente")
            : true;
        if (validarEndereco() && temFrete) {
            btnConfirmar.disabled = false;
            btnConfirmar.style.opacity = "1";
            btnConfirmar.style.cursor = "pointer";
        } else {
            btnConfirmar.disabled = true;
            btnConfirmar.style.opacity = "0.5";
            btnConfirmar.style.cursor = "not-allowed";
        }
    }

    ["endereco-cep", "endereco-rua", "endereco-numero", "endereco-complemento",
        "endereco-bairro", "endereco-cidade", "endereco-estado"].forEach(id => {
            document.getElementById(id)?.addEventListener("input", () => {
                salvarEndereco();
                atualizarBotaoConfirmar();
            });
        });

    // ==========================
    // BUSCA CEP VIA VIACEP
    // ==========================
    function buscarCep(silencioso = false) {
        console.log("Buscando CEP:", cepEnderecoInput?.value);

        const cep = cepEnderecoInput?.value.replace(/\D/g, "");
        if (!cep || cep.length !== 8) {
            if (!silencioso) alert("Digite um CEP válido");
            return;
        }

        // Remove flag de apagado ao buscar novo CEP
        sessionStorage.removeItem('cep_foi_apagado');

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
                salvarEndereco();

                if (!silencioso) document.getElementById("endereco-numero")?.focus();

                sessionStorage.setItem("cep_digitado", cep);

                // Sincroniza campo de frete
                if (cepInput) {
                    cepInput.value = cep.slice(0, 5) + "-" + cep.slice(5);
                }

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
    cepEnderecoInput?.addEventListener("keydown", (e) => {
        if (e.key === "Enter") { e.preventDefault(); buscarCep(false); }
    });

    // ==========================
    // MÁSCARA + AUTOCOMPLETE PROFISSIONAL
    // ==========================
    cepEnderecoInput?.addEventListener("input", (e) => {
        let v = e.target.value.replace(/\D/g, "").substring(0, 8);
        if (v.length > 5) v = v.slice(0, 5) + "-" + v.slice(5);
        e.target.value = v;

        if (cepInput) cepInput.value = v;

        const cepLimpo = v.replace(/\D/g, "");

        // Se está digitando, remove flag de apagado
        if (cepLimpo.length > 0) {
            sessionStorage.removeItem('cep_foi_apagado');
        }

        sessionStorage.setItem("cep_digitado", cepLimpo);

        // 🔥 AUTOCOMPLETE PROFISSIONAL quando CEP completo
        if (cepLimpo.length === 8) {
            // Cancela qualquer timeout anterior
            clearTimeout(window.cepTimeout);

            // Só executa após 500ms sem digitar
            window.cepTimeout = setTimeout(() => {
                // Busca endereço automaticamente
                buscarCep(true);

                // Calcula frete automaticamente (com um pequeno delay extra)
                setTimeout(() => {
                    if (btnCalcular) btnCalcular.click();
                }, 300);
            }, 500);
        }

        // Limpeza quando apaga o CEP
        if (cepLimpo.length === 0) {
            // Marca que foi apagado
            sessionStorage.setItem('cep_foi_apagado', 'true');

            document.getElementById("endereco-rua").value = "";
            document.getElementById("endereco-bairro").value = "";
            document.getElementById("endereco-cidade").value = "";
            document.getElementById("endereco-estado").value = "";
            salvarEndereco();

            if (freteResultado) freteResultado.style.display = "none";
            if (linhafretePendente) {
                linhafretePendente.innerHTML = `<span>Frete</span><span>A calcular</span>`;
                linhafretePendente.classList.add("frete-pendente");
            }
            fetch("/carrinho/frete/limpar/", {
                method: "POST",
                headers: { "X-CSRFToken": getCSRFToken(), "X-Requested-With": "XMLHttpRequest" }
            });
        }

        atualizarBotaoConfirmar();
    });


    // CARREGA CEP E ENDEREÇO SALVOS AO ENTRAR NA PÁGINA
    restaurarEndereco();

    const cepSalvo = sessionStorage.getItem("cep_digitado");
    const cepBackend = cepEnderecoInput?.value.replace(/\D/g, "");

    // Só usa cepSalvo se NÃO tiver sido apagado
    const foiApagado = sessionStorage.getItem('cep_foi_apagado') === 'true';
    const cepFinal = !foiApagado && cepSalvo && cepSalvo.length === 8 ? cepSalvo : cepBackend;

    if (cepFinal && cepFinal.length === 8 && !foiApagado) {

        const formatado = cepFinal.slice(0, 5) + "-" + cepFinal.slice(5);

        if (cepEnderecoInput) cepEnderecoInput.value = formatado;
        if (cepInput && !cepInput.value) cepInput.value = formatado;

        // 🔥 SEMPRE BUSCA O ENDEREÇO AO CARREGAR
        setTimeout(() => buscarCep(true), 300);

        // 🔥 E CALCULA FRETE AO CARREGAR
        setTimeout(() => btnCalcular?.click(), 600);
    }

    // ==========================
    // CEP FRETE — ENTER + LIMPAR + SINCRONIZA ENDEREÇO
    // ==========================
    cepInput?.addEventListener("keydown", (e) => {
        if (e.key === "Enter") { e.preventDefault(); btnCalcular.click(); }
    });

    cepInput?.addEventListener("input", () => {
        const v = cepInput.value;
        if (cepEnderecoInput) {
            cepEnderecoInput.value = v;

            const cepLimpo = v.replace(/\D/g, "");

            // Se está digitando, remove flag de apagado
            if (cepLimpo.length > 0) {
                sessionStorage.removeItem('cep_foi_apagado');
            }

            sessionStorage.setItem("cep_digitado", cepLimpo);
        }

        // CEP completo — busca endereço automaticamente
        if (v.replace(/\D/g, "").length === 8) {
            setTimeout(() => buscarCep(true), 400);
        }

        if (v.replace(/\D/g, "").length === 0) {

            // Marca que foi apagado
            sessionStorage.setItem('cep_foi_apagado', 'true');

            // 🔥 LIMPA CAMPOS DE ENDEREÇO
            [
                "endereco-cep",
                "endereco-rua",
                "endereco-numero",
                "endereco-complemento",
                "endereco-bairro",
                "endereco-cidade",
                "endereco-estado"
            ].forEach(id => {
                const el = document.getElementById(id);
                if (el) el.value = "";
            });

            // 🔥 LIMPA SESSION STORAGE
            [
                "cep_digitado",
                "endereco_cep",
                "endereco_rua",
                "endereco_numero",
                "endereco_complemento",
                "endereco_bairro",
                "endereco_cidade",
                "endereco_estado"
            ].forEach(key => sessionStorage.removeItem(key));

            // 🔥 LIMPA ENDEREÇO NO BACKEND
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

            // 🔥 LIMPA FRETE
            if (freteResultado) freteResultado.style.display = "none";

            if (linhafretePendente) {
                linhafretePendente.innerHTML = `<span>Frete</span><span>A calcular</span>`;
                linhafretePendente.classList.add("frete-pendente");
            }

            fetch("/carrinho/frete/limpar/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                    "X-Requested-With": "XMLHttpRequest"
                }
            });

            // 🔥 ATUALIZA TOTAL
            const subtotal = parseFloat(
                document.querySelector(".checkout-linha span:last-child")
                    ?.innerText.replace("R$", "").replace(",", ".").trim() || 0
            );

            if (totalEl) {
                totalEl.innerText = `R$ ${subtotal.toFixed(2).replace(".", ",")}`;
            }

            atualizarBotaoConfirmar();
        }
    });

    // ==========================
    // CALCULAR FRETE
    // ==========================
    btnCalcular.addEventListener("click", function () {
        const cep = cepInput.value.replace(/\D/g, "");

        // Remove flag de apagado ao calcular novo CEP
        sessionStorage.removeItem('cep_foi_apagado');
        sessionStorage.setItem("cep_digitado", cep);

        if (cepEnderecoInput) {
            cepEnderecoInput.value = cep.length > 5 ? cep.slice(0, 5) + "-" + cep.slice(5) : cep;
        }

        if (cep.length !== 8) { alert("CEP inválido"); return; }

        btnCalcular.disabled = true;
        btnCalcular.textContent = "Calculando...";

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
                btnCalcular.disabled = false;
                btnCalcular.textContent = "Calcular";

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

                if (freteResultado) { freteResultado.innerHTML = html; freteResultado.style.display = "block"; }

                selecionarOpcao(data.opcoes[0], cep);

                document.querySelectorAll('input[name="frete-opcao-checkout"]').forEach(radio => {
                    radio.addEventListener("change", function () {
                        document.querySelectorAll(".frete-opcao").forEach(el => el.classList.remove("selecionada"));
                        this.closest(".frete-opcao").classList.add("selecionada");
                        selecionarOpcao({
                            id: this.value, preco: this.dataset.valor, nome: this.dataset.nome,
                            prazo: this.dataset.prazo, transportadora: this.dataset.transportadora,
                        }, cep);
                    });
                });
            });
    });

    // ==========================
    // SELECIONAR OPÇÃO DE FRETE
    // ==========================
    function selecionarOpcao(opcao, cep) {
        fetch("/carrinho/frete/selecionar/", {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-CSRFToken": getCSRFToken(), "X-Requested-With": "XMLHttpRequest" },
            body: JSON.stringify({
                id: opcao.id, valor: opcao.preco, nome: opcao.nome,
                prazo: opcao.prazo, transportadora: opcao.transportadora, cep: cep,
            })
        }).then(() => {
            const subtotal = parseFloat(
                document.querySelector(".checkout-linha span:last-child")
                    ?.innerText.replace("R$", "").replace(",", ".").trim() || 0
            );
            const frete = parseFloat(opcao.preco) || 0;
            if (totalEl) totalEl.innerText = `R$ ${(subtotal + frete).toFixed(2).replace(".", ",")}`;

            if (linhafretePendente) {
                linhafretePendente.innerHTML = `
                    <span>Frete (${opcao.transportadora} — ${opcao.nome})</span>
                    <span>R$ ${parseFloat(opcao.preco).toFixed(2).replace(".", ",")}</span>
                `;
                linhafretePendente.classList.remove("frete-pendente");
            }

            atualizarBotaoConfirmar();
        });
    }

    // Executa verificação inicial
    verificarCepApagado();
    atualizarBotaoConfirmar();

    // Garantir que se tiver CEP no campo, busque o endereço
    if (cepEnderecoInput && cepEnderecoInput.value.replace(/\D/g, "").length === 8) {
        setTimeout(() => buscarCep(true), 100);
    }

    // Verificação extra
    setTimeout(() => {
        const cepAtual = cepEnderecoInput?.value.replace(/\D/g, "");
        const ruaAtual = document.getElementById("endereco-rua")?.value.trim();
        const foiApagado = sessionStorage.getItem('cep_foi_apagado') === 'true';

        if (cepAtual && cepAtual.length === 8 && !ruaAtual && !foiApagado) {
            buscarCep(true);
        }
    }, 500);
});