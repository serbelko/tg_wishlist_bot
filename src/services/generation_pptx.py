import requests

url = "https://auth.powerpointgeneratorapi.com/v1.0/token/create"
payload={'username': '<your_username>', 'password': '<your_password>', 'key': '<your_security_key>'}
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)