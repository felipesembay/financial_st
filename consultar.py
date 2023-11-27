import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import timedelta
import time

def consultar_titulos():
    st.title('Consultar Títulos')
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        symbol = st.text_input("Digite o símbolo da ação (exemplo: VALE3):")
    with col2:
        start_date = st.date_input("Data de início:")
    with col3:
        end_date = st.date_input("Data de fim:")
    with col4:
        periodo = st.selectbox("Periodicidade", options=["1m", "2m", "5m", "15m", "30m", "60m","90m","1h", "1d","1wk", "1mo", "3mo"])

    col5, col6 = st.columns(2)
    with col5:
        update_interval = st.slider("Intervalo de atualização (segundos)", min_value=5, max_value=60, value=10, step=5)
    with col6:
        auto_update = st.toggle('Atualização')

    def load_data():
        try:
            end_date_adj = end_date + timedelta(days=1)
            stock_data = yf.download(symbol, start=start_date, end=end_date_adj, interval=periodo)
            end_date_adj -= timedelta(days=1)
            return stock_data
        except Exception as e:
            st.error(f"Erro ao obter dados da ação: {e}")
            return pd.DataFrame()

    def plot_data(stock_data):
        if not stock_data.empty:
            fig = go.Figure(data=[go.Candlestick(x=stock_data.index,
                                                open=stock_data['Open'],
                                                high=stock_data['High'],
                                                low=stock_data['Low'],
                                                close=stock_data['Close'])])
            fig.update_layout(title=f"Gráfico de Candlestick para {symbol}",
                              xaxis_title='Data',
                              yaxis_title='Preço',
                              xaxis_rangeslider_visible=True,
                              width=1200,
                              height=1000)
            st.plotly_chart(fig)
        else:
            st.warning("Dados não disponíveis para o símbolo e período especificados.")
    
    if st.button("Consultar"):
        stock_data = load_data()
        plot_data(stock_data)

    while auto_update:
        time.sleep(update_interval)
        stock_data = load_data()
        plot_data(stock_data)
        #st.rerun()

if __name__ == "__main__":
    consultar_titulos()
