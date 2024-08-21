import unittest
import os
import json
import shutil
from unittest.mock import patch, MagicMock
from src.moniari_log.logger import MoniariLog

class TestMoniariLog(unittest.TestCase):

    def setUp(self):
        self.config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config'))
        self.log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
        self.config_file = os.path.join(self.config_dir, 'dev.json')
        self.log_file = os.path.join(self.log_dir, 'data_transfer.log')
        self.logger = None

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

    @patch('time.time', return_value=1692625286.295)
    @patch('src.moniari_log.logger.KafkaProducer')
    def test_info_log_to_kafka(self, MockKafkaProducer, mock_time):
        """
        Testa se uma mensagem de log INFO é enviada corretamente para o Kafka.
        """
        mock_producer = MockKafkaProducer.return_value
        self._set_log_config(log_to_file=False, log_to_kafka=True)
        self.logger = MoniariLog(config_file=self.config_file)
        self.logger.info('This is an info message for Kafka logging')

        expected_message = '2023-08-21 10:41:26,295 - [moniari_log] - INFO - This is an info message for Kafka logging'

        mock_producer.send.assert_called_once_with(self.logger.kafka_topic, {
            'level': 'info',
            'message': expected_message
        })
        self.logger.close()

    @patch('time.time', return_value=1692625286.295)
    @patch('src.moniari_log.logger.KafkaProducer')
    def test_error_log_to_kafka(self, MockKafkaProducer, mock_time):
        """
        Testa se uma mensagem de log ERROR é enviada corretamente para o Kafka.
        """
        mock_producer = MockKafkaProducer.return_value
        self._set_log_config(log_to_file=False, log_to_kafka=True)
        self.logger = MoniariLog(config_file=self.config_file)
        self.logger.error('This is an error message for Kafka logging')

        expected_message = '2023-08-21 10:41:26,295 - [moniari_log] - ERROR - This is an error message for Kafka logging'

        mock_producer.send.assert_called_once_with(self.logger.kafka_topic, {
            'level': 'error',
            'message': expected_message
        })
        self.logger.close()

    def _set_log_config(self, log_to_file, log_to_kafka):
        """
        Modifica o arquivo de configuração para o teste.
        """
        with open(self.config_file, 'r', encoding='utf-8') as file:
            config = json.load(file)
        config['log']['log_to_file'] = log_to_file
        config['log']['log_to_kafka'] = log_to_kafka
        config['log']['log_file'] = 'logs/data_transfer.log'
        config['log']['kafka_bootstrap_servers'] = ['localhost:9092']
        config['log']['kafka_topic'] = 'test_topic'
        with open(self.config_file, 'w', encoding='utf-8') as file:
            json.dump(config, file, indent=4)

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

        for dirpath, dirnames, filenames in os.walk(os.path.dirname(__file__)):
            for dirname in dirnames:
                if dirname == '__pycache__':
                    shutil.rmtree(os.path.join(dirpath, dirname))
        
        src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
        for dirpath, dirnames, filenames in os.walk(src_dir):
            for dirname in dirnames:
                if dirname == '__pycache__':
                    shutil.rmtree(os.path.join(dirpath, dirname))

if __name__ == '__main__':
    unittest.main()
