import pandas as pd
import requests
from tqdm import tqdm
from typing import List, Dict
import json

class DataFrame:

    def __init__(self, path_to_df: str, path_to_label_frequency_file: str, path_to_mapping: str):
        self.df = pd.read_excel(path_to_df, engine='openpyxl')
        self.pmcs = list(set(self.df.pmcs.to_list()))
        self.links = [f'https://www.ncbi.nlm.nih.gov/pmc/articles/{x}/' for x in self.pmcs]
        self.labels = pd.read_excel(path_to_label_frequency_file, header=None, engine='openpyxl')
        self.mapping = json.load(open(path_to_mapping))

    def get_all_tables(self) -> Dict[str, List[pd.DataFrame]]:
        tables = {pmc: [] for pmc in self.pmcs}
        for link, pmc in tqdm(zip(self.links, self.pmcs), total=len(self.pmcs)):
            r = requests.get(link)
            try:
                t = pd.read_html(r.text, header=0)
                for tab in t:
                    tables[pmc].append(tab)
            except:
                print(f"There aren't any tables in the page {link}")
        return tables

    def get_labels(self) -> List[str]:
        self.labels.columns = ['name', 'count']
        labs = self.labels.name[:50].to_list()
        res = ['pmcs', 'patient_description']
        res.extend(labs)
        return res

    def get_final_dataset(self, labels: List[str], tables: Dict[str, List[pd.DataFrame]]) -> pd.DataFrame:

        df = pd.DataFrame(columns=labels)

        for pmc in self.pmcs:
            rows = self.df[self.df.pmcs == pmc]['patient_description'].to_list()
            tab = tables[pmc]
            t = []
            for table in tab:
                colnames = table.columns
                if len(set(colnames) & set(list(self.mapping.keys()))) > 1:
                    columns = [col for col in table.columns if col in self.mapping]
                    table = table[columns]
                    table.columns = [self.mapping[col] for col in table.columns]
                    if len(table) == len(rows):
                        t.append(table)
                elif len(set(table[table.columns[0]].to_list()) & set(list(self.mapping.keys()))) > 1:
                    table = table.T
                    table.columns = table.iloc[0]
                    table = table[1:]
                    columns = [col for col in table.columns.to_list() if col in self.mapping]
                    table = table[columns]
                    table.columns = [self.mapping[col] for col in table.columns]
                    if len(table) == len(rows):
                        t.append(table)
            for i, patient in enumerate(rows):
                dict_series = {c: None for c in df.columns}
                dict_series['pmcs'] = pmc
                dict_series['patient_description'] = patient
                for table in t:
                    row = table.iloc[i].squeeze().to_dict()
                    for k, v in dict_series.items():
                        if k in row and not v:
                            dict_series[k] = row[k]
                        elif k in row and v:
                            dict_series[k] = [v].append(row[k])
                df = df.append(dict_series, ignore_index=True)
        return df

    def create_df(self) -> pd.DataFrame:
        tables = self.get_all_tables()
        labels = self.get_labels()
        dataframe = self.get_final_dataset(
            labels=labels,
            tables=tables
        )
        return dataframe


if __name__ == "__main__":
    d = DataFrame(
        path_to_df='data/patients_update.xlsx',
        path_to_label_frequency_file='data/label_frequency_update_october2021.xlsx',
        path_to_mapping='data/final_mapping.json'
    )
    data = d.create_df()
    data.to_excel('data/parsed_df.xlsx', index=False, engine='openpyxl')

