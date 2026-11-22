# Guia de estudo para a apresentação — MediSUS IoT

Este guia explica o protótipo com palavras simples para ajudar a equipe a compreender e apresentar o que foi implementado. Não é necessário decorar nomes de bibliotecas: o mais importante é conseguir explicar o caminho dos dados, o papel de cada componente e os limites do protótipo.

> **Apresente com honestidade:** a demonstração usa leituras sintéticas do simulador. O ESP32 e o DS18B20 aparecem como referência de integração, mas não foram testados em hardware. Os limites de 2 °C e 8 °C são apenas parâmetros de demonstração. A IA resume leituras sob demanda; não calcula os alertas. Os testes automatizados da IA usam uma resposta simulada. Uma chamada real à API exige uma chave válida e pode gerar cobrança.

## 1. A ideia do MediSUS e a contribuição IoT

O MediSUS busca facilitar o acesso da população aos medicamentos da rede pública, conectando tecnologia e serviços de saúde.

O projeto IoT contribui para esse contexto ao demonstrar o monitoramento da temperatura de armazenamento de medicamentos em uma UBS. O fluxo recebe leituras, compara com parâmetros de demonstração, salva os dados e registra alertas. Para dispensar hardware na apresentação, as leituras são sintéticas e publicadas pelo simulador.

### Como explicar a proposta

> “O MediSUS usa tecnologia para facilitar o acesso da população aos medicamentos da rede pública. Nosso projeto IoT aborda as condições de armazenamento em uma UBS: o simulador envia leituras de temperatura e o sistema registra os dados e sinaliza valores fora dos parâmetros de demonstração.”

## 2. Como explicar a arquitetura

O caminho de uma leitura é:

```text
Sensor DS18B20 → ESP32 → MQTT/Mosquitto → serviço Python
                                            ├─ valida a leitura
                                            ├─ compara com os limites
                                            ├─ salva no SQLite
                                            └─ escreve no log
                                                   ↓
                                       resumo opcional por IA
```

Na apresentação feita sem hardware, o simulador substitui o sensor e o ESP32 e publica quatro leituras sintéticas: 4.5, 5.2, 8.3 e 3.8 °C.

### Termos técnicos em linguagem simples

| Termo | O que significa neste projeto |
|---|---|
| **DS18B20** | Sensor digital de temperatura previsto para o protótipo físico. |
| **ESP32** | Placa que poderia ler o sensor e enviar sua temperatura pela rede Wi-Fi. |
| **MQTT** | Protocolo leve para enviar mensagens pequenas entre dispositivos e serviços. |
| **Broker / Mosquitto** | A central que recebe mensagens MQTT e as encaminha a quem assinou o tópico. |
| **Tópico** | O endereço/canal da mensagem. O monitor assina `medisus/ubs/+/temperatura`. |
| **Payload** | O conteúdo da mensagem, neste caso um JSON com identificador, temperatura e horário. |
| **Monitor** | O serviço Python que recebe a leitura, valida, decide se está fora dos limites, grava e registra o resultado. |
| **SQLite** | Um banco de dados simples, guardado em arquivo, onde as leituras ficam registradas. |
| **Log** | Um registro textual do que o programa fez. É como um diário de execução: conexão, leitura recebida, alerta ou erro. |
| **Docker Compose** | Uma ferramenta que inicia os componentes da demonstração juntos, sem instalar Mosquitto e as dependências Python manualmente. |
| **IA generativa** | Neste projeto, um recurso opcional que transforma as últimas leituras e alertas em um resumo escrito. |

Uma analogia: o sensor prepara o recado, o MQTT é o serviço de entrega, o Mosquitto é a central de distribuição, o monitor é quem confere o recado e o SQLite é o caderno onde ele é anotado.

## 3. O que acontece com uma leitura

O monitor recebe uma mensagem como esta:

```json
{
  "device_id": "simulador-ubs-demo",
  "temperature_c": 8.3,
  "timestamp": "2026-11-22T20:11:56Z"
}
```

Ele verifica se o JSON está correto, se a temperatura é um número válido e se o horário informa o fuso. A faixa de −55 °C a 125 °C é a faixa física declarada para o sensor DS18B20; ela **não** é o limite de armazenamento de medicamentos.

