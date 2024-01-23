import requests
import pandas as pd 

USER_AUTHENTICATION = {
			"X-RapidAPI-Key": "f2e1092fdfmsh426df4ce1a202edp190c71jsnc16dabc266d3",
			"X-RapidAPI-Host": "apartments-com1.p.rapidapi.com"
		}

class api_access:   
	def __init__(self, location):
		self.apartment_data = pd.DataFrame()
		self.location = location

	def search_property(self):
		url = "https://apartments-com1.p.rapidapi.com/properties"
		querystring = {'location': self.location}
		try:
			response = requests.get(url, headers=USER_AUTHENTICATION, params=querystring)
			if response.status_code == 200:
				return response.json()['data']
			else:
				print(f"Failed to get property list: {response.status_code}")
				return None
		except requests.RequestException as e:
			print(f"Request failed: {e}")
			return None
            
            
	def get_property_details(self, apartment_id):
		url = f"https://apartments-com1.p.rapidapi.com/properties/{apartment_id}"
		response = requests.get(url, headers=USER_AUTHENTICATION)
		if response.status_code == 200:
			return response.json()['data']
		else:
			return None

	def get_property_review(self, apartment_id):
		url = f"https://apartments-com1.p.rapidapi.com/properties/{apartment_id}/reviews"
		response = requests.get(url, headers=USER_AUTHENTICATION)
		if response.status_code == 200:
			return response.json()['data']
		else:
			return None

	def get_all_apartment_data(self, request_cap=50):
		property_search = self.search_property()
		if property_search:
			all_data = []
			for apartment in property_search[:request_cap]:
				if apartment['id']:
					print(f"Fetching data for apartment ID: {apartment['id']}")
					id = apartment['id']
					apartment_data = self.get_property_details(id)
					# apartment_reviews = self.get_property_review(id)
					if apartment_data:
						all_data.append(apartment_data)
			if all_data:
				self.apartment_data = pd.DataFrame(all_data)
			
	def dump(self):
		self.apartment_data.to_csv(f'{self.location}_apartment_data.csv')

	def main(self):
		self.get_all_apartment_data()
		self.dump()

	
if __name__ == "__main__":
	access = api_access("Austin")
	access.main()
