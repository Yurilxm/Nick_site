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
// Valida que a URL é interna (mesma origem)
// =============================================
function urlSegura(url) {
    if (!url) return null;
    try {
        const parsed = new URL(url, window.location.origin);
        if (parsed.origin === window.location.origin) {
            return parsed.pathname + parsed.search + parsed.hash;
        }
    } catch (_) { /* URL inválida */ }
    return null;
}

// =============================================
// POLLING — verifica pagamento a cada 5s
// =============================================
const polling = setInterval(() => {
    const verificarUrl = urlSegura(window.VERIFICAR_PAGAMENTO_URL);
    if (!verificarUrl) return;

    fetch(verificarUrl)
        .then(r => r.json())
        .then(data => {
            if (data.pago) {
                clearInterval(polling);
                clearInterval(interval);
                const destino = urlSegura(window.PEDIDO_CONFIRMADO_URL);
                if (destino) window.location.href = destino;
            }
        })
        .catch(() => {}); // silencioso
}, 5000);