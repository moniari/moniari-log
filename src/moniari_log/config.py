import os
import json

def get_env_bool(env_var, default=None):
    """
    Retorna o valor booleano de uma variável de ambiente.

    Args:
        env_var (str): Nome da variável de ambiente.
        default (bool): Valor padrão se a variável de ambiente não estiver definida.

    Returns:
        bool: Valor booleano da variável de ambiente.
    """
    value = os.getenv(env_var)
    if value is None:
        return default
    return value.lower() in ['true', '1', 't', 'yes', 'y']

def load_config(config_file):
    """
    Carrega as configurações de variáveis de ambiente ou do arquivo de configuração.

    Args:
        config_file (str): Caminho para o arquivo de configuração.

    Returns:
        dict: Dicionário contendo as configurações de log.
    """
    config = {}

    # Primeiramente carregar as variáveis de ambiente
    config['log_to_file'] = get_env_bool('LOG_TO_FILE')
    config['log_file'] = os.getenv('LOG_FILE')
    config['log_to_kafka'] = get_env_bool('LOG_TO_KAFKA')
    config['kafka_bootstrap_servers'] = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
    config['kafka_topic'] = os.getenv('KAFKA_TOPIC')
    config['log_to_stderr'] = get_env_bool('LOG_TO_STDERR', default=True)
    config['logger_name'] = os.getenv('LOGGER_NAME')
    config['log_level'] = os.getenv('LOG_LEVEL')

    try:
        with open(config_file, 'r', encoding='utf-8') as file:
            file_config = json.load(file)['log']

            config['log_to_file'] = config['log_to_file'] if config['log_to_file'] is not None else file_config.get('log_to_file', config['log_to_file'])
            config['log_file'] = config['log_file'] if config['log_file'] is not None else file_config.get('log_file', config['log_file'])
            config['log_to_kafka'] = config['log_to_kafka'] if config['log_to_kafka'] is not None else file_config.get('log_to_kafka', config['log_to_kafka'])
            config['kafka_bootstrap_servers'] = config['kafka_bootstrap_servers'] if config['kafka_bootstrap_servers'] is not None else file_config.get('kafka_bootstrap_servers', config['kafka_bootstrap_servers'])
            config['kafka_topic'] = config['kafka_topic'] if config['kafka_topic'] is not None else file_config.get('kafka_topic', config['kafka_topic'])
            config['log_to_stderr'] = config['log_to_stderr'] if config['log_to_stderr'] is not None else file_config.get('log_to_stderr', config['log_to_stderr'])
            config['logger_name'] = config['logger_name'] if config['logger_name'] is not None else file_config.get('logger_name', config['logger_name'])
            config['log_level'] = config['log_level'] if config['log_level'] is not None else file_config.get('log_level', config['log_level'])

    except FileNotFoundError:
        config['log_to_stderr'] = True
    
    return config