Depois, compara a leitura com as variáveis de demonstração `MIN_TEMP_C=2` e `MAX_TEMP_C=8`:

- 4.5 °C: dentro do intervalo de demonstração; sem alerta.
- 5.2 °C: dentro; sem alerta.
- 8.3 °C: acima; alerta.
- 3.8 °C: dentro; sem alerta.

As pontas são permitidas: exatamente 2 °C ou 8 °C não gera alerta. A regra é fixa e fácil de explicar: alerta se a temperatura for menor que o mínimo ou maior que o máximo.

O resultado também é salvo no SQLite. O log mostra o que aconteceu; ele não é o banco de dados. Na demonstração, os logs confirmaram quatro leituras e um alerta para 8.3 °C.

## 4. Onde encontrar cada parte do código

| Arquivo | Responsabilidade |
|---|---|
| `docker-compose.yml` | Define o broker, o monitor, o simulador, o banco persistente e o comando opcional da IA. |
| `mosquitto/mosquitto.conf` | Configura o broker MQTT local da demonstração. |
| `src/medisus_iot/simulator.py` | Publica as quatro leituras sintéticas. |
| `src/medisus_iot/monitor.py` | Assina o tópico MQTT, processa as mensagens, grava e registra alertas. |
| `src/medisus_iot/readings.py` | Valida o conteúdo da mensagem e contém a regra de faixa. |
| `src/medisus_iot/storage.py` | Cria a tabela SQLite, salva leituras e consulta as mais recentes. |
| `src/medisus_iot/ai_summary.py` | Envia as leituras recentes à API de IA e imprime um resumo em português. |
| `firmware/esp32_ds18b20/esp32_ds18b20.ino` | Exemplo de firmware para uma integração futura com ESP32 e DS18B20. |
| `tests/` | Testes automáticos da validação, dos limites, do SQLite e da integração de IA simulada. |

### Por que foi corrigido o acesso ao SQLite?

O cliente MQTT recebe mensagens em uma thread — uma linha de execução em segundo plano. Por padrão, o SQLite do Python não permite usar em outra thread a conexão criada pela thread principal. Isso poderia fazer o monitor receber a mensagem, falhar ao tentar salvá-la e não concluir o processamento.

O armazenamento agora permite o uso dessa conexão entre threads e usa um lock para que duas operações não mexam nela ao mesmo tempo. O teste `test_records_from_another_thread_like_mqtt_callback` verifica esse caso. A demonstração Docker enviada pela equipe confirmou o recebimento das quatro leituras depois da correção.

## 5. Como demonstrar no VS Code

Abra **Terminal > Novo Terminal** na pasta do projeto. Com o Docker Desktop aberto:

```bash
docker compose up -d --build mosquitto monitor
docker compose --profile demo run --rm simulator
docker compose logs --no-color monitor
```

O primeiro comando inicia o broker e o monitor; o segundo publica as leituras; o terceiro mostra o diário de execução. Procure a leitura `8.3` com `"alert": true`.

Para mostrar o conteúdo persistido:

```bash
docker compose exec monitor python -c "import sqlite3; c=sqlite3.connect('/data/readings.sqlite3'); [print(r) for r in c.execute('SELECT temperature_c, alert FROM readings ORDER BY id DESC LIMIT 10')]"
```

O resultado deve listar as temperaturas e `1` para leituras com alerta, `0` para as demais. Para parar os serviços sem apagar o banco:

```bash
docker compose down
```

## 6. Como explicar a parte de IA

A IA não acompanha cada mensagem MQTT e não participa da decisão de alerta. Primeiro o monitor valida, classifica e grava as leituras. Depois, quando alguém executa o comando da IA, `ai_summary.py` consulta até 20 registros recentes e envia à API OpenAI somente a temperatura, o horário e a flag de alerta — não envia `device_id`.

O prompt instrui o modelo a escrever um resumo curto em português, descrever os alertas já calculados e não recomendar ações clínicas. O resumo aparece no terminal. A resposta é gerada por um modelo e pode conter erros; não substitui uma avaliação profissional.

