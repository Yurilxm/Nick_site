document.addEventListener('DOMContentLoaded', function () {
    const input = document.getElementById('search-input');
    const resultsBox = document.getElementById('search-results');

    if (!input || !resultsBox) return;

    let timeout = null;

    input.addEventListener('input', function () {
        const query = this.value.trim();

        clearTimeout(timeout);

        if (query.length < 2) {
            resultsBox.style.display = 'none';
            resultsBox.innerHTML = '';
            return;
        }

        timeout = setTimeout(() => {
            fetch(`/buscar-produtos/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    resultsBox.innerHTML = '';

                    if (!data.results.length) {
                        resultsBox.style.display = 'none';
                        return;
                    }

                    data.results.forEach(produto => {
                        const item = document.createElement('div');
                        item.classList.add('search-item');

                        item.innerHTML = `
                            <img src="${produto.imagem}" alt="${produto.nome}">
                            <div>
                                <strong>${produto.nome}</strong><br>
                                <small>R$ ${produto.preco}</small>
                            </div>
                        `;

                        item.addEventListener('click', () => {
                            window.location.href = `/produtos/${produto.id}/${produto.slug}/`;
                        });

                        resultsBox.appendChild(item);
                    });

                    resultsBox.style.display = 'block';
                });
        }, 300);
    });

    document.addEventListener('click', function (e) {
        if (!e.target.closest('.navbar')) {
            resultsBox.style.display = 'none';
        }
    });
});