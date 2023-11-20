import requests
import tabula
import pandas as pd
import os
import json
import logging

# # Configure logging
# logging.basicConfig(filename='pdf_extraction.log', level=logging.ERROR)


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
    area = [70, 30, 750, 570]
    try:
        # Read PDF file
        dfs = tabula.read_pdf(pdf_path, pages='all',
                              guess=False, lattice=False,
                              stream=True, multiple_tables=True, area=area)

        # print(dfs)
        # Write the combined DataFrame to a CSV file

        for index, df in enumerate(dfs):
            if "** List of Section 13F Securities **" not in df:
                continue
            # print(f"Table {index + 1}:\n{df}\n")
            df = df.T.reset_index().T.reset_index(drop=True)

            # Assign column names based on the number of columns
            head = range(len(df.columns))
            df.columns = head
            # if index == 0:
            # print(df)
            for id, row in enumerate(df.itertuples()):
                if id == 1 or id == 0 or id == 2:
                    continue
                parts = [str(val) for val in row]
                issuer_description = ''
                status = ''
                print(len(parts), parts)
                if len(parts) == 4:
                    if parts[2].startswith('*'):
                        parts[1] = parts[1] + ' *'
                        parts[2] = parts[2].replace("*","")
                    issuer_description = parts[3]
                elif len(parts) == 5:
                    if parts[2].startswith('*'):
                        parts[1] = parts[1] + ' *'
                        parts[2] = parts[2].replace("*","")
  
                    issuer_description = parts[3]

                    if parts[4] != "nan":
                        status = parts[4]

                cusip_no = parts[1]
                issuer_name = parts[2]
                if cusip_no == "nan":
                    continue
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
    except Exception as e:
        print(e)
        # logging.error(f"Error during PDF extraction: {e}")


# Specify your PDF and xlsx file paths
pdf_file_path = 'file.pdf'
csv_file_path = 'output.csv'
pdf_to_csv(pdf_file_path, csv_file_path)
# # Save the scraped data to a file
outputFileName = "scrapedData.json"
print("", len(listData))
with open(outputFileName, "w", encoding='utf-8') as file:
    json.dump({"data": listData}, file, indent=4, ensure_ascii=False)
delete_file(pdf_file_path)
