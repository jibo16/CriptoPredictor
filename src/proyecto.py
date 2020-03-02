import pandas as pd
import requests
from fbprophet import Prophet
from matplotlib import pyplot as plt
from fbprophet.diagnostics import performance_metrics
import statsmodels.api as sm
from statsmodels.tsa.arima_model import ARMA
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.ar_model import AR
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression as Linreg
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error
import numpy as np




def csv_reader(path):
	df = pd.read_csv(path)
	return df





def stock_arma(path,columna):
	df = csv_reader(path)


def stock_fab(path, columna):
	df = pd.read_csv(path)
	X = df.drop(columns=['Date',columna])
	y = df[columna]
	X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2)
	linreg = Linreg()
	reg_lin = linreg.fit(X_test,y_test)
	y_pred = linreg.predict(X_test)
	error2 = r2_score(y_test,y_pred)
	error=(y_pred-y_test).abs().sum()/len(y_pred)
	res = pd.DataFrame({'real': y_test, 'prediccion': y_pred})

	return res, error



def out_elim(path, columna):
	""" Eliminar los outliers de x columna """
	df = csv_reader(path)
	new_df = df.rename(columns={'Date': 'ds', columna:'y'})
	new_df = new_df[['ds','y']]
	stats = new_df.describe(percentiles=[.35,.5,.65]).T
	stats['IQR'] = stats['65%'] -stats['35%']
	cutoff = stats['IQR']* 1.5
	stats['LimiteSuperior'] = stats['65%']+cutoff
	stats['LimiteInferior'] = (stats['35%']-cutoff)
	new_df['y'] = new_df['y'].drop(new_df[new_df['y']> stats['LimiteSuperior']['y']].index)
	new_df = new_df.dropna().reset_index()
	new_df = new_df.drop(columns='index')
	return new_df


def ar_model(path,columna):
	df = out_elim(path,columna)
	train = df['y'][:150]
	test =df['y'][150:]
	model = AR(train)
	model_fit = model.fit()
	model_predict = model_fit.predict()
	return model_predict
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


def ARMA_model(url):
	df = convert(url)
	X = df.drop(columns='High')
	y = df['High']
	X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2)
	linreg = Linreg()
	linreg.fit(X_train,y_train)
	y_pred = linreg.predict(X_test)
	error = r2_score(y_test,y_pred)
	return y_pred


#def ARIMA_model():




#print(df_y('https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit=100'))

print(ar_model('Dow.csv','High'))