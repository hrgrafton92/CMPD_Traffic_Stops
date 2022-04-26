import pandas as pd
import numpy as np

stops = pd.read_csv("Raw_Data/Officer_Traffic_Stops (1).csv")
stops2 = pd.read_csv("Raw_Data/Officer_Traffic_Stops_2016-17.csv")

stops.head()

stops = stops.drop(['OBJECTID','GlobalID'],1)

stops2.head()

stops2 = stops2.drop(['ObjectID','CreationDate','Creator','EditDate','Editor'],1)

stops = stops.append(stops2, ignore_index=True)

stops

print(stops.isna().any())
print(stops.dtypes)

#Checking for any typo's during data entry. Potential variations of the same input.
#No typo's. 48 entries for each month of 2020-2021, and 2016-2017.

stops.Month_of_Stop.unique()

# convert the 'Date' column to datetime format
import datetime as dt
isinstance(stops['Month_of_Stop'], dt.date) # False

stops['Month_of_Stop'] = stops['Month_of_Stop'].astype('datetime64[ns]')
stops['Month_of_Stop'] = pd.to_datetime(stops['Month_of_Stop'], format='%y%m%d')

#Checking for any typo's during data entry. Potential variations of the same input.
#No typo's found.

stops.Reason_for_Stop.unique()

#Checking for any typo's during data entry. Potential variations of the same input.
#No typo's found.

stops.Officer_Race.unique()

#Checking for any typo's during data entry. Potential variations of the same input.
#No typo's found.

stops.Officer_Gender.unique()

#Checking for any typo's during data entry. Potential variations of the same input.
#No typo's found.

stops.Officer_Years_of_Service.unique()

#Checking for any typo's during data entry. Potential variations of the same input.
#No typo's found.
#Driver_Race options are not the same as Officer_Race options. Officers have 'Hispanic/Latino option, as well as a mixed race option.'

stops.Driver_Race.unique()

#Checking for any typo's during data entry. Potential variations of the same input.
#No typo's found.

stops.Driver_Ethnicity.unique()

#Checking for any typo's during data entry. Potential variations of the same input.
#No typo's found.

stops.Driver_Gender.unique()

#Checking for all ages
#Ages below 15 (earliest age eligible for driver's permit) are recorded. Typo or someone illegally driving underage? Ages 10-14 represented
#Keep in dataset or remove? 68 observations in this Driver_Age range

a = stops.Driver_Age.unique()
sorted(a)
stops[stops['Driver_Age']<15]

#reason for stop of drivers below drivers permit age
#reasons do not appear to be specifically related to age. Reasons are not exclusive to officer observing a young driver behind the wheel.
#Remove?
young = stops[stops["Driver_Age"] <15]
print(young.groupby('Reason_for_Stop').count())
print(young.groupby('Result_of_Stop').count())

stops = stops[stops["Driver_Age"]>14]

#Checking for any typo's during data entry. Potential variations of the same input.
#No typo's found.

stops.Was_a_Search_Conducted.unique()

#Checking for any typo's during data entry. Potential variations of the same input.
#No typo's found.

stops.Result_of_Stop.unique()

#Checking for any typo's during data entry. Potential variations of the same input.
#No typo's found.
#Contains NULL values. For location analysis should remove. For aggregate demographic analysis is helpful.
#Create 2nd version of the dataset??

print(stops.CMPD_Division.unique())
stops['CMPD_Division'].isna().sum()

#Setting binary variables

from sklearn.preprocessing import LabelEncoder
label_encoder = LabelEncoder()
stops['Officer_Gender'] = label_encoder.fit_transform(stops['Officer_Gender']) #0 female, 1 male
stops['Driver_Ethnicity'] = label_encoder.fit_transform(stops['Driver_Ethnicity']) #0 Hispanic, 1 Non-Hispanic
stops['Driver_Gender'] = label_encoder.fit_transform(stops['Driver_Gender']) #0 female, 1 male
stops['Was_a_Search_Conducted'] = label_encoder.fit_transform(stops['Was_a_Search_Conducted']) # 0 yes, 1 no

stops

# Grouping Result_of_Stop into fewer categories. Combing 'No Action Taken', 'Verbal Warning', and 'Written Warning'
stops['Outcome'] = pd.np.where(stops.Result_of_Stop.str.contains("Arrest"), "Arrest",
                   pd.np.where(stops.Result_of_Stop.str.contains("Citation Issued"), "Citation","Warning/No Action"))

stops['Arrest'] = pd.np.where(stops.Result_of_Stop.str.contains("Arrest"), "Arrest","Other")
stops

# Grouping Officer_Race into same racial groupings as Driver_Age to be able to determine if they match

stops['Officer_Race'] = pd.np.where(stops.Officer_Race.str.contains("White"), "White",
                pd.np.where(stops.Officer_Race.str.contains("Black/African American"), "Black",
                pd.np.where(stops.Officer_Race.str.contains("Asian / Pacific Islander"), "Asian",
                pd.np.where(stops.Officer_Race.str.contains("American Indian/Alaska Native"),"Native American","Other/Unknown"))))

stops['Racial_Match'] = np.where(stops.Driver_Race == stops.Officer_Race,1,0)

stops

# all years dataset, and separating 2016-2017 from 2020-2021

stops_all = stops

stops_2016 = stops[stops['Month_of_Stop'] < '2018-01-01']

stops_2020 = stops[stops['Month_of_Stop'] > '2018-01-01']

stops_all_trimmed = stops_all.dropna()

stops_2016_trimmed = stops_2016.dropna()

stops_2020_trimmed = stops_2020.dropna()

# compare proportion of trimmed rows to the total set along each variable.
# Ensure there is a normal distribution of the missing CMPD divisions along other variables

missing = stops_2020.loc[stops_2020.isnull().any(axis=1)]
print(missing.groupby('Racial_Match').count())
print(stops_2020.groupby('Racial_Match').count())

from sklearn.model_selection import train_test_split
stops_2020_train, stops_2020_test = train_test_split(stops_2020_trimmed,test_size = .25, random_state=101)

print(stops_2020_train)
print(stops_2020_test)

# export to csv. Versions with all stops, and separated by year grouping. 
# Then the same versions duplicated but with missing CMPD Division entries removed

#only using 2020-2021 traffic stops ultimately

# 2020-2021 with NAs removed
#stops_2020_trimmed.to_csv('stops_2020_trimmed.csv')
#stops_2020_train.to_csv('/stops_2020_train.csv')
#stops_2020_test.to_csv('/stops_2020_test.csv')

