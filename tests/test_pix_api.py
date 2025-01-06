import unittest
from unittest.mock import patch
import requests
import logging
import os

# Criação do diretório 'logs' caso não exista
log_directory = '../logs'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Configuração do Logger com codificação UTF-8
logging.basicConfig(
    filename=f'{log_directory}/pix_transactions.log',  # Arquivo onde os logs serão armazenados
    level=logging.DEBUG,  # Nível de log (DEBUG captura tudo)
    format='%(asctime)s - %(message)s',  # Formato da mensagem de log
    encoding='utf-8'  # Garante que o arquivo de log seja salvo com codificação UTF-8
)

# Funções para realizar as requisições
def create_pix_key(payload):
    url = 'https://cbf3d611-197c-46bb-8932-ded5230f469f.mock.pstmn.io/pix/keys'
    response = requests.post(url, json=payload)
    return response

def validate_transaction(payload):
    url = 'https://cbf3d611-197c-46bb-8932-ded5230f469f.mock.pstmn.io/pix/validate'
    response = requests.post(url, json=payload)
    return response

def create_charge(payload):
    url = 'https://cbf3d611-197c-46bb-8932-ded5230f469f.mock.pstmn.io/pix/charges'
    response = requests.post(url, json=payload)
    return response

class TestPixAPI(unittest.TestCase):

    # Testes para Criação de Chave PIX
    @patch('requests.post')
    def test_create_pix_key_valid(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "status": "success",
            "key": "12345678900"
        }
        payload = {"key": "12345678900", "keyType": "CPF"}
        response = create_pix_key(payload)
        logging.debug(f'Test create_pix_key_valid: {response.status_code} - {response.json()}')  # Log do teste
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")

    @patch('requests.post')
    def test_create_pix_key_invalid(self, mock_post):
        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = {
            "status": "error",
            "message": "Chave PIX inválida"
        }
        payload = {"key": "00000000000", "keyType": "CPF"}
        response = create_pix_key(payload)
        logging.debug(f'Test create_pix_key_invalid: {response.status_code} - {response.json()}')  # Log do teste
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "Chave PIX inválida")

    # Testes para Validação de Transação
    @patch('requests.post')
    def test_validate_transaction_success(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "status": "success",
            "message": "Transação aprovada"
        }
        payload = {
            "transactionId": "abc123456",
            "amount": 100.00,
            "recipient": "+55-11-99999-8888",
            "keyType": "CPF",
            "key": "12345678900"
        }
        response = validate_transaction(payload)
        logging.debug(f'Test validate_transaction_success: {response.status_code} - {response.json()}')  # Log do teste
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Transação aprovada")

    @patch('requests.post')
    def test_validate_transaction_auth_error(self, mock_post):
        mock_post.return_value.status_code = 401
        mock_post.return_value.json.return_value = {
            "status": "error",
            "message": "Token expirado"
        }
        payload = {
            "transactionId": "abc123456",
            "amount": 100.00,
            "recipient": "+55-11-99999-8888",
            "keyType": "CPF",
            "key": "01010101010"
        }
        response = validate_transaction(payload)
        logging.debug(f'Test validate_transaction_auth_error: {response.status_code} - {response.json()}')  # Log do teste
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["message"], "Token expirado")

    @patch('requests.post')
    def test_validate_transaction_timeout(self, mock_post):
        mock_post.return_value.status_code = 504
        mock_post.return_value.json.return_value = {
            "status": "error",
            "message": "Timeout no servidor"
        }
        payload = {
            "transactionId": "abc123456",
            "amount": 100.00,
            "recipient": "+55-11-99999-8888",
            "keyType": "CPF",
            "key": "65656565656"
        }
        response = validate_transaction(payload)
        logging.debug(f'Test validate_transaction_timeout: {response.status_code} - {response.json()}')  # Log do teste
        self.assertEqual(response.status_code, 504)
        self.assertEqual(response.json()["message"], "Timeout no servidor")

    # Testes para Criação de Cobrança
    @patch('requests.post')
    def test_create_charge_success(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "status": "success",
            "message": "Cobrança criada com sucesso",
            "charge_id": "charge123"
        }
        payload = {"amount": 100.0, "description": "Test charge"}
        response = create_charge(payload)
        logging.debug(f'Test create_charge_success: {response.status_code} - {response.json()}')  # Log do teste
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Cobrança criada com sucesso")

    @patch('requests.post')
    def test_create_charge_error(self, mock_post):
        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = {
            "status": "error",
            "message": "Erro na criação da cobrança. Dados inválidos"
        }
        payload = {"amount": -100.0, "description": "Invalid charge"}
        response = create_charge(payload)
        logging.debug(f'Test create_charge_error: {response.status_code} - {response.json()}')  # Log do teste
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "Erro na criação da cobrança. Dados inválidos")

if __name__ == '__main__':
    unittest.main()
