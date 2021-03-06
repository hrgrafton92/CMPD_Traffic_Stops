# Contrast Model & Fairness Model
This notebook will explore the possibilities of creating predictive models for traffic stop outcome while including race in a fair way. To do this, it will explore two main approaches: obfuscating race and gender through a "contrast" datasource, and using scikit-learn fairness metrics to penalize race in model performance and selection.

## Import Packages
"""

!pip install scikit-lego
# uncomment to install scikit-lego (sklego)

#!pip install imbalanced-learn
from imblearn.over_sampling import SMOTENC

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklego.linear_model import DemographicParityClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import matthews_corrcoef, classification_report, confusion_matrix, ConfusionMatrixDisplay
from sklearn.preprocessing import OneHotEncoder


"""## Loading Data"""

train = pd.read_csv('Processed_Data/stops_2020_train.csv')
test = pd.read_csv('Processed_Data/stops_2020_test.csv')

train['Was_a_Search_Conducted'].value_counts()

"""## Upsampling"""

def upsample_process(data, desired_col):
  # Drops uninteresting columns
  # Upsamples appropriately and returns training data, upsampled.
  data_colsdropped = data.drop(['Unnamed: 0', 'Month_of_Stop', 'Result_of_Stop', 'Outcome'], axis = 1)
  X = data_colsdropped[(data_colsdropped.columns[data_colsdropped.columns != 'Was_a_Search_Conducted']) \
                       & (data_colsdropped.columns[data_colsdropped.columns != 'Arrest'])]
  Y = data_colsdropped[['Was_a_Search_Conducted', 'Arrest']]
  cat_cols = X.columns.isin(['Reason_for_Stop', 'Officer_Race',\
                             'Officer_Gender', 'Driver_Race',\
                             'Driver_Ethnicity','Driver_Gender',\
                             'CMPD_Division', 'Racial_Match'])
  su = SMOTENC(categorical_features=cat_cols, random_state=42)
  try:
    X_upsample, Y_upsample = su.fit_resample(X, Y[desired_col])
  except KeyError:
    print('Could not find that column in data!')
    return _,_
  print('X resample shape: {}'.format(X_upsample.shape))
  print('Y resample shape: {}'.format(Y_upsample.shape))
  return pd.concat([X_upsample, Y_upsample], axis = 1)

train_upsample = upsample_process(train, 'Was_a_Search_Conducted')

train_upsample.head()

# if you'd like to run models with not-upsampled data, try uncommenting this line of code.
# the result of the pipeline will still be called "X_train"
# train_upsample = train.copy()

"""## Creating Contrast Datasource"""

def OH_Encode(df, columns):
  OH = OneHotEncoder()

  new = pd.DataFrame(OH.fit_transform(df[columns]).toarray())
  cols = []
  for index, val in enumerate(columns):
    cols += [val + '_' + x.strip() for x in list(OH.categories_[index])]

  new.columns = cols

  return pd.concat([df, new], axis = 1).drop(columns, axis = 1)

def prepare_contrast(data, desired_col):
  contrast_start = data.copy()
  contrast_mid = OH_Encode(contrast_start, ['Reason_for_Stop', 'CMPD_Division'])

  try:
    contrast_mid = contrast_mid.drop(['Unnamed: 0', 'Month_of_Stop', 'Result_of_Stop', 'Outcome', 'Arrest'], axis = 1)
  except:
    pass
  
  contrast_mid['Gender_Match'] = (contrast_mid['Officer_Gender'] == contrast_mid['Driver_Gender']).astype('int')
  contrast_final = contrast_mid.drop(['Officer_Race', 'Driver_Race',  'Officer_Gender', 'Driver_Gender'], axis = 1)
  contrast_X = contrast_final[(contrast_final.columns[contrast_final.columns != 'Was_a_Search_Conducted']) & (contrast_final.columns[contrast_final.columns != 'Arrest'])]
  contrast_T = contrast_final[desired_col]
  return contrast_X, contrast_T

X_train_contrast, T_train_contrast = prepare_contrast(train_upsample, 'Was_a_Search_Conducted')

X_test_contrast, T_test_contrast = prepare_contrast(test, 'Was_a_Search_Conducted')

X_test_contrast.head()

"""## Creating Datasource for Main Classifiers

"""

def return_race(s):
  race_dict = {'Black':1, 'White':0, 'Other/Unknown':1, 'Asian':1, 'Native American':1}
  return race_dict[s]

