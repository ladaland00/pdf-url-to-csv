import requests
import tabula
import pandas as pd
import os
import json


def delete_file(file_path):
    try:
        # Attempt to remove the file
        os.remove(file_path)
        print(f"File '{file_path}' deleted successfully.")
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"Error deleting file '{file_path}': {e}")


def download_pdf(url, save_path):
    response = requests.get(url)

    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"PDF downloaded successfully at {save_path}")
    else:
        print(f"Failed to download PDF. Status code: {response.status_code}")


# Specify the URL of the PDF and the desired save path
pdf_url = 'https://www.sec.gov/files/investment/13flist2023q3.pdf'
save_path = 'file.pdf'

# Download the PDF
download_pdf(pdf_url, save_path)
listData = []


def pdf_to_csv(pdf_path, csv_path):
    global listData
    # Read PDF file
    dfs = tabula.read_pdf(pdf_path, pages='all')

    # Write the combined DataFrame to a CSV file
    for index, df in enumerate(dfs):
        for row in df.values:
            parts = [str(val) for val in row]
            issuer_description = ''
            status = ''

            if len(parts) == 3:
                issuer_description = parts[2]
            elif len(parts) == 4:
                if '*' == parts[1]:
                    parts[0] = parts[0] + ' *'
                elif 'nan' == parts[1]:
                    parts[0] = parts[0] + ' '
                parts.pop(1)
                issuer_description = parts[2]
            elif len(parts) == 5:
                if '*' in parts:
                    parts[0] = parts[0] + ' *'
                elif 'nan' == parts[1]:
                    parts[0] = parts[0] + ' '
                parts.pop(1)
                issuer_description = parts[2]

                if parts[3] != "nan":
                    status = parts[3]

            cusip_no = parts[0]
            issuer_name = parts[1]
            listData.append({
                "CUSIP NO": cusip_no,
                'ISSUER NAME': issuer_name,
                'ISSUER DESCRIPTION': issuer_description,
                'STATUS': status
            })
    # Convert the list to a DataFrame
    result_df = pd.DataFrame(listData)

    # Write the DataFrame to a CSV file
    result_df.to_csv(csv_path, index=False)
    print(f"Data from PDF saved to CSV file: {csv_path}")


# Specify your PDF and xlsx file paths
pdf_file_path = 'file.pdf'
csv_file_path = 'output.csv'
pdf_to_csv(pdf_file_path, csv_file_path)
# # Save the scraped data to a file
outputFileName = "scrapedData.json"
with open(outputFileName, "w", encoding='utf-8') as file:
    json.dump({"data": listData}, file, indent=4, ensure_ascii=False)
delete_file(pdf_file_path)
