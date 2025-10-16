import requests
import json

def pin_to_ipfs(data):
	assert isinstance(data,dict), f"Error pin_to_ipfs expects a dictionary"
	
	pinata_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiJlZTNkNDFhMC1jMjAxLTQyY2ItODJkZC02NDg0MTRhMTc3YmIiLCJlbWFpbCI6ImppYW9kaWFuMDhAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsInBpbl9wb2xpY3kiOnsicmVnaW9ucyI6W3siZGVzaXJlZFJlcGxpY2F0aW9uQ291bnQiOjEsImlkIjoiRlJBMSJ9LHsiZGVzaXJlZFJlcGxpY2F0aW9uQ291bnQiOjEsImlkIjoiTllDMSJ9XSwidmVyc2lvbiI6MX0sIm1mYV9lbmFibGVkIjpmYWxzZSwic3RhdHVzIjoiQUNUSVZFIn0sImF1dGhlbnRpY2F0aW9uVHlwZSI6InNjb3BlZEtleSIsInNjb3BlZEtleUtleSI6ImM2MDA3MWI2MWJkZTllYWRlYzUyIiwic2NvcGVkS2V5U2VjcmV0IjoiYjEyYjRjNGZhOWQzYjhhODM4ZTZhYWQ4NDJlNThkMjY4NTI4YTAyNTQ3MmQwN2NkZmI5YjNlMjY4NGQwOTlhMiIsImV4cCI6MTc5MjE1NDA3OH0.H_D-7-Ii9K0cBxNIQvTDinBOaGy_g9RI5VnLYiH5gzQ"
	
	url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
	headers = {
		"Authorization": f"Bearer {pinata_jwt}",
		"Content-Type": "application/json"
	}
	
	response = requests.post(url, json=data, headers=headers)
	response.raise_for_status()
	
	result = response.json()
	cid = result['IpfsHash']
	
	return cid

def get_from_ipfs(cid,content_type="json"):
	assert isinstance(cid,str), f"get_from_ipfs accepts a cid in the form of a string"
	
	gateway_url = f"https://gateway.pinata.cloud/ipfs/{cid}"
	
	response = requests.get(gateway_url)
	response.raise_for_status()
	
	data = response.json()
	
	assert isinstance(data,dict), f"get_from_ipfs should return a dict"
	return data