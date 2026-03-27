document.querySelectorAll('.metodo-aba').forEach(aba => {
    aba.addEventListener('click', () => {
        document.querySelectorAll('.metodo-aba').forEach(a => a.classList.remove('ativa'));
        document.querySelectorAll('.metodo-painel').forEach(p => p.classList.remove('ativo'));
        aba.classList.add('ativa');
        document.getElementById('painel-' + aba.dataset.metodo).classList.add('ativo');
    });
});

// =============================================
// MÁSCARA DE CPF
// =============================================
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

const cpfInputs = document.querySelectorAll('#cpf, #cpf-boleto');
cpfInputs.forEach(input => {
    input.addEventListener('input', e => mascaraCPF(e.target));
});

// =============================================
// MÁSCARAS DO CARTÃO
// =============================================
const campoNumero = document.getElementById('card-number');
const campoValidade = document.getElementById('card-expiry');

if (campoNumero) {
    campoNumero.addEventListener('input', e => {
        let v = e.target.value.replace(/\D/g, '').substring(0, 16);
        e.target.value = v.replace(/(.{4})/g, '$1 ').trim();
        carregarParcelas();
    });
}

if (campoValidade) {
    campoValidade.addEventListener('input', e => {
        let v = e.target.value.replace(/\D/g, '').substring(0, 4);
        if (v.length > 2) v = v.slice(0, 2) + '/' + v.slice(2);
        e.target.value = v;
    });
}

// =============================================
// DETECÇÃO DE BANDEIRA
// =============================================
function detectarBandeira(numero) {
    const n = numero.replace(/\s/g, '');
    if (/^4/.test(n)) return 'visa';
    if (/^(5[1-5]|2[2-7]|50[0-9])/.test(n)) return 'master';
    if (/^3[47]/.test(n)) return 'amex';
    if (/^(636368|438935|504175|451416|509)/.test(n)) return 'elo';
    return 'master';
}

// =============================================
// PARCELAS VIA AJAX
// =============================================
let parcelasTimeout;

function carregarParcelas() {
    clearTimeout(parcelasTimeout);
    parcelasTimeout = setTimeout(() => {
        const numero = (campoNumero?.value || '').replace(/\s/g, '');
        if (numero.length < 6) return;

        const bandeira = detectarBandeira(numero);
        const valor = (window.TOTAL_GERAL || '0').replace(',', '.');
        const url = `${window.PARCELAS_URL}?valor=${valor}&bandeira=${bandeira}`;

        fetch(url)
            .then(r => r.json())
            .then(data => {
                const sel = document.getElementById('select-parcelas');
                if (!sel || !Array.isArray(data) || !data.length) return;

                sel.innerHTML = '';
                data.forEach(p => {
                    const opt = document.createElement('option');
                    opt.value = p.numero;
                    const parcela = Number(p.valor_parcela).toLocaleString('pt-BR', { minimumFractionDigits: 2 });
                    const total = Number(p.valor_total).toLocaleString('pt-BR', { minimumFractionDigits: 2 });

                    if (p.sem_juros) {
                        opt.textContent = `${p.numero}x de R$ ${parcela} sem juros`;
                    } else {
                        opt.textContent = `${p.numero}x de R$ ${parcela} (total R$ ${total})`;
                    }

                    sel.appendChild(opt);
                });

                sel.onchange = () => {
                    document.getElementById('parcelas-hidden').value = sel.value;
                };
                sel.dispatchEvent(new Event('change'));
            })
            .catch(() => { });
    }, 600);
}

// =============================================
// MERCADO PAGO — TOKENIZAÇÃO (CARTÃO)
// =============================================
let mp;
if (window.MP_PUBLIC_KEY) {
    mp = new MercadoPago(window.MP_PUBLIC_KEY, { locale: 'pt-BR' });
}

document.getElementById('form-cartao')?.addEventListener('submit', async function (e) {
    e.preventDefault();

    const btn = document.getElementById('btn-pagar-cartao');
    const erroEl = document.getElementById('cartao-erro');
    erroEl.textContent = '';
    btn.disabled = true;
    btn.textContent = 'Processando...';

    // Valida CPF
    const cpf = document.getElementById('cpf').value.replace(/\D/g, '');
    if (!cpf || cpf.length !== 11) {
        erroEl.textContent = 'CPF inválido. Digite um CPF válido.';
        btn.disabled = false;
        btn.textContent = 'Pagar com cartão';
        return;
    }

    const numero = document.getElementById('card-number').value.replace(/\s/g, '');
    const nome = document.getElementById('card-name').value;
    const validade = document.getElementById('card-expiry').value;
    const cvv = document.getElementById('card-cvv').value;
    const [mes, ano] = (validade || '/').split('/');

    if (!numero || !nome || !mes || !ano || !cvv) {
        erroEl.textContent = 'Preencha todos os campos do cartão.';
        btn.disabled = false;
        btn.textContent = 'Pagar com cartão';
        return;
    }

    if (!mp) {
        erroEl.textContent = 'Gateway de pagamento não configurado.';
        btn.disabled = false;
        btn.textContent = 'Pagar com cartão';
        return;
    }

    try {
        const token = await mp.createCardToken({
            cardNumber: numero,
            cardholderName: nome,
            cardExpirationMonth: mes,
            cardExpirationYear: '20' + ano,
            securityCode: cvv,
        });

        document.getElementById('card-token').value = token.id;
        document.getElementById('parcelas-hidden').value =
            document.getElementById('select-parcelas').value || '1';
        document.getElementById('card-bandeira').value = detectarBandeira(numero);

        this.submit();

    } catch (err) {
        const msg = err?.cause?.[0]?.description
            || 'Erro ao processar cartão. Verifique os dados e tente novamente.';
        erroEl.textContent = msg;
        btn.disabled = false;
        btn.textContent = 'Pagar com cartão';
    }
});

// =============================================
// BOLETO – garante envio do CPF
// =============================================
document.getElementById('form-boleto')?.addEventListener('submit', function(e) {
    const cpf = document.getElementById('cpf-boleto').value.replace(/\D/g, '');
    if (!cpf || cpf.length !== 11) {
        e.preventDefault();
        alert('CPF inválido. Digite um CPF válido para gerar o boleto.');
    }
});


// =============================================
// BOTÕES - ATIVAR COM CPF (CARTÃO + BOLETO)
// =============================================
const cpfCartao = document.getElementById("cpf");
const btnCartao = document.getElementById("btn-pagar-cartao");

const cpfBoleto = document.getElementById("cpf-boleto");
const btnBoleto = document.getElementById("btn-boleto");

function validarCPFInput(input, button) {
    if (!input || !button) return;

    input.addEventListener("input", () => {
        const cpfLimpo = input.value.replace(/\D/g, "");
        button.disabled = cpfLimpo.length !== 11;
    });
}

// aplica nos dois
validarCPFInput(cpfCartao, btnCartao);
validarCPFInput(cpfBoleto, btnBoleto);