Para uma demonstração **real** da resposta da IA, é necessária uma chave válida da API OpenAI, acesso à internet e uma conta com acesso à API. Sem a chave, não afirme que houve chamada real. Os testes automatizados substituem a resposta da API por uma resposta simulada para testar o código sem internet, sem chave e sem custo de API.

Se a equipe for fazer a chamada real, copie `.env.example` para `.env`, coloque a chave apenas no arquivo local e execute:

```bash
docker compose --profile ai run --rm ai-summary
```

Não exiba nem envie a chave ao GitHub, ao chat ou à gravação da apresentação. O `.env` é ignorado pelo Git; `.env.example` não contém segredo. A chamada pode ter custo.

## 7. Como responder sobre escolhas e limitações

**Por que usar MQTT?** As mensagens de temperatura são pequenas, e o padrão publish/subscribe separa quem envia da aplicação que recebe. Isso permite trocar o simulador por um dispositivo sem mudar o formato central do monitor.

**Por que usar SQLite?** Ele guarda os registros em um arquivo e não exige instalar um servidor de banco separado, o que simplifica a demonstração. Não é uma escolha apropriada para garantir uma operação clínica de alta disponibilidade.

**Os dados são reais?** Não. São valores sintéticos publicados pelo simulador. O hardware é apenas uma referência e não foi validado.

**O que o alerta prova?** Prova que a regra configurada detecta um valor fora do intervalo de demonstração e o registra no log e no banco. Não prova que o produto esteja seguro ou inseguro.

**Quais são as limitações?** Não há calibração, teste físico, painel visual, notificações a pessoas ou segurança de produção no broker local. O intervalo é único e demonstrativo. O resumo de IA pode errar e depende de um serviço externo.

## 8. Como mostrar adaptação a uma nova exigência

Se pedirem para alterar o intervalo geral de demonstração para 3–7 °C, mude `MIN_TEMP_C` e `MAX_TEMP_C` no serviço `monitor` em `docker-compose.yml` e recrie o monitor:

```bash
docker compose up -d --force-recreate monitor
```

Se a mudança for “cada medicamento tem seu próprio intervalo”, explique que a versão atual **ainda não faz isso**: hoje existe um par de limites global. Para implementar, seria necessário identificar o produto em cada leitura, guardar limites por produto numa configuração ou tabela e escolher o intervalo certo antes de classificar. Depois, seriam necessários testes para produtos e limites diferentes.

Uma boa resposta a qualquer mudança inesperada é: entender exatamente a regra nova, apontar qual componente decide isso, propor a menor alteração, cobrir os limites com testes e repetir a demonstração.

## 9. Roteiro curto para falar

> “Nosso projeto é uma demonstração de monitoramento de temperatura para armazenamento em uma UBS. O fluxo previsto é sensor DS18B20, ESP32, broker MQTT e serviço Python. Como não usamos hardware na demonstração, o simulador publica dados sintéticos. O monitor valida cada leitura, compara com limites configuráveis de demonstração, salva no SQLite e registra alerta quando sai do intervalo. Na execução, o broker iniciou e o monitor recebeu quatro leituras; 8.3 °C gerou alerta. A IA é um recurso opcional separado: resume leituras já registradas, mas não calcula os alertas. O sistema não está validado para uso clínico nem em hardware.”

É melhor explicar esse fluxo com suas próprias palavras do que decorar o texto exatamente.

## 10. Declaração transparente de IA

O material de orientação da Global Solution pede que o uso de IA generativa seja declarado e que o grupo entenda e revise o material entregue. Uma declaração honesta pode ser:

> “Utilizamos uma ferramenta de IA generativa como apoio à implementação e à documentação. Revisamos o fluxo, executamos os testes automatizados e a demonstração sintética, e reconhecemos as limitações do protótipo.”

Cada integrante deve estudar o suficiente para explicar e responder perguntas sobre o que a equipe apresenta. Não afirmem que o protótipo físico ou a chamada real da IA foram testados se isso não aconteceu.

## Como usar este guia

Este é o material de estudo da equipe: explica a arquitetura, o caminho das leituras, a demonstração, a IA, as limitações e como pensar em mudanças de requisito. O objetivo é compreender e explicar o projeto com as próprias palavras, não decorar o texto.
