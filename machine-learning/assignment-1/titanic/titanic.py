# Note: converted from .ipynb format
import numpy as np
import pandas as pd
import sklearn as sk
from sklearn import linear_model

# file paths
TRAIN_PATH = "data/train.csv"
TEST_PATH = "data/test.csv"

# read in the datasets from the respective CSV files
train_data = pd.read_csv(TRAIN_PATH)
test_data = pd.read_csv(TEST_PATH)

# replace the categorical classes with binary
train = train_data.replace({'Sex': {'male': 0, 'female': 1}})
test = test_data.replace({'Sex': {'male': 0, 'female': 1}})

def replace_na (data_set):
    # find mean male age
    male_age = data_set.loc[data_set['Sex'] == 0]['Age'].dropna()
    male_mean_age = np.mean(male_age)
    print "Mean male age: ", male_mean_age

    # find mean female age
    female_age = data_set.loc[data_set['Sex'] == 1]['Age'].dropna()
    female_mean_age = np.mean(female_age)
    print "Mean female age: ", female_mean_age

    # replace empty cells with appropriate mean age based on sex
    data_set[(data_set['Sex']==0) & (pd.isnull(data_set['Age']))] = data_set[(data_set['Sex']==0) & (pd.isnull(data_set['Age']))].fillna(male_mean_age)
    data_set[(data_set['Sex']==1) & (pd.isnull(data_set['Age']))] = data_set[(data_set['Sex']==1) & (pd.isnull(data_set['Age']))].fillna(female_mean_age)
    return

replace_na(train)
replace_na(test)

# choose features to include
x_train = train[['Pclass', 'Age', 'Sex', 'SibSp', 'Parch']].values
y_train = train['Survived'].values

x_test = test[['Pclass', 'Age', 'Sex', 'SibSp', 'Parch']].values

# fit
lr = linear_model.LogisticRegression(random_state=1).fit(x_train, y_train)

# cross validation, k=3
scores = sk.cross_validation.cross_val_score(lr, x_train, y_train, cv=3)
print scores.mean()

# predict and submit!
predicted_values = lr.predict(x_test)
p_id = test_data[['PassengerId']].values.flatten()

submission = pd.DataFrame({'PassengerId': p_id, 'Survived': predicted_values})
submission.to_csv('titanic_submission.csv', index=False)
print submission
