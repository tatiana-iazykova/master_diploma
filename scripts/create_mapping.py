import pandas as pd
import json

def main():
    df1 = pd.read_excel('../data/thesis_labels.xlsx', engine='openpyxl')
    df2 = pd.read_excel('../data/label_mapping_new.xlsx', engine='openpyxl')

    df_list = df1.values.tolist()
    ultimate_dict = dict()

    for l in df_list:
        l = [x for x in l if type(x) != float]
        for el in l:
            ultimate_dict[el] = l[0]

    d = df2.set_index('Before').to_dict()['After']
    d = {k: v for k, v in d.items() if type(v) == str}

    ultimate_dict_fin = {k: d[k] if k in d else v for k, v in ultimate_dict.items()}

    with open('../data/final_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(ultimate_dict_fin, f, indent=4, ensure_ascii=4)

if __name__ == "__main__":
    main()