#source code to get started
#https://code.datasciencedojo.com/datasciencedojo/tutorials/blob/master/Web%20Scraping%20with%20Python%20and%20BeautifulSoup/Web%20Scraping%20with%20Python%20and%20Beautiful%20Soup.py
from bs4 import BeautifulSoup as soup  # HTML data structure
from urllib.request import urlopen as uReq  # Web client
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import time
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

out_filename_out_standing = "out_standing_players_20.csv"

headers_outstanding = "season_name,club_name,player_name,position,player_image,Appearances,Clean_sheets,Goals,Assists \n"

s = open(out_filename_out_standing, "w")

s.write(headers_outstanding)

#called when player contributing to full time results atleast once every two games
def write_to_outstanding (attributes):

    club_name = attributes["club_name"]
    season_name = attributes["season_name"]
    player_name = attributes["name"]
    position = attributes["position"]
    player_image = attributes["player_image"]
    Appearances = str(attributes["Appearances"])
    Clean_sheets = str(attributes["Clean sheets"])
    Goals =  str(attributes["Goals"])
    Assists = str(attributes["Assists"])

    output_str = season_name + "," + club_name + "," + player_name + "," + position + "," + player_image + "," + Appearances + "," + Clean_sheets + "," + Goals + "," + Assists +"\n"
    s.write(output_str)

#deals with one single player
def player_data_work_with_relevant (data, meta, club_name, season_name) :

    player_name = meta.find("h4", {"class":"name"}).text

    position = meta.find("span", {"class":"position"}).text

    player_image = None
    try:
        player_image = meta.find("img", {"class":"img"})["src"]
    except:
        pass

    useful = data.findAll("dl")
    
    name = useful[1]
    
    useful.pop(0)

    attributes = {"name":player_name, "position":position, "player_image":player_image, "Appearances":0, "Clean sheets":0, "Goals":0, "Assists":0, "club_name":club_name, "season_name":season_name}

    for a in useful:
        name = a.find("dt").text
        result = int(a.find("dd").text)

        if result != 0:
            attributes[name] = result

    if attributes["Appearances"] != 0:

        player_quality = ( attributes["Clean sheets"] + attributes["Goals"] + attributes["Assists"] ) / attributes["Appearances"]
        clean_ver = int(attributes["Clean sheets"])

        if (player_quality >= 0.5) | (position=="Goalkeeper" and clean_ver >= 13)  :
            write_to_outstanding(attributes)

        if player_quality > 1 :
            player_quality = 1
        return player_quality

    else:
        return False

def get_data (club_id, season_id, club_name, season_name):

    url_ = "https://www.premierleague.com/clubs/"+str(club_id)+"/club/squad?se="+str(season_id)

    driver = webdriver.Chrome(executable_path=r"../chromedriver_win32/chromedriver.exe")

    driver.get(url_)

    time.sleep(3)

    html = driver.page_source

    soup_ = soup(html, features="lxml")

    squad_block = "squadListContainer squadList block-list-4 block-list-3-m block-list-2-s block-list-padding"

    driver.close()

    try:
        block = soup_.find("ul", {"class":squad_block})

        player_meta = block.findAll("header", {"class":"squadPlayerHeader"})
        player_containers = block.findAll("ul", {"class":"squadPlayerStats"})
        print(len(player_meta), len(player_containers))

        player_qualities = []

        for x_a in range(len(player_containers)):
            x = player_containers[x_a]
            m = player_meta[x_a]
            player_contribution = player_data_work_with_relevant(x, m, club_name, season_name)
            if player_contribution != False:
                player_qualities.append(player_contribution)


        squad_depth = 1 - (11/len(player_qualities))

        contribution_average = sum(player_qualities) / len(player_qualities)
        return { "contribution_average":contribution_average, "squad_depth":squad_depth  }

    except Exception as e:

        print("an error occured!")
        print(repr(e))
        return False

#manage operation for multiple years
def get_team_information_for_all_years(team_index, club_name):

    output_all = { "contribution_average":0, "squad_depth":0 }

    seasons_that_count = 0

    for a in seasons:

        data_for_year = get_data(team_index, a["_id"], club_name, a["name"])

        if data_for_year != False:
            seasons_that_count+=1

            output_all["contribution_average"] += data_for_year["contribution_average"]

            output_all["squad_depth"] += data_for_year["squad_depth"]

    if seasons_that_count != 0:

        output_all["contribution_average"] = output_all["contribution_average"] / seasons_that_count

        output_all["squad_depth"] = output_all["squad_depth"] / seasons_that_count

    return output_all

out_filename = "team_player_averages_4.csv"

headers = "prem_name,contribution_average,squad_depth \n"

f = open(out_filename, "w")

f.write(headers)

teams = pd.read_csv('./team_details.csv')


for row in teams.iterrows():

    base_data = row[1]
    
    seasons_average_data = get_team_information_for_all_years(base_data["prem_index"], base_data["prem_name"])
    
    prem_name_ = base_data["prem_name"]
    
    contribution_average = seasons_average_data["contribution_average"]

    squad_depth = seasons_average_data["squad_depth"]

    f.write(prem_name_ + ", " + str(contribution_average) + ", " + str(squad_depth) + "\n")

f.close()
s.close()
