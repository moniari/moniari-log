import logging
import json
import sys
import colorlog
from .config import load_config

# Compatibilidade kafka-python 2.0.2 para Python 3.12
import six
if sys.version_info >= (3, 12, 0):
    sys.modules['kafka.vendor.six.moves'] = six.moves
from kafka import KafkaProducer

class KafkaLoggingHandler(logging.Handler):
    """
    Handler personalizado para enviar logs para o Kafka.

    Args:
        kafka_producer (KafkaProducer): Instância do KafkaProducer para enviar mensagens.
        kafka_topic (str): Nome do tópico Kafka para onde as mensagens serão enviadas.
    """

    def __init__(self, kafka_producer, kafka_topic):
        super().__init__()
        self.kafka_producer = kafka_producer
        self.kafka_topic = kafka_topic

    def emit(self, record):
        """
        Envia o registro de log formatado para o Kafka.

        Args:
            record (LogRecord): Registro de log a ser enviado.
        """
        try:
            message = self.format(record)
            self.kafka_producer.send(
                self.kafka_topic, 
                {'level': record.levelname.lower(), 'message': message}
            )
        except Exception:
            self.handleError(record)

class MoniariLog:
    """
    Classe para configuração e gerenciamento de logging.

    Args:
        config_file (str): Caminho para o arquivo de configuração.
    """

    def __init__(self, config_file):
        self.config = load_config(config_file)
        self.logger_name = self.config.get('logger_name', __name__)
        self.log_level = self.config.get('log_level', 'DEBUG').upper()
        self.kafka_producer = None
        self.kafka_topic = None
        self.setup_logging()

    def setup_logging(self):
        """
        Configura os handlers de logging com base nas configurações carregadas.
        """
        self.logger = logging.getLogger(self.logger_name)
        self.logger.setLevel(getattr(logging, self.log_level, logging.DEBUG))

        # Formatter para logs coloridos no console ou arquivo
        formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - [%(name)s] - %(levelname)s - %(message)s",
            datefmt=None,
            reset=True,
            log_colors={
                'DEBUG': 'bold_blue',
                'INFO': 'bold_green',
                'WARNING': 'bold_yellow',
                'ERROR': 'bold_red',
                'CRITICAL': 'bold_red,bg_white',
            }
        )

        # Formatter para Kafka, sem cores
        kafka_formatter = logging.Formatter(
            '%(asctime)s - [%(name)s] - %(levelname)s - %(message)s'
        )

        any_log_active = False

        if self.config.get('log_to_file') and self.config['log_file']:
            any_log_active = True
            file_handler = logging.FileHandler(
                self.config['log_file'], encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        if self.config.get('log_to_kafka'):
            if isinstance(self.config.get('kafka_bootstrap_servers'), list) and self.config.get('kafka_topic'):
                any_log_active = True
                self.kafka_producer = KafkaProducer(
                    bootstrap_servers=self.config['kafka_bootstrap_servers'],
                    value_serializer=lambda v: json.dumps(v).encode('utf-8')
                )
                self.kafka_topic = self.config['kafka_topic']
                kafka_handler = KafkaLoggingHandler(self.kafka_producer, self.kafka_topic)
                kafka_handler.setFormatter(kafka_formatter)
                self.logger.addHandler(kafka_handler)
            else:
                self.logger.warning(
                    "Configuração incompleta para o log no Kafka. "
                    "Verifique as configurações 'kafka_bootstrap_servers' e 'kafka_topic'."
                )

        if not any_log_active or self.config.get('log_to_stderr', False):
            stderr_handler = logging.StreamHandler(sys.stderr)
            stderr_handler.setLevel(logging.DEBUG)
            stderr_handler.setFormatter(formatter)
            self.logger.addHandler(stderr_handler)

            if not any_log_active:
                self.logger.warning(
                    "Nenhuma configuração de log encontrada, utilizando stderr como padrão."
                )

    def info(self, message):
        """
        Registra uma mensagem de log no nível INFO.

        Args:
            message (str): Mensagem a ser registrada.
        """
        self.log('info', message)

    def debug(self, message):
        """
        Registra uma mensagem de log no nível DEBUG.

        Args:
            message (str): Mensagem a ser registrada.
        """
        self.log('debug', message)

    def warning(self, message):
        """
        Registra uma mensagem de log no nível WARNING.

        Args:
            message (str): Mensagem a ser registrada.
        """
        self.log('warning', message)

    def error(self, message):
        """
        Registra uma mensagem de log no nível ERROR.

        Args:
            message (str): Mensagem a ser registrada.
        """
        self.log('error', message)

    def critical(self, message):
        """
        Registra uma mensagem de log no nível CRITICAL.

        Args:
            message (str): Mensagem a ser registrada.
        """
        self.log('critical', message)

    def log(self, level, message):
        """
        Registra uma mensagem de log no nível especificado.

        Args:
            level (str): Nível do log (info, debug, warning, error, critical).
            message (str): Mensagem a ser registrada.
        """
        getattr(self.logger, level.lower())(message)

    def close(self):
        """
        Fecha todos os handlers e libera recursos.
        """
        if self.kafka_producer:
            self.kafka_producer.close()
        for handler in self.logger.handlers:
            handler.close()
        self.logger.handlers.clear()
        logging.shutdown()
