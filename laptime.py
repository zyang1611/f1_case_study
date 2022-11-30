import os
import fastf1
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def main():
    """
    Unlike other sports, you can get an idea of how a race will turn out before the race itself! Practice sessions in F1 offer a glimpse at each car's relative performance at a track and can provide useful information on predicting who will have the fastest car in qualifying and on race day.
    """
    # Get session data from Fastf1
    this_year = 2022
    this_session = "FP2"
    this_race = "Abu Dhabi"
    fastf1.Cache.enable_cache("/users/zhenyang/documents/f1data_cache")
    session = fastf1.get_session(this_year, this_race, this_session)
    # session = fastf1.get_testing_session(2022, 3, 1)
    
    # Load data
    session.load(telemetry=False, messages=False, weather=False)

    # Get lap times and filter only relevant info
    lap_times = session.laps.pick_accurate()
    lap_times = lap_times.loc[:, ["Driver", "Team" , "Stint", "LapTime", "TyreLife", "Compound", "SpeedI1", "SpeedI2", "SpeedFL", "SpeedST", "LapNumber"]]
    
    # Convert pd.timedelta to seconds
    lap_times.LapTime = lap_times.LapTime.dt.total_seconds()
    
    # fig, ax4 = plt.subplots(figsize=(10, 8.5))
    # ax4.scatter(lap_times.TyreLife, lap_times.LapTime)
    
    # Get representative race practice times
    rr_times = get_race_runs(lap_times)
    
    # Get best times for each driver
    best = lap_times.loc[:, ["Driver", "LapTime"]]
    best = best.groupby(["Driver"]).min()
    best.sort_values(by="LapTime", inplace=True, kind="mergesort")
    
    # Get best posted race run time 
    best_rr = rr_times.groupby("Driver").min()["LapTime"]
    best_times = pd.merge(best, best_rr, how="left", on="Driver")
    best_times.columns = ["Best_Q", "Best_RR"]
    
    # Plot best times 
    fig0, ax0 = plt.subplots(figsize=(10, 8.5))
    formatter = plt.FuncFormatter(format_func)
    
    # Plot on a horizontal bar plot
    y_pos = np.arange(len(best_times))
    p1 = ax0.barh(y_pos, best_times.Best_RR, label="Race")
    p2 = ax0.barh(y_pos, best_times.Best_Q, label="Qualifying")
    ax0.set_yticks(y_pos, labels=best_times.index)
    ax0.invert_yaxis()
    ax0.yaxis.set_major_locator(plt.MultipleLocator(base=1))

    # Label bars
    container = ax0.containers[1]
    ax0.bar_label(p2, labels=[format_func(x, 0) for x in container.datavalues], padding=-55)
    
    # Set x-axis plot range 
    x_range = [best_times.min()["Best_Q"]-1, best_times.max()["Best_RR"]+0.2]
    ax0.set_xlim(x_range)
    ax0.xaxis.set_major_formatter(formatter)
    ax0.legend()
    ax0.set(xlabel="Lap Time", title="Best Lap Times")
    
    # Define plot groups
    top_teams = ["Red Bull Racing", "Ferrari", "Mercedes"]
    mid_teams = ["McLaren", "Alpine"]
    bottom_teams = ["Alfa Romeo", "AlphaTauri", "Haas F1 Team", "Aston Martin", "Williams"]
    
    # Populate list of teams with representative times
    teams_with_time = [x for n, x in rr_times.Team.drop_duplicates().items()]
    
    # Create axes
    ax1 = ax2 = ax3 = False
    if any([x in bottom_teams for x in teams_with_time]):
        fig3, ax3 = plt.subplots(figsize=(10, 8.5))
    if any([x in top_teams for x in teams_with_time]):
        fig1, ax1 = plt.subplots(figsize=(10, 8.5))
    if any([x in mid_teams for x in teams_with_time]):
        fig2, ax2 = plt.subplots(figsize=(10, 8.5))
    
    # Plot each stint 
    stints_with_time = rr_times.loc[:, ["Driver" , "Stint"]]
    stints_index = stints_with_time.drop_duplicates().itertuples(index=False)
    for x in stints_index:
        driver = x[0]
        stint = int(x[1])
        driver_times = rr_times[(rr_times.Driver == driver) & (rr_times.Stint == stint)]
        if driver_times.Team.iloc[0] in top_teams:
            ax1.plot(driver_times.TyreLife, driver_times.LapTime, label=(driver, driver_times.Compound.iloc[0]), marker="x", linewidth=2)
        elif driver_times.Team.iloc[0] in mid_teams:
            ax2.plot(driver_times.TyreLife, driver_times.LapTime, label=(driver, driver_times.Compound.iloc[0]), marker="x", linewidth=2)
        else:
            ax3.plot(driver_times.TyreLife, driver_times.LapTime, label=(driver, driver_times.Compound.iloc[0]), marker="x", linewidth=2)
            
    # Format axes and save plots
    path = os.path.join("data", str(this_year), str(this_race), str(this_session))
    if not os.path.exists(path):
        os.makedirs(path)
        
    fig0.savefig(os.path.join(path, "best_times.jpg"), dpi=300)
    if ax1:
        ax1.set(title="Top Teams")
        plot_formatter(formatter, ax1)
        fig1.savefig(os.path.join(path, "top.jpg"), dpi=300)
    if ax2:
        ax2.set(title="Mid Teams")
        plot_formatter(formatter, ax2)
        fig2.savefig(os.path.join(path, "mid.jpg"), dpi=300)
    if ax3:
        ax3.set(title="Bottom Teams")
        plot_formatter(formatter, ax3)
        fig3.savefig(os.path.join(path, "bottom.jpg"), dpi=300)
    
def get_race_runs(lap_times):
    """
    Takes a Laps df and returns only laps from stints that represent high fuel race practice laps. Uses st.dev to select the correct stints. 
    """
    # Get race run practice times by choosing stints with st.dev < 17s. 
    stints2 = lap_times.loc[:, ["Driver", "Stint", "LapTime"]]
    laps_std = stints2.groupby(["Driver", "Stint"]).std(numeric_only=True)
    race_runs = laps_std.loc[lambda sel: sel.LapTime < 17].reset_index()
    race_runs.rename(columns={"LapTime": "LapTime_std"}, inplace=True)
    
    # Create race run times table with laptimes for each lap in the chosen stints
    rr_times = pd.merge(race_runs.loc[:, ["Driver", "Stint", "LapTime_std"]], lap_times.loc[:, ["Driver", "Team", "Stint", "LapTime", "TyreLife", "Compound"]], how="inner", on=["Driver", "Stint"])
    
    # Filter outliers 
    rr_times = rr_times[rr_times.LapTime-rr_times.LapTime.mean() <= 0.5*rr_times.LapTime.std()]
    
    return rr_times

def get_race_runs_ml(lap_times):
    """
    Takes a Laps df and returns only laps from stints that represent high fuel race practice laps. Uses SVM to classify the correct stints/laps.
    """
    pass

def format_func(x, pos):
    minutes = int((x%3600)//60)
    seconds = x%60
    return "{:02d}:{:.3f}".format(minutes, seconds)

def plot_formatter(formatter, ax):
    ax.set(xlabel="Tyre Life", ylabel="Lap Time")
    ax.legend()
    ax.yaxis.set_major_formatter(formatter)
    ax.grid(axis="both", linewidth=1.5)
    ax.grid(axis="both", which="minor", linewidth=0.5, linestyle="dotted")
    ax.minorticks_on()
    
if __name__ == "__main__":
    main()
    
