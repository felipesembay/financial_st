import mysql.connector
import pandas as pd
import plotly.graph_objs as go
import plotly.offline as pyo
import streamlit as st
import plotly.express as px
from streamlit_option_menu import option_menu
from plotly.subplots import make_subplots


# Conecte-se ao banco de dados MySQL
cnx = mysql.connector.connect(user='root', password='airflow',
                              host='172.17.0.2', database='financial')
cursor = cnx.cursor()
###########################################################################################
# Criar três colunas
f1, f2, f3, f4 = st.columns(4)
m1, m2, m3 = st.columns((1,1,1))

# Criar as queris dos filtros-----------------------------------------------------
query_data_receita = """
SELECT MONTH(Data) as mes
FROM receitas 
GROUP BY MONTH(Data)
"""
# Execute a consulta SQL para as receitas
cursor.execute(query_data_receita)
resultados_receitas = cursor.fetchall()
#-----------------------------------------------------------------------------------#
query_data_despesa = """
SELECT MONTH(Data) as mes
FROM despesas 
GROUP BY MONTH(Data)
"""
# Execute a consulta SQL para as receitas
cursor.execute(query_data_despesa)
resultados_receitas = cursor.fetchall()
#-------------------------------------------------------------------------------------#
# Primeira coluna com filtro de data inicial
with f1:
    st.write("Data Inicial")
    data_inicial = st.date_input("", value=None, key="data_inicial", help=None)

# Segunda coluna com filtro de data final
with f2:
    st.write("Data Final")
    data_final = st.date_input("", value=None, key="data_final", help=None)


# Terceira coluna com os outros filtros

##################################################################
#m1.write('')
#m2.metric(label ='Total Poupança',value = int(to['Value']), delta = str(int(to['Previous']))+' Compared to 1 hour ago', delta_color = 'inverse')
#m3.metric(label ='Current Handover Average',value = str(int(ch['Value']))+" Mins", delta = str(int(ch['Previous']))+' Compared to 1 hour ago', delta_color = 'inverse')
#m1.write('')

#################################################################################################
# Construa a consulta SQL para as receitas
query_receitas = """
SELECT MONTH(Data) as mes, SUM(Valor) as receita
FROM receitas 
GROUP BY MONTH(Data)
"""

# Execute a consulta SQL para as receitas
cursor.execute(query_receitas)
resultados_receitas = cursor.fetchall()

# Construa a consulta SQL para as despesas
query_despesas = """
SELECT MONTH(Data) as mes, SUM(Valor) as despesa 
FROM despesas
GROUP BY MONTH(Data)
"""
# Execute a consulta SQL para as despesas
cursor.execute(query_despesas)
resultados_despesas = cursor.fetchall()

# Combine os resultados das receitas e despesas em um único DataFrame
df = pd.DataFrame(resultados_receitas, columns=["mes", "receita"])
df["despesa"] = pd.DataFrame(resultados_despesas, columns=["mes", "despesa"])["despesa"]

# Crie o gráfico de barras
fig = go.Figure()
fig.add_trace(go.Bar(x=df["mes"], y=df["receita"], name="Receitas", marker_color='green'))
fig.add_trace(go.Bar(x=df["mes"], y=df["despesa"], name="Despesas", marker_color='red'))

# Personalize o layout do gráfico
fig.update_layout(barmode="group", title="Receitas e Despesas por Mês")

# Exiba o gráfico no Streamlit
st.plotly_chart(fig)
#############################################################################################
# Criar duas colunas
col1, col2 = st.columns(2)

# Filtrar receitas por centro de receitas
query = """SELECT Categoria, SUM(Valor) as total FROM receitas GROUP BY Categoria"""
cursor.execute(query)
receitas_data = cursor.fetchall()

# Filtrar despesas por centro de custo
query = """SELECT Categoria, SUM(Valor) as total FROM despesas GROUP BY Categoria"""
cursor.execute(query)
despesas_data = cursor.fetchall()

# Filtrar valores nulos das receitas
receitas_data_filtered = [(d[0], float(d[1])) for d in receitas_data if d[0] is not None and d[1] is not None]

# Filtrar valores nulos das despesas
despesas_data_filtered = [(d[0], float(d[1])) for d in despesas_data if d[0] is not None and d[1] is not None]

# Definir lista de cores para as receitas
cores_receitas = ['green', 'limegreen', 'darkgreen', 'forestgreen']

# Criar gráfico de pizza para as receitas
fig_receitas = px.pie(values=[d[1] for d in receitas_data_filtered], names=[d[0] for d in receitas_data_filtered], 
                      color_discrete_sequence=cores_receitas,
                      width=350, height=350, hole=0.5)

# Definir lista de cores para as despesas
cores_despesas = ['red', 'orangered', 'darkred', 'indianred']

# Criar gráfico de pizza para as despesas
fig_despesas = px.pie(values=[d[1] for d in despesas_data_filtered], names=[d[0] for d in despesas_data_filtered], 
                      color_discrete_sequence=cores_despesas, 
                      width=370, height=370, hole=0.5)

