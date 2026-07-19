import pandas as pd
import sys

old_file = r"D:\dawnloads\vendas_teste_limpo.csv"
new_file = "vendas_teste_resultado_v2.csv"

df_old = pd.read_csv(old_file)
df_new = pd.read_csv(new_file)

print(f"Old file: {len(df_old)} rows, {len(df_old.columns)} columns")
print(f"New file: {len(df_new)} rows, {len(df_new.columns)} columns")

if df_old.shape != df_new.shape:
    print("Shapes are different!")
    # Just to compare the ones with the same index
    min_len = min(len(df_old), len(df_new))
    df_old = df_old.iloc[:min_len]
    df_new = df_new.iloc[:min_len]

# Ensure same columns
common_cols = [c for c in df_old.columns if c in df_new.columns]
df_old = df_old[common_cols]
df_new = df_new[common_cols]

try:
    df_diff = df_old.compare(df_new)
    print("\nDifferences:")
    print(df_diff.head(10))
    print(f"\nTotal differences found in {len(df_diff)} rows.")
except Exception as e:
    print("Error comparing:", e)
    # Check manual differences if indexes mismatch
    for col in common_cols:
        diffs = (df_old[col].astype(str) != df_new[col].astype(str)).sum()
        if diffs > 0:
            print(f"Column '{col}' has {diffs} differences")