def prepare_normal(data, desired_col):
  normal_data = OH_Encode(data, ['Reason_for_Stop', 'CMPD_Division', 'Officer_Race'])

  # Tries to drop columns if it can.
  try:
    normal_data = normal_data.drop(['Racial_Match'], axis = 1)
    normal_data = normal_data.drop(['Unnamed: 0', 'Month_of_Stop', 'Result_of_Stop', 'Outcome'], axis = 1)
  except:
    pass

  # Transform Values for Arrest, Race, and Searches.
  #normal_data['Arrest'] = [1 if x == 'Arrest' else 0 for x in normal_data['Arrest']]
  normal_data['Driver_Race'] = normal_data['Driver_Race'].map(return_race)
  # normal_data['Was_a_Search_Conducted'] = [1 if x == 0 else 0 for x in normal_data['Was_a_Search_Conducted']]

  # Subset to desired columns.
  final_X = normal_data[(normal_data.columns[normal_data.columns != 'Was_a_Search_Conducted']) & (normal_data.columns[normal_data.columns != 'Arrest'])]
  final_T = normal_data[desired_col]
  return final_X, final_T

X_train, T_train = prepare_normal(train_upsample, 'Was_a_Search_Conducted')
X_test, T_test = prepare_normal(test, 'Was_a_Search_Conducted')

"""## Train and Eval Functions"""

def train_eval(clf, X_train, t_train, X_test, t_test, info):
    clf.fit(X_train, t_train)

    train_score = clf.score(X_train, t_train)
    test_score = clf.score(X_test, t_test)

    print("{}> Train Accuracy: {}, Test Accuracy: {}".format(info['clf'], train_score, test_score))
    test_pred = clf.predict(X_test)
    
    print("{}> MCC is {}".format(info['clf'], matthews_corrcoef(t_test, test_pred)))
    print(classification_report(t_test, test_pred))
    
    cm = confusion_matrix(t_test, test_pred, labels=clf.classes_)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=clf.classes_)
    disp.plot()
    plt.title(info['clf'])
    plt.show()
    
    # Residual Plot
    #residuals = t_test - test_pred
    #plt.scatter(X_test[col], residuals)
    #plt.title('Residuals for {} for {}'.format(name, col))
    #plt.show()

models = [LogisticRegression(max_iter = 500), GradientBoostingClassifier(), KNeighborsClassifier(), GaussianNB(), RandomForestClassifier(), DemographicParityClassifier(sensitive_cols="Driver_Race", covariance_threshold=0.80)]
names = ["Logistic Reg", "GradientBoostingClassifier", 'KNeighborsClassifier', 'GaussianNB', 'RandomForest', 'DemographicParityClassifier']

"""## Baseline Classifier Performance - Upsampled Data"""

for name, model in zip(names, models):
    info = {'clf':name, 'data':'Charlotte Policing'}
    train_eval(model, X_train, T_train, X_test, T_test, info)

"""## Baseline Classifier Performance - Contrast

"""

models = [LogisticRegression(max_iter = 1000), GradientBoostingClassifier(), GaussianNB()]
names = ["Logistic Reg", "GradientBoostingClassifier", 'GaussianNB']

for name, model in zip(names, models):
    info = {'clf':name, 'data':'Charlotte Policing'}
    train_eval(model, X_train, T_train, X_test, T_test, info)

"""## Fine Tuning Best Normal Classifiers (Include and Exclude Race)

#### Drop "Driver_Race" variable to see how it affects metrics.
"""

# Creating dataframes (from upsampled DFs) with Driver_Race dropped
X_train_res_race_dropped = X_train.drop(["Driver_Race"], axis = 1)
X_test_normal_race_dropped = X_test.drop(["Driver_Race"], axis = 1)

# Modeling DFs with Driver_Race dropped.
for name, model in zip(names, models):
    info = {'clf':name, 'data':'Charlotte Policing'}
    # NOTE: DemographicParityClassifier doesn't work with the new X train/test DFs due to shape issues
    train_eval(model, X_train_res_race_dropped, T_train, X_test_normal_race_dropped, T_test, info)

### The performance was negligibly different across the board with regards to Prec. and Recall for each 
#   classifier, with marginal drops in Train and Test accuracy for a majority of classifiers. Thus, 
#   Driver_Race has some marginal positive effect on Train/Test accuracy for most of the classifiers
#   so it should be kept, especially if the runtime is largely the same with or w/o it.

"""#### Drop low-covariance columns to see how they affect metrics."""

# see what columns are in X_train
X_train.head()

import seaborn as sns

# checking correlation between variables, esp. between race and other variables
plt.figure(figsize=(25,20))
sns.heatmap(X_train.corr(), annot=True)

# drop a few neg. correlated vars from train/test

