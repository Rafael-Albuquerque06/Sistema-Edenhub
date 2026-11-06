"""Integrações com APIs externas gratuitas (ViaCEP e ReceitaWS).

Ambas as APIs são públicas, sem chave e sem cadastro. Falhas de rede,
rate limit (ReceitaWS ~3 consultas/min) ou resposta inválida retornam
None — o chamador deve sempre oferecer preenchimento manual como fallback.
"""

import json

from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen, Request

from app.utils import limpar_cnpj, limpar_cep

VIA_CEP_URL = 'https://viacep.com.br/ws/{cep}/json/'
RECEITA_WS_URL = 'https://www.receitaws.com.br/v1/cnpj/{cnpj}'
TIMEOUT_SEGUNDOS = 10



def _buscar_json(url):
    """Faz um GET e retorna o JSON decodificado, ou None em qualquer falha."""
    try:
        requisicao = Request(url, headers={'Accept': 'application/json'})
        with urlopen(requisicao, timeout=TIMEOUT_SEGUNDOS) as resposta:
            return json.loads(resposta.read().decode('utf-8'))
    except (HTTPError, URLError, ValueError, OSError):
        return None



def consultar_cep(cep):
    """Consulta o ViaCEP. Retorna dict com endereço ou None."""
    cep = limpar_cep(cep)
    if not (len(cep) == 8 and cep.isdigit()):
        return None

    dados = _buscar_json(VIA_CEP_URL.format(cep=cep))
    if not dados or dados.get('erro'):
        return None
    return {
        'cep': dados.get('cep', ''),
        'logradouro': dados.get('logradouro', ''),
        'complemento': dados.get('complemento', ''),
        'bairro': dados.get('bairro', ''),
        'municipio': dados.get('localidade', ''),
        'estado': dados.get('uf', ''),
    }



def consultar_cnpj(cnpj):
    """Consulta a ReceitaWS. Retorna dict com dados cadastrais ou None."""
    cnpj = limpar_cnpj(cnpj)
    if not (len(cnpj) == 14 and cnpj.isdigit()):
        return None

    dados = _buscar_json(RECEITA_WS_URL.format(cnpj=cnpj))
    if not dados or dados.get('status') not in (None, 'OK'):
        return None
    return {
        'razao_social': dados.get('nome', ''),
        'logradouro': dados.get('logradouro', ''),
        'numero': dados.get('numero', ''),
        'complemento': dados.get('complemento', ''),
        'bairro': dados.get('bairro', ''),
        'municipio': dados.get('municipio', ''),
        'estado': dados.get('estado') or dados.get('uf') or '',
        'cep': dados.get('cep', ''),
    }
