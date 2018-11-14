

# Problem
 
As defined in https://github.com/InsightDataScience/h1b_statistics:

"A newspaper editor was researching immigration data trends on H1B(H-1B, H-1B1, E-3) visa application processing over the past years, trying to identify the occupations and states with the most number of approved H1B visas. She has found statistics available from the US Department of Labor and its [Office of Foreign Labor Certification Performance Data](https://www.foreignlaborcert.doleta.gov/performancedata.cfm#dis). But while there are ready-made reports for [2018](https://www.foreignlaborcert.doleta.gov/pdf/PerformanceData/2018/H-1B_Selected_Statistics_FY2018_Q4.pdf) and [2017](https://www.foreignlaborcert.doleta.gov/pdf/PerformanceData/2017/H-1B_Selected_Statistics_FY2017.pdf), the site doesn’t have them for past years."

This python 3 code aims to solve the problem and provides report for any year with available data. The input takes the form of .csv files downloaded from the Google drive [folder](https://drive.google.com/drive/folders/1Nti6ClUfibsXSQw5PUIWfVGSIrpuwyxf?usp=sharing). The outputs are two files under the output folder:

* `top_10_occupations.txt`: Top 10 occupations for certified visa applications
* `top_10_states.txt`: Top 10 states for certified visa applications

As stated in https://github.com/InsightDataScience/h1b_statistic:

"Each line holds one record and each field on each line is separated by a semicolon (;).

Each line of the `top_10_occupations.txt` file should contain these fields in this order:
1. __`TOP_OCCUPATIONS`__: Use the occupation name associated with an application's Standard Occupational Classification (SOC) code
2. __`NUMBER_CERTIFIED_APPLICATIONS`__: Number of applications that have been certified for that occupation. An application is considered certified if it has a case status of `Certified`
3. __`PERCENTAGE`__: % of applications that have been certified for that occupation compared to total number of certified applications regardless of occupation. 

The records in the file must be sorted by __`NUMBER_CERTIFIED_APPLICATIONS`__, and in case of a tie, alphabetically by __`TOP_OCCUPATIONS`__.

Each line of the `top_10_states.txt` file should contain these fields in this order:
1. __`TOP_STATES`__: State where the work will take place
2. __`NUMBER_CERTIFIED_APPLICATIONS`__: Number of applications that have been certified for work in that state. An application is considered certified if it has a case status of `Certified`
3. __`PERCENTAGE`__: % of applications that have been certified in that state compared to total number of certified applications regardless of state.

The records in this file must be sorted by __`NUMBER_CERTIFIED_APPLICATIONS`__ field, and in case of a tie, alphabetically by __`TOP_STATES`__."

# Approach

Each data file is associated with an instance of a custom class "h1b_report". We use the built-in cvs module to load the data, and use the header (first line) to determine the index for the relevant column:  the "status" (whether the application was certified or not), "soc_code" (code for occupation), "soc_name" (name of occupation) and the "state". We then iterate through and parse each line (application) to extract the corresponding values in these columns. 

For all the "certified" applications, we first check if the entry for the "soc_code" or "state" is valid; invalid data are stored in "dumps" for further examination. Since our output has the precision on the first significant digit, warnings messages are raised if invalid data exceeds 0.1\% of the total "certified" applications. During my test I found the invalid entries were but a tiny fraction of all data, which did not seems to affect our output. 

For all the valid values, we use two python dictionaries to update the number of applications associated with each unique "soc_code" or "state", in which the key is "soc_code" or "state" and the value the number of relevant applications. For the `top_10_states.txt` output it is straightforward: after we iterate through all the data, we simply sort the state / application number dictionary values and pick the top 10. For  `top_10_occupations.txt` there is one extra step, as there could be multiple variations of "soc_name"  associated with an unique "soc_code". We therefore check the occurrence of different "soc_name" for each "soc_code", and choose the most frequently used "soc_name" for each "soc_code". This allows us to sort first the application number then the "soc_name". 

# Note

 . This version does not support .xlsx file format available on the US Department of Labor website. Normally to handle .xlsx file we could use the xlrd module, but it is not a build-in one for python, so I am not sure if it is allowed in this challenge.
 . As we know, python's float datatype does not always round percentage as intended, for instance, sometimes 0.5 round to 0. This is fairly trivial, but for precision we use decimal datatype instead. 
 . It took ~7 seconds to process a ~200 Mbyte data on a Macbook pro.  
 
# Run

Simply run the bash script: bash run.sh


 

