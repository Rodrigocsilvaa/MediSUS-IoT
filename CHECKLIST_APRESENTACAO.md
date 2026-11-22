# Checklist de estudo e apresentação — MediSUS IoT

Este checklist é para a equipe revisar antes da apresentação. O objetivo não é decorar o código: é conseguir contar o que o protótipo faz, demonstrar o fluxo e ser transparente sobre o que ainda não faz.

## Antes de estudar: alinhem o escopo

O MediSUS, como proposta maior, ajuda o paciente a fotografar uma receita, identificar medicamentos e encontrar UBS com disponibilidade e informação sobre a Farmácia Popular.

**Este repositório não implementa esse fluxo principal.** Ele contém um protótipo IoT complementar para monitorar temperatura de armazenamento:

- não lê a foto de uma receita;
- não identifica medicamentos prescritos;
- não pesquisa estoque ou UBS próximas;
- não verifica a Farmácia Popular;
- ainda não envia os dados ao aplicativo MediSUS.

Não apresentem essas funções como se estivessem implementadas. A conexão proposta é que, no futuro, dados de armazenamento por produto e UBS poderiam complementar a informação de estoque.

## Roteiro de estudo em 30 minutos

### 1. Entendam o caminho de uma leitura

Leiam a seção **“Como os componentes se conectam”** do README e expliquem juntos:

1. O simulador faz o papel do sensor e publica temperaturas sintéticas.
2. O broker Mosquitto recebe a mensagem MQTT e a encaminha pelo tópico.
3. O monitor Python valida a mensagem e verifica os limites de demonstração.
4. O monitor salva a temperatura e a flag de alerta no SQLite e registra o evento no log.
5. Se alguém executar separadamente o resumidor, a IA pode criar um resumo escrito das últimas leituras.

### 2. Reconheçam os arquivos principais

- `docker-compose.yml`: define os componentes e como iniciá-los.
- `src/medisus_iot/simulator.py`: publica quatro leituras sintéticas.
- `src/medisus_iot/monitor.py`: recebe mensagens, registra os resultados e controla o ciclo do serviço.
- `src/medisus_iot/readings.py`: valida os dados e aplica a regra de alerta.
- `src/medisus_iot/storage.py`: grava e consulta as leituras SQLite.
- `src/medisus_iot/ai_summary.py`: solicita à OpenAI um resumo opcional.
- `tests/`: verifica as regras, o banco e a integração de IA usando uma resposta simulada.

### 3. Reproduzam a demonstração

Com Docker Desktop aberto, no terminal do VS Code e dentro da pasta do repositório:

```bash
docker compose up -d --build mosquitto monitor
docker compose --profile demo run --rm simulator
docker compose logs --no-color monitor
```

Confiram a saída esperada: quatro leituras (4.5, 5.2, 8.3 e 3.8 °C) e uma linha `WARNING` com `"alert": true` para 8.3 °C. São valores **sintéticos**, não uma medição de equipamento real.

O log é o diário de execução do serviço. Ele mostra que o monitor conectou ao broker, recebeu e registrou as leituras ou encontrou algum erro.

### 4. Pratiquem explicar a IA sem exagerar

A IA é opcional e separada da regra de alertas. O serviço já calcula a flag `alert`; quando executado, o resumidor envia até 20 temperaturas, horários e flags para a API e imprime um resumo em português. Ele não identifica medicamentos e não faz OCR da receita.

Os testes com mock usam uma resposta inventada no próprio teste; eles verificam o formato da integração, mas **não são uma resposta real da OpenAI**. Uma chamada real exige chave de API, internet e pode gerar cobrança. Não mostrem a chave e não enviem dados de saúde reais.

Se não tiverem uma chamada real disponível, digam claramente: “A integração foi testada com resposta simulada; a chamada real à API ainda não foi demonstrada.”

### 5. Revisem as limitações

- Não há ESP32 nem DS18B20 físicos validados.
- Os limites 2–8 °C são apenas parâmetros de demonstração, não recomendação clínica ou regulatória.
- Os alertas aparecem no log e no banco; não há notificação para uma pessoa.
- O broker local não usa autenticação nem TLS.
- O SQLite e o protótipo não são destinados a operação clínica.
- A integração de temperatura não está ligada ao estoque ou à busca do MediSUS.
- O resumo generativo pode errar e não deve orientar decisões clínicas.

## Perguntas prováveis

**“Como a mensagem chega ao monitor?”**

O publicador envia uma mensagem MQTT. O Mosquitto a distribui pelo tópico, e o monitor assina esse tópico.

**“O que é o log?”**

É um registro textual do que o programa fez. Aqui, mostra conexão, temperaturas recebidas e alertas.

**“A IA decide se a temperatura está fora do limite?”**

Não. Uma regra fixa no Python calcula o alerta. A IA, quando chamada, só resume os dados e as flags já calculadas.

**“O que faria se os limites mudassem?”**

Para mudar o intervalo global de demonstração, alteraria `MIN_TEMP_C` e `MAX_TEMP_C`, recriaria o monitor e repetiria os testes. Limites reais precisam vir de fonte oficial para o produto específico.

**“E se cada medicamento tiver um limite diferente?”**

Essa versão não suporta isso. Seria preciso identificar o produto em cada leitura, guardar limites por produto, selecionar o limite correspondente e criar testes para cada cenário.

**“Como esse módulo se conecta ao MediSUS?”**

Hoje, apenas como ideia complementar: acompanhar armazenamento poderia ser útil para um sistema de estoque. No código atual não há integração com medicamentos, UBS, receita ou Farmácia Popular.

## Uma forma simples de iniciar a apresentação

> “Vou mostrar um protótipo complementar à proposta MediSUS. Ele demonstra monitoramento de temperatura de armazenamento numa UBS. Para dispensar hardware na apresentação, usamos um simulador com dados sintéticos. As mensagens passam por MQTT até um serviço Python, que valida, classifica pelos limites de demonstração, salva no SQLite e registra alertas. A IA é opcional e somente resume as leituras; não decide os alertas. Este repositório ainda não está integrado à busca de medicamentos do MediSUS.”

Falemos com nossas próprias palavras. Se algo não foi testado, digamos isso claramente em vez de afirmar que funciona.

## Uso de IA e entrega no GitHub

O material da disciplina orienta declarar o uso de IA generativa e não entregar código sem entender e revisar. Uma declaração que a equipe pode adaptar:

> “Utilizamos uma ferramenta de IA generativa como apoio à implementação e à documentação. Revisamos o fluxo, executamos os testes e a demonstração sintética e reconhecemos as limitações do protótipo.”

Para a disciplina **Disruptive Architectures: IoT, IoB & Generative IA**, o PDF de orientações pede o repositório com código, dependências, configurações de exemplo sem credenciais, README e evidências; para entrega, pede **um arquivo `.txt` com RM, nome completo de cada integrante e link do GitHub**.

O repositório público na branch `main`, o README, o código, as imagens e o relatório de evidências já estão no GitHub. O arquivo [`link_repositorio_iot.txt`](link_repositorio_iot.txt) contém os dados informados pela equipe; confirmem se cada nome está completo conforme o cadastro acadêmico antes de anexar. A presença do `.txt` no GitHub não o envia ao Portal: o grupo ainda precisa anexá-lo à entrega da disciplina.

Confiram a página da própria entrega no Portal para instruções adicionais ou situação do envio. O prazo que aparece no PDF é 19/11/2026 às 23h55; se o trabalho ainda não foi enviado, verifiquem com a coordenação se há possibilidade de entrega após o prazo.
