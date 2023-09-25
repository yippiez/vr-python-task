
from flask import Flask, request, jsonify
import pandas as pd
import requests
import json

from secret import get_oauth_acces_token

# Get token
OAUTH_TOKEN = get_oauth_acces_token()

# ------------ Constants ------------

RESOURCES_ENDPOINT = "https://api.baubuddy.de/dev/index.php/v1/vehicles/select/active"
app = Flask(__name__)

# ------------ Functions ------------

def get_resources(oauth_token: str) -> dict:
    """
    Get resources from API.
    :param oauth_token: oauth token.
    :return: resources from API. (if fails returns None)
    """
    headers = {
        "Authorization": f"Bearer {oauth_token}",
        "Content-Type": "application/json",
    }

    response = requests.get(RESOURCES_ENDPOINT, headers=headers)

    data = response.json()

    # if it has key 'error' with message 'Unauthorized' then we need to get new token
    if isinstance(data, dict):
        if 'error' in data.keys() and data['error']['message'] == 'Unauthorized':
            print("[!] Unauthorized.")
            return None

    return response.json()


def csv_to_pd_dataframe(csv_path: str, delimeter: str = ',') -> pd.DataFrame:
    """
    Read csv file and return pandas dataframe.
    :param csv_path: path to csv file.
    :param delimeter: delimeter for csv file.
    :return: pandas dataframe. (if fails returns None)
    """
    try:
        return pd.read_csv(csv_path, delimiter=delimeter)
    except pd.errors.ParserError as e:
        print('Parsing error when reading CSV file. (Please check delimeter)')
        return None


def get_label_id_color_code(label_id: str, oauth_token: str):
    """
    Get color code from label id.
    :param label_id: label id.
    :param oauth_token: oauth token.
    :return: color code. (if fails returns None)
    """
    if not label_id:
        return None

    response_url = f'https://api.baubuddy.de/dev/index.php/v1/labels/{label_id}'

    headers = {
        "Authorization": f'Bearer {oauth_token}',
    }

    response = requests.get(response_url, headers=headers)

    try:
        colorCode = response.json()[0]['colorCode']
        return colorCode if colorCode else None
    except KeyError:
        print("Error when reciving color code from API")
        print(f"Got response: {response.json()}")
        return None


# --------------- API ---------------

@app.route('/api/v1/post_csv_data', methods=['POST'])
def post_csv_data():

    # Check if file is present
    if 'file' not in request.files:
        print("[!] No file part in the request. Sending eror response.")
        return jsonify({"status": "error"})

    file_storage_object = request.files['file']

    # Convert CSV to dataframe for easier manipulation
    df = csv_to_pd_dataframe(file_storage_object, delimeter=';')

    if df is None:
        print("[!] Invalid CSV file. Sending error response.")
        return jsonify({"status": "csv_parsing_error"})

    # Get resources from API
    resources = get_resources(OAUTH_TOKEN)

    for resource in resources:
        new_row = pd.DataFrame(resource, index=[0])

        if new_row['hu'].isnull().values.any():
            print("Skipping row (hu is unset)")
            continue

        df = pd.concat([df, new_row], ignore_index=True)

    # Make all rows unique
    df = df.drop_duplicates()

    # Convert all NaNs to None
    df = df.where(pd.notnull(df), None)

    # Add colorCode column
    df['colorCode'] = df['labelIds'].apply(lambda x: get_label_id_color_code(x, OAUTH_TOKEN))

    response = df.to_json(orient="index")

    return jsonify({"status": "success", "data": response})

# --------------------------------------------

if __name__ == '__main__':
    # Run app in debug mode on port 8080
    app.run(debug=True, port=8080)
