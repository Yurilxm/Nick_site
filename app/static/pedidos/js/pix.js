document.getElementById('btn-copiar')?.addEventListener('click', () => {
    const input = document.getElementById('pix-codigo');
    const aviso = document.getElementById('pix-copiado');

    navigator.clipboard.writeText(input.value).then(() => {
        aviso.classList.add('visivel');
        setTimeout(() => aviso.classList.remove('visivel'), 3000);
    });
});

// =============================================
// TIMER 30 MINUTOS
// =============================================
let segundosRestantes = 30 * 60;

const timerEl = document.getElementById('tempo-restante');

const interval = setInterval(() => {
    segundosRestantes--;

    if (segundosRestantes <= 0) {
        clearInterval(interval);
        clearInterval(polling);
        timerEl.textContent = 'Expirado';
        timerEl.closest('.pix-timer').classList.add('expirado');
        return;
    }

    const m = String(Math.floor(segundosRestantes / 60)).padStart(2, '0');
    const s = String(segundosRestantes % 60).padStart(2, '0');
    timerEl.textContent = `${m}:${s}`;
}, 1000);

// =============================================
// POLLING — verifica pagamento a cada 5s
// =============================================
const polling = setInterval(() => {
    if (!window.VERIFICAR_PAGAMENTO_URL) return;

    fetch(window.VERIFICAR_PAGAMENTO_URL)
        .then(r => r.json())
        .then(data => {
            if (data.pago) {
                clearInterval(polling);
                clearInterval(interval);
                window.location.href = window.PEDIDO_CONFIRMADO_URL;
            }
        })
        .catch(() => {}); // silencioso
}, 5000);