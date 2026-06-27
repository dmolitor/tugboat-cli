import numpy as np
import pandas as pd
from sklearn.datasets import load_diabetes
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

data = load_diabetes(as_frame=True)
X, y = data.data.copy(), data.target.copy()

rng = np.random.default_rng(42)
missing_mask = rng.random(X.shape) < 0.05
X[missing_mask] = np.nan
X = X.fillna(X.median())

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

model = Ridge(alpha=1.0)
model.fit(X_train_s, y_train)
y_pred = model.predict(X_test_s)

pd.DataFrame({
    "actual": y_test.values,
    "predicted": y_pred,
    "residual": y_test.values - y_pred,
}).to_csv("predictions.csv", index=False)
