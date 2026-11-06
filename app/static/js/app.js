/* Edenhub — JS global: máscaras, preenchimento de endereço (ViaCEP),
   feedback de envio (loading nos botões) e auto-fechamento dos alertas. */

(function () {
    'use strict';

    // ---------- MÁSCARAS ----------
    function mascara(valor, formatar) {
        const apenasDigitos = valor.replace(/\D/g, '');
        return formatar(apenasDigitos);
    }

    const regrasMascara = {
        telefone: (d) => d.length > 10 && d.length <= 11
            ? `(${d.slice(0, 2)}) ${d.slice(2, 7)}-${d.slice(7, 11)}`.slice(0, 15)
            : `(${d.slice(0, 2)}) ${d.slice(2, 11)}`,
        telefone_contato: (d) => regrasMascara.telefone(d),
        celular_contato: (d) => regrasMascara.telefone(d),
        cep: (d) => d.length > 5 ? `${d.slice(0, 5)}-${d.slice(5, 8)}` : d,
        cnpj: (d) => {
            if (d.length <= 2) { return d; }
            if (d.length <= 5) { return `${d.slice(0, 2)}.${d.slice(2)}`; }
            if (d.length <= 8) { return `${d.slice(0, 2)}.${d.slice(2, 5)}.${d.slice(5)}`; }
            if (d.length <= 12) { return `${d.slice(0, 2)}.${d.slice(2, 5)}.${d.slice(5, 8)}/${d.slice(8)}`; }
            return `${d.slice(0, 2)}.${d.slice(2, 5)}.${d.slice(5, 8)}/${d.slice(8, 12)}-${d.slice(12, 14)}`;
        },
    };

    Object.keys(regrasMascara).forEach(function (nome) {
        document.querySelectorAll(`input[name="${nome}"]`).forEach(function (input) {
            input.addEventListener('input', function () {
                input.value = mascara(input.value, regrasMascara[nome]);
            });
        });
    });

    // ---------- PREENCHIMENTO DE ENDEREÇO PELO CEP (ViaCEP) ----------
    document.querySelectorAll('input[name="cep"]').forEach(function (inputCep) {
        inputCep.addEventListener('blur', function () {
            const cep = inputCep.value.replace(/\D/g, '');
            if (cep.length !== 8) { return; }

            fetch(`/api/cep/${cep}`)
                .then((res) => (res.ok ? res.json() : Promise.reject(new Error('CEP não encontrado'))))
                .then((d) => {
                    const mapa = {
                        logradouro: d.logradouro, bairro: d.bairro,
                        municipio: d.municipio, estado: d.estado,
                        complemento: d.complemento,
                    };
                    Object.keys(mapa).forEach(function (campo) {
                        const input = document.querySelector(`input[name="${campo}"]`);
                        if (input && !input.value && mapa[campo]) { input.value = mapa[campo]; }
                    });
                })
                .catch(() => { /* preenchimento manual é o fallback */ });
        });
    });

    // ---------- FEEDBACK DE ENVIO (botão carregando) ----------
    document.querySelectorAll('form').forEach(function (form) {
        form.addEventListener('submit', function () {
            if (form.dataset.enviando) { return; }
            if (form.checkValidity && !form.checkValidity()) {
                return;  // deixa o navegador mostrar os erros de validação
            }
            form.dataset.enviando = '1';
            form.querySelectorAll('button[type="submit"], input[type="submit"]').forEach(function (button) {
                button.disabled = true;
                button.classList.add('btn-loading');
            });
        });
    });

    // ---------- RESUMO DE ERROS DO FORMULÁRIO (foco pós-submit) ----------
    // Forms com {% if form.errors %} renderizam #errosForm (role="alert");
    // ao voltar da validação no servidor, o foco vai para o resumo.
    const resumoErros = document.getElementById('errosForm');
    if (resumoErros) { resumoErros.focus(); }

    // ---------- ALERTA AUTO-FECHÁVEL (estilo toast) ----------
    document.querySelectorAll('.alert-message').forEach(function (alerta) {
        alerta.setAttribute('aria-live', 'polite');
        setTimeout(function () {
            alerta.style.transition = 'opacity 0.4s ease';
            alerta.style.opacity = '0';
            setTimeout(function () { alerta.remove(); }, 500);
        }, 6000);
    });
})();
