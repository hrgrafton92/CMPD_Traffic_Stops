library(tidyverse)
library(scales)
library(sf)
library(viridis)
library(readxl)

df <- read_csv("Data/Officer_Traffic_Stops.csv")

glimpse(df)

#13 CMPD Divisions
unique(df$CMPD_Division)
n_distinct(df$CMPD_Division)


#4012 stops did not have any CMPD 
df %>%
  group_by(CMPD_Division) %>%
  summarize( n())


##Month of Stop to Year
df$year <- substr(df$Month_of_Stop, 1, 4)
df$year <- as.numeric(df$year)

glimpse(df)

cmpd <- st_read("./Data/CMPD_Police_Divisions.shp")


## CLT - Zip Codes - Avg.Household.Income - Population 
##source: https://www.oneclthealth.org/?module=demographicdata&controller=index&action=index&id=29820&sectionId=936
##https://www.unitedstateszipcodes.org/28134/
##https://www2.census.gov/geo/tiger/TIGER2020/ZCTA520/

clt_demg <-read_excel("Data/cmpd_demg.xlsx") 
glimpse(clt_demg)



# ## demography of each CMPD
# 
# cmpd_demog <- clt_inc %>%
#   group_by(CMPD_Division) %>%
#   summarise(total_pop_21  = sum(`21_pop`), 
#             weighed_avg_inc_21 = sum(`21_avg_h_hld_inc`)/sum(`21_pop`),
#             weighed_med_inc_21 = sum(`21_med_h_hld_inc`)/sum(`21_pop`),
#             total_pop_20  = sum(`20_pop`),
#             weighed_avg_inc_20 = sum(`20_avg_h_hld_inc`)/sum(`20_pop`),
#             weighed_med_inc_20 = sum(`20_med_h_hld_inc`)/sum(`20_pop`)
#             )
# glimpse(cmpd_demog)


cmpd_df <- cmpd %>%
  mutate(CMPD_Division = as.character(DNAME)) %>%
  inner_join(count(df, CMPD_Division, year), by = c("CMPD_Division")) %>%
  left_join(clt_demg, by = c("CMPD_Division", "year"))

#  inner_join(cmpd_demog, by = "CMPD_Division")

glimpse(df)

glimpse(cmpd_df)

#view(cmpd_df)


##1. A map showing total  Stops  per year 

cmpd_stop <- cmpd_df %>%
  ggplot()+
  geom_sf(aes(fill = n))+
  #ggtitle("CMPD Divisions")+
  labs(title = "Stops for each CMPD Divisions")+
  theme_bw()

cmpd_stop



##2 A map showing cmpd with fill = Pop or Med income or Avg income

#cmpd_df <- read_csv("Data/cmpd_df.csv")
  
cmpd_med_inc <- cmpd_df %>%
  ggplot()+
  geom_sf(aes(fill = cmpd_df$total_pop_21))+
  #ggtitle("CMPD Divisions")+
  labs(title = "Median income 2021 for CMPD Divisions")+
  theme_bw()

cmpd_med_inc

glimpse(cmpd_df)

d1 <- cmpd_df %>%
  filter(CMPD_Division == "Providence")

glipmse
  