X_train_reduced = X_train.drop(["Officer_Gender","Officer_Years_of_Service","Driver_Age"], axis = 1)
X_test_reduced = X_test.drop(["Officer_Gender","Officer_Years_of_Service","Driver_Age"], axis = 1)

# check metrics to see how dropping the vars affected metrics
for name, model in zip(names, models):
    info = {'clf':name, 'data':'Charlotte Policing'}
    train_eval(model, X_train_reduced, T_train, X_test_reduced, T_test, info)

### After running this with the reduced dataset, it was observed that the metrics either marginally improved for recall,
#   or were worse consistently across models. Next step could be statistical (K Best) and/or wrapper methods (Seq. Feature Selector)

"""#### Stats-based feature selection (Filter Methods)"""

from sklearn.feature_selection import SelectKBest, f_classif, chi2, mutual_info_classif
import matplotlib.pyplot as plt

# run this block if you'd like to try with Officer_POC to see its importance instead of the one-hot encoded race.
#X_train['Officer_POC'] = [0 if x == 'White' else 1 for x in X_train['Officer_Race_White']]
#X_train.drop(['Officer_Race_Asian', 'Officer_Race_Black', 'Officer_Race_Native American', 'Officer_Race_Other/Unknown', 'Officer_Race_White'], inplace = True, axis = 1)
#X_test['Officer_POC'] = [0 if x == 'White' else 1 for x in X_test['Officer_Race_White']]
#X_test.drop(['Officer_Race_Asian', 'Officer_Race_Black', 'Officer_Race_Native American', 'Officer_Race_Other/Unknown', 'Officer_Race_White'], inplace = True, axis = 1)

X_train.shape

X_train.columns

# feature selection: chi2
import numpy as np
from sklearn.preprocessing import MinMaxScaler
x_1 = MinMaxScaler().fit_transform(X_train)

def select_features(X_train, y_train, X_test):
	fs = SelectKBest(score_func=chi2, k='all')
	fs.fit(X_train, y_train)
	X_train_fs = fs.transform(X_train)
	X_test_fs = fs.transform(X_test)
	return X_train_fs, X_test_fs, fs


X_train_fs, X_test_fs, fs = select_features(x_1, T_train, X_test)
# what are scores for the features
for i in range(len(fs.scores_)):
	print('Feature %d, ' % (i) + X_train.columns[i] + ': %f' % (fs.scores_[i]))
# plot the scores
plt.bar([i for i in range(len(fs.scores_))], np.sort(fs.scores_))
#plt.xticks(rotation = 90)
plt.xlim(0,34)
plt.ylabel("Score")
plt.title("Chi-Squared Value per Variable")
plt.show()


plt.bar([X_train.columns[i] for i in range(len(fs.scores_))], fs.scores_)
plt.xticks(rotation = 90)
plt.xlim(0,34)
plt.ylabel("Score")
plt.title("Chi-Squared Value per Variable")
plt.show()

### NOTE, THE FEATURE NUMBERS DO NOT MATCH BETWEEN THE SORTED GRAPH AND THE TEXT OUTPUT

np.sort(fs.scores_)

# Obtain the indexes of the 7 columns that contain the lowest chi^2 values
lowest_7_indexes = [list(fs.scores_).index(val) for val in sorted(list(fs.scores_))[:7]]

# New DFs that will contain the undropped features (based on the chi^2 vals above)
X_train_res_c2_drop = X_train.copy()
X_test_norm_c2_drop = X_test.copy()

# Iteratively drop the variables that corresond the lowest 7 chi^2 vals
for index in lowest_7_indexes:
  X_train_res_c2_drop.drop(X_train.columns[index], axis=1, inplace=True)
  X_test_norm_c2_drop.drop(X_test.columns[index], axis=1, inplace=True)

# check metrics to see how dropping the lowest 7 relevant variables affected metrics
for name, model in zip(names, models):
    info = {'clf':name, 'data':'Charlotte Policing'}
    train_eval(model, X_train_res_c2_drop, T_train, X_test_norm_c2_drop, T_test, info)

# feature selection: mutual_info_classif
def select_features(X_train, y_train, X_test):
	fs = SelectKBest(score_func=mutual_info_classif, k='all')
	fs.fit(X_train, y_train)
	X_train_fs = fs.transform(X_train)
	X_test_fs = fs.transform(X_test)
	return X_train_fs, X_test_fs, fs


X_train_fs, X_test_fs, fs = select_features(X_train, T_train, X_test)
# what are scores for the features
for i in range(len(fs.scores_)):
	print('Feature %d, ' % (i) + X_train.columns[i] + ': %f' % (fs.scores_[i]))
