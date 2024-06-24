import logging
from kafka import KafkaProducer
import json
import sys
import os
from .config import load_config

class MoniariLog:
    """
    Classe para configuração e gerenciamento de logging.

    Args:
        config_file (str): Caminho para o arquivo de configuração.
    """
    def __init__(self, config_file=None):
        if config_file is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(base_dir)
            config_dir = os.path.join(project_dir, 'config')

            # Verifica a variável de ambiente para escolher entre dev.json e prod.json
            env = os.getenv('MONIARI_ENV', 'dev')
            config_file = os.path.join(config_dir, f'{env}.json')

        self.config_file_path = config_file
        self.config = load_config(self.config_file_path)

        self.setup_logging()

    def setup_logging(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.setup_file_logging()
        self.setup_kafka_logging()
        self.setup_stderr_logging()

    def setup_file_logging(self):
        if self.config.get('log_to_file') and self.config['log_file']:
            log_file_path = self.config['log_file']
            # Garantir que o caminho do arquivo de log seja absoluto
            if not os.path.isabs(log_file_path):
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                log_file_path = os.path.join(base_dir, log_file_path)

            # Certificar-se de que o diretório de logs existe
            log_dir = os.path.dirname(log_file_path)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(file_handler)
    
    def setup_kafka_logging(self):
        if self.config.get('log_to_kafka') and self.config['kafka_bootstrap_servers'] and self.config['kafka_topic']:
            self.kafka_producer = KafkaProducer(
                bootstrap_servers=self.config['kafka_bootstrap_servers'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            self.kafka_topic = self.config['kafka_topic']

    def setup_stderr_logging(self):
        if not self.config.get('log_to_file') and not self.config.get('log_to_kafka') or self.config.get('log_to_stderr', False):
            stderr_handler = logging.StreamHandler(sys.stderr)
            stderr_handler.setLevel(logging.DEBUG)
            stderr_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(stderr_handler)

            if not self.config.get('log_to_file') and not self.config.get('log_to_kafka'):
                self.logger.warning("Nenhuma configuração de log encontrada, utilizando stderr como padrão.")

    def info(self, message):
        self.log('info', message)

    def debug(self, message):
        self.log('debug', message)

    def warning(self, message):
        self.log('warning', message)

    def error(self, message):
        self.log('error', message)

    def critical(self, message):
        self.log('critical', message)

    def log(self, level, message):
        getattr(self.logger, level.lower())(message)

        if self.config.get('log_to_kafka') and hasattr(self, 'kafka_producer'):
            self.kafka_producer.send(self.kafka_topic, {'level': level, 'message': message})

    def close(self):
        if hasattr(self, 'kafka_producer'):
            self.kafka_producer.close()
        for handler in self.logger.handlers:
            handler.close()
        self.logger.handlers.clear()
        logging.shutdown()
