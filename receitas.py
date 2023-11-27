import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
import hashlib
from streamlit_option_menu import option_menu
from dateutil.relativedelta import relativedelta

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

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
def insert_receita(id_user, valor, data, fonte, categoria, descricao, metodo_pagamento, frequencia, banco_corretora, status):
    conn = create_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
            INSERT INTO receitas (ID_Users, Valor, Data, Fonte, Categoria, Descricao, Metodo_Pagamento, Frequencia, Banco_Corretora, Status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (id_user, valor, data, fonte, categoria, descricao, metodo_pagamento, frequencia, banco_corretora, status))
            conn.commit()
            cursor.close()
            conn.close()
            st.success("Receita adicionada com sucesso!")
        except Error as e:
            st.error(f"Erro ao inserir a receita: {e}")

def update_receita(id_receita, valor, data, fonte, categoria, descricao, metodo_pagamento, frequencia, banco_corretora, status):
    conn = create_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
            UPDATE receitas
            SET Valor = %s, Data = %s, Fonte = %s, Categoria = %s, Descricao = %s, Metodo_Pagamento = %s, Frequencia = %s, Banco_Corretora = %s, Status = %s
            WHERE ID_Receita = %s
            """
            # A ordem dos parâmetros deve corresponder aos campos na instrução SQL, exceto o ID_Receita no final, que é usado na cláusula WHERE.
            cursor.execute(query, (valor, data, fonte, categoria, descricao, metodo_pagamento, frequencia, banco_corretora, status, id_receita))
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
            return pd.DataFrame(result, columns=["ID_Receita", "ID_Users", "Valor", "Data", "Fonte", "Categoria", "Descricao", "Metodo_Pagamento", "Frequencia", "Banco_Corretora", "Status"])
        except Error as e:
            st.error(f"Erro ao obter receitas: {e}")
            return pd.DataFrame()

def importar_csv(id_user, file):
    try:
        # Lê o arquivo CSV
        data = pd.read_csv(file)
        conn = create_db_connection()
        if conn:
            cursor = conn.cursor()
            for _, row in data.iterrows():
                cursor.execute("""
                    INSERT INTO receitas (ID_Users, Valor, Data, Fonte, Categoria, Descricao, Metodo_Pagamento, Frequencia, Banco_Corretora, Status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (id_user, row['Valor'], row['Data'], row['Fonte'], row['Categoria'], row['Descricao'], row['Metodo_Pagamento'], row['Frequencia'], row['Banco_Corretora'], row['Status']))
            conn.commit()
            st.success("Receitas importadas com sucesso!")
    except Exception as e:
        st.error(f"Erro ao importar receitas: {e}")
    finally:
        if conn:
            conn.close()

def get_fontes_receitas():
    # Aqui você faria a consulta ao banco de dados para obter as fontes de receitas
    # Para o exemplo, vamos usar uma lista estática
    return ['Salário', 'Venda de Produtos', 'Serviços', 'Rendimentos de Investimentos', 'Aluguel', 'Dividendos', 'Royalties',
            'Doações', 'Subsídios Governamentais', 'Reembolsos de Despesas', 'Antecipação de Lucros',
            'Ganhos de Capital', 'Pensão', 'Licenciamento', 'Divisão de Lucros', 'Resgate de Seguro']

def get_categoria_receitas():
    return ['Renda Fixa', 'Renda Variável', 'Renda de Trabalho', 'Negócios e Empreendedorismo', 'Renda Passiva',
            'Prêmios', 'Reembolsos', 'Dividendos', 'Crowdfunding']
def get_bancos():
    return ['Banco do Brasil', 'Bradesco', 'Banco Inter','BTG Pactual','Caixa Econômica Federal', 'C6 Bank', 'Easy Invest',
            'Itaú Unibanco', 'ModalMais','Neon','Nubank','Original', 'Santander Brasil', 
            'Clear','Genial Investimentos','XP Investimentos', 'Rico Investimentos'
            ]

