library(shiny)
library(shinyWidgets)
library(dplyr)
library(ggplot2)
library(hrbrthemes)
library(CGPfunctions)
library(stringr)
library(tidyverse)
library(scales)
library(sf) 
library(viridis) 
library(readxl)
library(plotly)
library(ggthemes)
library(RColorBrewer)

##Data loading
cmpd <- st_read("./Data/CMPD_Police_Divisions.shp")
df <- read_csv("Data/Officer_Traffic_Stops.csv")
clt_demg <-read_excel("Data/cmpd_demg.xlsx") 
df_pop <- read_csv("./Data/stops_pop.csv")


##data prep
df$year <- substr(df$Month_of_Stop, 1, 4)
df$year <- as.numeric(df$year)
df$Driver_Race = factor(df$Driver_Race, levels=c('Other/Unknown','Native American','Asian','White','Black'))

myColors <- brewer.pal(5,"Set2")
names(myColors) <- levels(df$Driver_Race)
colscale <- scale_colour_manual(name = "grp",values = myColors)



##Creating Final data to be used for Tab 2
cmpd_df <- cmpd %>%
  mutate(CMPD_Division = as.character(DNAME)) %>%
  inner_join(count(df, CMPD_Division, year), by = c("CMPD_Division")) %>%
  inner_join(clt_demg, by = c("CMPD_Division", "year"))


