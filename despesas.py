import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
import hashlib
from streamlit_option_menu import option_menu
from dateutil.relativedelta import relativedelta

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

# Função para inserir uma nova despesa
def insert_despesa(id_user, valor, data, fornecedor, categoria, descricao, metodo_pagamento, bandeira_cartao, frequencia, banco_corretora, status):
    conn = create_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
            INSERT INTO despesas (ID_Users, Valor, Data, Fornecedor, Categoria, Descricao, Metodo_Pagamento, Bandeira_cartao, Frequencia, Banco_Corretora, Status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (id_user, valor, data, fornecedor, categoria, descricao, metodo_pagamento, bandeira_cartao, frequencia, banco_corretora, status))
            conn.commit()
            cursor.close()
            conn.close()
        except Error as e:
            st.error(f"Erro ao inserir a despesa: {e}")

# Função para atualizar uma despesa existente
def update_despesa(id_despesa, valor, data, fornecedor, categoria, descricao, metodo_pagamento, bandeira_cartao, frequencia, banco_corretora, status):
    conn = create_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
            UPDATE despesas
            SET Valor = %s, Data = %s, Fornecedor = %s, Categoria = %s, Descricao = %s, Metodo_Pagamento = %s, Bandeira_cartao = %s, Frequencia = %s, Banco_Corretora = %s, Status = %s
            WHERE ID_Despesa = %s
            """
            cursor.execute(query, (valor, data, fornecedor, categoria, descricao, metodo_pagamento, bandeira_cartao, frequencia, banco_corretora, status,id_despesa))
            conn.commit()
            st.success("Despesa atualizada com sucesso!")
        except Error as e:
            st.error(f"Erro ao atualizar a despesa: {e}")
        finally:
            conn.close()

# Função para excluir uma despesa
def delete_despesa(id_despesa):
    conn = create_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "DELETE FROM despesas WHERE ID_Despesa = %s"
            cursor.execute(query, (id_despesa,))
            conn.commit()
            cursor.close()
            st.success("Despesa excluída com sucesso!")
        except Error as e:
            st.error(f"Erro ao excluir a despesa: {e}")
        finally:
            conn.close()

# Função para buscar despesas do banco de dados
def get_despesas(user_id):
    conn = create_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM despesas WHERE ID_Users = %s", (user_id,))
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            return pd.DataFrame(result, columns=["ID_Despesa", "ID_Users", "Valor", "Data", "Fornecedor", "Categoria", "Descricao", "Metodo_Pagamento", "Bandeira_cartao", "Frequencia", "Banco_Corretora", "Status"])
        except Error as e:
            st.error(f"Erro ao obter despesas: {e}")
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
                    INSERT INTO despesas (ID_Users, Valor, Data, Fornecedor, Categoria, Descricao, Metodo_Pagamento, Bandeira_cartão ,Frequencia, Banco_Corretora, Status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (id_user, row['Valor'], row['Data'], row['Fonte'], row['Categoria'], row['Descricao'], row['Metodo_Pagamento'], row['Bandeira_cartão'],row['Frequencia'], row['Banco_Corretora'], row['Status']))
            conn.commit()
            st.success("Despesas importadas com sucesso!")
    except Exception as e:
        st.error(f"Erro ao importar despesas: {e}")
    finally:
        if conn:
            conn.close()

def get_fornecedor_despesas():
    return ['Sanepar', 'Sabesp', 'Energisa', 'Copel', 'Renner', 'Marisa', 'Carrefour']

def get_categoria_despesas():
    return ['Alimentação', 'Aluguel', 'Cuidados Pessoais', 'Educação', 'Empréstimo', 'Financiamento',
'Impostos', 'Investimento', 'Lazer e Entretenimento', 'Saúde', 'Seguro','Transporte', 'Utilidades','Vestuário']

def get_bancos():
    return ['Banco do Brasil', 'Bradesco', 'Banco Inter','BTG Pactual','Caixa Econômica Federal', 'C6 Bank', 'Easy Invest',
            'Itaú Unibanco', 'ModalMais','Neon','Nubank','Original', 'Santander Brasil', 
            'Clear','Genial Investimentos','XP Investimentos', 'Rico Investimentos'
            ]

def app():
    st.title('Gestão de Despesas')
    selected = option_menu(
        menu_title=None,
        options=["Adicionar", "Editar", "Excluir"],
        orientation="horizontal",
    )

    if 'user_id' in st.session_state:
        user_id = st.session_state['user_id']
        if selected == "Adicionar":
            metodo_lancamento = st.radio("Prefere lançar manualmente ou utilizar CSV?", ["Manual", "CSV"], horizontal=True)
            if metodo_lancamento == "Manual":
                id_user = st.session_state['user_id']
                valor = st.number_input("Valor da Despesa", min_value=0.0, format="%.2f")
                data = st.date_input("Data da Despesa")
                
                # Obter fontes de receitas e adicionar a opção para nova fonte
                fornecedor_despesas = get_fornecedor_despesas()
                fornecedor_opcao = st.selectbox("Fornecedor", fornecedor_despesas + ['Adicionar nova...'])
                if fornecedor_opcao == 'Adicionar nova...':
                    novo_fornecedor = st.text_input("Digite a novo fornecedor")
                    if novo_fornecedor:  # Se o usuário digitou uma nova fonte, usamos essa
                        fornecedor_despesas = novo_fornecedor
                else:
                    fornecedor_despesas = fornecedor_opcao # Caso contrário, usamos a opção selecionada

                categoria_despesas = get_categoria_despesas()
                categoria_opcao = st.selectbox("Categoria da Despesas", categoria_despesas + ['Adicionar nova categoria de Despesa'])
                if categoria_opcao == 'Adicionar nova categoria de Despesa':
                    nova_categoria = st.text_input("Digite a nova categoria de despesas")
                    if nova_categoria:
                        categoria = nova_categoria
                else:
                    categoria = categoria_opcao

                descricao = st.text_area("Descrição da Despesa")
                metodo_pagamento = st.selectbox("Método de Recebimento", ['Transferência Bancária', 'Cheque', 'Dinheiro', 'Online', 'Pix', 'Criptomoeda', 'Cartão de Crédito', 'Cartão de Débito'])
                bandeira_cartao = None
                if metodo_pagamento in ['Cartão de Crédito', 'Cartão de Débito']:
                    bandeira_cartao = st.selectbox('Bandeira do Cartão', ['Visa', 'MasterCard'])
                frequencia = st.selectbox("Frequência", ['Única', 'Recorrente'])
                meses_recorrentes = 0
                if frequencia == "Recorrente":
                    meses_recorrentes = st.number_input("Por quantos meses deseja lançar essa receita recorrente?", min_value=1, max_value=12, step=1)
                
                banco_corretoras_lancamento = get_bancos()
                banco_opcao = st.selectbox("Banco", banco_corretoras_lancamento + ['Adicionar novo banco ou corretora'])
                if banco_opcao == 'Adicionar novo banco ou corretora':
                    novo_banco_corretora = st.text_input("Digite o Banco ou Corretora")
                    if novo_banco_corretora:
                        banco_corretora = novo_banco_corretora
                else:
                    banco_corretora = banco_opcao

                status = st.selectbox("Status", ['Realizado', 'Previsão'])

                if st.button("Adicionar Despesa"):
                    # Aqui você adicionaria a lógica para salvar a nova fonte no banco de dados, se necessário
                    insert_despesa(id_user, valor, data, fornecedor_despesas, categoria, descricao, metodo_pagamento, bandeira_cartao,frequencia, banco_corretora, status)
                    if frequencia == 'Recorrente' and meses_recorrentes > 0:
                        for mes in range(1, meses_recorrentes + 1):
                            data_recorrente = data + relativedelta(months=mes)
                            insert_despesa(id_user, valor, data_recorrente, fornecedor_despesas, categoria, descricao, metodo_pagamento, bandeira_cartao,'Recorrente', banco_corretora, status)
                    st.success(f"Despesas(s) adicionada(s) com sucesso!")
                pass
            elif metodo_lancamento == "CSV":
                id_user = st.session_state['user_id']
                uploaded_file = st.file_uploader("Faça o upload do seu arquivo CSV", type="csv")
                if uploaded_file is not None:
                    importar_csv(id_user, uploaded_file)

        elif selected == "Editar":
            despesas_df = get_despesas(user_id)
            st.dataframe(despesas_df)
            st.subheader("Editar Receita")
            despesas_id_to_edit = st.selectbox("Selecione a despesa para editar", despesas_df['ID_Despesa'].tolist())
            despesas_to_edit = despesas_df[despesas_df['ID_Despesa'] == despesas_id_to_edit].iloc[0] if not despesas_df.empty else None

            if despesas_to_edit is not None:
                valor = st.number_input("Valor da Despesa", value=float(despesas_to_edit['Valor']))
                data = st.date_input("Data da Despesa", value=despesas_to_edit['Data'])

                fornecedor_despesas = get_fornecedor_despesas()
                fornecedor_opcao = st.selectbox("Fornecedor", fornecedor_despesas + ['Adicionar nova...'])
                if fornecedor_opcao == 'Adicionar nova...':
                    novo_fornecedor = st.text_input("Digite a novo fornecedor")
                    if novo_fornecedor:  # Se o usuário digitou uma nova fonte, usamos essa
                        fornecedor_despesas = novo_fornecedor
                else:
                    fornecedor_despesas = fornecedor_opcao # Caso contrário, usamos a opção selecionada

                categoria_despesas = get_categoria_despesas()
                categoria_opcao = st.selectbox("Categoria da Receita", categoria_despesas + ['Adicionar nova categoria de Receita'], index=categoria_despesas.index(despesas_to_edit['Categoria']) if despesas_to_edit['Categoria'] in categoria_despesas else len(categoria_despesas))
                if categoria_opcao == 'Adicionar nova categoria de Receita':
                    nova_categoria = st.text_input("Digite a nova categoria de receita")
                    categoria = nova_categoria if nova_categoria else despesas_to_edit['Categoria']
                else:
                    categoria = categoria_opcao

                descricao = st.text_area("Descrição da Despesa", value=despesas_to_edit['Descricao'])
                metodo_pagamento = st.selectbox("Método de Pagamento", ['Transferência Bancária', 'Cheque', 'Dinheiro', 'Online', 'Pix', 'Criptomoeda', 'Cartão de Crédito', 'Cartão de Débito'], index=['Transferência Bancária', 'Cheque', 'Dinheiro', 'Online', 'Pix', 'Criptomoeda', 'Cartão de Crédito', 'Cartão de Débito'].index(despesas_to_edit['Metodo_Pagamento']))
                bandeira_cartao = despesas_to_edit['Bandeira_cartao'] if 'Bandeira_cartao' in despesas_to_edit else None
                if metodo_pagamento in ['Cartão de Crédito', 'Cartão de Débito']:
                    bandeira_cartao = st.selectbox('Bandeira do Cartão', ['Visa', 'MasterCard'], index=['Visa', 'MasterCard'].index(bandeira_cartao) if bandeira_cartao in ['Visa', 'MasterCard'] else 0)
                frequencia = st.selectbox("Frequência", ['Única', 'Recorrente'], index=['Única', 'Recorrente'].index(despesas_to_edit['Frequencia']))

                banco_corretoras_lancamento = get_bancos()
                banco_opcao = st.selectbox("Banco/Corretora Vinculada", banco_corretoras_lancamento + ['Adicionar novo banco ou corretora'], index=banco_corretoras_lancamento.index(despesas_to_edit['Banco_Corretora']) if despesas_to_edit['Banco_Corretora'] in banco_corretoras_lancamento else len(banco_corretoras_lancamento))
                if banco_opcao == 'Adicionar novo banco ou corretora':
                    novo_banco_corretora = st.text_input("Digite o Banco ou Corretora")
                    banco_corretora = novo_banco_corretora if novo_banco_corretora else despesas_to_edit['Banco_Corretora']
                else:
                    banco_corretora = banco_opcao
                status = st.selectbox("Status", ['Realizado', 'Previsão'])

            if st.button("Salvar Alterações"):
                update_despesa(despesas_id_to_edit, valor, data, fornecedor_despesas, categoria, descricao, metodo_pagamento, bandeira_cartao,frequencia, banco_corretora, status)
                st.success(f"Receita atualizada com sucesso!")

        elif selected == "Excluir":
            st.subheader("Excluir Lançamento")
            # Certifique-se de que receitas_df está disponível
            despesas_df = get_despesas(user_id)
            st.dataframe(despesas_df)
            despesa_id_to_delete = st.selectbox("Selecione a ID da despesa para excluir:", despesas_df['ID_Despesa'].tolist())
            if st.button("Excluir Lançamento"):
                delete_despesa(despesa_id_to_delete)

    else:
        st.error("Usuário não está logado. Por favor, faça o login para acessar esta página.")

if __name__ == "__main__":
    app()