# plot the scores
plt.bar([i for i in range(len(fs.scores_))], np.sort(fs.scores_))
plt.xlim(0,34)
plt.ylabel("Score")
plt.title("Mutual Information Value per Variable")
plt.show()



plt.bar([X_train.columns[i] for i in range(len(fs.scores_))], fs.scores_)
plt.xticks(rotation = 90)
plt.xlim(0,34)
plt.ylabel("Score")
plt.title("Chi-Squared Value per Variable")
plt.show()

### From these scores, it seems that 1, 12, 15 , 21, and 33 are the top 5 most relevant features.

### NOTE, THE FEATURE NUMBERS DO NOT MATCH BETWEEN THE SORTED GRAPH AND THE TEXT OUTPUT

# check metrics to see how dropping the lowest 7 relevant variables affected metrics
for name, model in zip(names, models):
    info = {'clf':name, 'data':'Charlotte Policing'}
    train_eval(model, X_train_fs, T_train, X_test_fs, T_test, info)

"""#### SequentialFeatureSelector-based feature selection (Wrapper Method)"""

import joblib
from sklearn.feature_selection import SequentialFeatureSelector as SFS

# Define Sequential Forward Selection (sfs)
# This is based on the cross-validation score of an unfitted estimator (LogReg)
sfs = SFS(LogisticRegression(),
           n_features_to_select=0.8,
           cv=3)

#Use SFS to select the top features (KNN and GB take too long, drop to Logreg)
sfs.fit(x_1, T_train)

# See selected variables (Driver_Race seems to be a relevant variable)
X_train.columns[sfs.get_support()]

# See unselected variables
X_train.columns[~sfs.get_support()]

# New DFs that will contain the undropped features (based on the sfs above)
X_train_res_sfs_drop = X_train.copy()[X_train.columns[sfs.get_support()]]
X_test_norm_sfs_drop = X_test.copy()[X_test.columns[sfs.get_support()]]

# check metrics to see how dropping the irrelevant variables 
for name, model in zip(names, models):
    info = {'clf':name, 'data':'Charlotte Policing'}
    train_eval(model, X_train_res_sfs_drop, T_train, X_test_norm_sfs_drop, T_test, info)

"""#### Hyperparameter Tuning (Grid Search)"""

from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
import numpy as np

pipe = Pipeline(steps=[('estimator', LogisticRegression())])

# Add a dict of estimator and estimator related parameters in this list
params_grid = [{
                'estimator':[LogisticRegression()],
                'estimator__penalty' : ['elasticnet', 'l2']
                },
                {
                'estimator': [GradientBoostingClassifier()],
                'estimator__learning_rate' : [0.15,0.1,0.05,0.01,0.005,0.001],
                'estimator__n_estimators' : [5,10,25,50,75]
                },
                {
                'estimator':[RandomForestClassifier()],
                'estimator__n_estimators':list(range(40,100,10)),
                'estimator__max_features': list(range(1,5,1)),
                'estimator__max_depth': list(range(3,6,1))
                },
                {
                'estimator': [GaussianNB()],
                 'estimator__var_smoothing':np.logspace(0,-9, num=100)
                }
              ]

grid = GridSearchCV(pipe, params_grid,cv=3,scoring='recall')
_ = grid.fit(X_train,T_train)

grid.best_params_

grid.best_score_

grid_y_train = grid.predict(X_train)
grid_y_test = grid.predict(X_test)

from sklearn.metrics import recall_score
recall_score(T_test, grid_y_test)

grid.cm = confusion_matrix(T_test, grid_y_test, labels=grid.classes_)
    grid.disp = ConfusionMatrixDisplay(confusion_matrix=grid.cm, display_labels=grid.classes_)

    grid.disp.plot()
    plt.show()

"""#### Hyperparameter Tuning (Randomized Search)"""

from sklearn.model_selection import RandomizedSearchCV
import random
from random import randint

pipe_rand = Pipeline(steps=[('estimator', LogisticRegression())])

# Add a dict of estimator and estimator related parameters in this list
params_grid_rand = [{
                'estimator':[LogisticRegression()],
                'estimator__penalty' : ['elasticnet', 'l2']
                },
                {
                'estimator': [GradientBoostingClassifier()],
                'estimator__learning_rate' : [round(random.uniform(.001,0.15),2)],
                'estimator__n_estimators' : [randint(5,75)]
                },
                {
                'estimator':[RandomForestClassifier()],
                'estimator__n_estimators':[randint(40,100)],
                'estimator__max_features': [randint(1,5)],
                'estimator__max_depth': [randint(3,6)]
                },
                {
                'estimator': [GaussianNB()],
                 'estimator__var_smoothing':[random.uniform(min(np.logspace(0,-9, num=100)),max(np.logspace(0,-9, num=100)))]
                }
              ]

