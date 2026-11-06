"""Utilitários puros (sem acesso a banco ou rede)."""

import pytz

TZ_BRASIL = pytz.timezone('America/Sao_Paulo')



def formatar_data_brasil(dt):
    """Converte UTC para horário de Brasília e formata."""
    if not dt:
        return ""
    try:
        if dt.tzinfo is None:
            dt = pytz.utc.localize(dt)
        dt_brasil = dt.astimezone(TZ_BRASIL)
        return dt_brasil.strftime('%d/%m/%Y %H:%M')
    except Exception:
        return dt.strftime('%d/%m/%Y %H:%M')



def limpar_cnpj(cnpj):
    """Remove pontuação de um CNPJ, deixando apenas os dígitos."""
    if not cnpj:
        return ''
    for caractere in '.,-/ ':
        cnpj = cnpj.replace(caractere, '')
    return cnpj.strip()



def _calcular_digito(digitos, pesos):
    soma = sum(int(d) * p for d, p in zip(digitos, pesos))
    resto = soma % 11
    return '0' if resto < 2 else str(11 - resto)



def validar_cnpj(cnpj):
    """Valida um CNPJ (formato e dígitos verificadores). Retorna bool."""
    cnpj = limpar_cnpj(cnpj)
    if len(cnpj) != 14 or not cnpj.isdigit():
        return False
    if cnpj == cnpj[0] * 14:
        return False  # todos os dígitos iguais (ex.: 00000000000000)

    peso1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    peso2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    digito1 = _calcular_digito(cnpj[:12], peso1)
    digito2 = _calcular_digito(cnpj[:12] + digito1, peso2)
    return cnpj[-2:] == digito1 + digito2



def formatar_cnpj(cnpj):
    """Formata um CNPJ de 14 dígitos como XX.XXX.XXX/XXXX-XX."""
    cnpj = limpar_cnpj(cnpj)
    if len(cnpj) != 14:
        return cnpj
    return '{}.{}.{}/{}-{}'.format(
        cnpj[:2], cnpj[2:5], cnpj[5:8], cnpj[8:12], cnpj[12:],
    )



def limpar_cep(cep):
    """Remove pontuação de um CEP, deixando apenas os dígitos."""
    if not cep:
        return ''
    return cep.replace('.', '').replace('-', '').strip()
