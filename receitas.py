import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
import hashlib

db_config = {
    'host': '172.17.0.2',
    'port': '3306',
    'user': 'root',
    'password': 'airflow',
    'database': 'financial'
}

def create_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        st.error(f"Erro ao conectar ao banco de dados MySQL: {e}")
        return None

# Suponha que esta função conecte ao banco de dados e insira a receita
def insert_receita(id_user, valor, data, fonte, categoria, descricao, metodo_pagamento, frequencia, banco_corretora):
    conn = create_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
            INSERT INTO receitas (ID_Users, Valor, Data, Fonte, Categoria, Descricao, Metodo_Pagamento, Frequencia, Banco_Corretora)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (id_user, valor, data, fonte, categoria, descricao, metodo_pagamento, frequencia, banco_corretora))
            conn.commit()
            cursor.close()
            conn.close()
            st.success("Receita adicionada com sucesso!")
        except Error as e:
            st.error(f"Erro ao inserir a receita: {e}")

# Suponha que esta função busque as receitas do banco de dados
def get_receitas():
    conn = create_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM receitas")
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            return pd.DataFrame(result, columns=["ID_Receita", "ID_Users", "Valor", "Data", "Fonte", "Categoria", "Descricao", "Metodo_Pagamento", "Frequencia", "Banco_Corretora"])
        except Error as e:
            st.error(f"Erro ao obter receitas: {e}")
            return pd.DataFrame()


def app():
    st.title('Gestão de Receitas')

    # Verifique se o ID do usuário está disponível
    if 'user_id' in st.session_state:
        id_user = st.session_state['user_id']  # ID do usuário logado
        with st.form("Receita Form", clear_on_submit=True):
            valor = st.number_input("Valor da Receita")
            data = st.date_input("Data da Receita")
            fonte = st.text_input("Fonte da Receita")
            categoria = st.text_input("Categoria da Receita")
            descricao = st.text_area("Descrição da Receita")
            metodo_pagamento = st.selectbox("Método de Pagamento", ['Transferência Bancária', 'Cheque', 'Dinheiro', 'Online'])
            frequencia = st.selectbox("Frequência", ['Única', 'Recorrente'])
            banco_corretora = st.text_input("Banco/Corretora Vinculada")
            submit_button = st.form_submit_button("Adicionar Receita")
            if submit_button:
                insert_receita(id_user, valor, data, fonte, categoria, descricao, metodo_pagamento, frequencia, banco_corretora)

        receitas_df = get_receitas()
        st.data_editor(receitas_df)
    else:
        st.error("Usuário não está logado. Por favor, faça o login para acessar esta página.")

if __name__ == "__main__":
    app()
