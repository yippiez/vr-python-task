
import argparse
import requests
import pandas as pd

DATA_PATH = 'vr-python-task/vehicles.csv'
HOST_PATH = 'http://localhost:8080/api/v1/post_csv_data'

parser = argparse.ArgumentParser(description='CSV Transmitter.')
parser.add_argument('-k', '--keys', help="labelIds to color. (list of strings)", required=False)
parser.add_argument('-c', '--colored', help="Color each row if True. (default: True)", default=True, required=False)

args = parser.parse_args()

def csv_to_pd_dataframe(csv_path: str, delimeter: str = ',') -> pd.DataFrame:
    try:
        return pd.read_csv(csv_path, delimiter=delimeter)
    except pd.errors.ParserError as e:
        print('Parsing error when reading CSV file. (Please check delimeter)')
        return None

def send_binary_csv_to_server(hostname: str, csv_path: str) -> bool:
    with open(csv_path, 'rb') as f:
        file_data = {"file": f}
        response = requests.post(hostname, files=file_data)

        match (response.status_code):
            case 200:
                print('File successfully sent to server.')
                return True
            case _:
                print('Error when sending file to server.')
                return False

if __name__ == "__main__":
    send_binary_csv_to_server(HOST_PATH, DATA_PATH)
