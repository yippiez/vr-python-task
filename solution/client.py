
import pandas as pd
import argparse
import requests
import time
import json
import os

DATA_PATH = r'data\vehicles.csv'
HOST_PATH = 'http://localhost:8080/api/v1/post_csv_data'

parser = argparse.ArgumentParser(description='CSV Transmitter.')
parser.add_argument('-k', '--keys', help="labelIds to color. (list of strings)", nargs='+', required=False)
parser.add_argument('-c', '--colored', help="Color each row if True. (default: True)", default=True, required=False, action=argparse.BooleanOptionalAction) # noqa

args = parser.parse_args()


def csv_to_pd_dataframe(csv_path: str, delimeter: str = ',') -> pd.DataFrame:
    """
    Read csv file and return pandas dataframe.
    :param csv_path: path to csv file.
    :param delimeter: delimeter for csv file.
    :return: pandas dataframe.
    """
    try:
        return pd.read_csv(csv_path, delimiter=delimeter)
    except pd.errors.ParserError as e:
        print('Parsing error when reading CSV file. (Please check delimeter)')
        return None


def send_binary_csv_to_server(hostname: str, csv_path: str) -> dict:
    """
    Send binary csv file to server.
    :param hostname: hostname where to send csv file.
    :param csv_path: path to csv file.
    :return: response from server. (if fails returns None)
    """
    with open(csv_path, 'rb') as f:
        file_data = {"file": f}
        response = requests.post(hostname, files=file_data)

        try:
            status = response.json().get('status')
        except requests.exceptions.JSONDecodeError:
            print("Server returned invalid JSON response.")
            return None

        match (status):
            case "success":
                try:
                    data = response.json().get('data')
                    print('File successfully sent to server.')
                    return data
                except KeyError:
                    print("Server returned invalid JSON response.")
                    exit(1)

            case "error":
                print('Error when sending file to server.')
                return None

            case "csv_parsing_error":
                print('Succesfully sent csv file but there is an error when parsing CSV file.')
                return None

            case _:
                print(f'Unknown error {status} when sending file to server.')
                return None


def get_current_iso_time() -> str:
    """
    Get current ISO time.
    :return: current ISO time.
    """
    return time.strftime("%Y-%m-%dT%H-%M-%S", time.localtime())


def get_writer_for_excel() -> pd.ExcelWriter:
    """
    Get writer for excel.
    :param df: dataframe.
    :return: writer.
    """
    return pd.ExcelWriter(f'vehicles_{get_current_iso_time()}.xlsx', engine='xlsxwriter')


def highlight_for_hu(row):
    """
    Highlight row based on hu.
    :param row: row.
    :return: color code.

    If hu is not older than 3 months --> green (#007500)
    If hu is not older than 12 months --> orange (#FFA500)
    If hu is older than 12 months --> red (#b30000)
    """
    hu_time = row['hu']
    if hu_time is None:
        return ['background-color: white'] * len(row)

    hu_time = pd.to_datetime(hu_time)
    now = pd.Timestamp.now()

    if (now - hu_time).days < 90:
        return ['background-color: #007500'] * len(row)
    elif (now - hu_time).days < 365:
        return ['background-color: #FFA500'] * len(row)
    else:
        return ['background-color: #b30000'] * len(row)


def tint_text_colorCode_if_exists(row):
    """
    Tint text colorCode if exists.
    :param row: row.
    :return: color code.
    """
    colorCode = row['colorCode']
    if colorCode is None:
        return ['color: black'] * len(row)

    return [f'color: {colorCode}'] * len(row)


def apply_colors(df: pd.DataFrame, condition1: bool, condition2: bool):
    """
    Apply colors to dataframe.
    :param df: dataframe.
    :return: dataframe with colors.
    """

    styler = df.style

    if condition1:
        print("Coloring rows based on hu.")
        styler.apply(highlight_for_hu, axis=1)

    if condition2:
        print("Tinting text colorCode if exists.")
        styler.apply(tint_text_colorCode_if_exists, axis=1)

    return styler

def save_style_as_excel(styled_df, keys: list):
    """
    Save styled dataframe as excel.
    :param styled_df: styled dataframe.
    :param keys: columns to include in the final excel.
    """
    if keys is None:
        keys = styled_df.data.columns

    writer = get_writer_for_excel()
    styled_df.to_excel(writer, sheet_name='Sheet1', index=False, header=True, columns=keys)
    writer.save()


if __name__ == "__main__":

    data = send_binary_csv_to_server(HOST_PATH, DATA_PATH)
    df = pd.read_json(data, orient='index')

    # Check if columns always contain rnr field
    if "rnr" not in df.keys():
        print("Error when parsing CSV file.")
        exit(1)

    df = df.sort_values(by=['gruppe'])
    styled_df = apply_colors(df, args.colored, (args.keys is None) or ('labelIds' in args.keys))
    save_style_as_excel(styled_df, keys=args.keys)
