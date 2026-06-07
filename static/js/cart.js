// Aguarda todo o HTML da página carregar antes de aplicar os eventos
document.addEventListener("DOMContentLoaded", function () {
    
    // 1. Monitora todos os formulários que realizam a remoção de itens
    const formulariosRemover = document.querySelectorAll('form[action*="remover"]');
    formulariosRemover.forEach(function (form) {
        form.addEventListener("submit", function (event) {
            const confirmacao = confirm("Tem certeza que deseja remover este item do carrinho?");
            if (!confirmacao) {
                event.preventDefault(); // Cancela o envio do formulário se o usuário clicar em Cancelar
            }
        });
    });

    // 2. Monitora o formulário que esvazia todo o carrinho
    const formularioEsvaziar = document.querySelector('form[action*="esvaziar"]');
    if (formularioEsvaziar) {
        formularioEsvaziar.addEventListener("submit", function (event) {
            const confirmacao = confirm("Atenção: deseja realmente limpar TODO o seu carrinho?");
            if (!confirmacao) {
                event.preventDefault(); // Cancela o envio se clicar em Cancelar
            }
        });
    }

    // 3. FUNÇÃO PARA SUMIR COM AS NOTIFICAÇÕES SOZINHAS (NOVO)
    const alertas = document.querySelectorAll('.alerta');
    
    alertas.forEach(function (alerta) {
        // Define um temporizador de 4000 milissegundos (4 segundos) antes de começar a sumir
        setTimeout(function () {
            alerta.style.opacity = '0'; // Torna o alerta invisível suavemente devido ao CSS transition
            
            // Aguarda mais 500ms (tempo da transição do CSS) para remover fisicamente o bloco do HTML
            setTimeout(function () {
                alerta.remove();
            }, 500);
            
        }, 4000); 
    });
});
