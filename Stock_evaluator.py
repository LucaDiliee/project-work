import yfinance as yf
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np                   
import statsmodels.api as sm

if 'stock_returns_df' not in st.session_state:
    st.session_state.stock_returns_df = None
if 'index_returns_df' not in st.session_state:
    st.session_state.index_returns_df = None
if 'stock_return_mean' not in st.session_state:
    st.session_state.stock_return_mean = 0
if 'stock_return_std' not in st.session_state:
    st.session_state.stock_return_std = 0
if 'index_return_mean' not in st.session_state:
    st.session_state.index_return_mean = 0
if 'index_return_std' not in st.session_state:
    st.session_state.index_return_std = 0
if 'stock_sharpe_ratio' not in st.session_state:
    st.session_state.stock_sharpe_ratio = 0
if 'index_sharpe_ratio' not in st.session_state:
    st.session_state.index_sharpe_ratio = 0
if 'beta' not in st.session_state: 
    st.session_state.beta = None
if 'alpha' not in st.session_state: 
    st.session_state.alpha = None
if 'expected_return_capm' not in st.session_state: 
    st.session_state.expected_return_capm = None
if 'sharpe_capm' not in st.session_state: 
    st.session_state.sharpe_capm = None

st.set_page_config(page_title="Stocks Evaluator", layout="centered")

"""
# 📈 Stocks Evaluator
Ciao User, digita qui sotto il ticker della stock di cui vuoi analizzare i dati

**DISCLAIMER**: è necessario utilizzare i ticker di Yahoo Finance affinché l'applicazione funzioni
"""

# Dizionario exchange to index
exchange_to_index = {
    "NasdaqGS": "^GSPC", "NasdaqGM": "^GSPC", "NYSE": "^GSPC", "AMEX": "^GSPC", "NMS": "^GSPC",
    "MIL": "FTSEMIB.MI", "PAR": "^FCHI", "XETRA": "^GDAXI", "GER": "^GDAXI",
    "PNK": "^N225", "NSI": "^NSEI", "LSE": "^FTSE", "BSE": "^BSESN",
    "TSX": "^GSPTSE", "KRX": "^KS11", "SHE": "000300.SS", "FRA": "^GDAXI"
}

# Input
ticker = st.text_input("📌 Inserisci il ticker della stock:", "AAPL").upper()
periodo = st.selectbox("📆 Seleziona l'intervallo temporale per i dati:",
                       ("1mo", "3mo", "6mo", "1y", "5y", "ytd", "max"), index=2)

# Risk Free
treasury_10y = yf.Ticker("^TNX")
rf_data = treasury_10y.history(period="1d")
rf_today = rf_data['Close'].iloc[-1] / 100
risk_free_annual = rf_today
daily_risk_free_rate = risk_free_annual/252 

def is_valid_ticker(ticker_symbol):
    try:
        info = yf.Ticker(ticker_symbol).info
        return 'longName' in info or 'shortName' in info
    except:
        return False

def get_market_index(ticker_obj):
    stock_info = ticker_obj.info
    exchange = stock_info.get("exchange", "Unknown")
    market_index = exchange_to_index.get(exchange, "N/A")
    return exchange, market_index

# Bottone 
if st.button("📥 Avvia analisi completa"):
    if ticker and is_valid_ticker(ticker):
        stock = yf.Ticker(ticker)
        stock_data = stock.history(period=periodo)

        # Ottieni exchange e indice
        exchange, market_index = get_market_index(stock)

        st.session_state.ticker = ticker
        st.session_state.exchange = exchange
        st.session_state.market_index = market_index
        st.session_state.stock_data = stock_data

        # Scarica dati indice
        if market_index != "N/A":
            index_data = yf.Ticker(market_index).history(period=periodo)
            if not index_data.empty:
                st.session_state.index_data = index_data

                # Calcolo rendimenti
                stock_returns = stock_data['Close'].pct_change() * 100
                index_returns = index_data['Close'].pct_change() * 100

                stock_returns_df = stock_returns.dropna().to_frame(name='Returns %')
                st.session_state.stock_returns_df = stock_returns_df
                index_returns_df = index_returns.dropna().to_frame(name='Returns %')
                st.session_state.index_returns_df = index_returns_df

                st.session_state.stock_return_mean = stock_returns.mean()
                st.session_state.stock_return_std = stock_returns.std()
                st.session_state.index_return_mean = index_returns.mean()
                st.session_state.index_return_std = index_returns.std()

                # Sharpe Ratio
                sr_stock = (st.session_state.stock_return_mean - daily_risk_free_rate) / st.session_state.stock_return_std
                sr_index = (st.session_state.index_return_mean - daily_risk_free_rate) / st.session_state.index_return_std

                st.session_state.stock_sharpe_ratio = sr_stock
                st.session_state.index_sharpe_ratio = sr_index
                #  β e α via regressione 
                merged = pd.concat([stock_returns, index_returns], axis=1).dropna()
                merged.columns = ['rs', 'rm']        
                X = sm.add_constant(merged['rm'])
                model = sm.OLS(merged['rs'], X).fit()
                beta  = model.params['rm']
                alpha = model.params['const']
                st.session_state.beta  = beta
                st.session_state.alpha = alpha

                # Expected return CAPM (annual)  
                mkt_daily = st.session_state.index_return_mean / 100      
                mkt_ann   = (1 + mkt_daily) ** 252 - 1                    
                exp_capm  = risk_free_annual + beta * (mkt_ann - risk_free_annual)
                st.session_state.expected_return_capm = exp_capm * 100    # in %

                # Sharpe Ratio basato su CAPM  
                vol_daily_dec = st.session_state.stock_return_std / 100
                vol_ann = vol_daily_dec * np.sqrt(252)
                st.session_state.sharpe_capm = (exp_capm - risk_free_annual) / vol_ann

            else:
                st.error("⚠️ Nessun dato trovato per l'indice.")
        else:
            st.error("⚠️ Nessun indice di riferimento disponibile.")
    else:
        st.error("⚠️ Nessun dato trovato. Controlla il ticker.")

