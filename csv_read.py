import pandas as pd

# open the csv file
df = pd.read_csv("data.csv")
print(df.columns)

avg_scores = df.groupby('Subject')['Score'].transform('mean')
above_avg_df = df[df['Score'] > avg_scores]
print(above_avg_df[['Subject', 'Score']])