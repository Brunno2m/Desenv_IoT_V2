# Gêmeo Digital: Monitoramento de Qualidade do Ar na Mineração

Este projeto implementa uma arquitetura IoT ponta a ponta utilizando FIWARE, Node-RED e Docker para monitorizar zonas de mineração, garantindo segurança operacional através do controle inteligente de ventilação.

## Arquitetura do Sistema

O sistema é composto por:
* **Simulador (Python):** Gera telemetria (CH4, CO, O2, etc.) para 12 sensores distribuídos em 3 zonas.
* **Broker (Mosquitto):** Barramento de mensagens MQTT.
* **Gateway (Node-RED):** Processa regras de negócio (cálculo de média de CH4) e integra com o FIWARE.
* **Context Broker (Orion):** Mantém o estado atual do Gêmeo Digital (NGSIv2).
* **Persistência (QuantumLeap + CrateDB):** Armazenamento de séries temporais.
* **Interface (Streamlit):** Dashboard analítico para visualização de dados e eficiência energética.

## Pré-requisitos

* **Docker e Docker Compose** instalados.
* **Python 3.9+** com as bibliotecas instaladas:
  ```bash
  pip install streamlit pandas requests paho-mqtt
  ```

## Como Executar

### 1. Iniciar a Infraestrutura
Na raiz do projeto, suba os serviços FIWARE/MQTT:
```bash
docker compose up -d
```

### 2. Iniciar o Simulador de Sensores
Abra um terminal e execute o publicador de dados:
```bash
python publisher.py
```

### 3. Configurar o Fluxo no Node-RED
1. Acesse `http://localhost:1880`.
2. Importe o conteúdo do arquivo `FluxoNodeRED.json` (Menu > Import).
3. Verifique se o nó MQTT está conectado (bolinha verde).
4. Clique no botão vermelho **Deploy** no canto superior direito.

### 4. Executar o Dashboard
Em um novo terminal, inicie a interface de monitoramento:
```bash
python -m streamlit run dashboard.py
```
Acesse `http://localhost:8501` no seu navegador.

## Diagnóstico de Problemas

Se os dados não aparecerem, utilize o botão **"🛠️ Executar Diagnóstico do Sistema"** dentro do próprio Dashboard Streamlit. Ele valida automaticamente:
* Conexão com o Orion.
* Status das Subscriptions.
* Integridade da gravação no CrateDB.

## Estrutura de Arquivos

* `docker-compose.yml`: Definição de todos os contêineres.
* `publisher.py`: Simulador MQTT.
* `dashboard.py`: Interface de análise.
* `FluxoNodeRED.json`: Lógica de integração e regras de ventilação.
* `RegraDeNegocio.js`: Script de cálculo de médias dentro do Node-RED.

---
*Projeto desenvolvido para a disciplina de Desenvolvimento IoT - IFRN Campus Parnamirim.*