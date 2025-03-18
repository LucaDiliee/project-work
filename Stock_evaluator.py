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
    "MIL": "FTSEMIB.MI",  # Borsa Italiana → FTSE MIB
    "PAR": "^FCHI",     # Euronext Paris → CAC 40
    "XETRA": "^GDAXI",    # Borsa tedesca (Deutsche Börse) → DAX
    "GER": "^GDAXI",    # Borsa tedesca (Deutsche Börse) → DAX
    "Tokyo": "^N225",      # Borsa di Tokyo → Nikkei 225
    "PNK": "^N225"      # Borsa di Tokyo → Nikkei 225
}

if 'stock_data_loaded' not in st.session_state:
    st.session_state.stock_data_loaded = False
if 'index_data_loaded' not in st.session_state:  # Nuova variabile di stato
    st.session_state.index_data_loaded = False
if 'exchange' not in st.session_state:
    st.session_state.exchange = "Unknown"
if 'market_index' not in st.session_state:
    st.session_state.market_index = "N/A"
if 'stock_data' not in st.session_state:
    st.session_state.stock_data = None
if 'index_data' not in st.session_state:  # Nuova variabile per i dati dell'indice
    st.session_state.index_data = None
if 'beta' not in st.session_state:
    st.session_state.beta = "N/A"
if 'ticker' not in st.session_state:
    st.session_state.ticker = ""
 
 #Valore predefinito: Apple, upper per eviare case sensitivity   
ticker = st.text_input("Inserisci il ticker della stock:", "AAPL").upper()

#variabile utilizzata nelle formule
stock = yf.Ticker(ticker)

risk_free_rate = 0.025  

## Funzione per ottenere l'indice di riferimento per una determinata azienda
def get_market_index(ticker):
    stock_info = stock.info
    exchange = stock_info.get("exchange", "Unknown")
    market_index = exchange_to_index.get(exchange, "N/A")
    return exchange, market_index

# Add this function to check if ticker is valid
def is_valid_ticker(ticker_symbol):
    try:
        ticker_obj = yf.Ticker(ticker_symbol)
        info = ticker_obj.info
        # Check if we can get basic info about the stock
        return 'longName' in info or 'shortName' in info
    except:
        return False

#leave displayed first button results
def display_stock_data():
    if st.session_state.stock_data_loaded:
        st.write(f"Lo stock {st.session_state.ticker} è quotato su {st.session_state.exchange} e il suo indice di riferimento è {st.session_state.market_index}")
        st.write(f"📊 Prezzi storici di **{st.session_state.ticker}**:", st.session_state.stock_data)
        st.write("Il Beta dell'azienda è:", st.session_state.beta)

# Nuova funzione per visualizzare i dati dell'indice
def display_index_data():
    if st.session_state.index_data_loaded:
        st.write(f"📊 Dati storici per l'indice {st.session_state.market_index}:")
        st.write(st.session_state.index_data)

# Initialize exchange and market_index variables outside the button handlers
exchange = "Unknown"
market_index = "N/A"
# In the first button click handler, add this line before display_stock_data():
st.session_state.ticker = ticker

# Or better yet, modify the code to avoid the duplicate display:
if st.button("Scarica dati stock"):
    # Add validation check here
    if ticker and is_valid_ticker(ticker):
        data = stock.history(period="1mo")
        # Ottieni l'exchange e l'indice di mercato per lo stock
        exchange, market_index = get_market_index(ticker)

        # Save to session state
        st.session_state.ticker = ticker
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
            
            # Set flag that stock data has been loaded
            st.session_state.stock_data_loaded = True
            # Reset index data loaded flag when new stock is loaded
            st.session_state.index_data_loaded = False
    else:
        # This is what was missing - display error for invalid ticker
        st.error("⚠️ Nessun dato trovato. Controlla il ticker.")
       
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
                # Salva i dati nella session state
                st.session_state.index_data = index_data
                st.session_state.index_data_loaded = True
                
            else:
                st.error("⚠️ Nessun dato trovato per l'indice.")
        else:
            st.error("⚠️ Nessun indice di riferimento disponibile.")
 # Mostra sempre i dati dell'indice se sono stati caricati
if st.session_state.index_data_loaded:
    display_index_data()
    
if st.session_state.stock_data_loaded and st.session_state.index_data_loaded:
    if st.button("Calcola rendimenti giornalieri"):
    
    # Calcola i rendimenti giornalieri percentuali dello stock
        stock_returns = st.session_state.stock_data['Close'].pct_change() * 100
        st.write(f"📈 Rendimenti giornalieri percentuali di **{st.session_state.ticker}**:")
    
    # Crea un DataFrame dal rendimento, mantenendo l'indice temporale
        stock_returns_df = pd.DataFrame(stock_returns)
        stock_returns_df.columns = ['Returns %']
        st.write(stock_returns_df)
        stock_return_mean = stock_returns_df['Returns %'].mean()
        st.write(f"📊the expected return of the **{ticker}** is: **{stock_return_mean:.4f}%**")
        stock_return_std = stock_returns_df['Returns %'].std()
        st.write(f"📊the volatility of the **{ticker}** is: **{stock_return_std:.4f}**")
    
        st.markdown("---")

    # Se anche i dati dell'indice sono stati caricati, calcola i rendimenti dell'indice
        if st.session_state.index_data_loaded:
            index_returns = st.session_state.index_data['Close'].pct_change() * 100
            st.write(f"📈 Rendimenti giornalieri percentuali dell'indice **{st.session_state.market_index}**:")
        
            # Crea un DataFrame dal rendimento, mantenendo l'indice temporale
            index_returns_df = pd.DataFrame(index_returns)
            index_returns_df.columns = ['Returns %']
            st.write(index_returns_df)
            index_return_mean = index_returns_df['Returns %'].mean()
            st.write(f"📊the expected return of the **{st.session_state.market_index}** is: **{index_return_mean:.4f}%**")
            index_return_std = index_returns_df['Returns %'].std()
            st.write(f"📊the volatility of the **{st.session_state.market_index}** is: **{index_return_std:.4f}**")
            
            st.session_state.stock_return_mean = stock_return_mean
            st.session_state.stock_return_std = stock_return_std
            st.session_state.returns_calculated = True 

if 'returns_calculated' in st.session_state and st.session_state.returns_calculated:
    if st.button("Calcola Sharpe Ratio"):
 
