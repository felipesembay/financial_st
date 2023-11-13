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
            # A ordem dos parâmetros deve corresponder aos campos na instrução SQL, exceto o ID_Receita no final, que é usado na cláusula WHERE.
            cursor.execute(query, (valor, data, fonte, categoria, descricao, metodo_pagamento, frequencia, banco_corretora, id_receita))
            conn.commit()
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
    selected = option_menu(
    menu_title=None,
    options=["Adicionar", "Editar", "Excluir"],
    orientation="horizontal",
        )

    # Verifique se o ID do usuário está disponível
    if 'user_id' in st.session_state:
        if selected == "Adicionar":
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
        elif selected == "Editar":
            receitas_df = get_receitas()
            st.dataframe(receitas_df)
            st.subheader("Editar Receita")
            receita_id_to_edit = st.selectbox("Selecione a receita para editar", receitas_df['ID_Receita'].tolist())
            receita_to_edit = receitas_df[receitas_df['ID_Receita'] == receita_id_to_edit].iloc[0] if not receitas_df.empty else None

            if receita_to_edit is not None:
                with st.form("Edit Form", clear_on_submit=False):
                    valor = st.number_input("Valor da Receita", value=float(receita_to_edit['Valor']))
                    data = st.date_input("Data da Receita", value=receita_to_edit['Data'])
                    fonte = st.text_input("Fonte da Receita", value=receita_to_edit['Fonte'])
                    categoria = st.text_input("Categoria da Receita", value=receita_to_edit['Categoria'])
                    descricao = st.text_area("Descrição da Receita", value=receita_to_edit['Descricao'])
                    metodo_pagamento = st.selectbox("Método de Pagamento", ['Transferência Bancária', 'Cheque', 'Dinheiro', 'Online'], index=['Transferência Bancária', 'Cheque', 'Dinheiro', 'Online'].index(receita_to_edit['Metodo_Pagamento']))
                    frequencia = st.selectbox("Frequência", ['Única', 'Recorrente'], index=['Única', 'Recorrente'].index(receita_to_edit['Frequencia']))
                    banco_corretora = st.text_input("Banco/Corretora Vinculada", value=receita_to_edit['Banco_Corretora'])
                    submit_edicao = st.form_submit_button("Salvar Alterações")
                    if submit_edicao:
                        update_receita(receita_id_to_edit, valor, data, fonte, categoria, descricao, metodo_pagamento, frequencia, banco_corretora)

        elif selected == "Excluir":
            st.subheader("Excluir Receita")
            # Certifique-se de que receitas_df está disponível
            receitas_df = get_receitas()
            st.dataframe(receitas_df)
            receita_id_to_delete = st.selectbox("Selecione a ID da receita para excluir:", receitas_df['ID_Receita'].tolist())
            if st.button("Excluir Receita"):
                delete_receita(receita_id_to_delete)
                st.rerun()  # Atualiza a lista de receitas após a exclusão

    else:
        st.error("Usuário não está logado. Por favor, faça o login para acessar esta página.")

if __name__ == "__main__":
    app()
