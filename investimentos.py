import streamlit as st
import mysql.connector
from mysql.connector import Error
import yfinance as yf

#st.set_page_config(layout="wide")

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

def insert_investment(id_user, symbol, purchase_date, quantity, purchase_price, acquisition_cost, broker, portfolio, objective):
    conn = create_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
            INSERT INTO investimentos (ID_Users, Simbolo_Acao, Data_Compra, Quantidade, Preco_Compra, Custo_Aquisicao, Corretora, Carteira, Objetivo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (id_user, symbol, purchase_date, quantity, purchase_price, acquisition_cost, broker, portfolio, objective))
            conn.commit()
            cursor.close()
            conn.close()
            st.success("Investimento adicionado com sucesso!")
        except Error as e:
            st.error(f"Erro ao inserir o investimento: {e}")

def get_investments():
    conn = create_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM investimentos")
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            return result
        except Error as e:
            st.error(f"Erro ao obter os investimentos: {e}")
            return []

def app():
    st.title('Gestão de Investimentos')

    selected = st.selectbox("Selecione uma opção:", ["Adicionar Investimento", "Ver Investimentos"])

    if selected == "Adicionar Investimento":
        if 'user_id' in st.session_state:
            id_user = st.session_state['user_id']
            symbol = st.text_input("Símbolo da Ação (exemplo: VALE3.SA):")
            purchase_date = st.date_input("Data da Compra:")
            quantity = st.number_input("Quantidade de Ações:", min_value=0)
            purchase_price = st.number_input("Preço da Compra por Ação:", min_value=0.0, format="%.2f")
            acquisition_cost = quantity * purchase_price
            broker = st.text_input("Corretora:")
            portfolio = st.text_input("Carteira:")
            objective = st.text_area("Objetivo do Investimento:")

            if st.button("Adicionar Investimento"):
                insert_investment(id_user, symbol, purchase_date, quantity, purchase_price, acquisition_cost, broker, portfolio, objective)

        else:
            st.error("Você precisa estar logado para adicionar investimentos.")

    elif selected == "Ver Investimentos":
        investments = get_investments()
        if not investments:
            st.warning("Nenhum investimento encontrado.")
        else:
            st.subheader("Investimentos:")
            st.write(investments)

if __name__ == "__main__":
    app()
