#source code to get started
#https://code.datasciencedojo.com/datasciencedojo/tutorials/blob/master/Web%20Scraping%20with%20Python%20and%20BeautifulSoup/Web%20Scraping%20with%20Python%20and%20Beautiful%20Soup.py
from bs4 import BeautifulSoup as soup  # HTML data structure
from urllib.request import urlopen as uReq  # Web client

#this script is to get the team names in the right format for the sites we use to scrape data from

prem_data = {
    "url":"https://www.premierleague.com/clubs/",
    "component":"h4",
    "class_name":"clubName"
}

spotrac_data = {
    "url":"https://www.spotrac.com/epl/",
    "component":"a",
    "class_name":"team-name"
}


def extract_data (data):
    page_url = data["url"]
    uClient = uReq(page_url)
    page_soup = soup(uClient.read(), "html.parser")
    uClient.close()
    site_version_names = page_soup.findAll(data["component"], {"class":data["class_name"]})
    return site_version_names

def extract_prem_club_numbers (data):
    page_url = data["url"]
    uClient = uReq(page_url)
    page_soup = soup(uClient.read(), "html.parser")
    uClient.close()
    block_class = "block-list-5 block-list-3-m block-list-1-s block-list-1-xs block-list-padding dataContainer"
    block = page_soup.find("ul", {"class":block_class})
    block_components = block.findAll("a")
    block_links = [ x['href'].split("/")[2] for x in block_components ]
    return block_links


prem_indexes = extract_prem_club_numbers(prem_data)

prem_extracted_names = [ x.text for x in extract_data(prem_data) ]
spotrac_extracted_names = [ x.text for x in extract_data(spotrac_data) ]

out_filename = "team_details_2.csv"
headers = "prem_name,spotrac_name,prem_index \n"
# opens file, and writes headers
f = open(out_filename, "w")
f.write(headers)
def generate_dictionary (prem, spotrac, prem_indexes):

    for i in range (0, 20):

        prem_name_ = prem[i]

        spotrac_name_ = spotrac[i]

        prem_index_ = prem_indexes[i]

        f.write(prem_name_ + "," + spotrac_name_ + "," + prem_index_ + "\n")

    f.close()

generate_dictionary(prem_extracted_names, spotrac_extracted_names, prem_indexes)
