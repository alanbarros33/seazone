import pandas as pd
import streamlit as st
import plotly.express as px
import locale


# Carregar os dados
@st.cache_data
def load_data():
    return pd.read_excel("Base.xlsx")

df = load_data()

# Pré-processamento
st.title("Dashboard de Parceiros - Seazone")
df["Taxa Conversão"] = df["Quantidade de indicações que foram fechadas"] / df["Quantidade de indicações de proprietários"]
df["Data de último contato"] = pd.to_datetime(df["Data de último contato"])
df["Dias sem contato"] = (pd.to_datetime("today") - df["Data de último contato"]).dt.days

# Filtros
st.sidebar.header("Filtros")
cidade = st.sidebar.multiselect("Cidade", options=df["Cidade"].unique(), default=df["Cidade"].unique())
canal = st.sidebar.multiselect("Canal de Aquisição", options=df["Canal de aquisição"].unique(), default=df["Canal de aquisição"].unique())
tipo = st.sidebar.multiselect("Tipo de Parceiro", options=df["Tipo de parceiro"].unique(), default=df["Tipo de parceiro"].unique())

# Aplicar filtros
filtro = df[
    df["Cidade"].isin(cidade) &
    df["Canal de aquisição"].isin(canal) &
    df["Tipo de parceiro"].isin(tipo)
]

# Métricas principais
col1, col2, col3 = st.columns(3)
col1.metric("Parceiros Ativos", filtro[filtro["Status da parceria"] == "Ativo"].shape[0])
col2.metric("Média de Conversão", f"{filtro['Taxa Conversão'].mean():.1%}")
col3.metric("Média de NPS", f"{filtro['NPS da última interação'].mean():.1f}")

# Gráfico 1: Taxa de conversão por parceiro
st.subheader("Top 10 Parceiros por Conversão")
top_parceiros = filtro.sort_values(by="Taxa Conversão", ascending=False).head(10)
fig1 = px.bar(top_parceiros, x="Nome do Parceiro", y="Taxa Conversão", color="Taxa Conversão", text_auto=True)
st.plotly_chart(fig1, use_container_width=True)

# Gráfico 2: Conversão por Canal de Aquisição
st.subheader("Taxa Média de Conversão por Canal de Aquisição")
canal_conv = filtro.groupby("Canal de aquisição")["Taxa Conversão"].mean().reset_index()
fig2 = px.bar(canal_conv, x="Canal de aquisição", y="Taxa Conversão", color="Taxa Conversão", text_auto=True)
st.plotly_chart(fig2, use_container_width=True)

# Gráfico 3: Risco de churn
st.subheader("Parceiros com Maior Risco de Churn")
filtro["Risco"] = (
    (filtro["Status da parceria"] == "Inativo") |
    (filtro["NPS da última interação"] < 30) |
    (filtro["Dias sem contato"] > 60) |
    (filtro["Taxa Conversão"] < 0.2)
)
risco = filtro[filtro["Risco"]]
fig3 = px.scatter(risco, x="Dias sem contato", y="NPS da última interação", color="Taxa Conversão", hover_data=["Nome do Parceiro"])
st.plotly_chart(fig3, use_container_width=True)

# Tabela de dados filtrados
st.subheader("Base de Parceiros Filtrada")
st.dataframe(filtro.reset_index(drop=True))
