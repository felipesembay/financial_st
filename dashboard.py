import streamlit as st
from receitas import app as app_receitas
from despesas import app as app_despesas
from investimentos import app as app_investimentos


PAGES = {
    "Receitas": app_receitas,
    "Despesas": app_despesas,
    "Investimentos": app_investimentos
}

def main():
    st.sidebar.title('Navegação')
    selection = st.sidebar.radio("Ir para", list(PAGES.keys()))

    page = PAGES[selection]
    page.app()

if __name__ == "__main__":
    main()
