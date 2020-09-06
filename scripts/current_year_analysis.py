#source code to get started
#https://code.datasciencedojo.com/datasciencedojo/tutorials/blob/master/Web%20Scraping%20with%20Python%20and%20BeautifulSoup/Web%20Scraping%20with%20Python%20and%20Beautiful%20Soup.py
from bs4 import BeautifulSoup as soup  # HTML data structure
from urllib.request import urlopen as uReq  # Web client
from selenium import webdriver
import statistics
import pandas as pd

teams = pd.read_csv('./team_details.csv')
teams_output = {}
for row in teams.iterrows():
    teams_output[row[1]["spotrac_name"]] = {"club_value":0, "commitment_level":0, "prem_name":""}

#format data so it can be in the right format to be processed
def attach_prem_name (teams_output, teams):
    names = []
    for row in teams.iterrows():
        names.append(row[1]["prem_name"])
    counter = 0
    for a in teams_output:
        teams_output[a]["prem_name"] = names[counter]
        counter+=1

    return teams_output

teams_output = attach_prem_name(teams_output, teams)

#find commitment level for all teams by running function determine_commitment
def determine_commitment_all (teams_output):
    for a in teams_output:
        teams_output = determine_commitment(a, teams_output)
    return teams_output

#get length of time before contract for player expires
def extract_expire_year (row):
    all_tds = row.findAll("td", {"class":"center"})
    if len(all_tds) != 0:
        text = all_tds[len(all_tds)-1].text
        if text=="-":
            return 0
        else:
            return ( int(all_tds[len(all_tds)-1].text) - 2020 )
    else:
        return False

#find commitment levels of players and populate data accordingly
def determine_commitment (team_name, teams_output) :

    if team_name=="Leeds United F.C.":

        teams_output[team_name]["commitment_level"] = 0
        
        return teams_output
    else:
        #reformat team name for correct url
        team_name_format = team_name.lower()
        
        team_name_format = team_name_format.replace("& ", "")
        
        team_name_format = team_name_format.replace(" ", "-")
        
        team_name_format = team_name_format.replace(".", "")
        
        page_url = "https://www.spotrac.com/epl/"+team_name_format+"/contracts/"
        
        uClient = uReq(page_url)

        page_soup = soup(uClient.read(), "html.parser")

        uClient.close()

        all_players = page_soup.findAll("tr")

        player_expiry_years = [ extract_expire_year(y) for y in all_players[1:len(all_players)] ]

        player_commitment_average = 0

        if player_expiry_years != False:
            player_commitment_average = sum(player_expiry_years)

        teams_output[team_name]["commitment_level"] = player_commitment_average

        return teams_output

#extract the amount club spends on payroll  
def get_integers (text):
    text = text.replace("£", "")
    text = text.replace(",", "")
    return int(text)

#get payroll for each team and populate data
def get_team_values (teams_output):
    page_url = "https://www.spotrac.com/epl/payroll/"

    uClient = uReq(page_url)
    
    page_soup = soup(uClient.read(), "html.parser")
    
    uClient.close()
    
    team_names_ = page_soup.findAll("td", {"class":"player noborderleft"})
    
    estim_sal_val_ = page_soup.findAll("td", {"class":"result center"})

    team_names = [ x.text for x in team_names_ ]
    
    estim_sal_val = [ get_integers(x.text) for x in estim_sal_val_ ]

    try:
        for x in range(len(team_names)):
            team = team_names[x]
            teams_output[team]["club_value"] = estim_sal_val[x] 
    except:
        pass

    return teams_output

#run script
def determine_commitment_average (teams_output):

    out_filename = "current_year_analysis_20.csv"

    headers = "prem_name,club_value,commitment_level\n"

    f = open(out_filename, "w")

    f.write(headers)

    teams_output = get_team_values(teams_output)

    teams_output = determine_commitment_all(teams_output)

    for a in teams_output:
        f.write(teams_output[a]["prem_name"] + "," + str(teams_output[a]["club_value"]) + "," + str(teams_output[a]["commitment_level"]) + "\n")
    f.close()


determine_commitment_average(teams_output)