# Visualizzazione
if "stock_data" in st.session_state and st.session_state.stock_data is not None:
    st.write(f"✅ **{st.session_state.ticker}** è quotata su **{st.session_state.exchange}**, indice di riferimento: **{st.session_state.market_index}**")
    st.write("📊 Prezzi storici:", st.session_state.stock_data)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(st.session_state.stock_data.index, st.session_state.stock_data['Close'], label=f"{ticker} Closing Price")
    ax.set_title(f"{ticker} - Prezzo di Chiusura")
    ax.set_xlabel("Data")
    ax.set_ylabel("Prezzo")
    ax.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    st.pyplot(fig)

if "index_data" in st.session_state and st.session_state.index_data is not None:
    st.write(f"📊 Dati indice: {st.session_state.market_index}", st.session_state.index_data)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(st.session_state.index_data.index, st.session_state.index_data['Close'], label="Index Closing Price", color='red')
    ax.set_title(f"{st.session_state.market_index} - Prezzo di Chiusura")
    ax.set_xlabel("Data")
    ax.set_ylabel("Prezzo")
    ax.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    st.pyplot(fig)

if "stock_returns_df" in st.session_state:
    st.markdown("## 📈 Rendimenti e Volatilità")
    st.write("### Stock Returns", st.session_state.stock_returns_df)
    st.write(f"📊 Expected daily return: **{st.session_state.stock_return_mean:.4f}%**")
    st.write(f"📊 Daily Volatility: **{st.session_state.stock_return_std:.4f}%**")
    st.write(f"📊 Expected annual return: **{st.session_state.stock_return_mean*252:.4f}%**")
    st.write(f"📊 Annual Volatility: **{st.session_state.stock_return_std*np.sqrt(252):.4f}%**")
    st.markdown("---")

    st.write("### Index Returns", st.session_state.index_returns_df)
    st.write(f"📊 Expected daily return: **{st.session_state.index_return_mean:.4f}%**")
    st.write(f"📊 Daily Volatility: **{st.session_state.index_return_std:.4f}%**")
    st.write(f"📊 Expected annual return: **{st.session_state.index_return_mean*252:.4f}%**")
    st.write(f"📊 Annual Volatility: **{st.session_state.index_return_std*np.sqrt(252):.4f}%**")

if "stock_sharpe_ratio" in st.session_state:
    st.markdown("## 📌 Daily Sharpe Ratio")
    st.write(f"📈 **{ticker}**: **{st.session_state.stock_sharpe_ratio:.4f}**")
    st.write(f"📈 **{st.session_state.market_index}**: **{st.session_state.index_sharpe_ratio:.4f}**")
    st.markdown("## 📌 Annual Sharpe Ratio")
    st.write(f"📈 **{ticker}**: **{st.session_state.stock_sharpe_ratio*np.sqrt(252):.4f}**")
    st.write(f"📈 **{st.session_state.market_index}**: **{st.session_state.index_sharpe_ratio*np.sqrt(252):.4f}**")

if st.session_state.beta is not None:
    st.markdown("## 🧩 CAPM")
    st.write(f"α (alpha): **{st.session_state.alpha:.5f}**")
    st.write(f"β (beta): **{st.session_state.beta:.3f}**")
    st.write(f"Expected return (ann.): **{st.session_state.expected_return_capm:.2f}%**")
    st.write(f"Sharpe Ratio (ann.): **{st.session_state.sharpe_capm:.2f}**")
