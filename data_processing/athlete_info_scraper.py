# Import
from lxml import html
import requests
import json
import re

# Base URL
base_url = "http://www.olympedia.org/athletes/"
ath_data = []
ath_seen = 0

import time
start = time.time()
# (1, 138441) Full Range 
for ath_num in range(80000, 100000):
    url = base_url + str(ath_num)
    if ath_num % 1000 == 0:
        print(url)
    response = requests.get(url)
    tree = html.document_fromstring(response.text)

    page_not_found = False
    while(True):
        if len(tree.xpath("//table[@class='biodata']")) == 0:
            if "Rate Limit Exceeded" in response.text:
                print(str(ath_num) + " - RATE LIMIT EXCEEDED")
                time.sleep(60)
                response = requests.get(url)
                tree = html.document_fromstring(response.text)
            else:
                print(str(ath_num) + " - PAGE NOT FOUND")
                page_not_found = True
                break
        else:
            break

    if page_not_found == True:
        continue

    if len(tree.xpath("//td[contains(., 'Competed in Olympic Games')]")) == 0:
        print(str(ath_num) + " - NOT OLYMPIC ATHLETE")
        continue

    ath_seen += 1
    ath_info = {}

    # Name
    ath_info["Name"] = tree.xpath("//h1")[0].text_content().strip()

    bio = tree.xpath("//table[@class='biodata']")[0]
    # Sex
    tr = bio.xpath("tr[contains(., 'Sex')]")
    if len(tr) == 0:
        print(str(ath_num) + " - NO SEX")
        ath_info["Sex"] = ""
    else:
        sex = tr[0].text_content().replace("Sex", "")
        ath_info["Sex"] = sex
    # Birth
    ath_info["Birth"] = ""
    tr = bio.xpath("tr[contains(., 'Born')]")
    if len(tr) == 0:
        print(str(ath_num) + " - NO BIRTH")
    else:
        s = re.search(r"\d{4}", tr[0].text_content())
        if s:
            ath_info["Birth"] = s.group(0)

    # Fetch Results
    rows = tree.xpath("//table[@class='table table-striped'][1]//tbody/tr")
    results = []
    cur_games = ""
    cur_sport = ""
    cur_nat = ""
    for r in rows:
        result = {}
        entries = r.xpath("td")
        assert len(entries) == 8
        # Games
        s = " ".join(entries[0].text_content().split())
        if s != "":
            cur_games = s
        result["Games"] = cur_games
        # Sport
        s = " ".join(entries[1].text_content().split())
        if s != "":
            cur_sport = s
        result["Sport"] = cur_sport
        # Event
        s = " ".join(entries[2].text_content().split())
        result["Event"] = s
        # Status
        s = " ".join(entries[3].text_content().split())
        result["Status"] = s
        # Team (For Team Events)
        s = " ".join(entries[4].text_content().split())
        result["Team"] = s
        # Pos
        s = " ".join(entries[5].text_content().split())
        result["Pos"] = s
        # Medal
        s = " ".join(entries[6].text_content().split())
        result["Medal"] = s
        # Nat
        s = " ".join(entries[7].text_content().replace("Representing","").split())
        if s != "":
            cur_nat = s
        result["Nat"] = cur_nat
        results.append(result)
    ath_info["Results"] = results
    ath_data.append(ath_info)
        
end = time.time()
print((end - start)/60)
print(ath_seen)

import codecs

# Write CSV
f = codecs.open("athletes_80k_100k"+".txt", "w", "utf-8")
f.write("Name\tSex\tBirth\tGames\tSport\tEvent\tStatus\tTeam\tPos\tMedal\tNat\n")

for ath in ath_data:
    results = ath["Results"]
    for r in results:
        f.write( "\t".join([ath["Name"], ath["Sex"], ath["Birth"], r["Games"], r["Sport"], r["Event"], r["Status"], r["Team"], r["Pos"], r["Medal"], r["Nat"]]) + "\n")
f.close()
