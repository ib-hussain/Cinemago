import pandas as pd

df = pd.read_csv("movies.csv", encoding="ISO-8859-1")
df["year_genre"] = df["year_genre"].str.replace("\x95", "•", regex=False)
df.to_csv("movies.csv", index=False, encoding="utf-8")
print("✅ Cleaned and saved with UTF-8 bullet character.")