grid_rand = RandomizedSearchCV(pipe_rand, params_grid_rand,cv=3,scoring='recall',n_iter=250)
_ = grid_rand.fit(X_train,T_train)

grid_rand.best_params_

grid_rand.best_score_

grid_rand_y_train = grid_rand.predict(X_train)
grid_rand_y_test = grid_rand.predict(X_test)

recall_score(T_test, grid_rand_y_test)

grid_rand.cm = confusion_matrix(T_test, grid_rand_y_test, labels=grid_rand.classes_)
    grid_rand.disp = ConfusionMatrixDisplay(confusion_matrix=grid_rand.cm, display_labels=grid_rand.classes_)

    grid_rand.disp.plot()
    plt.show()

"""## Code for looking at LogReg Coefficients"""

logreg = LogisticRegression(max_iter = 1000)

info = {'clf':'Logistic Regression', 'data':'Charlotte Policing'}

train_eval(logreg, X_train, T_train, X_test, T_test, info)

for index, val in enumerate(list(logreg.coef_[0])):
  print('Column: {} | Coefficient: {}'.format(X_train.columns[index], val))

"""## Attempt at Using P% Score"""

GB = GradientBoostingClassifier()
GB.fit(X_train, T_train)

from sklego.metrics import p_percent_score
p_score = p_percent_score('Driver_Race')(GB, X_train, T_train)
p_score

"""## Drawing Some P% Graphs with FairClassifier
Once we have finished hyper-tuning some models (excluding Fairness Classifiers) we can draw these graphs for the presentation. Essentially, these show the trade-off between different covariance thresholds and performance.
"""

from sklearn.metrics import accuracy_score, make_scorer, recall_score
from sklearn.model_selection import GridSearchCV
import warnings
import numpy as np
from sklego.metrics import p_percent_score

# Be careful, this takes 30 minutes.
fair_classifier = GridSearchCV(estimator=DemographicParityClassifier(sensitive_cols="Driver_Race",
                                                        covariance_threshold=0.5),
                               param_grid={"estimator__covariance_threshold":
                                           np.linspace(0.01, 1.00, 10)},
                               cv=3,
                               refit="accuracy_score",
                               return_train_score=True,
                               scoring={"p_percent_score": p_percent_score('Driver_Race'),
                                        "accuracy_score": make_scorer(accuracy_score),
                                        "recall_score":make_scorer(recall_score)})

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    fair_classifier.fit(X_train, T_train);

    pltr = (pd.DataFrame(fair_classifier.cv_results_)
            .set_index("param_estimator__covariance_threshold"))

logreg = LogisticRegression(max_iter = 1000)
# "col" not needed here since T_train is initialized with T_train, which only has 1 column. Thus, T_train is a Series.
logreg.fit(X_train, T_train)

p_score = p_percent_score('Driver_Race')(logreg, X_train, T_train)
acc_score = accuracy_score(logreg.predict(X_train), T_train)
recall_score = recall_score(logreg.predict(X_train), T_train)

pltr

plt.figure(figsize=(12, 3))
plt.subplot(121)
plt.plot(np.array(pltr.index), pltr['mean_test_p_percent_score'], label='fairclassifier')
plt.plot(np.linspace(0, 1, 2), [p_score for _ in range(2)], label='logistic-regression')
plt.xlabel("covariance threshold")
plt.legend()
plt.title("p% score")
plt.subplot(122)
plt.plot(np.array(pltr.index), pltr['mean_test_accuracy_score'], label='fairclassifier')
plt.plot(np.linspace(0, 1, 2), [acc_score for _ in range(2)], label='logistic-regression')
plt.xlabel("covariance threshold")
plt.legend()
plt.title("accuracy");

plt.figure(figsize=(12, 3))
plt.subplot(121)
plt.plot(np.array(pltr.index), pltr['mean_test_p_percent_score'], label='fairclassifier')
plt.plot(np.linspace(0, 1, 2), [p_score for _ in range(2)], label='logistic-regression')
plt.xlabel("covariance threshold")
plt.legend()
plt.title("p% score")
plt.subplot(122)
plt.plot(np.array(pltr.index), pltr['mean_test_recall_score'], label='fairclassifier')
plt.plot(np.linspace(0, 1, 2), [recall_score for _ in range(2)], label='logistic-regression')
plt.xlabel("covariance threshold")
plt.legend()
plt.title("recall");
