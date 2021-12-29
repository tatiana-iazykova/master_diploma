import pandas as pd
import requests
from tqdm import tqdm
from typing import List, Dict
import json

class DataFrame:

    def __init__(self):
        self.df = pd.read_excel('../data/patients_update.xlsx')
        self.pmcs = list(set(self.df.pmcs.to_list()))
        self.links = [f'https://www.ncbi.nlm.nih.gov/pmc/articles/{x}/' for x in self.pmcs]
        self.labels = pd.read_excel('../data/label_frequency_update_october2021.xlsx', header=None)
        self.mapping = json.load(open('../data/final_mapping.json'))

    def get_all_tables(self) -> Dict[str, List[pd.DataFrame]]:
        tables = {pmc: [] for pmc in self.pmcs}
        for link, pmc in tqdm(zip(self.links, self.pmcs)):
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

    def get_tables(self, table: pd.DataFrame) -> pd.DataFrame:

        column_names = table.columns

        if len(set(column_names) & set(list(self.mapping.keys()))) > 1:
            columns = [col for col in table.columns if col in self.mapping]
            table = table[columns]
            table.columns = [self.mapping[col] for col in table.columns]
            return table

        elif len(set(table[table.columns[0]].to_list()) & set(list(self.mapping.keys()))) > 1:
            table = table.T
            table.columns = table.iloc[0]
            table = table[1:]
            columns = [col for col in table.columns.to_list() if col in self.mapping]
            table = table[columns]
            table.columns = [self.mapping[col] for col in table.columns]
            return table

        return pd.DataFrame()


    def get_final_dataset(self, labels: List[str], tables: Dict[str, List[pd.DataFrame]]) -> pd.DataFrame:

        df = pd.DataFrame(columns=labels)

        for pmc in self.pmcs:
            patients_histories = self.df[self.df.pmcs == pmc]['patient_description'].to_list()
            tab = tables[pmc]
            result_tables = []

            for table in tab:
                table = self.get_tables(table=table)
                if len(table) == len(patients_histories):
                    result_tables.append(table)

            for i, patient in enumerate(patients_histories):
                row = {c: None for c in df.columns}
                row['pmcs'] = pmc
                row['patient_description'] = patient
                for table in result_tables:
                    row = table.iloc[i].squeeze().to_dict()
                    for k, v in row.items():
                        if k in row and not v:
                            row[k] = row[k]
                        elif k in row and v:
                            row[k] = [v].append(row[k])
                df = df.append(row, ignore_index=True)

        return df
