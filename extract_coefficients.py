import requests
import json

# Base URL
url = "https://comp.uefa.com/v2/coefficients"

params_list = []

for i in range(2003, 2026):
    param = {
    "coefficientRange": "OVERALL",
    "coefficientType": "MEN_ASSOCIATION",
    "language": "EN",
    "page": 1,
    "pagesize": 100,
    "seasonYear": i
    }
    params_list.append(param)

# Headers (adjust as needed based on reqbin behavior)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept": "application/json",  # Explicitly requesting JSON
    "Referer": "https://reqbin.com",  # Some APIs require a referer header
}

data_list = []

try:
    for params in params_list:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)

        data = response.json()
        print("Data fetched successfully:")
        data_list.append(data)

    file_path = "coefficients.json"

    with open(file_path, "w") as json_file:
        json.dump(data_list, json_file, indent=4)

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
