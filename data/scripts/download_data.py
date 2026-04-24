from ucimlrepo import fetch_ucirepo

df = fetch_ucirepo(id=601).data.original
df.to_csv("data/raw/sample.csv", index=False)  # save to raw/ not data/ directlycd 

print(f"Done — {len(df)} rows saved")
print(df.columns.tolist())  # verify the columns are correct