#source code to get started
#https://code.datasciencedojo.com/datasciencedojo/tutorials/blob/master/Web%20Scraping%20with%20Python%20and%20BeautifulSoup/Web%20Scraping%20with%20Python%20and%20Beautiful%20Soup.py
from bs4 import BeautifulSoup as soup  # HTML data structure
from urllib.request import urlopen as uReq  # Web client
from selenium import webdriver
import statistics
import pandas as pd
# URl to web scrap from.
seasons = [
    # {"name":"2020/21", "_id":"363" },
    {"name":"2019/20", "_id":"274" },
    {"name":"2018/19", "_id":"210" },
    {"name":"2017/18", "_id":"79" },
    {"name":"2016/17", "_id":"54" },
    {"name":"2015/16", "_id":"42" },
    # {"name":"2014/15", "_id":"27" },
    # {"name":"2013/14", "_id":"22" },
    # {"name":"2012/13", "_id":"21" },
    # {"name":"2011/12", "_id":"20" },
    # {"name":"2010/11", "_id":"19" },
]

teams = pd.read_csv('./team_details.csv')
teams_output = {}
for row in teams.iterrows():
    teams_output[row[1]["prem_name"]] = []
# print(teams_output)

#push points into array
def process_points (points_arr):
    index_with_points = []

    for a in range(len(points_arr)):
        if(points_arr[a]=="\n"):
            index_with_points.append(a-1)

    points = []
    for a in index_with_points:
        points.append(points_arr[a])
    return points

#return the competition level and update the data we currently have
def get_league_data_for_each_team (data, existing_teams):
    
    page_url = "https://www.skysports.com/premier-league-table/"+data["name"].split("/")[0]
    
    print(page_url)
    
    uClient = uReq(page_url)
    
    page_soup = soup(uClient.read(), "html.parser")
    
    uClient.close()
    
    table = page_soup.find("table", {"class":"standing-table__table"})
    
    team_names = table.findAll("a", {"class":"standing-table__cell--name-link"})
    
    team_points = table.findAll("td")
    
    names_found = [ x.text for x in team_names ]
    
    points_found = process_points([ x.text for x in team_points ])

    points_found = [ int(y) for y in points_found ]

    competition_level = statistics.stdev(points_found) 

    for a in range(len(names_found)):
        temp_name = names_found[a]
        value = points_found[a]

        try:
            existing_teams[temp_name].append({"points":value, "competition_level":competition_level})
        except:
            pass

    return existing_teams

#run the get_league_data_for_each_team for the last 5 seasons
def iterate_over_all_years (seasons, teams_output) :
    for season in seasons:
        teams_output = get_league_data_for_each_team(season, teams_output)
    return teams_output

#average out the comp_level and points ratio over the course of 5 seasons
def average_out_per_team (teams_output) :

    new_teams_output = []
    
    for team_name in teams_output:
    
        team = teams_output[team_name]

        length = len(team)

        if length != 0:
            averaged = { "points":sum(x["points"] for x in team )/length, "competition_level":sum(x["competition_level"] for x in team )/length, "prem_name":team_name }
            new_teams_output.append(averaged)
        else:
            new_teams_output.append({ "points":0, "competition_level":0, "prem_name":team_name })

    return new_teams_output

teams_output = iterate_over_all_years(seasons, teams_output)

teams_output = average_out_per_team(teams_output)

out_filename = "league_data_each_team.csv"

headers = "prem_name,points,competition_level\n"

f = open(out_filename, "w")

f.write(headers)

for a in teams_output:
    f.write(a["prem_name"] + "," + str(a["points"]) + "," + str(a["competition_level"]) + "\n")
f.close()
