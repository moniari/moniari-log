import unittest
import os
import json
import shutil
from src.logger import MoniariLog

class TestMoniariLog(unittest.TestCase):

    def setUp(self):
        self.config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config'))
        self.log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
        self.config_file = os.path.join(self.config_dir, 'dev.json')
        self.log_file = os.path.join(self.log_dir, 'data_transfer.log')
        self.logger = None

        # Certifique-se de que o arquivo de log não existe antes do teste
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

    def test_dev_json_exists(self):
        """
        Testa se o arquivo de configuração dev.json local está presente.
        """
        self.assertTrue(os.path.isfile(self.config_file), f"Arquivo de configuração {self.config_file} não encontrado.")

    def test_info_log_to_file(self):
        """
        Testa se uma mensagem de log INFO é registrada corretamente no arquivo de log.
        """
        self._set_log_config(log_to_file=True, log_to_kafka=False)
        self.logger = MoniariLog(config_file=self.config_file)
        self.logger.info('This is an info message for file logging')
        self.logger.close()
        self.assertTrue(os.path.isfile(self.log_file), f"Arquivo de log {self.log_file} não foi criado.")
        self._check_log_contents('INFO', 'This is an info message for file logging')

    def test_warning_log_to_file(self):
        """
        Testa se uma mensagem de log WARNING é registrada corretamente no arquivo de log.
        """
        self._set_log_config(log_to_file=True, log_to_kafka=False)
        self.logger = MoniariLog(config_file=self.config_file)
        self.logger.warning('This is a warning message for file logging')
        self.logger.close()
        self.assertTrue(os.path.isfile(self.log_file), f"Arquivo de log {self.log_file} não foi criado.")
        self._check_log_contents('WARNING', 'This is a warning message for file logging')

    def test_error_log_to_file(self):
        """
        Testa se uma mensagem de log ERROR é registrada corretamente no arquivo de log.
        """
        self._set_log_config(log_to_file=True, log_to_kafka=False)
        self.logger = MoniariLog(config_file=self.config_file)
        self.logger.error('This is an error message for file logging')
        self.logger.close()
        self.assertTrue(os.path.isfile(self.log_file), f"Arquivo de log {self.log_file} não foi criado.")
        self._check_log_contents('ERROR', 'This is an error message for file logging')

    def _set_log_config(self, log_to_file, log_to_kafka):
        """
        Modifica o arquivo de configuração para o teste.
        """
        with open(self.config_file, 'r', encoding='utf-8') as file:
            config = json.load(file)
        config['log']['log_to_file'] = log_to_file
        config['log']['log_to_kafka'] = log_to_kafka
        config['log']['log_file'] = 'logs/data_transfer.log'
        with open(self.config_file, 'w', encoding='utf-8') as file:
            json.dump(config, file, indent=4)

        # Certifique-se de que as variáveis de ambiente não estejam interferindo
        os.environ.pop('LOG_TO_FILE', None)
        os.environ.pop('LOG_TO_KAFKA', None)
        os.environ.pop('LOG_FILE', None)

    def _check_log_contents(self, level, message):
        """
        Verifica se o conteúdo do arquivo de log contém a mensagem esperada.
        """
        with open(self.log_file, 'r', encoding='utf-8') as file:
            log_contents = file.read()
        self.assertIn(level, log_contents, f"Nível de log {level} não encontrado no arquivo de log.")
        self.assertIn(message, log_contents, f"Mensagem de log '{message}' não encontrada no arquivo de log.")

    def tearDown(self):
        """
        Limpa o ambiente de teste após cada método de teste.
        """
        if self.logger:
            self.logger.close()
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

        # Remover diretórios __pycache__ dentro do diretório de testes e src
        for dirpath, dirnames, filenames in os.walk(os.path.dirname(__file__)):
            for dirname in dirnames:
                if dirname == '__pycache__':
                    shutil.rmtree(os.path.join(dirpath, dirname))
        
        # Também limpar __pycache__ no diretório src
        src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
        for dirpath, dirnames, filenames in os.walk(src_dir):
            for dirname in dirnames:
                if dirname == '__pycache__':
                    shutil.rmtree(os.path.join(dirpath, dirname))

if __name__ == '__main__':
    unittest.main()