# Criar uma figura contendo os dois gráficos
specs = [[{'type': 'pie'}, {'type': 'pie'}]]
fig = make_subplots(rows=1, cols=2, specs=specs)
fig.add_trace(fig_receitas.data[0], row=1, col=1)
fig.add_trace(fig_despesas.data[0], row=1, col=2)

# Adicionar um título à figura
fig.update_layout(
    title={
        'text': "Categorias",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'}
)
# Mostrar a figura na coluna
col1.plotly_chart(fig)

#############################################################################################
# Criar duas colunas
col1, col2 = st.columns(2)

# Filtrar receitas por centro de receitas
query = """SELECT Cliente, SUM(Valor) as Total FROM receitas GROUP BY Cliente"""
cursor.execute(query)
receitas_data = cursor.fetchall()

# Filtrar despesas por centro de custo
query = """SELECT Fornecedor, SUM(Valor) as Total FROM despesas GROUP BY Fornecedor"""
cursor.execute(query)
despesas_data = cursor.fetchall()

# Filtrar valores nulos das receitas
receitas_data_filtered = [(d[0], float(d[1])) for d in receitas_data if d[0] is not None and d[1] is not None]

# Filtrar valores nulos das despesas
despesas_data_filtered = [(d[0], float(d[1])) for d in despesas_data if d[0] is not None and d[1] is not None]

# Definir lista de cores para as receitas
cores_receitas = ['green', 'limegreen', 'darkgreen', 'forestgreen']

# Criar gráfico de pizza para as receitas
fig_receitas = px.pie(values=[d[1] for d in receitas_data_filtered], names=[d[0] for d in receitas_data_filtered], 
                      color_discrete_sequence=cores_receitas,
                      width=350, height=350, hole=0.5)

# Definir lista de cores para as despesas
cores_despesas = ['red', 'orangered', 'darkred', 'indianred']

# Criar gráfico de pizza para as despesas
fig_despesas = px.pie(values=[d[1] for d in despesas_data_filtered], names=[d[0] for d in despesas_data_filtered], 
                      color_discrete_sequence=cores_despesas, 
                      width=370, height=370, hole=0.5)

# Criar uma figura contendo os dois gráficos
specs = [[{'type': 'pie'}, {'type': 'pie'}]]
fig = make_subplots(rows=1, cols=2, specs=specs)
fig.add_trace(fig_receitas.data[0], row=1, col=1)
fig.add_trace(fig_despesas.data[0], row=1, col=2)

# Adicionar um título à figura
fig.update_layout(
    title={
        'text': "Cliente e Fornecedores",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'}
)
# Mostrar a figura na coluna
col1.plotly_chart(fig)

####################################################################################
# Criar duas colunas
col1, col2 = st.columns(2)

# Filtrar receitas por centro de receitas
query = """SELECT Categoria, SUM(Valor) as Total FROM receitas GROUP BY Categoria"""
cursor.execute(query)
receitas_data = cursor.fetchall()

# Filtrar despesas por centro de custo
query = """SELECT Categoria, SUM(Valor) as Total FROM despesas GROUP BY Categoria"""
cursor.execute(query)
despesas_data = cursor.fetchall()

# Filtrar valores nulos das receitas
receitas_data_filtered = [(d[0], float(d[1])) for d in receitas_data if d[0] is not None and d[1] is not None]

# Filtrar valores nulos das despesas
despesas_data_filtered = [(d[0], float(d[1])) for d in despesas_data if d[0] is not None and d[1] is not None]

# Definir lista de cores para as receitas
cores_receitas = ['green', 'limegreen', 'darkgreen', 'forestgreen']

# Criar gráfico de pizza para as receitas
fig_receitas = px.pie(values=[d[1] for d in receitas_data_filtered], names=[d[0] for d in receitas_data_filtered], 
                      color_discrete_sequence=cores_receitas,
                      width=350, height=350, hole=0.5)

# Definir lista de cores para as despesas
cores_despesas = ['red', 'orangered', 'darkred', 'indianred']

# Criar gráfico de pizza para as despesas
fig_despesas = px.pie(values=[d[1] for d in despesas_data_filtered], names=[d[0] for d in despesas_data_filtered], 
                      color_discrete_sequence=cores_despesas, 
                      width=370, height=370, hole=0.5)

# Criar uma figura contendo os dois gráficos
specs = [[{'type': 'pie'}, {'type': 'pie'}]]
fig = make_subplots(rows=1, cols=2, specs=specs)
fig.add_trace(fig_receitas.data[0], row=1, col=1)
fig.add_trace(fig_despesas.data[0], row=1, col=2)

# Adicionar um título à figura
fig.update_layout(
    title={
        'text': "Tipo de Receita/ Despesa",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'}
)
# Mostrar a figura na coluna
col1.plotly_chart(fig)

