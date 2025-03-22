import yfinance as yf
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# N.B. il codice scarica dati da Yahoo finance, per questo non funziona su terminali esterni (CoLab, Streamlit Playground), è necessario runnare il codice su terminali interni (Codespace GitHub)

"""
# Stocks evaluator
Ciao User, digita qui sotto il ticker della stock di cui vuoi analizzare i dati

**DISCLAIMER**: è necessario utilizzare i ticker di Yahoo Finance purchè l'applicazione funzioni
"""

# Dizionario exchange to index
exchange_to_index = {
    "NasdaqGS": "^GSPC",  # Nasdaq Global Select → S&P 500
    "NasdaqGM": "^GSPC",  # Nasdaq Global Market → S&P 500
    "NYSE": "^GSPC",      # New York Stock Exchange → S&P 500
    "AMEX": "^GSPC",      # American Stock Exchange → S&P 500
    "NMS": "^GSPC",       # Nasdaq NMS → S&P 500
    "MIL": "FTSEMIB.MI",  # Borsa Italiana → FTSE MIB
    "PAR": "^FCHI",       # Euronext Paris → CAC 40
    "XETRA": "^GDAXI",    # Borsa tedesca (Deutsche Börse) → DAX
    "GER": "^GDAXI",      # Borsa tedesca (Deutsche Börse) → DAX
    "PNK": "^N225",       # Borsa di Tokyo → Nikkei 225
    "NSI": "^NSEI",       # Bosa dell'India → NIFTY 50
    "LSE": "^FTSE",       # Londra → FTSE 100
    "BSE": "^BSESN",       # Bombay Stock Exchange → SENSEX
    "TSX": "^GSPTSE",     # Borsa canadese (Toronto) → S&P/TSX Composite
    "ASX": "^AXJO",       # Borsa australiana → S&P/ASX 200
    "SAO": "^BVSP",       # Borsa brasiliana (B3) → Bovespa Index
    "KRX": "^KS11",       # Borsa coreana → KOSPI Index
    "SHE": "000300.SS",   # Borsa cinese Shenzhen → CSI 300
    "SHH": "000300.SS"    # Borsa cinese Shanghai → CSI 300
}

# Session state variables inizializzate
if 'stock_data_loaded' not in st.session_state:
    st.session_state.stock_data_loaded = False
if 'index_data_loaded' not in st.session_state:
    st.session_state.index_data_loaded = False
if 'exchange' not in st.session_state:
    st.session_state.exchange = "Unknown"
if 'market_index' not in st.session_state:
    st.session_state.market_index = "N/A"
if 'stock_data' not in st.session_state:
    st.session_state.stock_data = None
if 'index_data' not in st.session_state:
    st.session_state.index_data = None
if 'ticker' not in st.session_state:
    st.session_state.ticker = ""
if 'returns_calculated' not in st.session_state:
    st.session_state.returns_calculated = False
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
if 'sharpe_ratio_calculated' not in st.session_state:
    st.session_state.sharpe_ratio_calculated = False
if 'stock_sharpe_ratio' not in st.session_state:
    st.session_state.stock_sharpe_ratio = 0
if 'index_sharpe_ratio' not in st.session_state:
    st.session_state.index_sharpe_ratio = 0
 
# Valore predefinito: Apple, upper per eviare case sensitivity   
ticker = st.text_input("Inserisci il ticker della stock:", "AAPL").upper()

# Variabile utilizzata nelle formule
stock = yf.Ticker(ticker)

risk_free_rate = 0.025 
daily_risk_free_rate = 0.00009921 

# Funzione per ottenere l'indice di riferimento per una determinata azienda, get funzione di python, da dizionario cerca (argomento, default)
def get_market_index(ticker):
    stock_info = stock.info
    exchange = stock_info.get("exchange", "Unknown")
    market_index = exchange_to_index.get(exchange, "N/A")
    return exchange, market_index

# Controllo se il ticker è valido, try è necessario se mettessi if python darebbe errore
def is_valid_ticker(ticker_symbol):
    try:
        ticker_obj = yf.Ticker(ticker_symbol)
        info = ticker_obj.info
        # Semplice check qualsiasi, cerca nel dizionario info due informazioni 
        return 'longName' in info or 'shortName' in info
    except:
        return False

if st.button("Scarica dati stock"):
    # Check per la validità, truthy and falsy
    if ticker and is_valid_ticker(ticker):
        data = stock.history(period="1mo")
        # Ottieni l'exchange e l'indice di mercato per lo stock
        exchange, market_index = get_market_index(ticker)

        # Salva in session state
        st.session_state.ticker = ticker
        st.session_state.exchange = exchange
        st.session_state.market_index = market_index
        st.session_state.stock_data = data
            
        # Flagga che i dati sono stati salvati
        st.session_state.stock_data_loaded = True
        # Resetta tutti gli altri in caso venga lanciato uno stock diverso dal precedente
        st.session_state.index_data_loaded = False
        st.session_state.returns_calculated = False
        st.session_state.sharpe_ratio_calculated = False
    else:
        st.error("⚠️ Nessun dato trovato. Controlla il ticker.")       

