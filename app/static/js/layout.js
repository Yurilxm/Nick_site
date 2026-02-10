function ajustarAlturaTopbar() {
    const topbar = document.querySelector('.topbar');
    const siteContent = document.querySelector('.site-content');

    if (!topbar || !siteContent) return;

    const altura = topbar.offsetHeight;

    siteContent.style.paddingTop = altura + 'px';
    siteContent.style.minHeight = `calc(100vh - ${altura}px)`;
}

window.addEventListener('load', ajustarAlturaTopbar);
window.addEventListener('resize', ajustarAlturaTopbar);