import requests
from bs4 import BeautifulSoup, NavigableString
import sqlite3
import json
from discord_webhook import DiscordWebhook, DiscordEmbed
import time
import  re


url = "https://mugshotsorlando.com/arrests/"

with open("settings.json", "r") as f:
    settings = json.load(f)

if settings["discordWebhook6"] == "":
    print("Please add a webhook to settings.json")
    exit()

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}

#Create database for last inmate

conn = sqlite3.connect('orange.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS inmate (name text)")
conn.commit()
conn.close()


def main():
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # Get list of inmates
    inmates_div = soup.find("div", class_="clearfix row-fluid")
    inmates = inmates_div.find_all("section", class_="post_content")


    response2 = requests.get('https://mugshotsorlando.com/arrests/')

    soup2 = BeautifulSoup(response.content, 'html.parser')

    view_charges_link = soup2.find('a', class_='viewCharges')
    link = view_charges_link.get('href')
    print(link)
    
    url2 = link
    response3 = requests.get(url2)

    soup3 = BeautifulSoup(response3.text, 'html.parser')

    crime5 = soup3.find(class_='captalize')


    count = 0
    for item in soup2.find_all('img'):
        count += 1
        if count == 4:
            print(item['src'])
            break

    for inmate in inmates:
        # Filter data from HTML:
        name = inmate.find("h3", class_="h2").text

        # Open the inmate page
        view_charges_link = inmate.find('a', class_='viewCharges')
        link = view_charges_link.get('href')

        response3 = requests.get(link)
        soup3 = BeautifulSoup(response3.text, 'html.parser')

        count = 0
        for item in inmate.find_all('img'):
            count += 1
            if count == 4:
                img_url = item['src']
                break

        # Check if inmate already exists in database
        conn = sqlite3.connect('orange.db')
        c = conn.cursor()
        c.execute("SELECT * FROM inmate WHERE name=?", (name,))
        result = c.fetchone()
        conn.close()

        # If inmate doesn't exist, add to database and send webhook
        if result is None:
            conn = sqlite3.connect('orange.db')
            c = conn.cursor()
            c.execute("INSERT INTO inmate VALUES (?)", (name,))
            conn.commit()
            conn.close()

            webhook = DiscordWebhook(url=settings['discordWebhook6'])
            embed = DiscordEmbed()
            embed.set_title("**New Inmate Detected 🎉**")
            embed.set_description(f"**Name:** {name}\n\n **Crime:** Too Lazy To Fix This\n\n**Link:** "f"[Click Here]({link})")
            embed.set_image(url=item['src'])
            embed.set_color(0xFFFFFF)
            embed.set_timestamp()

            webhook.add_embed(embed)
            response = webhook.execute()

            print(f"New inmate detected: {name}")

        # If inmate already exists, do nothing
        else:
            print(f"Inmate already exists: {name}")

    print("Checking again in 1 minute...")




if __name__ == "__main__":
    print('\nStarting Inmates Monitor...')
    print()
    while True:
        main()
        time.sleep(60)


        
