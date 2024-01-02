import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Configuração de conexão com o banco de dados
db_config = {
    'host': '172.17.0.2',
    'port': '3306',
    'user': 'root',
    'password': 'airflow',
    'database': 'financial'
}

# String de conexão
connection_string = f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

# Criar engine de conexão
engine = create_engine(connection_string)

# Execute uma consulta SQL
receita_query = "SELECT SUM(Valor) as Total FROM receitas"
despesa_query = "SELECT SUM(Valor) as Total FROM despesas"
investimento_compra_query = "SELECT SUM(custo_aquisicao) as Total FROM investimentos WHERE Status = 'Compra'"
investimento_venda_query = "SELECT SUM(custo_aquisicao) as Total FROM investimentos WHERE Status = 'Venda'"

receitas = pd.read_sql(receita_query, engine)
despesas = pd.read_sql(despesa_query, engine)
investimentos_compra = pd.read_sql(investimento_compra_query, engine)
investimentos_venda = pd.read_sql(investimento_venda_query, engine)

# Verifica se os DataFrames não estão vazios antes de tentar acessar os valores
if not receitas.empty and not despesas.empty and not investimentos_compra.empty and not investimentos_venda.empty:
    total_receitas = receitas['Total'].iloc[0] if receitas['Total'].iloc[0] else 0
    total_despesas = despesas['Total'].iloc[0] if despesas['Total'].iloc[0] else 0
    total_investimentos_compra = investimentos_compra['Total'].iloc[0] if investimentos_compra['Total'].iloc[0] else 0
    total_investimentos_venda = investimentos_venda['Total'].iloc[0] if investimentos_venda['Total'].iloc[0] else 0

    total_investimentos_liquido = total_investimentos_compra - total_investimentos_venda

    # Layout de colunas
    col1, col2, col3, col4 = st.columns(4)
    
    # Usando st.metric para exibir os valores
    with col1:
        st.metric(label="Total Receitas", value=f"R$ {total_receitas:.2f}")
    with col2:
        st.metric(label="Total Despesas", value=f"R$ {total_despesas:.2f}")
    with col3:
        st.metric(label="Total Investimentos", value=f"R$ {total_investimentos_liquido:.2f}")
    with col4:
        saldo = total_receitas - total_despesas - total_investimentos_liquido
        st.metric(label="Caixa", value=f"R$ {saldo:.2f}")
else:
    st.error("Não foi possível recuperar os dados.")
