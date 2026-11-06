import io
import json
import urllib.error
from unittest.mock import patch

import pytest

from app.utils import limpar_cnpj, validar_cnpj, formatar_cnpj, limpar_cep
from app.api_client import consultar_cep, consultar_cnpj


# --- CNPJ ---

def test_validar_cnpj():
    """CN PJ válido passa; dígitos verificadores errados e formatos inválidos falham."""
    assert validar_cnpj('11222333000181') is True
    assert validar_cnpj('11.222.333/0001-81') is True
    assert validar_cnpj('11222333000180') is False  # DV errado
    assert validar_cnpj('123') is False
    assert validar_cnpj('11111111111111') is False  # dígitos repetidos
    assert validar_cnpj('') is False
    assert validar_cnpj(None) is False


def test_limpar_cnpj():
    """Limpeza de pontuação e entradas vazias."""
    assert limpar_cnpj('11.222.333/0001-81') == '11222333000181'
    assert limpar_cnpj('') == ''
    assert limpar_cnpj(None) == ''


def test_formatar_cnpj():
    """Formata CNPJ de 14 dígitos no padrão XX.XXX.XXX/XXXX-XX."""
    assert formatar_cnpj('11222333000181') == '11.222.333/0001-81'
    # formato de entrada não normalizado: retorna como veio
    assert formatar_cnpj('123') == '123'


def test_limpar_cep():
    """CEP é limpo mantendo apenas dígitos."""
    assert limpar_cep('01234-567') == '01234567'
    assert limpar_cep('') == ''
    assert limpar_cep(None) == ''


# --- ViaCEP ---

class _RespostaFake:
    def __init__(self, payload):
        self._bytes = json.dumps(payload).encode('utf-8')

    def read(self):
        return self._bytes

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None


def test_consultar_cep_sucesso():
    """ViaCEP retorna endereço mapeado nos campos do formulário."""
    payload = {
        'cep': '01310-100',
        'logradouro': 'Av. Paulista',
        'complemento': 'até 999',
        'bairro': 'Bela Vista',
        'localidade': 'São Paulo',
        'uf': 'SP',
    }
    with patch('app.api_client.urlopen', return_value=_RespostaFake(payload)):
        dados = consultar_cep('01310-100')
        assert dados == {
            'cep': '01310-100',
            'logradouro': 'Av. Paulista',
            'complemento': 'até 999',
            'bairro': 'Bela Vista',
            'municipio': 'São Paulo',
            'estado': 'SP',
        }


def test_consultar_cep_erro_viacep():
    """CEP inexistente (erro do ViaCEP) retorna None."""
    with patch('app.api_client.urlopen', return_value=_RespostaFake({'erro': True})):
        assert consultar_cep('00000000') is None


def test_consultar_cep_formato_invalido():
    """Formato inválido não faz requisição."""
    assert consultar_cep('123') is None


def test_consultar_cep_falha_rede():
    """Falha de rede/requisição retorna None (fallback manual)."""
    with patch('app.api_client.urlopen', side_effect=urllib.error.URLError('sem rede')):
        assert consultar_cep('01310100') is None


# --- ReceitaWS ---

def test_consultar_cnpj_sucesso():
    """ReceitaWS retorna dados mapeados nos campos do formulário."""
    payload = {
        'status': 'OK',
        'nome': 'EMPRESA TESTE LTDA',
        'logradouro': 'Rua X',
        'numero': '100',
        'complemento': '',
        'bairro': 'Centro',
        'municipio': 'SÃO PAULO',
        'estado': 'SP',
        'cep': '01310100',
    }
    with patch('app.api_client.urlopen', return_value=_RespostaFake(payload)):
        dados = consultar_cnpj('11222333000181')
        assert dados['razao_social'] == 'EMPRESA TESTE LTDA'
        assert dados['estado'] == 'SP'
        assert dados['municipio'] == 'SÃO PAULO'


def test_consultar_cnpj_status_erro():
    """Status de erro da ReceitaWS retorna None."""
    with patch('app.api_client.urlopen', return_value=_RespostaFake({'status': 'ERROR'})):
        assert consultar_cnpj('11222333000181') is None


def test_consultar_cnpj_falha_rede():
    """Rate limit / rede indisponível retorna None (fallback manual)."""
    with patch('app.api_client.urlopen', side_effect=urllib.error.HTTPError(
        'url', 429, 'Too Many Requests', None, io.BytesIO(b'')
    )):
        assert consultar_cnpj('11222333000181') is None