def app():
    st.title('Gestão de Receitas')
    selected = option_menu(
        menu_title=None,
        options=["Adicionar", "Editar", "Excluir"],
        orientation="horizontal",
    )

    if 'user_id' in st.session_state:
        if selected == "Adicionar":
            metodo_lancamento = st.radio("Prefere lançar manualmente ou utilizar CSV?", ["Manual", "CSV"], horizontal=True)
            if metodo_lancamento == "Manual":
                id_user = st.session_state['user_id']
                valor = st.number_input("Valor da Receita", min_value=0.0, format="%.2f")
                data = st.date_input("Data da Receita")
                
                # Obter fontes de receitas e adicionar a opção para nova fonte
                fontes_receitas = get_fontes_receitas()
                fonte_opcao = st.selectbox("Fonte da Receita", fontes_receitas + ['Adicionar nova...'])
                if fonte_opcao == 'Adicionar nova...':
                    nova_fonte = st.text_input("Digite a nova fonte de receita")
                    if nova_fonte:  # Se o usuário digitou uma nova fonte, usamos essa
                        fonte = nova_fonte
                else:
                    fonte = fonte_opcao  # Caso contrário, usamos a opção selecionada

                categoria_receitas = get_categoria_receitas()
                categoria_opcao = st.selectbox("Categoria da Receita", categoria_receitas + ['Adicionar nova categoria de Receita'])
                if categoria_opcao == 'Adicionar nova categoria de Receita':
                    nova_categoria = st.text_input("Digite a nova categoria de receita")
                    if nova_categoria:
                        categoria = nova_categoria
                else:
                    categoria = categoria_opcao

                descricao = st.text_area("Descrição da Receita")
                metodo_pagamento = st.selectbox("Método de Recebimento", ['Transferência Bancária', 'Cheque', 'Dinheiro', 'Online', 'Pix', 'Criptomoeda', 'Cartão de Crédito', 'Cartão de Débito'])
                frequencia = st.selectbox("Frequência", ['Única', 'Recorrente'])
                meses_recorrentes = 0
                if frequencia == "Recorrente":
                    meses_recorrentes = st.number_input("Por quantos meses deseja lançar essa receita recorrente?", min_value=1, max_value=12, step=1)
                
                banco_corretoras_lancamento = get_bancos()
                banco_opcao = st.selectbox("Qual seu banco", banco_corretoras_lancamento + ['Adicionar novo banco ou corretora'])
                if banco_opcao == 'Adicionar novo banco ou corretora':
                    novo_banco_corretora = st.text_input("Digite o Banco ou Corretora")
                    if novo_banco_corretora:
                        banco_corretora = novo_banco_corretora
                else:
                    banco_corretora = banco_opcao
                status = st.selectbox("Status", ['Realizado', 'Previsão'])

                if st.button("Adicionar Receita"):
                    # Aqui você adicionaria a lógica para salvar a nova fonte no banco de dados, se necessário
                    insert_receita(id_user, valor, data, fonte, categoria, descricao, metodo_pagamento, frequencia, banco_corretora, status)
                    if frequencia == 'Recorrente' and meses_recorrentes > 0:
                        for mes in range(1, meses_recorrentes + 1):
                            data_recorrente = data + relativedelta(months=mes)
                            insert_receita(id_user, valor, data_recorrente, fonte, categoria, descricao, metodo_pagamento, 'Recorrente', banco_corretora, status)
                    st.success(f"Receita(s) adicionada(s) com sucesso!")
                pass
            elif metodo_lancamento == "CSV":
                id_user = st.session_state['user_id']
                uploaded_file = st.file_uploader("Faça o upload do seu arquivo CSV", type="csv")
                if uploaded_file is not None:
                    importar_csv(id_user, uploaded_file)

        elif selected == "Editar":
            receitas_df = get_receitas()
            st.dataframe(receitas_df)
            st.subheader("Editar Receita")
            receita_id_to_edit = st.selectbox("Selecione a receita para editar", receitas_df['ID_Receita'].tolist())
            receita_to_edit = receitas_df[receitas_df['ID_Receita'] == receita_id_to_edit].iloc[0] if not receitas_df.empty else None

            if receita_to_edit is not None:
                valor = st.number_input("Valor da Receita", value=float(receita_to_edit['Valor']))
                data = st.date_input("Data da Receita", value=receita_to_edit['Data'])

                fontes_receitas = get_fontes_receitas()
                fonte_opcao = st.selectbox("Fonte da Receita", fontes_receitas + ['Adicionar nova...'], index=fontes_receitas.index(receita_to_edit['Fonte']) if receita_to_edit['Fonte'] in fontes_receitas else len(fontes_receitas))
                if fonte_opcao == 'Adicionar nova...':
                    nova_fonte = st.text_input("Digite a nova fonte de receita")
                    fonte = nova_fonte if nova_fonte else receita_to_edit['Fonte']
                else:
                    fonte = fonte_opcao

                categoria_receitas = get_categoria_receitas()
                categoria_opcao = st.selectbox("Categoria da Receita", categoria_receitas + ['Adicionar nova categoria de Receita'], index=categoria_receitas.index(receita_to_edit['Categoria']) if receita_to_edit['Categoria'] in categoria_receitas else len(categoria_receitas))
                if categoria_opcao == 'Adicionar nova categoria de Receita':
                    nova_categoria = st.text_input("Digite a nova categoria de receita")
                    categoria = nova_categoria if nova_categoria else receita_to_edit['Categoria']
                else:
                    categoria = categoria_opcao

                descricao = st.text_area("Descrição da Receita", value=receita_to_edit['Descricao'])
                metodo_pagamento = st.selectbox("Método de Pagamento", ['Transferência Bancária', 'Cheque', 'Dinheiro', 'Online', 'Pix', 'Criptomoeda', 'Cartão de Crédito', 'Cartão de Débito'], index=['Transferência Bancária', 'Cheque', 'Dinheiro', 'Online', 'Pix', 'Criptomoeda', 'Cartão de Crédito', 'Cartão de Débito'].index(receita_to_edit['Metodo_Pagamento']))
                frequencia = st.selectbox("Frequência", ['Única', 'Recorrente'], index=['Única', 'Recorrente'].index(receita_to_edit['Frequencia']))

                banco_corretoras_lancamento = get_bancos()
                banco_opcao = st.selectbox("Banco/Corretora Vinculada", banco_corretoras_lancamento + ['Adicionar novo banco ou corretora'], index=banco_corretoras_lancamento.index(receita_to_edit['Banco_Corretora']) if receita_to_edit['Banco_Corretora'] in banco_corretoras_lancamento else len(banco_corretoras_lancamento))
                if banco_opcao == 'Adicionar novo banco ou corretora':
                    novo_banco_corretora = st.text_input("Digite o Banco ou Corretora")
                    banco_corretora = novo_banco_corretora if novo_banco_corretora else receita_to_edit['Banco_Corretora']
                else:
                    banco_corretora = banco_opcao
                status = st.selectbox("Status", ['Realizado', 'Previsão'])

            if st.button("Salvar Alterações"):
                update_receita(receita_id_to_edit, valor, data, fonte, categoria, descricao, metodo_pagamento, frequencia, banco_corretora, status)
                st.success(f"Receita atualizada com sucesso!")

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