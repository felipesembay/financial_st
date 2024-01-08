import streamlit as st
import graficos as grafico


selected_option = st.radio("Selecione uma opção:", ["Dashboard Finanças Pessoais", "Dashboard Macroeconômico"], key='radio_option', horizontal=True)
if selected_option == "Dashboard Finanças Pessoais":
    grafico.grafico()


