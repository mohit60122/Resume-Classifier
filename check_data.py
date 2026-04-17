import pandas as pd

df = pd.read_csv('Data/Resume/Resume.csv')
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(f"\nCategories ({df['Category'].nunique()}):")
print(df['Category'].value_counts())
