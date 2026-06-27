import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats
import seaborn as sns
import statsmodels.api as sm
from joblib import parallel_backend
from sklearn.datasets import fetch_california_housing
from sklearn.preprocessing import StandardScaler

data = fetch_california_housing(as_frame=True)
df = data.frame

for col in df.columns:
    lo, hi = df[col].quantile([0.01, 0.99])
    df[col] = df[col].clip(lo, hi)

r, p = stats.pearsonr(df["MedInc"], df["MedHouseVal"])
print(f"MedInc vs MedHouseVal: r={r:.3f}, p={p:.3e}")

scaler = StandardScaler()
df_scaled = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)
X = sm.add_constant(df_scaled.drop("MedHouseVal", axis=1))
ols = sm.OLS(df_scaled["MedHouseVal"], X).fit()
print(ols.summary())

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

sns.heatmap(
    df.corr(), annot=True, fmt=".2f", cmap="coolwarm",
    center=0, square=True, ax=axes[0]
)
axes[0].set_title("Feature Correlations")

sns.histplot(df["MedHouseVal"], bins=40, kde=True, ax=axes[1], color="#2c7bb6")
axes[1].set_title("Distribution of Median House Value")
axes[1].set_xlabel("Median House Value ($100k)")

plt.tight_layout()
plt.savefig("eda.png", dpi=150)
print("Saved eda.png")
