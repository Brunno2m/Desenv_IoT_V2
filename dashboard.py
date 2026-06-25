import streamlit as st
import requests
import pandas as pd
import os

ORION_BASE_URL = os.getenv("ORION_BASE_URL", "http://127.0.0.1:1026")
QUANTUMLEAP_BASE_URL = os.getenv("QUANTUMLEAP_BASE_URL", "http://127.0.0.1:8668")
HTTP_TIMEOUT_SECONDS = float(os.getenv("HTTP_TIMEOUT_SECONDS", "5"))
FIWARE_SERVICE = os.getenv("FIWARE_SERVICE", "")
FIWARE_SERVICEPATH = os.getenv("FIWARE_SERVICEPATH", "/")


def fiware_headers(include_accept: bool = True):
    headers = {}
    if include_accept:
        headers["Accept"] = "application/json"
    headers["Fiware-ServicePath"] = FIWARE_SERVICEPATH
    if FIWARE_SERVICE:
        headers["Fiware-Service"] = FIWARE_SERVICE
    return headers

# Configuração da Página
st.set_page_config(page_title="Gêmeo Digital - Mineração", layout="wide")

st.title("Gêmeo Digital: Monitoramento de Qualidade do Ar")
st.markdown("Cenário 2: Análise de Série Temporal e Eficiência Energética")

# Função para buscar dados históricos do QuantumLeap com tratamento de erros detalhado
def get_historical_data(zona_id):
    # Adicionado o ?type=ZonaMineracao para forçar o QuantumLeap a procurar na tabela correta
    url = (
        f"{QUANTUMLEAP_BASE_URL}/v2/entities/{zona_id}"
        "?type=ZonaMineracao&attrs=media_ch4,status_ventilacao&lastN=200"
    )
    headers = fiware_headers()
    
    try:
        response = requests.get(url, headers=headers, timeout=HTTP_TIMEOUT_SECONDS)
        if response.status_code == 200:
            return response.json(), None
        elif response.status_code == 404:
            return None, f"Erro 404: O QuantumLeap ainda não tem histórico para a zona '{zona_id}'. O banco CrateDB pode estar bloqueado."
        else:
            return None, f"Erro da API QuantumLeap (Código {response.status_code}): {response.text}"
    except Exception as e:
        return None, f"Erro de Conexão: Não foi possível ligar ao QuantumLeap. Detalhe: {e}"

# Interface do Usuário - Seleção de Zona
st.sidebar.header("Controles")
zona_selecionada = st.sidebar.selectbox("Selecione a Zona de Mineração", [
    "urn:ngsi-ld:ZonaMineracao:frente_lavra",
    "urn:ngsi-ld:ZonaMineracao:galeria_acesso_02",
    "urn:ngsi-ld:ZonaMineracao:rampa_transporte"
])

st.sidebar.markdown("---")
st.sidebar.subheader("Ferramentas")

# --- BLOCO NOVO: DIAGNÓSTICO DO SISTEMA ---
if st.sidebar.button("🛠️ Executar Diagnóstico do Sistema"):
    st.header("🔍 Relatório de Diagnóstico da Arquitetura IoT")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Estado Atual no Orion (Gêmeo Digital)")
        try:
            orion_res = requests.get(f"{ORION_BASE_URL}/v2/entities", timeout=HTTP_TIMEOUT_SECONDS)
            if orion_res.status_code == 200 and len(orion_res.json()) > 0:
                st.success("✅ Orion a receber dados do Node-RED!")
                with st.expander("Ver Dados do Orion"):
                    st.json(orion_res.json())
            else:
                st.error("❌ Orion vazio. O Node-RED não está a enviar dados.")
        except Exception as e:
            st.error(f"❌ Falha de ligação ao Orion: {e}")

    with col2:
        st.subheader("2. Regras de Notificação (Subscriptions)")
        try:
            subs_res = requests.get(f"{ORION_BASE_URL}/v2/subscriptions", timeout=HTTP_TIMEOUT_SECONDS)
            if subs_res.status_code == 200:
                subs_data = subs_res.json()
                if len(subs_data) > 0:
                    status = subs_data[0].get("status", "desconhecido")
                    if status == "active":
                        st.success("✅ Subscription encontrada e Ativa (A enviar para o QL)!")
                    elif status == "failed":
                        st.error(f"❌ Falha ao enviar para o QuantumLeap. Status: {status}")
                    with st.expander("Ver Dados da Subscription"):
                        st.json(subs_data)
                else:
                    st.warning("⚠️ Nenhuma Subscription encontrada no Orion.")
            else:
                st.error("❌ Falha ao verificar Subscriptions.")
        except Exception as e:
            st.error(f"❌ Falha de ligação: {e}")
            
    st.markdown("---")
    
    # NOVA SEÇÃO: DIAGNÓSTICO PROFUNDO DO QUANTUMLEAP
    st.subheader("3. Teste Profundo: O que o QuantumLeap tem no Banco de Dados (CrateDB)?")
    try:
        ql_res = requests.get(
            f"{QUANTUMLEAP_BASE_URL}/v2/entities",
            headers=fiware_headers(),
            timeout=HTTP_TIMEOUT_SECONDS,
        )
        if ql_res.status_code == 200:
            ql_data = ql_res.json()
            if isinstance(ql_data, list) and len(ql_data) > 0:
                st.success(f"✅ SUCESSO! O banco de dados histórico tem {len(ql_data)} entidades gravadas. O gráfico já deve funcionar!")
                with st.expander("Ver Entidades no Banco"):
                    st.json(ql_data)
            else:
                st.error("❌ ALERTA: O QuantumLeap respondeu com Código 200, MAS O BANCO DE DADOS ESTÁ VAZIO.")
                st.warning("Problema de gravação silenciosa detetado no CrateDB.")
        elif ql_res.status_code == 404:
            st.error("❌ ALERTA: O Banco de Dados (CrateDB) está VAZIO! (Erro 404)")
            st.warning("O Orion está a enviar os dados e o QuantumLeap diz que os recebe, mas a gravação no disco está a falhar. Isto é um comportamento típico do CrateDB no GitHub Codespaces, que entra em 'Modo de Apenas Leitura' por restrições de espaço ou limites de memória mapeada do Linux.")
            st.info("💡 **SOLUÇÃO DEFINITIVA (Execute no terminal do Codespace):**\n\n"
                    "1. Limpar volumes corrompidos: `docker compose down -v`\n"
                    "2. Ajustar memória do sistema: `sudo sysctl -w vm.max_map_count=262144`\n"
                    "3. Subir de novo: `docker compose up -d`\n"
                    "4. Criar a Subscription via cURL e rodar o `publisher.py` de novo.")
        else:
            st.error(f"❌ Erro ao consultar a raiz do QL: {ql_res.status_code}")
    except Exception as e:
        st.error(f"❌ Falha de ligação direta ao QL: {e}")
            
    st.stop() # Interrompe a renderização do resto da página enquanto no modo diagnóstico