# Se stock data loaded in session state allora i dati rimangono sempre displayed
if st.session_state.stock_data_loaded:
    st.write(f"Lo stock **{st.session_state.ticker}** è quotato su **{st.session_state.exchange}** e il suo indice di riferimento è **{st.session_state.market_index}**")
    st.write(f"📊 Prezzi storici di **{st.session_state.ticker}**:", st.session_state.stock_data)
    st.write("📊 Grafico delle chiusure dello stock:")

    # Creazione del grafico per la stock
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(st.session_state.stock_data.index, st.session_state.stock_data['Close'], label=f"{st.session_state.ticker} Closing Price", color='blue')
    ax.set_xlabel("Date")
    ax.set_ylabel("Closing Price")
    ax.set_title(f"{st.session_state.ticker} - Prezzo di Chiusura")
    ax.legend()
    ax.grid(False)
    # Formatta asse X per mostrare solo i mesi (Jan, Feb, ...)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))

    # Mostra il grafico 
    st.pyplot(fig)

    # Mostra bottone solo se sono stati scaricati i dati dello stock
    if st.button("Scarica dati dell'indice di riferimento"):
        market_index = st.session_state.market_index

        if market_index != "N/A":
            index_data = yf.Ticker(market_index).history(period="1mo")
            if not index_data.empty:
                # Salva i dati nella session state
                st.session_state.index_data = index_data
                st.session_state.index_data_loaded = True
            else:
                st.error("⚠️ Nessun dato trovato per l'indice.")
        else:
            st.error("⚠️ Nessun indice di riferimento disponibile.")

    # Mostra sempre i dati se index data loaded
    if st.session_state.index_data_loaded:
        st.write(f"📊 Dati storici per l'indice {st.session_state.market_index}:")
        st.write(st.session_state.index_data)
        st.write("📊 Grafico della chiusura dell'indice di riferimento")

    # Creazione del grafico per l'indice
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(st.session_state.index_data.index, st.session_state.index_data['Close'], label=f"{st.session_state.market_index} Closing Price", color='red')
        ax.set_xlabel("Date")
        ax.set_ylabel("Closing Price")
        ax.set_title(f"{st.session_state.market_index} - Prezzo di Chiusura")
        ax.legend()
        ax.grid(False)
        # Formatta asse X per mostrare solo i mesi (Jan, Feb, ...)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))

    # Mostra il grafico in Streamlit
        st.pyplot(fig)
        
        # Mostra terzo bottone se i dati dell'indice sono stati caricati
        if st.button("Calcola rendimenti giornalieri"):
            # Calcola i rendimenti giornalieri percentuali dello stock
            stock_returns = st.session_state.stock_data['Close'].pct_change() * 100   
            stock_returns_df = pd.DataFrame(stock_returns)
            stock_returns_df.columns = ['Returns %']
            stock_return_mean = stock_returns_df['Returns %'].mean()
            stock_return_std = stock_returns_df['Returns %'].std()
            
            # Calcola i rendimenti dell'indice
            index_returns = st.session_state.index_data['Close'].pct_change() * 100
            index_returns_df = pd.DataFrame(index_returns)
            index_returns_df.columns = ['Returns %']
            index_return_mean = index_returns_df['Returns %'].mean()
            index_return_std = index_returns_df['Returns %'].std()
            
            # Salva in session state, flag returns_calculated
            st.session_state.stock_returns_df = stock_returns_df
            st.session_state.index_returns_df = index_returns_df
            st.session_state.stock_return_mean = stock_return_mean
            st.session_state.stock_return_std = stock_return_std
            st.session_state.index_return_mean = index_return_mean
            st.session_state.index_return_std = index_return_std
            st.session_state.returns_calculated = True

        # Mostra sempre i ritorni giornalieri se calcolati
        if st.session_state.returns_calculated:
            st.write(st.session_state.stock_returns_df)
            st.write(f"📊 the expected return of the **{st.session_state.ticker}** is: **{st.session_state.stock_return_mean:.4f}%**")
            st.write(f"📊 the volatility of the **{st.session_state.ticker}** is: **{st.session_state.stock_return_std:.4f}**")
            st.markdown("---")
            st.write(st.session_state.index_returns_df)
            st.write(f"📊 the expected return of the **{st.session_state.market_index}** is: **{st.session_state.index_return_mean:.4f}%**")
            st.write(f"📊 the volatility of the **{st.session_state.market_index}** is: **{st.session_state.index_return_std:.4f}**")
            
            # Mostra solo se i ritorni giornalieri sono stati calcolati
            if st.button("Calcola Sharpe Ratio"):
                # Utilizziamo i valori salvati in session_state
                stock_return_mean = st.session_state.stock_return_mean
                stock_return_std = st.session_state.stock_return_std
                index_return_mean = st.session_state.index_return_mean
                index_return_std = st.session_state.index_return_std
                
                # Calcolo dello Sharpe Ratio
                stock_risk_premium = (stock_return_mean - daily_risk_free_rate)
                stock_sharpe_ratio = stock_risk_premium / stock_return_std
                index_risk_premium = (index_return_mean - daily_risk_free_rate)
                index_sharpe_ratio = index_risk_premium / index_return_std
                
                # Salva i risultati in session state, Flag sharpe_ratio_calculated
                st.session_state.stock_sharpe_ratio = stock_sharpe_ratio
                st.session_state.index_sharpe_ratio = index_sharpe_ratio
                st.session_state.sharpe_ratio_calculated = True
            
            # Mostra sempre lo Sharpe se calcolato
            if st.session_state.sharpe_ratio_calculated:
                st.write(f'📈 Lo Sharpe Ratio di **{st.session_state.ticker}** è: **{st.session_state.stock_sharpe_ratio:.4f}**')
                st.write(f'📈 Lo Sharpe Ratio di **{st.session_state.market_index}** è: **{st.session_state.index_sharpe_ratio:.4f}**')
 