# Define UI for application
ui <- fluidPage(

    # Application title
    titlePanel("CMPD Traffic Stops"),
    br(),
    fluidRow(
      tabsetPanel(
        
#---------------------------------------------HOME PAGE----------------------------------------------------------------        
        tabPanel("Home Page",
          sidebarLayout(
            sidebarPanel(
            h2("Traffic Stops in Charlotte, NC from 2020-2021."),
            br(),
            p('The city of Charlotte has made police traffic stops for this two year span available at',a("Charlotte Data Portal. ", href="https://data.charlottenc.gov/"), 'The available tabs in this app provide different angles from which to view the dataset. While not implying any causation, there are observations along racial lines that can be drawn from the data about policing practices.')
            ),
            mainPanel(
            img(src = "pulled_over_green.png", width="70%", height="70%",style= 'position:flex;left:65px;'),
            br(),
            br(),
            br(),
            br(),
            strong("2",style= 'position:fixed;left:38%;color:#6b9b4a;font-size:200%;'),
            strong("13",style= 'position:fixed;left:52%;color:#6b9b4a;font-size:200%;'),
            strong("139,524",style= 'position:fixed;left:64%;color:#6b9b4a;font-size:200%;'),
            strong("7,892",style= 'position:fixed;left:80%;color:#6b9b4a;font-size:200%;'),
            br(),
            br(),
            p("Years of", br()," Traffic Stops",style="position:fixed;left:35%;"),
            p("CMPD",br()," Divisions",style="position:fixed;left:50%;"),
            p("Total", br()," Traffic Stops",style="position:fixed;left:65%;"),
            p("Total", br()," Vehicle Searches",style="position:fixed;left:80%;"),
            br(),
            br(),
            br(),
            img(src = "calendar_transparent_2.png", width="8%", height="8%",style= 'position:fixed;left:35%;'),
            img(src = "cmpd_transparent2.png", width="8%", height="8%",style= 'position:fixed;left:50%;'),
            img(src = "siren_transparent.png", width="8%", height="8%",style= 'position:fixed;left:65%;'),
            img(src = "search_transparent.png", width="8%", height="7%",style= 'position:fixed;left:80%;')
            )
          )
        ),

#---------------------------------------------------------------STOPS BY DIVISION---------------------------------------
        tabPanel("Traffic Stops By CMPD Division",
          sidebarLayout(
            sidebarPanel(  
              h4("Explore the racial breakdown of traffic stops by division"),
              p("Select one race/ethnicity from the dropdown menu below"),
              hr(),
              selectInput("Map_Race", "Race/Ethnicity", choices=c("White", "Black", "Native American","Asian"),
                          selected = "Black",
                          multiple = FALSE),
              hr(),
              p("Select Year:"),
              selectInput("map_years_selected", "Year", choices = c('2020','2021'),
                          selected = "2020",
                          multiple = FALSE),
              hr(),
              p("Here percent difference represents the difference in percentage of stops as compared to the percentage of the population. A positive percentage
                represents that race is stopped at higher rate than their percentage of the overall population. It is important to note that there are many factors
                that cause this, and further research would be required to determine cause.")
            ),
            mainPanel(fluidRow(plotlyOutput("map", height = "650px", width = "800px")))
          )
        ),

#--------------------------------------------------------------STOPS BY INCOME-------------------------------------------
        tabPanel("Traffic Stops V.S. Income",
          sidebarLayout(
            sidebarPanel(
              h3("Explore the relationship between Demographics & Traffic Stops"),
              br(),
              p("We aim to explore any siginificant correlations between the demographics
                (Population, Average Household Income, Median Household Income) of 
                a CMPD division and the totoal number of stops over the years."),
              radioButtons("year", "Choose year:",
                           choiceNames = list(
                             2020, 2021
                           ),
                           choiceValues = list(
                             2020, 2021
                           ),
                           selected = NULL),
              selectInput(inputId = "factor", label = "Choose Demographic Factor",
                          choices = list( 'Population', 'Average_Household_Income', 'Median_Household_Income'),
                          selected = NULL),
              
              #Action button 'Rerun'
              actionButton(inputId = 'Analyse',
                           label = 'Analyse'
              ),
              br(),
              br(),
              h4("Analysis"),
              br(),
              p("Over the past two years, we can notice that there is inverse relation with traffic stops against average or median household income except for South. 
              We notice that even though North is not as populated as other divisions, we still have second highest number of stops in this division. The story gets completed when 
              we compare the stops in North against the mean & median household income; the division has one of the lowest income.
                Similar trend can be observed for Independence as well and in Steele Creek we 
                can observe that even though it has relatively higher population 
                but just because it has higher income values; we observe least amount of stops here."),
              br(),
              br(),
              p('Note:',br(),'The demographic data was manually collected and consolidated for 
                each CMPD Division using zip codes so there is a chance
                of discrepency in conclusions. Providence Division is missing because we were unable to collect zips in that area.',
                br(), br(), 'Sources:',a("Census", href="https://www2.census.gov/geo/tiger/TIGER2020/ZCTA520/"), ', ',
                a("OneCLTHealth", href= "https://www.oneclthealth.org/?module=demographicdata&controller=index&action=index&id=29820&sectionId=936")
              )
              
            ),
            mainPanel(
              br(),
              plotOutput(outputId = "cmpd_stop"),
              plotOutput(outputId = "cmpd_inc")
            )
          )
        ),

#-------------------------------------------------------------SEARCHES & OUTCOMES----------------------------------------
        tabPanel("Vehicle Searches & Outcomes",
            div(
            style = "display:flex; align-items:flex-start",
            wellPanel( #~~ Sidebar ~~#
            style = "overflow-y: auto; position:fixed; width:300px; top:125px; bottom:0",
          #sidebarLayout(
            #sidebarPanel(
              h4("Explore which traffic stops also involved a vehicle search."),
              br(),
              p("We have seen on the earlier tabs who, and where, experience the most traffic stops in Charlotte, NC. What outcomes do drivers experience after being stopped though? We focused on vehicle searches as this is a simpler designation (yes/no) than 5 different outcomes of Arrest,Citation, Written Warning, Verbal Warning, and No Action. The most serious outcome, Arrest, is also more likely when there is also a vehicle search."),
              br(),
              p("Select one or more driver races to view."),
              pickerInput("tab.3.driver.race","Driver Race",selected="Black", 
                                               choices=c("White", "Black", "Native American","Asian","Other/Unknown"), 
                                               options = list(`actions-box` = TRUE),
                                               multiple = T),
              radioButtons("tab.3.count.percent", "How would you like to view the data?",
                           choices = c("Counts", "Percentages")),
              pickerInput("years_selected","Select one or more years to view traffic stops for:",
                           selected = '2020',
                           choices = c('2020','2021'),
                           multiple=T)
              
              
            )),
          div(
            style = "flex-grow:1; resize:horizontal; overflow: hidden; position:relative; margin-left: 310px",
            #mainPanel(
            plotOutput("searches.results",height="600px",width="600px"),
            br(),
            br(),
            plotOutput("search.race",height = "600px",width="600px"),
            br(),
            br(),
            pickerInput('graph.choice',"Select another variable to view vehicle searches by:",
                        selected = 'Driver Ethnicity',
                        choices = c('Driver Ethnicity', 'Driver Gender', 'Driver Age'),
                        multiple = F),
            br(),
            plotOutput('graph.selected',height='600px',width='600px')
            )
          ),

#------------------------------------------------------------OFFICER INFO--------------------------------------------------
        tabPanel("Officer Information",
          sidebarLayout(
            sidebarPanel(
              h4("Exploring How Officer Experience affects Stops and Searches"),
              br(),
              p("After exploring the trends in traffic stops and vehicle searches, let's briefly look at who is committing the stops and searches in the first place. Initial appearances suggest that as officers become more experienced, their stops and searches by driver race better represent the racial makeup of Charlotte overall."),
              br(),
              br(),
              p("Select a bindwidth"),
              pickerInput('officer_bin_width',"Officer Bin Width for Years of Service",selected=5,
                          choices = c(1,2,3,4,5,6,7,8,9,10)),
              
              radioButtons("tab.4.count.percent", "What would you like to display?",
                           choices = c("Counts", "Percentages"))
            ),
            mainPanel(
              plotOutput("officer.service",height='600px',width='600px')
            )
          )    
        ),

#------------------------------------------------------------ABOUT AUTHORS--------------------------------------------------
        tabPanel("About Authors",
            column(8,
                   h3("Contributing developers to this app:")),
            br(),
            br(),
            br(),
            column(12,
            p("This app was developed by Harley Grafton, Joseph Burnes, and Syed Muhammad Suffwan as part of the Visual Analytics course taught by Chase Romano at the University of North Carolina at Charlotte through the Data Science and Business Analytics MS program.")
            ,
              br(),
              HTML('<a href="https://github.com/hrgrafton92/CMPD_Traffic_Stops">View Harley\'s GitHub</a>'),
              br(),
              HTML('<a href="https://www.linkedin.com/in/harley-grafton-284a9ab8/">View Harley\'s LinkedIn</a>'),
              br(),
              br(),
              HTML('<a href="https://github.com/joeburns91">View Joseph\'s GitHub</a>'),
              br(),
              HTML('<a href="https://www.linkedin.com/in/joeburns91/">View Joseph\'s LinkedIn</a>'),
              br(),
              br(),
              HTML('<a href="https://github.com/ss03516">View Syed\'s GitHub</a>'),
              br(),
              HTML('<a href="https://www.linkedin.com/in/syed-muhammad-suffwan-58599a14b/">View Syed\'s LinkedIn</a>')
            )
        )
        )
      )
    )
#--------------------------------------------------------------------------------------------------------------------------

# Define server logic
server <- function(input, output) {
#---------------------------------------------------Traffic Stops vs Income------------------------------
  observeEvent(input$Analyse, {
    
    
    ct <- cmpd_df %>%
      filter(year == input$year) %>%
      ggplot()+
      geom_sf(aes(fill = n))+
      ggtitle(paste("Total Traffic Stops Per CMPD Division In", input$year))+
      theme_bw() +
      labs(fill='Total Stops') +
      scale_fill_viridis("Traffic Stops", labels = scales::comma) +
      theme(plot.title = element_text(face = "bold", size = rel(1.5)),
            axis.text.x=element_blank(),
            axis.text.y=element_blank(),
            axis.ticks.x=element_blank(),
            axis.ticks.y=element_blank(),
            plot.background = element_blank(),
            panel.grid.major = element_blank(),
            panel.grid.minor = element_blank(),
            panel.border = element_blank(),
            panel.background = element_blank()
      )
    
    output$cmpd_stop <- renderPlot({
      
      ct
    })
    
    dg <- cmpd_df %>%
      filter(year == input$year) %>%
      ggplot()+
      geom_sf(aes_string(fill = input$factor))+
      theme_bw()+
      ggtitle(paste(input$factor,"In",input$year , "Per CMPD Division"))+
      scale_fill_viridis(input$factor, labels = scales::comma) +
      theme(plot.title = element_text(face = "bold", size = rel(1.5)),
            axis.text.x=element_blank(),
            axis.text.y=element_blank(),
            axis.ticks.x=element_blank(),
            axis.ticks.y=element_blank(),
            plot.background = element_blank(),
            panel.grid.major = element_blank(),
            panel.grid.minor = element_blank(),
            panel.border = element_blank(),
            panel.background = element_blank()
            
      )
    
    output$cmpd_inc <- renderPlot({
      
      dg
    })
  })
  
  
  
  
#--------------------------------------------------------SEARCHES & OUTCOMES------------------------------------------------

  df_result.race <- reactive({
    df %>% filter(Driver_Race %in% input$tab.3.driver.race)
  })
  
  result_percent <- reactive({
    df_result.race() %>% filter(year %in% input$years_selected) %>%
        count(Was_a_Search_Conducted,Result_of_Stop) %>%
        group_by(Was_a_Search_Conducted) %>%
        mutate(freq = n / sum(n))
  })


  output$searches.results <- renderPlot({
    if(input$tab.3.count.percent== 'Percentages') {
      result_percent() %>%
        ggplot(aes(Was_a_Search_Conducted,freq,fill=Result_of_Stop))+
        geom_bar(stat='identity',position='fill')+
        scale_fill_manual(values=c('Arrest'= "#AC8181",
                                 'Citation Issued'= "#CFCECA",
                                 'No Action Taken'= "#99ced3",
                                 "Verbal Warning"="#C9A959",
                                 "Written Warning"="#253D5B"))+
        theme_minimal()+
        xlab("Was a Search Conducted")+
        ylab("Percent of Stops")+
        ggtitle("Result of Traffic Stops When 
A Vehicle Search Was (Or Was Not) Conducted")+
        theme(axis.title.x = element_text(size = 15),
              axis.text.x = element_text(size=12),
              axis.title.y = element_text(size=15),
              axis.text.y = element_text(size=12),
              plot.title = element_text(size=18))
    }
    else if (input$tab.3.count.percent == 'Counts'){
      result_percent() %>%
        ggplot(aes(Was_a_Search_Conducted,n,fill=Result_of_Stop))+
        geom_bar(stat='identity')+
        scale_fill_manual(values=c('Arrest'= "#AC8181",
                                   'Citation Issued'= "#CFCECA",
                                   'No Action Taken'= "#99ced3",
                                   "Verbal Warning"="#C9A959",
                                   "Written Warning"="#253D5B"))+
        theme_minimal()+
        theme(axis.title.x = element_text(size = 15),
              axis.text.x = element_text(size=12),
              axis.title.y = element_text(size=15),
              axis.text.y = element_text(size=12),
              plot.title = element_text(size=18))+
        xlab("Was a Search Conducted")+
        ylab("Number of Stops")+
        ggtitle("Result of Traffic Stops When 
A Vehicle Search Was (Or Was Not) Conducted")
    }
  })
  
  

#Plot 2 
  race_percent <- reactive({
    if(input$tab.3.count.percent == "Percentages") {
      df %>% filter(year %in% input$years_selected) %>%
        count(Was_a_Search_Conducted,Driver_Race) %>%
        group_by(Driver_Race) %>%
        mutate(freq = n / sum(n)) %>%
        filter(Was_a_Search_Conducted=="Yes")
    } else if(input$tab.3.count.percent == "Counts") {
      df %>% filter(year %in% input$years_selected) %>%
        count(Was_a_Search_Conducted,Driver_Race) %>%
        group_by(Driver_Race) %>%
        mutate(freq = sum(n)) %>%
        filter(Was_a_Search_Conducted=="Yes")
    }
  })
  
  df_search.race <- reactive({
    race_percent() %>% filter(Driver_Race %in% input$tab.3.driver.race)
  })
  
  
  output$search.race <- renderPlot({
    if(input$tab.3.count.percent== 'Percentages'){
      df_search.race() %>%
      ggplot(aes(reorder(Driver_Race,-freq),freq,fill=Driver_Race))+
      geom_bar(stat='identity')+
      theme(legend.position="none")+
      scale_fill_manual(values=c('White'="#800000FF",
                                 'Black'= "#ADB17DFF",
                                 'Asian'="#5B8FA8FF",
                                 "Native American"="#725663FF",
                                 "Other/Unknown"="#D49464FF"))+
      theme_minimal()+
      theme(legend.position = "none")+
      xlab("Driver Race")+
      ylab("Percent Searched")+
      ggtitle("Percent of Stopped Driver's Who Had Their Vehicle Searched 
By Race")+
        theme(axis.title.x = element_text(size = 15),
              axis.text.x = element_text(size=12),
              axis.title.y = element_text(size=15),
              axis.text.y = element_text(size=12),
              plot.title = element_text(size=18))
    }
    else if(input$tab.3.count.percent== 'Counts'){
      df_search.race() %>%
        ggplot(aes(reorder(Driver_Race,-freq),freq,fill=Driver_Race))+
        geom_bar(stat='identity')+
        theme(legend.position="none")+
        scale_fill_manual(values=c('White'="#800000FF",
                                   'Black'= "#ADB17DFF",
                                   'Asian'="#5B8FA8FF",
                                   "Native American"="#725663FF",
                                   "Other/Unknown"="#D49464FF"))+
        theme_minimal()+
        theme(legend.position = "none")+
        xlab("Driver Race")+
        ylab("Numbers of Vehicles Searched")+
        ggtitle("Count of Stopped Driver's Who Had Their Vehicle Searched 
By Race")+
        theme(axis.title.x = element_text(size = 15),
              axis.text.x = element_text(size=12),
              axis.title.y = element_text(size=15),
              axis.text.y = element_text(size=12),
              plot.title = element_text(size=18))
    }
  })
    
  #Plot 3
  choice <- reactive({
    df %>% filter(Was_a_Search_Conducted=='Yes') %>%
      filter(Driver_Race %in% input$tab.3.driver.race) %>%
      filter(year %in% input$years_selected)
  })
  
  output$graph.selected <- renderPlot({
      if (input$graph.choice=='Driver Ethnicity'){
        choice() %>% count(Driver_Ethnicity,Was_a_Search_Conducted) %>%
        ggplot(aes(Driver_Ethnicity,n))+
        geom_bar(stat='identity',fill='#056879')+
        theme_minimal()+
        xlab("Driver Ethnicity")+
        ylab("Number of Searches")+
        ggtitle("Vehicle Searches By Driver Ethnicity")+
          theme(axis.title.x = element_text(size = 15),
                axis.text.x = element_text(size=12),
                axis.title.y = element_text(size=15),
                axis.text.y = element_text(size=12),
                plot.title = element_text(size=18))
      } else if(input$graph.choice=='Driver Gender'){
        choice() %>% count(Driver_Gender,Was_a_Search_Conducted) %>%
          ggplot(aes(Driver_Gender,n))+
          geom_bar(stat='identity',fill='#056879')+
          theme_minimal()+
          xlab("Driver Gender")+
          ylab("Number of Searches")+
          ggtitle("Vehicle Searches By Driver Gender")+
          theme(axis.title.x = element_text(size = 15),
                axis.text.x = element_text(size=12),
                axis.title.y = element_text(size=15),
                axis.text.y = element_text(size=12),
                plot.title = element_text(size=18))
      } else if(input$graph.choice=='Driver Age'){
        choice() %>%
          ggplot(aes(Driver_Age))+
          geom_histogram(binwidth=5,fill='#056879')+
          theme_minimal()+
          xlab("Driver Age")+
          ylab("Number of Searches")+
          ggtitle("Vehicle Searches By Driver Age")+
          theme(axis.title.x = element_text(size = 15),
                 axis.text.x = element_text(size=12),
                 axis.title.y = element_text(size=15),
                 axis.text.y = element_text(size=12),
                 plot.title = element_text(size=18))
      }
  })
#----------------------------------------------Officer Info -----------------------------------------
  
  bin_width <- reactive({
   as.numeric(input$officer_bin_width)
  })

  officer.years <- reactive({
    df %>% mutate(new_service = (df$Officer_Years_of_Service %/% bin_width()) * 4)
  })
  
  officer.percent <- reactive({
    officer.years() %>% filter(year %in% input$years_selected) %>%
      count(new_service,Driver_Race) %>%
      group_by(new_service) %>%
      mutate(freq = n / sum(n))
  })
  
  
  output$officer.service <- renderPlot({
    if(input$tab.4.count.percent== 'Percentages') {
      officer.percent() %>%
        ggplot(aes(new_service,freq,fill=Driver_Race))+
        geom_bar(stat='identity',position='fill')+
        scale_fill_manual(values=c('White'="#800000FF",
                                   'Black'= "#ADB17DFF",
                                   'Asian'="#5B8FA8FF",
                                   "Native American"="#725663FF",
                                   "Other/Unknown"="#D49464FF"))+
        theme_minimal()+
        xlab("Officer Years of Service")+
        ylab("Percent of Searches")+
        ggtitle("Percent Of Driver Race Searched By 
Each Grouping Of Officer Years Of Service")+
        theme(axis.title.x = element_text(size = 15),
              axis.text.x = element_text(size=12),
              axis.title.y = element_text(size=15),
              axis.text.y = element_text(size=12),
              plot.title = element_text(size=18))
    }
    else if (input$tab.4.count.percent == 'Counts'){
      officer.percent() %>%
        ggplot(aes(new_service,n,fill=Driver_Race))+
        geom_bar(stat='identity')+
        scale_fill_manual(values=c('White'="#800000FF",
                                  'Black'= "#ADB17DFF",
                                  'Asian'="#5B8FA8FF",
                                  "Native American"="#725663FF",
                                  "Other/Unknown"="#D49464FF"))+
        theme_minimal()+
        xlab("Officer Years of Service")+
        ylab("Number of Searches")+
        ggtitle("Count Of Vehicle Searches Of Driver Race By 
Each Grouping Of Officer Years Of Service")+
        theme(axis.title.x = element_text(size = 15),
              axis.text.x = element_text(size=12),
              axis.title.y = element_text(size=15),
              axis.text.y = element_text(size=12),
              plot.title = element_text(size=18))
    }
  })

  
  
  
  #------------------MAP-----------------------------------------------------------------
  
  ggplot(cmpd) +
    geom_sf(aes(fill=DNAME), show.title = "CMPD Divisions")+theme_bw()
  labs(title = "CMPD Divisions")
  
  cmpd_chloropleth <- cmpd %>% 
    mutate(CMPD_Division = as.character(DNAME))
  
  cmpd_map <- merge(x=cmpd_chloropleth, y= df_pop[, c("driver_race_clean","year","pct_difference","CMPD_Division")],by = "CMPD_Division", all.x = TRUE)
  
  #----Reactive function to select year
  map_selected_year <- reactive({ input$map_years_selected })
  
  #----Reactive dataframe for race and year to be used in the map
  cmpd_map_final <- reactive({
    cmpd_map %>% filter(driver_race_clean == input$Map_Race
                        , year == map_selected_year()
    )
  })
  
  output$map <- renderPlotly({
    map_plot <-
    ggplot(cmpd_map_final()) +
      geom_sf(aes(fill=pct_difference))+
      scale_fill_viridis(direction = -1) + 
      theme_map()
    labs(title = "CMPD Divisions")
    map_plot
  })

}

# Run the application 
shinyApp(ui = ui, server = server)
