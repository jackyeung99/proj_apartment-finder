import requests
import pandas as pd 

class api_access:

	def __init__():
		apartment_data = pd.DataFrame()

	def send_access_keys(self,location):
		url = "https://apartments-com1.p.rapidapi.com/properties"

		querystring = {"location": location}

		headers = {
			"X-RapidAPI-Key": "f2e1092fdfmsh426df4ce1a202edp190c71jsnc16dabc266d3",
			"X-RapidAPI-Host": "apartments-com1.p.rapidapi.com"
		}

		data = requests.get(url, headers=headers, params=querystring).json()
		
		return data['data']

	def main(self):
		data = self.send_access_keys("Austin")

	
if __name__ == "__main__":
	main()
		
cd On