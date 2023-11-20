import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
import hashlib
from streamlit_option_menu import option_menu

st.set_page_config(layout="wide")

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

def update_receita(id_receita, valor, data, fonte, categoria, descricao, metodo_pagamento, frequencia, banco_corretora):
    conn = create_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
            UPDATE receitas
            SET Valor = %s, Data = %s, Fonte = %s, Categoria = %s, Descricao = %s, Metodo_Pagamento = %s, Frequencia = %s, Banco_Corretora = %s
            WHERE ID_Receita = %s
            """
            cursor.execute(query, (valor, data, fonte, categoria, descricao, metodo_pagamento, frequencia, banco_corretora, id_receita))
            conn.commit()
            cursor.close()
            st.success("Receita atualizada com sucesso!")
        except Error as e:
            st.error(f"Erro ao atualizar a receita: {e}")
        finally:
            conn.close()

def delete_receita(id_receita):
    conn = create_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "DELETE FROM receitas WHERE ID_Receita = %s"
            cursor.execute(query, (id_receita,))
            conn.commit()
            cursor.close()
            st.success("Receita excluída com sucesso!")
        except Error as e:
            st.error(f"Erro ao excluir a receita: {e}")
        finally:
            conn.close()

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
        st.dataframe(receitas_df)
    else:
        st.error("Usuário não está logado. Por favor, faça o login para acessar esta página.")

if __name__ == "__main__":
    app()





#BackUP tela Login

import streamlit as st
import mysql.connector
from mysql.connector import Error
import hashlib
import receitas as Receita
import despesas as Despesas
import investimentos as Investimentos
import dashboard as Dashboard
from streamlit_option_menu import option_menu

st.set_page_config(layout="wide")

# Configuração do banco de dados
db_config = {
    'host': '172.17.0.2',
    'port': '3306',
    'user': 'root',
    'password': 'airflow',
    'database': 'financial'
}

# Função de conexão ao banco de dados
def create_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        st.error(f"Erro ao conectar ao banco de dados MySQL: {e}")
        return None
# Funções de autenticação: check_login, create_user...
def login_user(username, password):
    conn = create_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            query = "SELECT ID FROM users WHERE Usuario = %s AND Senha = %s"
            cursor.execute(query, (username, hashed_password))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            if result:
                st.session_state['logged_in'] = True
                st.session_state['user_id'] = result[0]  # ID do usuário
                return True
            else:
                return False
        except Error as e:
            st.error(f"Erro ao verificar as credenciais: {e}")
            return False


def create_user(username, email, password):
    conn = create_db_connection()
    if conn:
        try:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            cursor = conn.cursor()
            query = "INSERT INTO users (Usuario, Email, Senha) VALUES (%s, %s, %s)"
            cursor.execute(query, (username, email, hashed_password))
            conn.commit()
            cursor.close()
            conn.close()
            st.success("Usuário cadastrado com sucesso!")
        except Error as e:
            st.error(f"Erro ao inserir o usuário no banco de dados: {e}")

# Funções das páginas: receitas_app, despesas_app, investimentos_app...

# Inicializa a sessão se ainda não estiver inicializada
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['username'] = ''

def main():
    st.title("Sistema de Acesso")


    # Função de logout
    def logout():
        st.session_state['logged_in'] = False
        st.session_state['username'] = ''

    # Se estiver logado, mostrar o botão de logout e mensagem de boas-vindas
    if st.session_state['logged_in']:
        st.sidebar.button("Logout", on_click=logout)
        st.sidebar.write(f"Bem-vindo {st.session_state['username']}!")

    # Se não estiver logado, mostre as opções de Login ou Cadastro
    if not st.session_state['logged_in']:
        menu = ["Login", "Cadastro"]
        choice = st.sidebar.selectbox("Menu", menu)

        if choice == "Login":
            username = st.sidebar.text_input("Usuário")
            password = st.sidebar.text_input("Senha", type='password')

            if st.sidebar.button("Login"):
                if login_user(username, password):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.success("Login bem-sucedido!")
                else:
                    st.error("Usuário ou senha incorretos.")

        elif choice == "Cadastro":
            with st.form(key='user_form'):
                username = st.text_input("Usuário")
                email = st.text_input("Email")
                password = st.text_input("Senha", type='password')
                submit_button = st.form_submit_button(label='Cadastrar')

                if submit_button:
                    create_user(username, email, password)

    # Se estiver logado, mostre a navegação para as outras páginas
    if st.session_state['logged_in']:
        with st.sidebar:
            selected = option_menu(
            menu_title=None,
            options=["Dashboard","Receitas", "Despesas", "Investimentos"])
        #choice = st.selectbox("Navegar", menu)

        # As funções de página devem ser definidas em módulos separados e importadas aqui
        if selected == "Dashboard":
            Dashboard.app()
        if selected == "Receitas":
            Receita.app()  # Esta função deve ser definida em receitas.py
        elif selected == "Despesas":
            Despesas.app()  # Esta função deve ser definida em despesas.py
        elif selected == "Investimentos":
            Investimentos.app()  # Esta função deve ser definida em investimentos.py

if __name__ == "__main__":
    main()

