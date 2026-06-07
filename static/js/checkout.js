//  JAVASCRIPT LOCAL PARA ALTERNÂNCIA DE TELAS
document.addEventListener("DOMContentLoaded", function () {
    const seletorMetodo = document.getElementById("metodo_pagamento");
    const blocoPix = document.getElementById("container-pix");
    const blocoBoleto = document.getElementById("container-boleto");
    const blocoCartao = document.getElementById("container-cartao");

    // Campos do cartão para controle de obrigatoriedade dinâmica
    const inputNumero = document.getElementById("numero_cartao");
    const inputNome = document.getElementById("nome_titular");

    if (seletorMetodo) {
        seletorMetodo.addEventListener("change", function () {
            // Esconde todos os blocos primeiro
            blocoPix.style.display = "none";
            blocoBoleto.style.display = "none";
            blocoCartao.style.display = "none";
            
            // Desativa a obrigatoriedade dos campos de cartão por padrão
            inputNumero.removeAttribute("required");
            inputNome.removeAttribute("required");

            // Mostra o bloco específico baseado na escolha do usuário
            if (seletorMetodo.value === "Pix") {
                blocoPix.style.display = "block";
            } else if (seletorMetodo.value === "Boleto Bancário") {
                blocoBoleto.style.display = "block";
            } else if (seletorMetodo.value === "Cartão de Crédito") {
                blocoCartao.style.display = "block";
                // Torna os campos obrigatórios apenas se o usuário escolher pagar com cartão
                inputNumero.setAttribute("required", "required");
                inputNome.setAttribute("required", "required");
            }
        });
    }

    // FUNÇÃO PARA SUMIR COM AS NOTIFICAÇÕES SOZINHAS (MANTENDO A CONSISTÊNCIA)
    const alertas = document.querySelectorAll('.alerta');
    
    alertas.forEach(function (alerta) {
        setTimeout(function () {
            alerta.style.opacity = '0'; // Aplica o fade-out do CSS
            
            setTimeout(function () {
                alerta.remove(); // Remove do HTML após a transição de 0.5s
            }, 500);
            
        }, 4000); // 4 segundos de exibição
    });

});