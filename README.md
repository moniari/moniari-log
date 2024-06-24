# Moniari Log

Pacote de logging para uso interno da empresa, proporcionando uma interface de log simples e direta. Suporta gravação de logs em arquivos, saída padrão de erro (stderr) e integração com o Kafka para distribuição em um ambiente de mensageria. Configurável para diferentes ambientes como desenvolvimento e produção através de arquivos JSON.

## Instalação

Para instalar o pacote, use o [Poetry](https://python-poetry.org/):

```bash
poetry add moniari-log
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
Para utilizar o Moniari-Log em seu projeto, você pode importar a classe MoniariLog e configurá-la para usar o arquivo de configuração desejado. A estrutura de diretórios deve conter uma pasta config dentro do diretório principal do projeto, onde devem estar os arquivos de configuração JSON (dev.json e prod.json).

### Exemplo de uso

```python
import os
from moniari_log.logger import MoniariLog

# Define o caminho para o arquivo de configuração do novo projeto
config_file_path = os.path.join(os.path.dirname(__file__), 'config/dev.json')

# Cria uma instância do MoniariLog com o arquivo de configuração do novo projeto
logger = MoniariLog(config_file=config_file_path)

# Usa o logger para registrar mensagens
logger.info("This is an info message from my new project")
logger.error("This is an error message from my new project")

# Fecha o logger ao finalizar
logger.close()
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

