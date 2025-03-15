import yfinance as yf
import pandas as pd
import os
import streamlit as st

"""
# Stocks evaluator
hi user, write a stock name
"""

#Dizionario exchange to index
exchange_to_index = {
    "NasdaqGS": "^GSPC",  # Nasdaq Global Select → S&P 500
    "NasdaqGM": "^GSPC",  # Nasdaq Global Market → S&P 500
    "NYSE": "^GSPC",      # New York Stock Exchange → S&P 500
    "AMEX": "^GSPC",      # American Stock Exchange → S&P 500
    "NMS": "^GSPC",       # Nasdaq NMS → S&P 500 (aggiunto!)
    "Milan": "FTSEMIB.MI",  # Borsa Italiana → FTSE MIB
    "Paris": "^FCHI",     # Euronext Paris → CAC 40
    "XETRA": "^GDAXI",    # Borsa tedesca (Deutsche Börse) → DAX
    "Tokyo": "^N225"      # Borsa di Tokyo → Nikkei 225
}

if 'stock_data_loaded' not in st.session_state:
    st.session_state.stock_data_loaded = False
if 'exchange' not in st.session_state:
    st.session_state.exchange = "Unknown"
if 'market_index' not in st.session_state:
    st.session_state.market_index = "N/A"
if 'stock_data' not in st.session_state:
    st.session_state.stock_data = None
if 'beta' not in st.session_state:
    st.session_state.beta = "N/A"
if 'ticker' not in st.session_state:
    st.session_state.ticker = ""
 
 #Valore predefinito: Apple, upper per eviare case sensitivity   
ticker = st.text_input("Inserisci il ticker della stock:", "AAPL").upper()

#variabile utilizzata nelle formule
stock = yf.Ticker(ticker)

## Funzione per ottenere l'indice di riferimento per una determinata azienda
def get_market_index(ticker):
    stock_info = stock.info
    exchange = stock_info.get("exchange", "Unknown")
    market_index = exchange_to_index.get(exchange, "N/A")
    return exchange, market_index

#leave displayed first button results
def display_stock_data():
    if st.session_state.stock_data_loaded:
        st.write(f"Lo stock {st.session_state.ticker} è quotato su {st.session_state.exchange} e il suo indice di riferimento è {st.session_state.market_index}")
        st.write(f"📊 Prezzi storici di **{st.session_state.ticker}**:", st.session_state.stock_data)
        st.write("Il Beta dell'azienda è:", st.session_state.beta)

# Initialize exchange and market_index variables outside the button handlers
exchange = "Unknown"
market_index = "N/A"


#Scarica i dati se è stato inserito un ticker  
if st.button("Scarica dati stock"):
    if ticker: # Scarica i dati dell'ultimo mese
        data = stock.history(period="1mo")
        # Ottieni l'exchange e l'indice di mercato per lo stock
        exchange, market_index = get_market_index(ticker)

        st.session_state.exchange = exchange
        st.session_state.market_index = market_index
        st.session_state.stock_data = data

        if data.empty:
            st.error("⚠️ Nessun dato trovato. Controlla il ticker.")
        else:
            st.write((f"Lo stock {ticker} è quotato su {exchange} e il suo indice di riferimento è {market_index}"))
            st.write(f"📊 Prezzi storici di **{ticker}**:",data)  #f-string fa leggere e sostituire i valori con le variabili
            stock_info = stock.info
            beta = stock_info.get("beta", "N/A")
            st.session_state.beta = beta
            st.write("Il Beta dell'azienda è:", beta)

             # Display stock data
            display_stock_data()

              # Set flag that stock data has been loaded
            st.session_state.stock_data_loaded = True

# Always display stock data if it has been loaded
elif st.session_state.stock_data_loaded:
    display_stock_data()

# Show the second button only if stock data has been loaded
if st.session_state.stock_data_loaded:
    if st.button("Scarica dati dell'indice di riferimento"):
        market_index = st.session_state.market_index

        if market_index != "N/A":
            index_data = yf.Ticker(market_index).history(period="1mo") # Dati per l'ultimo mese
            if not index_data.empty:
                st.write(f"📊 Dati storici per l'indice {market_index}:")
                st.write(index_data)
            else:
                st.error("⚠️ Nessun dato trovato per l'indice.")
        else:
            st.error("⚠️ Nessun indice di riferimento disponibile.")
else:
    st.info("⚠️ Scarica prima i dati dello stock per poter visualizzare l'indice di riferimento.")
