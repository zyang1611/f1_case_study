# F1 Data Case Study
### Description
#### **Introduction**
Unlike other sports, in F1 you can get an idea of how a race will turn out before the race itself! Teams use practice sessions to decide on car set-up for the weekend and so recorded practice lap times can offer a glimpse in to each car's relative performance at a specific track. This may prove useful if you are trying to predict who will have the fastest car in qualifying and on race day. 

During practice, teams will normally conduct test laps to simulate car qualifying and race performance.
- Qualifying: low fuel load, soft tyres, full push laps followed by cool down laps.
- Race: high fuel load, any tyre, a few laps with consecutive and consistent times.

The objective of this script is to plot and compare qualifying and race simulation lap times for drivers from top, mid and bottom teams for any past race and also for future races when practice session lap times become available.
By plotting this info, the goal is to find out which car has the best set up or has dynamics that particularly suited to a specific track and hopefully predict if that car will perform better than its direct rivals. Very useful if you are playing F1 Fantasy!
Some examples below...

![best times](/data/2022/Abu%20Dhabi/FP2/best_times.jpg "Best Lap Times")
![top teams](/data/2022/Abu%20Dhabi/FP2/top.jpg "Top Teams")
![mid teams](/data/2022/Abu%20Dhabi/FP2/mid.jpg "Mid Teams")
![bottom teams](/data/2022/Abu%20Dhabi/FP2/bottom.jpg "Bottom Teams")

#### **The Data**
##### **Data Source**
Data is fetched using the FastF1 API which relies on F1's live timing service. I will primarily be using FastF1's Laps object which is a pandas DataFrame containing timing and other data such as tyre life, tyre compound, top speeds and more for each lap. 
##### **Transform and Analyse**
Below is a rough outline of the data processing steps used.
1. Filter out outlaps(exiting pits) and inlaps(entering pits).
2. Slice DataFrame to select only required columns.
3. Convert recorded lap time from a pd.timedelta to seconds for analysis.
4. Select the fastest lap recorded by each driver, this is his qualifying simulation time. 
5. Calculate standard deviation for each recorded stint and select stints with st.dev <17s. This represents the race simulation stints where drivers record a few consecutive laps with very similar times. 
6. Filter outlier laps from the selected stints. 
7. The results are then plotted as shown using matplotlib. 

#### **Further Improvement**
This is a work in progress. Next steps will be:
- To link the output data from this script to a Tableau dashboard.
- To implement an SVM classifier to select race simulation times and see if improvements to accuracy can be made.