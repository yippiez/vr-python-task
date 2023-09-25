
import argparse
import requests
import pandas as pd

DATA_PATH = 'vr-python-task/vehicles.csv'

parser = argparse.ArgumentParser(description='CSV Transmitter.')
parser.add_argument('-k', '--keys', help="labelIds to color. (list of strings)", required=False)
parser.add_argument('-c', '--colored', help="Color each row if True. (default: True)", default=True, required=False)

args = parser.parse_args()

def csv_to_pd_dataframe(path: str, delimeter: str = ',') -> pd.DataFrame:
    try:
        return pd.read_csv(path, delimiter=delimeter)
    except pd.errors.ParserError as e:
        print('Parsing error when reading CSV file. (Please check delimeter)')
        return None

print('Reading CSV file...')
df = csv_to_pd_dataframe(DATA_PATH, delimeter=';')
print(df)
print('Done.')
