# MediSUS IoT — evidências de avaliação

Este diretório reúne os logs de execução e as capturas fornecidos pela equipe para documentar os testes do protótipo. As leituras mostradas são sintéticas, geradas pelo simulador; nenhuma medição física foi realizada. Os arquivos não representam uma execução independente feita pelo repositório ou pelo GitHub Actions.

## Ambiente registrado

- Python 3.13 e `paho-mqtt 2.1.0`.
- Broker Mosquitto local com a configuração `mosquitto/mosquitto.conf`.
- Limites demonstrativos: `MIN_TEMP_C=2`, `MAX_TEMP_C=8`.
- Tópico MQTT: `medisus/ubs/+/temperatura`.
- Data registrada nas capturas: 19/11/2026.
- Reexecução da suíte neste workspace: Python 3.14.5; 12 testes passaram.

## Fontes e dados

Os dados são gerados por `src/medisus_iot/simulator.py`, que publica quatro valores fixos para fins de demonstração: 4.5, 5.2, 8.3 e 3.8 °C. O tópico, o formato JSON e as validações estão descritos no README e implementados em `src/medisus_iot/readings.py`.

Uma quinta leitura sintética, de 1.5 °C, foi publicada separadamente para testar o limite inferior. Nenhum dado de paciente, funcionário ou sensor físico é usado. Os logs e screenshots T02–T09 incluídos foram recebidos no arquivo de evidências da equipe. A suíte também foi executada novamente neste workspace; o workflow de CI foi adicionado e começará a rodar após o push desta atualização.

## Critérios e resultados

| ID | Caso de teste | Critério de aprovação | Resultado documentado |
|---|---|---|---|
| T01 | Suíte automatizada | Todos os testes de validação, alertas, armazenamento e integração de IA simulada passam | 12/12 passaram; consulte [`T01_testes_unitarios.txt`](logs/T01_testes_unitarios.txt) e [`T01_testes_unitarios.png`](prints/T01_testes_unitarios.png). |
| T02 | Simulador MQTT | Quatro temperaturas sintéticas são publicadas no tópico da demonstração | 4 publicações registradas; [`log`](logs/T02_simulador.txt) e [captura](prints/T02_simulador.png). |
| T03 | Alertas de temperatura | 8.3 °C e 1.5 °C são marcados fora dos limites demonstrativos; 4.5, 5.2 e 3.8 °C não | 5 leituras observadas, 2 alertas; [`log`](logs/T03_logs_alerta.txt) e [captura](prints/T03_logs_alerta.png). |
| T04 | Persistência SQLite | Leituras válidas e flag de alerta ficam armazenadas | 5 linhas, 2 alertas; [`log`](logs/T04_sqlite_leituras.txt) e [captura](prints/T04_sqlite_leituras.png). |
| T05 | Payloads inválidos | Seis formatos/campos inválidos são rejeitados pelo monitor | 6 rejeições registradas; [`log`](logs/T05_payloads_invalidos.txt) e [captura](prints/T05_payloads_invalidos.png). |
| T06 | Persistência após reinício | Os registros permanecem no banco após reiniciar o monitor | 5 registros antes e depois; [`log`](logs/T06_persistencia.txt) e [captura](prints/T06_persistencia.png). |
| T07 | Configuração inválida | Limites invertidos ou não numéricos impedem a inicialização | As duas configurações foram rejeitadas; [`log`](logs/T07_config_invalida.txt) e [captura](prints/T07_config_invalida.png). |
| T08 | Proteções do resumidor de IA | Sem chave ou sem leituras, o comando termina com mensagem clara; só temperaturas, horários e flags são enviados | Comportamentos documentados; [`log`](logs/T08_ia_sem_chave.txt) e [captura](prints/T08_ia_sem_chave.png). |
| T09 | Integração de IA simulada | Testes mock validam requisição, resposta e erros sem chamar serviço externo | 3/3 passaram; [`log`](logs/T09_ia_testes_mock.txt) e [captura](prints/T09_ia_testes_mock.png). |
| T10 | Configuração Docker Compose | Serviços base e serviços de cada perfil aparecem na configuração | Verificação reproduzida no log [`T10_docker_config.txt`](logs/T10_docker_config.txt). A captura recebida para este teste não foi incluída porque os serviços listados nela não correspondiam ao arquivo Compose atual. |
| T11 | Execução ponta a ponta em Docker Compose | Broker, serviço e simulador sobem juntos e produzem leituras/alertas | **Passou no computador da equipe:** broker `Healthy`, monitor `Started`, quatro leituras publicadas e alerta `8.3 °C` confirmado no log; consulte [`T11_docker_compose.txt`](logs/T11_docker_compose.txt). |
| T12 | Resumo com chamada real à IA | Uma chamada autenticada retorna um resumo; a chave permanece privada | **Pendente.** Requer chave de API válida e pode gerar cobrança. Os testes mock T09 não substituem uma chamada real. |

O workflow [`tests.yml`](../.github/workflows/tests.yml) executou com sucesso no GitHub Actions: 12 testes passaram no runner Windows. Consulte o [histórico das execuções](https://github.com/Rodrigocsilvaa/MediSUS-IoT/actions/workflows/tests.yml).

## Interpretação

Nos limites meramente demonstrativos de 2–8 °C, o conjunto observado contém cinco leituras válidas: três dentro do intervalo e duas marcadas como alerta. Isso corresponde a **2/5 leituras sinalizadas (40%) neste cenário sintético**, não a uma taxa de erro ou desempenho clínico. Os seis payloads malformados do T05 foram recusados. O T01 documenta 12 testes automatizados aprovados; T09 isola os três testes específicos do resumidor de IA.

Os alertas são determinados por regras fixas no serviço. A IA generativa, quando solicitada, apenas resume as últimas leituras e alertas; ela não calcula limites, diagnostica condições ou substitui uma avaliação profissional.

## Limitações e reprodução

- Os valores 2 °C e 8 °C são parâmetros de demonstração, não orientação universal ou regulatória. Para qualquer produto real, limites devem ser obtidos em fonte oficial aplicável àquele produto.
- As capturas e logs T02–T09 foram fornecidos pela equipe; T01 foi executado novamente neste workspace e no GitHub Actions; T10 foi verificado no ambiente atual. O log T11 foi enviado pela equipe em 22/11/2026 e confirma a execução ponta a ponta via Compose no computador dela. T12 continua pendente.
- O sensor, o ESP32 e a ligação elétrica não foram testados em hardware.
- O broker de demonstração permite conexões anônimas e não usa TLS. Não exponha a porta 1883 em uma rede não confiável.
- O resumo por IA depende de uma API externa, pode custar dinheiro e pode produzir erros. Use somente dados sintéticos; nunca envie informações pessoais ou dados reais de saúde.
- SQLite, logs e limites demonstrativos não são adequados para operar armazenamento clínico.

Para repetir a demonstração e os testes no Windows, siga as instruções de execução e os comandos no [README principal](../README.md).
