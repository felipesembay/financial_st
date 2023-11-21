import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import timedelta

def consultar_titulos():
    st.title('Consultar Títulos')
    col1, col2, col3 = st.columns(3)
    with col1:
        symbol = st.text_input("Digite o símbolo da ação (exemplo: VALE3.SA):")
    with col2:
        start_date = st.date_input("Data de início:")
    with col3:
        end_date = st.date_input("Data de fim:")

    if st.button("Consultar"):
        try:
            end_date += timedelta(days=1)
            stock_data = yf.download(symbol, start=start_date, end=end_date)
            end_date -= timedelta(days=1)

            if not stock_data.empty:
                fig = go.Figure(data=[go.Candlestick(x=stock_data.index,
                                                    open=stock_data['Open'],
                                                    high=stock_data['High'],
                                                    low=stock_data['Low'],
                                                    close=stock_data['Close'])])

                # Aumente o tamanho da figura ajustando a largura e a altura
                fig.update_layout(title=f"Gráfico de Candlestick para {symbol}",
                                  xaxis_title='Data',
                                  yaxis_title='Preço',
                                  xaxis_rangeslider_visible=True,
                                  width=1200,  # Defina a largura desejada
                                  height=1000)  # Defina a altura desejada

                st.plotly_chart(fig)
            else:
                st.warning("Dados não disponíveis para o símbolo e período especificados.")
        except Exception as e:
            st.error(f"Erro ao obter dados da ação: {e}")

if __name__ == "__main__":
    consultar_titulos()
