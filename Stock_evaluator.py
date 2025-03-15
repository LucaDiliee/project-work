import yfinance as yf
import pandas as pd
import os
import streamlit as st

"""
# Stocks evaluator
hi user, write a stock name
"""

ticker = st.text_input("Inserisci il ticker della stock:", "AAPL")  
# Valore predefinito: Apple

# Scarica i dati se è stato inserito un ticker 
    
if st.button("Scarica dati"):
    if ticker: # Scarica i dati dell'ultimo mese
        stock = yf.Ticker(ticker)
        data = stock.history(period="1mo")
        if data.empty:
            st.error("⚠️ Nessun dato trovato. Controlla il ticker.")
        else:
            st.write(data)

def calculate_mean_close (data):
    return data["Close"].mean()  # Media della colonna 'Close'
