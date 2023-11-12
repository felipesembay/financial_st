import streamlit as st
from streamlit_authenticator import Authenticate

# Configuração inicial
authenticator = Authenticate(
    'users_db', # Nome do arquivo db (será criado como users_db.json)
    'users', # Prefixo da tabela
    'username', # Campo de usuário
    'password', # Campo de senha
    'cookie_name', # Nome do cookie
    'signature_key', # Chave de assinatura para os cookies
    'use_cookie', # Se deve usar cookie para armazenar a sessão
)

# Criação do usuário (execute apenas uma vez para criar o administrador ou os primeiros usuários)
if st.checkbox("Criar conta de administrador"):
    username = st.text_input("Nome de usuário")
    password = st.text_input("Senha", type='password')
    hashed_password = authenticator.hasher(password).decode()
    if st.button('Cadastrar'):
        authenticator.create_user(username, hashed_password)
        st.success("Usuário administrador criado com sucesso.")

# Função de login
def login_form():
    username = st.text_input('Nome de usuário')
    password = st.text_input('Senha', type='password')
    return username, password

# Página de login
username, password = login_form()
hashed_password = authenticator.hasher(password).decode()

if authenticator.login(username, hashed_password):
    st.write('Bem-vindo ao sistema, ', username)
    # Aqui você coloca a navegação para outras páginas ou funções do seu aplicativo
else:
    st.warning('Nome de usuário/senha incorretos.')

# Logout
if authenticator.logout('Sair'):
    st.write('Você saiu da conta.')
