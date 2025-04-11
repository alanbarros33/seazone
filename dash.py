import pandas as pd
import streamlit as st
import plotly.express as px

# Carregar os dados
df = pd.read_excel("Base.xlsx")

# Pré-processamento
st.title("Dashboard de Parceiros - Seazone")

# Verificar se as colunas necessárias existem antes de calcular
if all(col in df.columns for col in ["Quantidade de indicações que foram fechadas", "Quantidade de indicações de proprietários"]):
    df["Taxa Conversão"] = df["Quantidade de indicações que foram fechadas"] / df["Quantidade de indicações de proprietários"]
else:
    st.error("Colunas necessárias para cálculo da Taxa de Conversão não encontradas!")

if "Data de último contato" in df.columns:
    df["Data de último contato"] = pd.to_datetime(df["Data de último contato"])
    df["Dias sem contato"] = (pd.to_datetime("today") - df["Data de último contato"]).dt.days
else:
    st.error("Coluna 'Data de último contato' não encontrada!")

# Filtros
st.sidebar.header("Filtros")

# Verificar se as colunas existem antes de criar filtros
if "Cidade" in df.columns:
    cidade = st.sidebar.multiselect("Cidade", options=df["Cidade"].unique(), default=df["Cidade"].unique())
else:
    cidade = []
    st.sidebar.error("Coluna 'Cidade' não encontrada!")

if "Canal de aquisição" in df.columns:
    canal = st.sidebar.multiselect("Canal de Aquisição", options=df["Canal de aquisição"].unique(), default=df["Canal de aquisição"].unique())
else:
    canal = []
    st.sidebar.error("Coluna 'Canal de aquisição' não encontrada!")

if "Tipo de parceiro" in df.columns:
    tipo = st.sidebar.multiselect("Tipo de Parceiro", options=df["Tipo de parceiro"].unique(), default=df["Tipo de parceiro"].unique())
else:
    tipo = []
    st.sidebar.error("Coluna 'Tipo de parceiro' não encontrada!")

# Aplicar filtros
filtro = df.copy()
if cidade:
    filtro = filtro[filtro["Cidade"].isin(cidade)]
if canal:
    filtro = filtro[filtro["Canal de aquisição"].isin(canal)]
if tipo:
    filtro = filtro[filtro["Tipo de parceiro"].isin(tipo)]

# Métricas principais
col1, col2, col3 = st.columns(3)

if "Status da parceria" in filtro.columns:
    col1.metric("Parceiros Ativos", filtro[filtro["Status da parceria"] == "Ativo"].shape[0])
else:
    col1.error("Coluna 'Status da parceria' não encontrada")

if "Taxa Conversão" in filtro.columns:
    col2.metric("Média de Conversão", f"{filtro['Taxa Conversão'].mean():.1%}")
else:
    col2.error("Taxa de Conversão não calculada")

if "NPS da última interação" in filtro.columns:
    col3.metric("Média de NPS", f"{filtro['NPS da última interação'].mean():.1f}")
else:
    col3.error("Coluna 'NPS da última interação' não encontrada")

# Gráfico 1: Taxa de conversão por parceiro
if all(col in filtro.columns for col in ["Nome do Parceiro", "Taxa Conversão"]):
    st.subheader("Top 10 Parceiros por Conversão")
    top_parceiros = filtro.sort_values(by="Taxa Conversão", ascending=False).head(10)
    fig1 = px.bar(top_parceiros, x="Nome do Parceiro", y="Taxa Conversão", color="Taxa Conversão", text_auto=True)
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.error("Dados necessários para gráfico de Taxa de Conversão não encontrados")

# Gráfico 2: Conversão por Canal de Aquisição
if all(col in filtro.columns for col in ["Canal de aquisição", "Taxa Conversão"]):
    st.subheader("Taxa Média de Conversão por Canal de Aquisição")
    canal_conv = filtro.groupby("Canal de aquisição")["Taxa Conversão"].mean().reset_index()
    fig2 = px.bar(canal_conv, x="Canal de aquisição", y="Taxa Conversão", color="Taxa Conversão", text_auto=True)
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.error("Dados necessários para gráfico de Canal de Aquisição não encontrados")

# Gráfico 3: Risco de churn
if all(col in filtro.columns for col in ["Status da parceria", "NPS da última interação", "Dias sem contato", "Taxa Conversão"]):
    st.subheader("Parceiros com Maior Risco de Churn")
    filtro["Risco"] = (
        (filtro["Status da parceria"] == "Inativo") |
        (filtro["NPS da última interação"] < 30) |
        (filtro["Dias sem contato"] > 60) |
        (filtro["Taxa Conversão"] < 0.2)
    )
    risco = filtro[filtro["Risco"]]
    fig3 = px.scatter(risco, x="Dias sem contato", y="NPS da última interação", 
                     color="Taxa Conversão", hover_data=["Nome do Parceiro"])
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.error("Dados necessários para análise de risco de churn não encontrados")

# Tabela de dados filtrados
st.subheader("Base de Parceiros Filtrada")
st.dataframe(filtro.reset_index(drop=True))
