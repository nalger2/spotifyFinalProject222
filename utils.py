import pandas as pd 
import numpy as np
import datetime
import matplotlib.pyplot as plt

def load_listening_history(filename):
    df = pd.read_csv(filename)
    return df

def load_song_library(filename):
    df = pd.read_json(filename)
    df.to_csv("your_library.csv")
    return df

def clean_endtime_column(df):
    #remove end time column, add column for year, month, day, time
    endTime_ser = df.pop("endTime")
    endTime_ser = pd.to_datetime(endTime_ser, dayfirst=1)
    #date = endTime_ser.dt.date
    #time = endTime_ser.dt.time
    day_of_week = endTime_ser.dt.dayofweek
    df["end_time"] = endTime_ser
    df["day_of_week"] = day_of_week
    #df["date"] = date
    #df["time_of_day"] = time

def clean_msplayed_column(df):
    msplayed_ser = df.pop("msPlayed")
    msplayed_ser = pd.to_timedelta(msplayed_ser, unit='ms')
    df["time_played"] = msplayed_ser

def add_skipped_column(df):
    skipped_time = datetime.timedelta(seconds=30)
    df["skipped"] = df["time_played"] < skipped_time

def add_inlibrary_column(history_df, library_df):
    import warnings
    warnings.filterwarnings("ignore", 'This pattern has match groups')
    pd.options.mode.chained_assignment = None  # default='warn'
    #history_df["in_library"] = library_df["track"].str.contains(history_df["trackName"].any() and library_df["artist"].str.contains(history_df["artistName"]).any()
    for i in range(len(history_df)): 
        if library_df["track"].str.contains(history_df.loc[i, "trackName"]).any() and library_df["artist"].str.contains(history_df.loc[i, "artistName"]).any():
            history_df.loc[i, "in_library"] = 1
        else:
            history_df.loc[i, "in_library"] = 0                                                  

def visualize_songs_per_month(df):
    #group by month
    grouped_by_month = df.groupby(pd.Grouper(key="end_time", freq='M'))
    month_labels = ["September 2019", "October 2019", "November 2019", "December 2019", 
    "January 2020", "February 2020", "March 2020", "April 2020", "May 2020", 
    "June 2020", "July 2020", "August 2020", "September 2020"]
    songs_played = pd.Series(dtype=float)
    time_listened = pd.Series(dtype=float)
    for group_name, group_df in grouped_by_month:
        songs_played[group_name] = group_df.size
        time_listened[group_name] = group_df["time_played"].sum()
    
    #2 plots on the same x axis
    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Songs', color=color)
    ax1.plot(month_labels, songs_played, color=color)
    
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax2.set_ylabel('Total Time (days)', color=color)  # we already handled the x-label with ax1
    ax2.plot(month_labels, time_listened, color=color)

    for tick in ax1.get_xticklabels():
        #tick.set_label
        tick.set_rotation(90)

    fig.tight_layout()  
    fig.suptitle("Songs & Time Listened By Month")
    plt.show()
    return month_labels, grouped_by_month

def visualize_skips_per_month(month_labels, grouped_by_month):
    skipped = pd.Series(dtype=float)
    unskipped = pd.Series(dtype=float)
    for group_name, group_df in grouped_by_month:
        skipped[group_name] = group_df.skipped.sum()
        unskipped[group_name] = group_df.skipped.size - group_df.skipped.sum()
    
    x = np.arange(len(month_labels))  # the label locations
    width = 0.35  # the width of the bars

    plt.figure()
    plt.bar(x - width/2, skipped, width, color="orange", label="Skipped")
    plt.bar(x + width/2, unskipped, width, color="purple", label="Played")
    plt.legend()
    plt.title("Number of Skipped vs Played Songs")
    plt.xticks(x, month_labels, rotation=90)
    plt.show()
    
