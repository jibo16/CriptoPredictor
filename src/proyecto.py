import pandas as pd
import requests
from fbprophet import Prophet
from matplotlib import pyplot as plt
from fbprophet.diagnostics import performance_metrics
import statsmodels.api as sm

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



def auto_reg(url,columna):
	df = crypto_definer(url)
	dias = df[columna].loc['2019-11-17':'2020-02-25']
	dias.plot()
	dias.show();




def convert(url):
	df = crypto_definer(url)
	df['UNIX_TIME'] = df['UNIX_TIME'].astype(int)
	df['UNIX_TIME'] = pd.to_datetime(df['UNIX_TIME'], unit='s')
	fig, axs = plt.subplots(nrows = 2,ncols= 2, figsize=(12,12))
	axs[0,0].plot(df['UNIX_TIME'], df['Open'], c='r')
	axs[0,0].set_title('OPEN PRICE')
	axs[0,1].plot(df['UNIX_TIME'],df['High'], c='purple')
	axs[0,1].set_title('HIGH PRICE')
	axs[1,0].plot(df['UNIX_TIME'], df['Low'], c= 'blue')
	axs[1,0].set_title('LOW PRICE')
	axs[1,1].plot(df['UNIX_TIME'],df['Close'], c = 'green')
	axs[1,1].set_title('CLOSE PRICE')
#	plt.show();
	plt.savefig('OHLC.png')
	return df


#def out_remover(url,columna):




def df_y(url, columna='High'):
	""" Convierte las columnas de time y precio X a un formato predeterminado
	 que pide facebook prophet, la fecha como DS y la columna a predecir como y """
	m = Prophet()
	df = convert(url)
	new_df = df.rename(columns = {'UNIX_TIME': 'ds', columna : 'y'})
	new_df = new_df[['ds', 'y']]
	m.fit(new_df)
	future = m.make_future_dataframe(periods=50)
	forecast = m.predict(future)
	forecast = forecast[['ds', 'trend', 'yhat', 'yhat_upper', 'yhat_lower', 'trend_upper']] 
	nuevo = new_df.merge(forecast, on='ds')
	return nuevo


print(auto_reg('https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit=100', 'High'))