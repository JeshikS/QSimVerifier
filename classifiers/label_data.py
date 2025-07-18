# classifiers/label_data.py

import pandas as pd

def infer_label_from_filename(filename):
    for keyword in ['grover', 'vqe', 'qaoa', 'dnn', 'knn', 'qft', 'qpe', 'ghz', 'wstate']:
        if keyword in filename:
            return keyword
    return 'unknown'

def label_dataset(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    df['label'] = df['filename'].apply(infer_label_from_filename)
    df.to_csv(output_csv, index=False)
    print(f"Labeled dataset saved to {output_csv}")

if __name__ == '__main__':
    label_dataset('data/processed_features.csv', 'data/labeled_features.csv')