def visualize_2month_skips(june, july):
    june_grouped = june.groupby("skipped")
    june_x = ["Played", "Skipped"]
    june_y = []
    for group_name, group_df in june_grouped:
        june_y.append(group_df.trackName.count())
    plt.figure()
    plt.pie(june_y, labels=june_x, autopct="%1.1f%%", colors=["yellow", "purple"])
    plt.title("June Skips Breakdown")
    plt.show()
    
    july_grouped = july.groupby("skipped")
    july_x = ["Played", "Skipped"]
    july_y = []
    for group_name, group_df in july_grouped:
        july_y.append(group_df.trackName.count())
    plt.figure()
    plt.pie(july_y, labels=july_x, autopct="%1.1f%%", colors=["yellow", "purple"])
    plt.title("July Skips Breakdown")
    plt.show()
                                                                
def visualize_2month_discovery(june, july):
    june_grouped = june.groupby("in_library")
    june_x = ["Songs Not In Library", "Songs In Library"]
    june_y = []
    for group_name, group_df in june_grouped:
        june_y.append(group_df.trackName.count())
    
    #print(june_x, june_y)
    plt.figure()
    plt.pie(june_y, labels=june_x, autopct="%1.1f%%")
    plt.title("June Song Discovery Breakdown")
    plt.show()

    july_grouped = july.groupby("in_library")
    july_x = ["Songs Not In Library", "Songs In Library"]
    july_y = []
    for group_name, group_df in july_grouped:
        july_y.append(group_df.trackName.count())
    
    #print(july_x, july_y)
    plt.figure()
    plt.pie(july_y, labels=july_x, autopct="%1.1f%%")
    plt.title("July Song Discovery Breakdown")
    plt.show()

def find_spd(month_listening_history):
    grouped_by_day = month_listening_history.groupby(pd.Grouper(key="end_time", freq='D'))
    spd = pd.Series()
    for group_name, group_df in grouped_by_day:
        spd[group_name] = group_df["trackName"].count()
    return spd.tolist()

def find_avg_tpd(month_listening_history):
    grouped_by_day = month_listening_history.groupby(pd.Grouper(key="end_time", freq='D'))
    tpd = pd.Series()
    for group_name, group_df in grouped_by_day:
        tpd[group_name] = group_df["time_played"].sum()
    tpd = tpd.tolist()
    avg = sum(tpd, datetime.timedelta(0)) / len(tpd)
    return avg



    

'''
#test functions:
#load datasets
spotify_df = load_listening_history("StreamingHistoryALL.csv")
library_df = load_song_library("YourLibrary.json")
#clean listening history
clean_endtime_column(spotify_df)
clean_msplayed_column(spotify_df)
add_skipped_column(spotify_df)

#separate by month, to analyze by month
#visualize songs per month
month_labels, grouped_by_month = visualize_songs_per_month(spotify_df)

#visualize skipped vs not skipped by month
visualize_skips_per_month(month_labels, grouped_by_month)

#JUNE & JULY DISCOVERY ANALYSIS
june_listening_history = grouped_by_month.get_group("2020-06-30 00:00:00")
july_listening_history = grouped_by_month.get_group("2020-07-31 00:00:00")

#add in library column
june_listening_history.reset_index(inplace=True)
july_listening_history.reset_index(inplace=True)
add_inlibrary_column(june_listening_history, library_df)
add_inlibrary_column(july_listening_history, library_df)

#Visualize June & July discovery
visualize_2month_discovery(june_listening_history, july_listening_history)
                                                                
#visualize june and july skipped
visualize_2month_skips(june_listening_history, july_listening_history)
'''

'''
played_songs, skipped_songs = separate_skipped_songs(spotify_df)
skipped_songs.to_csv("skipped.csv")

#print(played_songs[1:50])
played_songs.reset_index(inplace=True)
skipped_songs.reset_index(inplace=True)
#print(played_songs[1:50])

#test_df = load_listening_history("testhistory.csv")
#july_df = load_listening_history("spotify_streaming_history_july_2020.csv")
#add_inlibrary_column(test_df, library_df)
#add_inlibrary_column(july_df, library_df)

add_inlibrary_column(played_songs, library_df)
#add_inlibrary_column(skipped_songs, library_df)

print(played_songs[300:350])
#print(skipped_songs[300:350])

'''


