document.addEventListener("DOMContentLoaded", function () {
    const elementoContador = document.getElementById("contador");
    const elementoUrl = document.getElementById("url_destino");

    if (elementoContador && elementoUrl) {
        let tempoRestante = 4;
        const urlRedirecionamento = elementoUrl.value;

        const intervalo = setInterval(function () {
            tempoRestante--;
            elementoContador.textContent = tempoRestante;

            if (tempoRestante <= 0) {
                clearInterval(intervalo);
                window.location.href = urlRedirecionamento; // Faz o redirecionamento via navegador
            }
        }, 1000); // Executa a cada 1 segundo
    }
});