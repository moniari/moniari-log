# Moniari Log

Pacote de logging para uso interno da empresa, proporcionando uma interface de log simples e direta. Suporta gravação de logs em arquivos, saída padrão de erro (stderr) e integração com o Kafka para distribuição em um ambiente de mensageria. Configurável para diferentes ambientes como desenvolvimento e produção através de arquivos JSON.

## Instalação

Para instalar o pacote diretamente do repositório Git, use o [Poetry](https://python-poetry.org/):


```bash
poetry add git+https://github.com/moniari/moniari-log.git
```

## Configuração

O pacote Moniari-Log utiliza um arquivo de configuração JSON para definir as opções de logging. Exemplos de arquivos de configuração (dev.json e prod.json) são fornecidos na pasta config do projeto.

### Exemplo de config/dev.json

```json
{
    "log": {
        "log_file": "logs/data_transfer.log",
        "log_to_file": true,
        "log_to_kafka": false,
        "kafka_bootstrap_servers": [
            "localhost:9092"
        ],
        "kafka_topic": "logs"
    }
}
```

### Exemplo de config/prod.json

```json
{
    "log": {
        "log_file": "logs/data_transfer.log",
        "log_to_file": true,
        "log_to_kafka": true,
        "kafka_bootstrap_servers": [
            "localhost:9092"
        ],
        "kafka_topic": "logs"
    }
}
```

## Uso

###Configuração Global do Logger

Para configurar o Moniari-Log globalmente no seu projeto, você pode utilizar a classe LoggerConfig definida no arquivo log_setup.py. Essa classe facilita a configuração e inicialização do logger em diferentes ambientes.

### Exemplo de uso

```python
from pathlib import Path
from moniari_log import MoniariLog

class LoggerConfig:
    def __init__(self, config_file: str = "config/dev.json"):
        """
        Inicializa a configuração do logger com o caminho do arquivo de configuração especificado.

        Parâmetros:
            config_file (str): Caminho relativo para o arquivo de configuração.
        """
        # Obtenha o diretório atual de trabalho
        current_working_directory = Path.cwd()
        
        # Construa o caminho absoluto para o arquivo de configuração baseado no cwd
        self.config_file_path = current_working_directory / config_file

        self.logger = self.setup_logger()

    def setup_logger(self) -> MoniariLog:
        """
        Configura e retorna o logger MoniariLog.

        Retorna:
            MoniariLog: Instância configurada do logger.
        """
        logger = MoniariLog(config_file=str(self.config_file_path))
        logger.debug(f"Logger configurado com o arquivo: {self.config_file_path}")
        return logger
    
# Instancia e configura o logger para uso global
logger = LoggerConfig().logger
```

## Exemplo de Uso
Após configurar o logger globalmente com log_setup.py, você pode utilizá-lo em qualquer lugar do seu projeto da seguinte forma:

```python
from log_setup import logger

# Usa o logger para registrar mensagens
logger.info("This is an info message from my new project")
logger.error("This is an error message from my new project")
```

## Variáveis de Ambiente

Você pode substituir as configurações do arquivo JSON com variáveis de ambiente. As variáveis de ambiente têm prioridade sobre as configurações do arquivo JSON.

### Variáveis de Ambiente Suportadas

- `LOG_TO_FILE`: Define se o log deve ser escrito em arquivo (`true` ou `false`).
- `LOG_FILE`: Caminho para o arquivo de log.
- `LOG_TO_KAFKA`: Define se o log deve ser enviado para o Kafka (`true` ou `false`).
- `KAFKA_BOOTSTRAP_SERVERS`: Lista de servidores Kafka.
- `KAFKA_TOPIC`: Tópico Kafka para envio dos logs.
- `LOG_TO_STDERR`: Define se o log deve ser enviado para stderr (`true` ou `false`).

### Exemplo de uso com variáveis de ambiente

```bash
export LOG_TO_FILE=true
export LOG_FILE="logs/data_transfer.log"
export LOG_TO_KAFKA=false
export KAFKA_BOOTSTRAP_SERVERS="localhost:9092"
export KAFKA_TOPIC="logs"
export LOG_TO_STDERR=true
```

## Testes

Para executar os testes, utilize o comando:

```bash
poetry run python -m unittest discover -s tests
```
Isso irá descobrir e executar todos os testes na pasta tests.

