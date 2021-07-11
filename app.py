from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here

url_get = requests.get('https://www.exchange-rates.org/history/IDR/USD/T')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
data = []
table = soup.find('table')
table_body = table.find('tbody')

rows = table_body.find_all('tr')
for row in rows:
	cols = row.find_all('td')
	cols = [el.text.strip() for el in cols]
	data.append([el for el in cols])

import pandas as pd

dataawal = pd.DataFrame(data, columns=['date', 'day', 'rate', 'description'])


#change into dataframe
dataawal = pd.DataFrame(data, columns=['date', 'day', 'rate', 'description'])

#insert data wrangling here
dataolah = dataawal.drop('description',1)

dataolah.rate = dataolah.rate.str.replace(",", "")
dataolah.rate = dataolah.rate.str.replace(" IDR", "")
dataolah.rate = dataolah.rate.astype('float64')
dataolah.date = dataolah.date.astype('datetime64')
dataolah.day = dataolah.day.astype('category')

dataolah = dataolah.set_index('date')
dataolah = dataolah[::-1]


#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{dataolah["rate"].mean().round(2):,}' #be careful with the " and ' 

	# generate plot
	ax = dataolah.plot(figsize = (10,6))
	ax.set_xlabel('Tanggal')
	ax.set_ylabel('Nilai Kurs')
	ax.set_xticklabels(dataolah.index, minor=True)

	# calculate start and end date
	index_olah = dataolah.index
	start_date = '%s-%s-%s' % (str(index_olah.min().day), str(index_olah.min().month), str(index_olah.min().year))
	end_date = '%s-%s-%s' % (str(index_olah.max().day), str(index_olah.max().month), str(index_olah.max().year))
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result,
		start_date = start_date,
		end_date = end_date,
	)


if __name__ == "__main__": 
    app.run(debug=True)