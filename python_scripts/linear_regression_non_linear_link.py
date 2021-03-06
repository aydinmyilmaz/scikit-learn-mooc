# %% [markdown]
# # Linear regression with non-linear link between data and target
#
# In the previous exercise, you were asked to train a linear regression model
# on a dataset where the matrix `X` and the target `y` do not have a linear
# link.
#
# In this notebook, we show that even if the parametrization of linear models
# is not natively adapated to data with non-linearity, it is still possible
# to make linear model more flexible and expressive.
#
# To illustrate these concepts, we will reuse the same dataset generated in the
# previous exercise.

# %%
import numpy as np

rng = np.random.RandomState(0)

n_sample = 100
x_max, x_min = 1.4, -1.4
len_x = (x_max - x_min)
x = rng.rand(n_sample) * len_x - len_x / 2
sorted_idx = np.argsort(x)
noise = rng.randn(n_sample) * .3
y = x ** 3 - 0.5 * x ** 2 + noise

# %% [markdown]
# ```{note}
# To ease the plotting, we will create a Pandas dataframe containing the data
# and target
# ```

# %%
import pandas as pd
data = pd.DataFrame({"x": x, "y": y})

# %%
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_context("talk")

_ = sns.scatterplot(data=data, x="x", y="y")
# %% [markdown]
# We will highlight the limitations of fitting a linear regression model as
# done in the previous exercise.
#
# ```{warning}
# In scikit-learn, by convention `X` should be a 2D matrix of shape
# `(n_samples, n_features)`. If `X` is a 1D vector, you need to reshape it
# into a matrix with a single column if the vector represents a feature or a
# single row if the vector represents a sample.
# ```

# %%
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

linear_regression = LinearRegression()
# X should be 2D for sklearn
X = x.reshape((-1, 1))
linear_regression.fit(X, y)

y_pred = linear_regression.predict(X)
mse = mean_squared_error(y, y_pred)

ax = sns.scatterplot(data=data, x="x", y="y")
ax.plot(x, y_pred, color="tab:orange")
_ = ax.set_title(f"Mean squared error = {mse:.2f}")


# %% [markdown]
# Here the coefficients learnt by `LinearRegression` is the best "straight
# line" that fits the data. We can inspect the coefficients using the
# attributes of the model learnt as follows:

# %%
print(f"weight: {linear_regression.coef_[0]:.2f}, "
      f"intercept: {linear_regression.intercept_:.2f}")

# %% [markdown]
# It is important to note that the model learnt will not be able to handle
# the non-linear relationship between `x` and `y` since linear models assume
# the relationship between `x` and `y` to be linear.
#
# Indeed, there are 3 possibilities to solve this issue:
#
# 1. choose a model that natively can deal with non-linearity,
# 2. "augment" features by including expert knowledge which can be used by
#    the model, or
# 3. use a "kernel" to have a locally-based decision function instead of a
#    global linear decision function.
#
# Let's illustrate quickly the first point by using a decision tree regressor
# which can natively handle non-linearity.

# %%
from sklearn.tree import DecisionTreeRegressor

tree = DecisionTreeRegressor(max_depth=3).fit(X, y)
y_pred = tree.predict(X)
mse = mean_squared_error(y, y_pred)

ax = sns.scatterplot(data=data, x="x", y="y")
ax.plot(x[sorted_idx], y_pred[sorted_idx], color="tab:orange")
_ = ax.set_title(f"Mean squared error = {mse:.2f}")

# %% [markdown]
# Instead of having a model
# which can natively deal with non-linearity, we could also modify our data: we
# could create new features, derived from the original features, using some
# expert knowledge. In this example, we know that we have a cubic and squared
# relationship between `x` and `y` (because we generated the data). Indeed,
# we could create two new features (`x^2` and `x^3`) using this information.

# %%
X = np.vstack([x, x ** 2, x ** 3]).T

linear_regression.fit(X, y)
y_pred = linear_regression.predict(X)
mse = mean_squared_error(y, y_pred)

ax = sns.scatterplot(data=data, x="x", y="y")
ax.plot(x[sorted_idx], y_pred[sorted_idx],
        linewidth=4, color="tab:orange")
_ = ax.set_title(f"Mean squared error = {mse:.2f}")

# %% [markdown]
# We can see that even with a linear model, we can overcome the linearity
# limitation of the model by adding the non-linear component into the design of
# additional features. Here, we created new features by knowing the way the
# target was generated. In practice, this is usually not the case.
#
# Instead, one is usually creating interaction between features (e.g. $x_1
# \times x_2$) with different orders (e.g. $x_1, x_1^2, x_1^3$), at the risk of
# creating a model with too much flexibility where the polynomial terms allows
# to fit noise in the dataset and thus lead overfit. In scikit-learn, the
# `PolynomialFeatures` is a transformer to create such feature interactions
# which we could have used instead of manually creating new features.
#
# To demonstrate `PolynomialFeatures`, we are going to use a scikit-learn
# pipeline which will first create the new features and then fit the model.
# We come back to scikit-learn pipelines and discuss them in more detail later.

# %%
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures

X = x.reshape(-1, 1)

model = make_pipeline(PolynomialFeatures(degree=3),
                      LinearRegression())
model.fit(X, y)
y_pred = model.predict(X)
mse = mean_squared_error(y, y_pred)

ax = sns.scatterplot(data=data, x="x", y="y")
ax.plot(x[sorted_idx], y_pred[sorted_idx], color="tab:orange")
_ = ax.set_title(f"Mean squared error = {mse:.2f}")

# %% [markdown]
# Thus, we saw that `PolynomialFeatures` is actually doing the same
# operation that we did manually above.
#
# The last possibility is to make a linear model more expressive is to use a
# "kernel". Instead of learning a weight per feature as we previously
# emphasized, a weight will be assign by sample instead. However, not all
# samples will be used. This is the base of the support vector machine
# algorithm.

# %%
from sklearn.svm import SVR

svr = SVR(kernel="linear")
svr.fit(X, y)
y_pred = svr.predict(X)
mse = mean_squared_error(y, y_pred)

ax = sns.scatterplot(data=data, x="x", y="y")
ax.plot(x[sorted_idx], y_pred[sorted_idx], color="tab:orange")
_ = ax.set_title(f"Mean squared error = {mse:.2f}")

# %% [markdown]
# The algorithm can be modified so that it can use non-linear kernel. Then,
# it will compute interaction between samples using this non-linear
# interaction.

# %%
svr = SVR(kernel="poly", degree=3)
svr.fit(X, y)
y_pred = svr.predict(X)
mse = mean_squared_error(y, y_pred)

ax = sns.scatterplot(data=data, x="x", y="y")
ax.plot(x[sorted_idx], y_pred[sorted_idx], color="tab:orange")
_ = ax.set_title(f"Mean squared error = {mse:.2f}")

# %% [markdown]
# A method supporting kernel, as SVM, allows to efficiently create a non-linear
# model.
