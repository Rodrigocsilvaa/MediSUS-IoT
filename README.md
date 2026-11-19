# MediSUS IoT — monitoramento demonstrativo de temperatura

Protótipo independente para demonstrar o fluxo de monitoramento da temperatura de armazenamento de medicamentos em uma UBS. O fluxo usa um broker MQTT, um serviço Python que valida e registra leituras e um simulador com dados sintéticos. O sketch do ESP32 com sensor DS18B20 é uma referência para integração futura.

> **Atenção:** os limites padrão deste projeto são parâmetros de demonstração, não recomendações médicas nem limites regulatórios. Antes de qualquer uso real, configure os limites a partir de uma fonte oficial aplicável ao produto específico. Este protótipo não foi validado em hardware e não substitui instrumentos ou procedimentos qualificados.

## Requisitos

- Docker com Docker Compose v2 para executar o broker e o serviço.
- Python 3.10+ e `pip` para executar os testes localmente.
- Para o sketch: Arduino IDE ou PlatformIO, placa ESP32 e bibliotecas `PubSubClient`, `OneWire` e `DallasTemperature`.

## Executar a demonstração

Na raiz deste repositório:

```sh
docker compose up -d --build mosquitto monitor
docker compose --profile demo run --rm simulator
docker compose logs monitor
```

O simulador publica quatro leituras sintéticas no tópico `medisus/ubs/demo/temperatura`. Com os limites de demonstração padrão (`2 °C` a `8 °C`), uma leitura acima do limite gera um alerta nos logs. As demais leituras válidas também são registradas no banco SQLite do serviço.

Para acompanhar o broker e o serviço:

```sh
docker compose logs -f mosquitto monitor
```

Para parar os contêineres:

```sh
docker compose down
```

Os dados ficam no volume Docker `medisus-iot-data`. Para descartá-los junto com o volume, execute `docker compose down --volumes`.

### Ajustar os limites da demonstração

Edite `MIN_TEMP_C` e `MAX_TEMP_C` no serviço `monitor` em `docker-compose.yml` e recrie o serviço:

```sh
docker compose up -d --build --force-recreate monitor
```

Os valores `2` e `8` existem exclusivamente para tornar a demonstração visível. Não os use como parâmetros de operação clínica.

## Executar testes localmente

Os testes usam apenas a biblioteca padrão do Python:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

No Linux/macOS, use `PYTHONPATH=src python -m unittest discover -s tests -v`.

Para executar o monitor fora do Compose, instale as dependências em um ambiente virtual e configure o endereço do broker:

```sh
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate
pip install -r requirements.txt
```

No PowerShell:

```powershell
$env:MQTT_HOST = "localhost"
python -m medisus_iot.monitor
```

## ESP32 e DS18B20

Conexão de referência para um módulo DS18B20:

| DS18B20 | ESP32 |
|---|---|
| VDD | 3V3 |
| GND | GND |
| DATA | GPIO 4 |

Use um resistor de pull-up de 4,7 kΩ entre DATA e 3V3. Confira a pinagem da placa e do sensor utilizados antes de conectar.

Abra `firmware/esp32_ds18b20/esp32_ds18b20.ino`, instale as bibliotecas listadas nos comentários e preencha as configurações de Wi-Fi e broker no próprio dispositivo. Os valores do sketch são placeholders, não credenciais. O firmware publica JSON no mesmo tópico consumido pelo serviço. Para a demonstração local, o broker não usa TLS nem autenticação; não exponha essa configuração em uma rede não confiável.

O firmware e o circuito não foram testados em hardware real. A simulação via Compose é independente do ESP32.

## Evidências para apresentação

1. Capture os serviços iniciados (`docker compose ps`).
2. Mostre a execução do simulador e as mensagens de leitura/alerta (`docker compose logs monitor`).
3. Se houver hardware, registre uma foto do ESP32 e da ligação do DS18B20, sem incluir senhas, tokens ou dados pessoais.
4. Identifique claramente quais evidências são simuladas e quais foram obtidas em hardware. Não apresente leituras sintéticas como medições reais.

## Formato MQTT

O serviço assina `medisus/ubs/+/temperatura`. Cada payload deve conter:

```json
{
  "device_id": "simulador-ubs-demo",
  "temperature_c": 8.3,
  "timestamp": "2026-01-01T12:00:00Z"
}
```

`temperature_c` precisa ser um número finito dentro da faixa física do DS18B20 (-55 °C a 125 °C); `timestamp` deve ser ISO 8601 com fuso horário. Payloads inválidos são rejeitados e registrados no log, sem interromper o monitor.

## Limitações

- Demonstração acadêmica; sem calibração, redundância, retenção validada, autenticação ou transporte MQTT criptografado.
- O SQLite e o alerta em log não são um sistema de notificação nem uma garantia de entrega.
- A qualidade da medição depende de instalação, sensor, calibração e condições ambientais que não são avaliadas aqui.
- Limites de armazenamento devem ser obtidos para cada produto em fontes oficiais aplicáveis.
