import pandas as pd

df = pd.read_csv("data.csv", index_col="Name")

print(df[["Height", "Weight"]].to_string())

print(df.iloc[0:11])

pokemon = input("Enter a Pokemon Name: ")

try:
  print(df.loc[pokemon])

except KeyError:
  print(f"Pokemon {pokemon} Not Found")

# Filtering

tall_pokemon = df[df["Height"] >= 2]

heavy_pokemon = df[df["Weight"] >= 100]

Legendary_pokemon = df[df["Legendary"] == True]

print(tall_pokemon)

print("\n____________________________________________________________\n")

print(heavy_pokemon)

print("\n____________________________________________________________\n")

print(Legendary_pokemon)

#Aggregate Function 1

print("\n____________________________________________________________\n")

print(df.mean(numeric_only=True))

print("\n____________________________________________________________\n")

print(df.sum(numeric_only=True))

print("\n____________________________________________________________\n")

print(df.min(numeric_only=True))

print("\n____________________________________________________________\n")

print(df.max(numeric_only=True))

print("\n____________________________________________________________\n")

print(df.count(numeric_only=True))

#Aggregate Function 2

print(df["Height"].mean())

print("\n____________________________________________________________\n")

print(df["Height"].max())

print("\n____________________________________________________________\n")

print(df["Type2"].count())

#Group By

group = df.groupby("Type1")

print(group.mean(numeric_only=True))

print("\n____________________________________________________________\n")

print(group.max(numeric_only=True))

print("\n____________________________________________________________\n")

print(group.count())

#Data Cleaning 1

#Handel Missing Data
df = df.dropna(subset=["Type2"])

df = df.fillna({"Type2" : "None"})

print(df.to_string())

#Data Cleaning 2

# Fix inconsistent value

df["Type1"] = df["Type1"].replace({"Grass" : "GRAAS"})

print(df.to_string())

#Data Cleaning 3

# Standardix Text

df.index = df.index.str.lower()

print(df.to_string())

#Data Cleaning 4

# Fix Data Type

df["Legendary"] = df["Legendary"].astype(bool)
print(df)