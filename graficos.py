import mysql.connector
import pandas as pd
import plotly.graph_objs as go
import plotly.offline as pyo
import streamlit as st
import plotly.express as px
from streamlit_option_menu import option_menu
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import plotly.subplots as sp

# Conecte-se ao banco de dados MySQL
cnx = mysql.connector.connect(user='root', password='airflow',
                              host='172.17.0.2', database='financial')
cursor = cnx.cursor()

# Criar três colunas
f1, f2, f3, f4 = st.columns(4)
m1, m2, m3 = st.columns((1,1,1))
col1, col2 = st.columns(2)

# Definindo a data padrão como 01/01/2022
data_padrao = datetime(2023, 12, 1)

# Criando os filtros
with f1:
    data_inicial = st.date_input("Data Inicial", value=data_padrao)
with f2:
    data_final = st.date_input("Data Final")
#with f3:
#    selecao = st.selectbox("Categoria", ["Receitas", "Despesas"])
with f4:
    st.write("") # Espaço em branco para alinhar os filtros

# Consultando o banco de dados MySQL
query_receita = "SELECT DATE_FORMAT(Data, '%Y-%m') AS mes_ano, SUM(Valor) AS Total FROM receitas WHERE Data BETWEEN %s AND %s GROUP BY mes_ano"
query_despesa = "SELECT DATE_FORMAT(Data, '%Y-%m') AS mes_ano, SUM(Valor) AS Total FROM despesas WHERE Data BETWEEN %s AND %s GROUP BY mes_ano"
investimento_compra_query = """
SELECT DATE_FORMAT(data_compra, '%Y-%m') AS mes_ano, SUM(custo_aquisicao) as Total 
FROM investimentos 
WHERE Status = 'Compra' AND data_compra BETWEEN %s AND %s 
GROUP BY mes_ano
"""
investimento_venda_query = """
SELECT DATE_FORMAT(data_compra, '%Y-%m') AS mes_ano, SUM(custo_aquisicao) as Total 
FROM investimentos 
WHERE Status = 'Venda' AND data_compra BETWEEN %s AND %s 
GROUP BY mes_ano
"""
params = (data_inicial.strftime('%Y-%m-%d'), data_final.strftime('%Y-%m-%d'))

receitas = pd.read_sql_query(query_receita, cnx, params=params)
despesas = pd.read_sql_query(query_despesa, cnx, params=params)
investimentos_compra = pd.read_sql(investimento_compra_query, cnx, params=params)
investimentos_venda = pd.read_sql(investimento_venda_query, cnx, params=params)

# Verifica se os DataFrames não estão vazios antes de tentar acessar os valores
if not receitas.empty and not despesas.empty and not investimentos_compra.empty and not investimentos_venda.empty:
    total_receitas = receitas['Total'].sum()
    total_despesas = despesas['Total'].sum()
    total_investimentos_compra = investimentos_compra['Total'].sum()
    total_investimentos_venda = investimentos_venda['Total'].sum()

    #total_investimentos_liquido = total_investimentos_compra - total_investimentos_venda

    # Layout de colunas
    col1, col2, col3, col4 = st.columns(4)
    
    # Usando st.metric para exibir os valores
    with col1:
        st.metric(label="Total Receitas", value=f"R$ {total_receitas:.2f}")
    with col2:
        st.metric(label="Total Despesas", value=f"R$ {total_despesas:.2f}")
    with col3:
        st.metric(label="Total Investimentos", value=f"R$ {total_investimentos_compra:.2f}")
    with col4:
        saldo = total_receitas - total_despesas - (total_investimentos_compra - total_investimentos_venda)
        st.metric(label="Caixa", value=f"R$ {saldo:.2f}")
else:
    st.error("Não foi possível recuperar os dados.")

# Crie o gráfico de barras
fig = go.Figure()
fig.add_trace(go.Bar(x=receitas["mes_ano"], y=receitas["Total"], name="Receitas", marker_color='green'))
fig.add_trace(go.Bar(x=despesas["mes_ano"], y=despesas["Total"], name="Despesas", marker_color='red'))
fig.add_trace(go.Bar(x=investimentos_compra["mes_ano"], y=investimentos_compra["Total"], name="Investimento", marker_color='orange'))

# Personalize o layout do gráfico
fig.update_layout(barmode="group", title={
        'text': "Receitas e Despesas por mês",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})

# Exiba o gráfico no Streamlit
st.plotly_chart(fig)

#################################################################

# Filtrar despesas por centro de custo
query_receita_cat = "SELECT Categoria, SUM(Valor) as total FROM receitas WHERE Data BETWEEN %s AND %s GROUP BY Categoria"
query_despesa_cat= "SELECT Categoria, SUM(Valor) as total FROM despesas WHERE Data BETWEEN %s AND %s GROUP BY Categoria"
params = (data_inicial.strftime('%Y-%m-%d'), data_final.strftime('%Y-%m-%d'))
df3 = pd.read_sql_query(query_receita_cat, cnx, params=params)
df4 = pd.read_sql_query(query_despesa_cat, cnx, params=params)

# Definir lista de cores para as despesas e receitas
cores_despesas = ['red', 'orangered', 'darkred', 'indianred']
cores_receitas = ['green', 'limegreen', 'darkgreen', 'forestgreen']

# Cria os gráficos de pizza para despesas e receitas
fig1 = px.pie(df3, values='total', names='Categoria', color_discrete_sequence=cores_receitas)
fig2 = px.pie(df4, values='total', names='Categoria', color_discrete_sequence=cores_despesas)

# Define o layout dos subplots
fig = sp.make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
fig.add_trace(fig1.data[0], 1, 1)
fig.add_trace(fig2.data[0], 1, 2)

# Atualiza as configurações de layout
fig.update_layout(title_text='Categorias', title_x=0.5)

# Define as configurações do gráfico de pizza
fig.update_traces(hole=0.5, hoverinfo="label+percent+name", textinfo="label+value")

# Exibe o gráfico
st.plotly_chart(fig)