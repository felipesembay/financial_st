import streamlit as st
import mysql.connector
from mysql.connector import Error
import hashlib
import receitas as Receita
import despesas as Despesas
import investimentos as Investimentos
import dashboard as Dashboard
from streamlit_option_menu import option_menu

#st.set_page_config(layout="wide")

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
                    st.success("Seja Bem-Vindo")
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
            options=["Receitas", "Despesas", "Investimentos", "Dasboard"])
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
