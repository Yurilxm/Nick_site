document.addEventListener('DOMContentLoaded', function () {
    const cepInput = document.getElementById("cep");

    if (!cepInput) return;

    const fields = {
        rua: document.getElementById("rua"),
        bairro: document.getElementById("bairro"),
        cidade: document.getElementById("cidade"),
        estado: document.getElementById("estado"),
    };

    let timeout = null;
    let lastCep = "";

    // limpa todos os campos de endereço
    function clearAddress() {
        Object.values(fields).forEach(el => {
            if (el) el.value = "";
        });
    }

    // bloqueia/desbloqueia campos durante a busca
    function setLoading(status) {
        Object.values(fields).forEach(el => {
            if (el) el.disabled = status;
        });
    }

    cepInput.addEventListener("input", function () {
        clearTimeout(timeout);

        const cep = this.value.replace(/\D/g, "");

        // se apagou o CEP → limpa tudo
        if (cep.length === 0) {
            clearAddress();
            lastCep = "";
            return;
        }

        // evita requisição repetida pro mesmo CEP
        if (cep === lastCep) return;

        timeout = setTimeout(() => {
            // se ainda não tem 8 dígitos, só limpa e espera
            if (cep.length < 8) {
                clearAddress();
                return;
            }

            // trava UI enquanto busca
            setLoading(true);

            fetch(`/ajax/cep/?cep=${cep}`)
                .then(res => res.json())
                .then(data => {
                    setLoading(false);

                    if (data.erro) {
                        clearAddress();
                        return;
                    }

                    // preenche automaticamente
                    if (fields.rua) fields.rua.value = data.logradouro || "";
                    if (fields.bairro) fields.bairro.value = data.bairro || "";
                    if (fields.cidade) fields.cidade.value = data.localidade || "";
                    if (fields.estado) fields.estado.value = data.uf || "";

                    lastCep = cep;
                })
                .catch(() => {
                    setLoading(false);
                    clearAddress();
                });

        }, 450);
    });
});


document.addEventListener('DOMContentLoaded', function () {
    const cpfInput = document.querySelector('input[name="cpf"]');

    function mascaraCPF(input) {
        let value = input.value.replace(/\D/g, '');
        if (value.length > 11) value = value.slice(0, 11);
        if (value.length > 9) {
            value = value.replace(/^(\d{3})(\d{3})(\d{3})(\d{2})$/, '$1.$2.$3-$4');
        } else if (value.length > 6) {
            value = value.replace(/^(\d{3})(\d{3})(\d{0,3})$/, '$1.$2.$3');
        } else if (value.length > 3) {
            value = value.replace(/^(\d{3})(\d{0,3})$/, '$1.$2');
        }
        input.value = value;
    }

    if (cpfInput) {
        // Formata o CPF existente ao carregar
        if (cpfInput.value) {
            mascaraCPF(cpfInput);
        }

        // Aplica a máscara enquanto digita
        cpfInput.addEventListener('input', function (e) {
            mascaraCPF(e.target);
        });
    }
});