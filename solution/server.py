
from flask import Flask, request, jsonify
import pandas as pd
import requests

from solution.secret import get_oauth_acces_token, OAUTH_TOKEN

app = Flask(__name__)

def get_resources(oauth_token: str):
    RESOURCES_ENDPINT = "https://api.baubuddy.de/dev/index.php/v1/vehicles/select/active"

    headers = {
        "Authorization": f"Bearer {oauth_token}",
        "Content-Type": "application/json",
    }

    response = requests.post(RESOURCES_ENDPINT, headers=headers)
    return response.json()

def csv_to_pd_dataframe(csv_path: str, delimeter: str = ',') -> pd.DataFrame:
    try:
        return pd.read_csv(csv_path, delimiter=delimeter)
    except pd.errors.ParserError as e:
        print('Parsing error when reading CSV file. (Please check delimeter)')
        return None

@app.route('/api/v1/post_csv_data', methods=['POST'])
def post_csv_data():

    if 'file' not in request.files:
        print("[!] No file part in the request. Sending eror response.")
        return jsonify({"status": "error"})

    file_storage_object = request.files['file']
    # file_storage_object.save('test.csv')  # (WORKING)

    df = csv_to_pd_dataframe(file_storage_object, delimeter=';')

    # if df is none csv file is invalid
    if df is None:
        print("[!] Invalid CSV file. Sending error response.")
        return jsonify({"status": "csv_parsing_error"})

    return jsonify({"status": "success"})

if __name__ == '__main__':
    # run app in debug mode on port 8080
    app.run(debug=True, port=8080)
