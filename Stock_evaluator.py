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


#Scarica i dati se è stato inserito un ticker  
if st.button("Scarica dati stock"):
    if ticker: # Scarica i dati dell'ultimo mese
        data = stock.history(period="1mo")
        # Ottieni l'exchange e l'indice di mercato per lo stock
        exchange, market_index = get_market_index(ticker)
        if data.empty:
            st.error("⚠️ Nessun dato trovato. Controlla il ticker.")
        else:
            st.write((f"Lo stock {ticker} è quotato su {exchange} e il suo indice di riferimento è {market_index}"))
            st.write(f"📊 Prezzi storici di **{ticker}**:",data)  #f-string fa leggere e sostituire i valori con le variabili
            stock_info = stock.info
            beta = stock_info.get("beta", "N/A")
            st.write("Il Beta dell'azienda è:", beta)

if st.button("Scarica dati dell'indice di riferimento"):
    if market_index != "N/A":
        index_data = yf.Ticker(market_index).history(period="2mo")  # Dati per gli ultimi 2 mesi
    if not index_data.empty:
        st.write(f"📊 Dati storici per l'indice {market_index}:")
        st.write(index_data)
    else:
        st.error("⚠️ Nessun dato trovato per l'indice.")
else:
    st.error("⚠️ Nessun indice di riferimento disponibile.")
