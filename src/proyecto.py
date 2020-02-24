import pandas as pd
import requests
from fbprophet import Prophet
from matplotlib import pyplot as pl

m = Prophet()

def call(url):
	''' 
	funcion que llama a la api de cryptocompare

	'''
	response = requests.get(url)
	read = response.json()
	return read

def crypto_definer(url):
	''' Extrae los valores de la crypto y los pega en un dataframe '''
	moneda = call(url)
	high = []
	low = []
	Open=[]
	close = []
	unx_time= []
	for i in moneda['Data']['Data']:
		unx_time.append(i['time'])
		high.append(i['high'])
		low.append(i['low'])
		Open.append(i['open'])
		close.append(i['close'])
	df = pd.DataFrame()
	df['UNIX_TIME'] = unx_time
	df['Open'] = Open
	df['High'] = high
	df['Low'] = low
	df['Close'] = close
	return df

def convert(url):
	df = crypto_definer(url)
	df['UNIX_TIME'] = df['UNIX_TIME'].astype(int)
	df['UNIX_TIME'] = pd.to_datetime(df['UNIX_TIME'], unit='s')

	return df

def df_y(url, columna='High'):
	""" Convierte las columnas de time y precio X a un formato predeterminado
	 que pide facebook prophet, la fecha como DS y la columna a predecir como y """
	df = convert(url)
	new_df = df.rename(columns = {'UNIX_TIME': 'ds', columna : 'y'})
	new_df = new_df[['ds', 'y']]
	return new_df

def fit_proph(url,columna='High'):
	""" Inicializa facebook prophet y crea el dataframe a x periodos en el futuro """
	global m
	df = df_y(url,columna)
	m.fit(df)
	future = m.make_future_dataframe(periods=10)
	forecast = m.predict(future)
	return forecast[['ds', 'yhat', 'yhat_lower','yhat_upper']]






print(fit_proph('https://min-api.cryptocompare.com/data/v2/histominute?fsym=ETH&tsym=USD&limit=1000'))