# --- FIM DO BLOCO DE DIAGNÓSTICO ---

if st.button("Atualizar Dados Históricos"):
    with st.spinner("A consultar banco de dados temporal (QuantumLeap)..."):
        data, error_msg = get_historical_data(zona_selecionada)
        
        # Se houver um erro de conexão ou 404, exibe-o claramente
        if error_msg:
            st.error(error_msg)
            
        elif data and 'index' in data:
            # O QuantumLeap retorna as datas no 'index' e os valores em 'attributes'
            timestamps = data['index']
            
            # Vamos extrair os atributos dinamicamente de forma segura
            attr_dict = {
                attr['attrName']: attr['values']
                for attr in data.get('attributes', [])
                if 'attrName' in attr and 'values' in attr
            }
            
            if 'media_ch4' in attr_dict and 'status_ventilacao' in attr_dict:
                # Converte os dados brutos para um DataFrame (tabela) do Pandas
                df = pd.DataFrame({
                    'Horário': pd.to_datetime(timestamps),
                    'Média CH4 (%vol)': attr_dict['media_ch4'],
                    'Status Ventilação': attr_dict['status_ventilacao']
                })
                
                # Formata a data para ficar mais legível no fuso horário local
                df['Horário'] = df['Horário'].dt.tz_convert('America/Sao_Paulo') if df['Horário'].dt.tz is not None else df['Horário']
                
                # --- VISUALIZAÇÃO 1: SÉRIE TEMPORAL ---
                st.subheader("📈 Comportamento do Metano (CH4) no Tempo")
                st.markdown("**Pergunta respondida:** *Os níveis de metano estão a ultrapassar o limite de segurança operacional?*")
                
                # Gráfico de linha nativo do Streamlit
                chart_data = df.set_index('Horário')[['Média CH4 (%vol)']]
                st.line_chart(chart_data, color="#ff4b4b")
                
                # --- VISUALIZAÇÃO 2: INDICADOR DE NEGÓCIO (ECONOMIA) ---
                st.markdown("---")
                st.subheader("💰 Indicador de Eficiência Operacional")
                st.markdown("**Pergunta respondida:** *Qual a percentagem de tempo em que economizamos energia mantendo a ventilação no modo mínimo de forma segura?*")
                
                # Cálculo da regra de negócio: Tempo em economia vs Tempo em alerta
                total_leituras = len(df)
                leituras_economia = len(df[df['Status Ventilação'] == 'MODO_ECONOMIA - VENTILACAO MINIMA'])
                
                if total_leituras > 0:
                    economia_pct = (leituras_economia / total_leituras) * 100
                    alerta_pct = 100 - economia_pct
                    
                    col1, col2 = st.columns(2)
                    col1.metric(label="🔌 Tempo em Modo de Economia", value=f"{economia_pct:.1f}%", delta="KW/h economizados")
                    col2.metric(label="⚠️ Tempo em Risco (Ventilação Ligada)", value=f"{alerta_pct:.1f}%", delta="- Risco ambiental", delta_color="inverse")
                
                # Tabela de dados brutos
                with st.expander("Ver telemetria bruta"):
                    st.dataframe(df.sort_values(by="Horário", ascending=False))
                    
            else:
                st.warning("Os atributos 'media_ch4' ou 'status_ventilacao' ainda não foram registados para esta zona.")
        else:
            st.warning("A API retornou dados, mas estão vazios ou num formato inesperado.")
            st.json(data if data else {})