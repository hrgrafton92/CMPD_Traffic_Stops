# Predicting Charlotte Traffic Stop Outcomes
This project was the result of two courses in the Data Science & Business Analytics master's program at UNC-Charlotte. The modeling and streamlit app were completed in Minwoo Lee's Applied Machine Learning class alongside [Mitchell Jones](https://github.com/mitchell-jones), [Srikar Vavilala](https://github.com/SrikarVavilala), Jordan Register, and Marianna Shaver. The R Shiny app was created in Chase Romano's Visual Analytics class alongside [Joseph Burnes](https://github.com/joeburns91) and [Syed Muhammad Suffwan](https://github.com/ss03516). The tableau dashboard is my own.

## Data Source
Data is available at the [Charlotte Data Portal](https://data.charlottenc.gov/datasets/officer-traffic-stops/explore).

## Research Questions
1. Which of the **general attributes** correlate the most with the **outcome of the traffic stop** (i.e. search conducted, verbal warning, written warning, citation issued, no action, arrest).
2. What **driver attributes** (race, ethnicity, gender, age) correlate the most with the **outcome of the traffic stop**?
3. What **officer attributes** (race, gender, years of service) correlate the most with the **outcome of the traffic stop**?

## Steps and Approaches
### Preprocessing/clean the dataset: 
- Check for missing values
- Consistency (spelling, etc.)
- Skewness → normalization
### Identify variables to be used. EDA
### Identify most appropriate models to use
- Multi class prediction. 5 different outcomes.
- Binary. Search conducted or not
- Sklearn fairness metrics
### Analysis
- Naive/Gaussian Bayes
- Decision Tree/Random Forest
- Logistic regression
- Parameter tuning

All modeling efforts can be found within the Preprocessing_and_Modeling folder

### Create Streamlit App
Streamlit app to make the dataset easily accessible for anyone. Preliminary EDA efforts are made available [here](https://share.streamlit.io/hrgrafton92/cmpd_traffic_stops/main/Streamlit/CMPD_Traffic_Stops.py). Source code and files are located in Streamlit folder to be able to run the app from an IDE rather than going to the link provided.

### Create R Shiny App
R Shiny app to make the dataset easily accessible for anyone [here](https://grafton-shiny.shinyapps.io/CMPD_Traffic_Stops_Final/). The app contains EDA insights for the dataset as well as comparing the location of the traffic stop to local population demographics and income. Source code and files for the R Project are located in R_Shiny folder to be able to run the app from Rstudio rather than going to the link provided. To do so,
- Download all items in the R_Shiny folder
- Open CMPD_Traffic_Stops_Shiny.R
- Click "Run App" in the top-right corner of the code panel

### Create Tableau dashboard
Tableau Public dashboard to concisely show EDA on the dataset, while also identifying main trends present within the data. The dashboard can be found [here](https://public.tableau.com/app/profile/harley.grafton2858/viz/CMPDTrafficStops/HomeDashboard)


## Findings
Once finished, findings go here.

## Import Endnotes
We realize that by analyzing this dataset, we could shed light on a potentially controversial topic, that is, how the race/ethnicity/gender of the driver/officier can help to predict the outcome of a traffic stop. 

If this is a finding, it should not be used to guide police targeting, but rather to illuminate bias in traffic stops.  Note that being able to predict the outcome of a traffic stop based on race, ethnicity or gender is inherently unethical/discriminatory. Ideally, traffic stop outcomes based on these characteristics should be proportional to the demographic population of the area under observation.  

Regardless of our findings, we would like to be explicit about the fact that none of our findings are causal. Rather they shed light on correlations in the data that may be used to dismantle bias in policing. 
