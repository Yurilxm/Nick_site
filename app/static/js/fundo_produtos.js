document.addEventListener('DOMContentLoaded', () => {
  const emojis = document.querySelectorAll('.bg-emojis span');
  if (!emojis.length) return;

  let targetX = 0, targetY = 0;
  let currentX = 0, currentY = 0;
  let rafId = null;

  // Suaviza o movimento com lerp (interpolação linear)
  function lerp(a, b, t) { return a + (b - a) * t; }

  function animate() {
    currentX = lerp(currentX, targetX, 0.06);
    currentY = lerp(currentY, targetY, 0.06);

    emojis.forEach(emoji => {
      const speed = parseFloat(emoji.dataset.speed) || 1;
      const mx = currentX * speed * 25;
      const my = currentY * speed * 25;
      emoji.style.setProperty('--mx', `${mx}px`);
      emoji.style.setProperty('--my', `${my}px`);
    });

    rafId = requestAnimationFrame(animate);
  }

  document.addEventListener('mousemove', (e) => {
    targetX = (e.clientX / window.innerWidth) - 0.5;
    targetY = (e.clientY / window.innerHeight) - 0.5;
    if (!rafId) animate();
  });

  // Para o loop quando o mouse sai da janela
  document.addEventListener('mouseleave', () => {
    targetX = 0;
    targetY = 0;
  });
});