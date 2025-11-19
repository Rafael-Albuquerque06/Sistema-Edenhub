const produtosPorBU = {
    'Combo': [
        ['Combo Básico', 'Combo Básico'],
        ['Combo Premium', 'Combo Premium'], 
        ['Combo Empresarial', 'Combo Empresarial']
    ],
    'Edenred Pay': [
        ['Cartão Corporativo', 'Cartão Corporativo'],
        ['Pagamento Digital', 'Pagamento Digital'],
        ['Gestão de Despesas', 'Gestão de Despesas'],
        ['Solução PIX Empresa', 'Solução PIX Empresa']
    ],
    'Golntegro': [
        ['Seguro Saúde', 'Seguro Saúde'],
        ['Plano Odontológico', 'Plano Odontológico'],
        ['Benefício Bem-estar', 'Benefício Bem-estar']
    ],
    'Punto': [
        ['Punto Básico', 'Punto Básico'],
        ['Punto Premium', 'Punto Premium'],
        ['Punto Corporativo', 'Punto Corporativo']
    ],
    'Repom': [
        ['Gestão de Frotas', 'Gestão de Frotas'],
        ['Controle de Abastecimento', 'Controle de Abastecimento'],
        ['Manutenção Preventiva', 'Manutenção Preventiva']
    ],
    'Ticket Log': [
        ['Gestão de Abastecimento', 'Gestão de Abastecimento'],
        ['Abastecimento', 'Abastecimento'],
        ['Gestão de manutenção', 'Gestão de manutenção'],
        ['Controle de Frotas', 'Controle de Frotas']
    ],
    'Ticket Serviços': [
        ['Vale Refeição', 'Vale Refeição'],
        ['Vale Alimentação', 'Vale Alimentação'], 
        ['Vale Transporte', 'Vale Transporte'],
        ['Benefício Flex', 'Benefício Flex']
    ]
};

function atualizarProdutos() {
    const buSelecionado = document.getElementById('buEscolhido').value;
    const container = document.getElementById('produtosContainer');
    const hiddenSelect = document.getElementById('produtosHidden');
    const errorDiv = document.getElementById('produtosError');
    
    // Limpa o container e o hidden select
    container.innerHTML = '';
    hiddenSelect.innerHTML = '';
    errorDiv.style.display = 'none';
    
    if (buSelecionado && produtosPorBU[buSelecionado]) {
        const produtos = produtosPorBU[buSelecionado];
        
        produtos.forEach(produto => {
            const [valor, label] = produto;
            
            // Adiciona checkbox visível
            const div = document.createElement('div');
            div.className = 'form-check';
            div.innerHTML = `
                <input class="form-check-input produto-checkbox" type="checkbox" value="${valor}" id="produto_${valor.replace(/\s+/g, '_')}">
                <label class="form-check-label text-dark" for="produto_${valor.replace(/\s+/g, '_')}">
                    ${label}
                </label>
            `;
            container.appendChild(div);
            
            // Adiciona option no hidden select para o WTForms
            const option = document.createElement('option');
            option.value = valor;
            option.textContent = label;
            hiddenSelect.appendChild(option);
        });
        
    } else {
        container.innerHTML = '<div class="text-muted">Selecione um BU primeiro para ver os produtos disponíveis</div>';
    }
}

// Atualiza o hidden select quando checkboxes são alterados
document.addEventListener('change', function(e) {
    if (e.target.classList.contains('produto-checkbox')) {
        const hiddenSelect = document.getElementById('produtosHidden');
        const checkboxes = document.querySelectorAll('.produto-checkbox:checked');
        
        // Atualiza as opções selecionadas no hidden select
        Array.from(hiddenSelect.options).forEach(option => {
            option.selected = false;
        });
        
        checkboxes.forEach(checkbox => {
            const option = Array.from(hiddenSelect.options).find(opt => opt.value === checkbox.value);
            if (option) {
                option.selected = true;
            }
        });
    }
});

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    const buSelect = document.getElementById('buEscolhido');
    if (buSelect) {
        buSelect.addEventListener('change', atualizarProdutos);
    }
    
    // Atualiza produtos se já tiver um BU selecionado
    if (buSelect && buSelect.value) {
        atualizarProdutos();
    }
    
    // Validação antes do envio do formulário
    const form = document.getElementById('buForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            const buSelecionado = document.getElementById('buEscolhido').value;
            const checkboxes = document.querySelectorAll('.produto-checkbox:checked');
            const errorDiv = document.getElementById('produtosError');
            
            if (!buSelecionado) {
                e.preventDefault();
                alert('Por favor, selecione um BU');
                return false;
            }
            
            if (checkboxes.length === 0) {
                e.preventDefault();
                errorDiv.style.display = 'block';
                return false;
            }
            
            errorDiv.style.display = 'none';
            return true;
        });
    }
});
