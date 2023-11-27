import streamlit as st
import mysql.connector
from mysql.connector import Error
import yfinance as yf
from streamlit_option_menu import option_menu
import pandas as pd
import consultar as Consulta

# Configuração do banco de dados
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

def insert_investment(id_user, symbol, purchase_date, quantity, purchase_price, acquisition_cost, broker, portfolio, objective, status):
    conn = create_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
            INSERT INTO investimentos (ID_Users, Simbolo_Acao, Data_Compra, Quantidade, Preco_Compra, Custo_Aquisicao, Corretora, Carteira, Objetivo, Status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (id_user, symbol, purchase_date, quantity, purchase_price, acquisition_cost, broker, portfolio, objective, status))
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
            return pd.DataFrame(result, columns=["ID", "ID_Users", "simbolo_acao", "data_compra", "quantidade", "preco_compra", "custo_aquisicao", "corretora", "carteira", "objetivo", "data_criacao", "data_atualizacao", "status"])
        except Error as e:
            st.error(f"Erro ao obter os investimentos: {e}")
            return pd.DataFrame()  # Retornar um DataFrame vazio em caso de erro

def delete_investimentos(id):
    conn = create_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "DELETE FROM investimentos WHERE ID = %s"
            cursor.execute(query, (id,))
            conn.commit()
            cursor.close()
            st.success("Investimento excluído com sucesso!")
        except Error as e:
            st.error(f"Erro ao excluir: {e}")
        finally:
            conn.close()

def app():
    st.title('Gestão de Investimentos')

    selected = option_menu(
        menu_title=None,
        options=["Carteira de Ações", "Consultar título", "Simulador e BackTesting"],
        orientation="horizontal",
    )
    if selected == "Carteira de Ações":
        selected_option = st.radio("Selecione uma opção:", ["Exibir Lançamentos", "Adicionar Lançamentos", "Excluir Lançamentos"], key='radio_option', horizontal=True)

        if selected_option == "Exibir Lançamentos":
            investments = get_investments()
            if investments.empty:
                st.warning("Nenhum investimento encontrado na carteira.")
            else:
                st.subheader("Carteira de Ações:")
                st.dataframe(investments)

        elif selected_option == "Adicionar Lançamentos":
            if 'user_id' in st.session_state:
                id_user = st.session_state['user_id']

                # Divide a tela em 4 colunas e 2 linhas
                col1, col2, col3, col4 = st.columns(4)
                col5, col6, col7, col8 = st.columns(4)

                # Coluna 1
                with col1:
                    symbol = st.text_input("Símbolo da Ação (exemplo: VALE3.SA):")
                with col2:
                    purchase_date = st.date_input("Data da Compra:")
                with col3:
                    quantity = st.number_input("Quantidade de Ações:", min_value=1)
                with col4:
                    purchase_price = st.number_input("Preço da Compra por Ação:", min_value=0.0, format="%.2f")

                # Coluna 2
                with col5:
                    broker = st.text_input("Corretora:")
                with col6:
                    portfolio = st.text_input("Carteira:")
                with col7:
                    status = st.selectbox("Status", options=["Compra", "Venda"])
                with col8:
                    acquisition_cost = quantity * purchase_price

                objective = st.text_area("Objetivo do Investimento:")


                # Verifique se os dados da ação estão disponíveis
                try:
                    stock_data = yf.download(symbol, start=purchase_date)
                    if not stock_data.empty and len(stock_data) > 0:
                        min_price = stock_data['Low'][0]
                        max_price = stock_data['High'][0]

                        if min_price <= purchase_price <= max_price:
                            st.success(f"O preço de compra de {purchase_price} está dentro do intervalo entre {min_price} e {max_price}.")
                            if st.button("Adicionar Investimento"):
                                insert_investment(id_user, symbol, purchase_date, quantity, purchase_price, acquisition_cost, broker, portfolio, objective, status)
                        else:
                            st.error(f"O preço de compra de {purchase_price} está fora do intervalo entre {min_price} e {max_price}.")
                    else:
                        st.error(f"Dados da ação não disponíveis para a data de compra especificada.")
                except Exception as e:
                    st.error(f"Erro ao obter dados da ação: {e}")
        
        elif selected_option == "Excluir Lançamentos":
            # Certifique-se de que receitas_df está disponível
            investimentos_df = get_investments()
            st.dataframe(investimentos_df)
            investimento_id_to_delete = st.selectbox("Selecione a ID da receita para excluir:", investimentos_df['ID'].tolist())
            if st.button("Excluir Lançamento"):
                delete_investimentos(investimento_id_to_delete)

    if selected == "Consultar título":
        Consulta.consultar_titulos()



if __name__ == "__main__":
    app()
