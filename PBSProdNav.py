import json
import requests
import os
import yt_dlp

from datetime import datetime, time, timedelta

# Written by snowmanila/manilamania (Updated: 9/22/25)

def searchExpired(showList):
    print('All Expired Episodes (From PBS Kids Player):')
    for show in showList:
        episodeList = requests.get(f'https://producerplayer.services.pbskids.org/show-list/?shows={show[1]}&type=episode')
        if episodeList.status_code == 200 and 'items' in episodeList.json():
            for episode in episodeList.json()['items']:
                if episode['expirationdate']:
                    date_object = datetime.strptime(episode['expirationdate'][:-10], '%Y-%m-%d').date()
                    if not date_object >= datetime.now().date():
                        print(f"\n{show[0]}: {episode['title']} ({episode['nola_episode']}) - {episode['description_long']} (Released on: {episode['premiered_on']}, encored on: {episode['encored_on']}, expired on {str(episode['expirationdate'])[:10]})")
                        print(f"Thumbnail: {episode['images']['kids-mezzannine-16x9']['url']}")

def searchFutureClip(showList):
    print('All Upcoming New Clips (From PBS Kids Player):')
    for show in showList:
        clipList = requests.get(f'https://producerplayer.services.pbskids.org/show-list/?shows={show[1]}&type=clip')
        if clipList.status_code == 200 and 'items' in clipList.json():
            for clip in clipList.json()['items']:
                date_object = datetime.strptime(clip['encored_on'], '%Y-%m-%d').date()
                if date_object >= datetime.now().date() and datetime.strptime(clip['premiered_on'], '%Y-%m-%d').date() >= datetime.now().date():
                    print(f"\n{show[0]}: {clip['title']} ({clip['nola_episode']}) - {clip['description_long']} (Releases on: {clip['premiered_on']}, expires on {str(clip['expirationdate'])[:10]})")
                    print(f"Thumbnail: {clip['images']['kids-mezzannine-16x9']['url']}")

def searchFutureRot(showList):
    print('All Upcoming Rotated Episodes (From PBS Kids Player):')
    for show in showList:
        episodeList = requests.get(f'https://producerplayer.services.pbskids.org/show-list/?shows={show[1]}&type=episode')
        if episodeList.status_code == 200 and 'items' in episodeList.json():
            for episode in episodeList.json()['items']:
                date_object = datetime.strptime(episode['encored_on'], '%Y-%m-%d').date()
                if date_object >= datetime.now().date() and not datetime.strptime(episode['premiered_on'], '%Y-%m-%d').date() >= datetime.now().date():
                    print(f"\n{show[0]}: {episode['title']} ({episode['nola_episode']}) - {episode['description_long']} (Released on: {episode['premiered_on']}, encores on: {episode['encored_on']}, expires on {str(episode['expirationdate'])[:10]})")
                    print(f"Thumbnail: {episode['images']['kids-mezzannine-16x9']['url']}")

def searchFuture(showList):
    print('All Upcoming New Episodes (From PBS Kids Player):')
    for show in showList:
        episodeList = requests.get(f'https://producerplayer.services.pbskids.org/show-list/?shows={show[1]}&type=episode')
        if episodeList.status_code == 200 and 'items' in episodeList.json():
            for episode in episodeList.json()['items']:
                date_object = datetime.strptime(episode['premiered_on'], '%Y-%m-%d').date()
                if date_object >= datetime.now().date():
                    print(f"\n{show[0]}: {episode['title']} ({episode['nola_episode']}) - {episode['description_long']} (Releases on: {episode['premiered_on']}, expires on {str(episode['expirationdate'])[:10]})")
                    print(f"Thumbnail: {episode['images']['kids-mezzannine-16x9']['url']}")

def searchStation():
    start_date = datetime.now().date()
    #start_date = datetime.strptime('2025-12-01', '%Y-%m-%d').date() # Individual date for debugging
    episodes = []
    hours = '00-24'
    channel = '2'
    # Reads all dates between now and a year from now
    print('All Upcoming New Episodes (From PBS WGTE):')
    for i in range(0, 366):
        date = start_date + timedelta(days=i)
        print(f'\nNew episodes for {date}:')
        payDate = (str(date)).split('-')
        payload = {'year': str(payDate[0]), 'month': payDate[1], 'day': payDate[2], 'hours': hours, 'channels': channel} # Data that is sent to WGTE to get the full PBS Kids schedule for the respective date
        
        # Send a POST request to fetch the webpage content for each day
        schedule = requests.post('https://www.wgte.org/schedule-update', data=payload)
        if schedule.status_code == 200:
            newDate = True
            response = schedule.text
            # Exits program when no schedule is posted
            if not schedule.text.__contains__('<div class="schedule-programs">'):
                if channel != '2':
                    break
                channel = '1'
                payload = {'year': str(payDate[0]), 'month': payDate[1], 'day': payDate[2], 'hours': '06-13', 'channels': channel}
                schedule = requests.post('https://www.wgte.org/schedule-update', data=payload)
                response = schedule.text
            
            # Reads every episode detail on PBS WHRO's Kids schedule
            while response.__contains__('<div class="schedule-programs">'):
                response = response[response.find('<div class="schedule-programs">')+41:]
                showTitle = response[response.find('"> ')+3:]
                showTitle = showTitle[:showTitle.find(':')]
                episodeTitle = response[response.find('<br /> ')+7:]
                episodeTitle = episodeTitle[:episodeTitle.find(' </a>')]
                
                response2 = response[:response.find('"')] # Episode page link
                # If episode title is not listed directly
                if showTitle.__contains__(f' </a></div>'):
                    showTitle = showTitle[:showTitle.find(f' </a></div>')]
                    episodeTitle = response2.split('/')[5]
                    episodeTitle = episodeTitle.replace('-', ' ')
                    episodeTitle = episodeTitle[0].capitalize() + episodeTitle[1:]
                
                # Skips episode if already checked
                if [showTitle, episodeTitle] in episodes:
                    continue
                
                timeCheck = datetime.strptime(response2.split('/')[7], "%H-%M-%S").time()
                if channel == '1' and timeCheck >= time(13, 00):
                    continue
                
                # Gets data from episode page
                response3 = requests.get(f'https://www.wgte.org{response2}') 
                if response3.status_code == 200 and (channel == '2' or timeCheck >= time(6, 00)):
                    description = response3.text
                    description = description[description.find(f'{episodeTitle}</h2>')+5:]
                    description = description[description.find('<p>')+3:]
                    description = description[:description.find('</p><p ')]
                    if description.__contains__('Receive info from WGTE') or description.__contains__('WGTE Passport'):
                        description = "No description available."
                    description = description.replace("&#039;", "'")
                    description = description.replace("&quot;", "'")
                    
                    newDate = response3.text[response3.text.find('class="table-bordered">')+47:]
                    newDate = newDate[newDate.find('</td><td>')+9:]
                    newDate = newDate[:newDate.find('</td><td>')].replace('/', '-')
                    newDate = datetime.strptime(newDate, "%m-%d-%Y")
                    newDate = newDate.strftime("%Y-%m-%d")
                    newDate = datetime.strptime(newDate, '%Y-%m-%d').date()
                    if newDate >= date:
                        if not [showTitle, episodeTitle] in episodes:
                            showTitle2 = showTitle.replace("&#039;", "'")
                            showTitle2 = showTitle2.replace("&quot;", "'")
                            showTitle2 = showTitle2.replace("&amp;", "&")
                            episodeTitle2 = episodeTitle.replace("&#039;", "'")
                            episodeTitle2 = episodeTitle2.replace("&quot;", "'")
                            episodeTitle2 = episodeTitle2.replace("&amp;", "&")
                            print(f'- {showTitle2}: {episodeTitle2} - {description}')
                    episodes.append([showTitle, episodeTitle])

def searchShow(showList):
    show = showList[int(input('Select show index here: '))]
    print(f'\n1 - Search {show[0]} episodes')
    print(f'2 - Search {show[0]} clips')
    match int(input('Select show material here: ')):
        case 1:
            os.system('cls') # Clears terminal; replace with os.system('clear') if on Unix/Linux/Mac
            print(f'{show[0]} Episode List:')
            
            episodeList = requests.get(f'https://producerplayer.services.pbskids.org/show-list/?shows={show[1]}&type=episode').json()
            IDList = []
            prodIDList = []
            videoList = []
            episodeList2 = []
            i = 0
            # Reads through show's data and saves/prints data
            for episode in episodeList['items']:
                IDList.append(episode['id'])
                prodIDList.append(episode['nola_episode'])
                videoList.append(episode['videos'][1]['url'])
                episodeList2.append(episode['title'])
                print(f"\n{i} - {episode['title']}: {episode['description_long']} (Released on: {episode['premiered_on']}, encored on: {episode['encored_on']}, expires on {str(episode['expirationdate'])[:10]})")
                print(f"Thumbnail: {episode['images']['kids-mezzannine-16x9']['url']}")
                i += 1
            index2 = int(input('Select episode index here: '))
            
            ydl_opts = {}
            os.system('cls') # Clears terminal; replace with os.system('clear') if on Unix/Linux/Mac
            
            # Runs yt-dlp through redirect link, and prints video info if valid link is found,
            # or an error message if link is invalid.
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(videoList[index2], download=False)
                    # ℹ️ ydl.sanitize_info makes the info json-serializable
                    print(json.dumps(ydl.sanitize_info(info)))
                    return
                except:
                    print(f"Episode '{episodeList2[index2]}' not currently available.")
                    return
        case 2:
            os.system('cls') # Clears terminal; replace with os.system('clear') if on Unix/Linux/Mac
            print(f'{show[0]} Clip List:')
            
            clipList = requests.get(f'https://producerplayer.services.pbskids.org/show-list/?shows={show[1]}&type=clip').json()
            IDList = []
            prodIDList = []
            videoList = []
            clipList2 = []
            i = 0
            # Reads through show's data and saves/prints data
            for clip in clipList['items']:
                IDList.append(clip['id'])
                prodIDList.append(clip['nola_episode'])
                videoList.append(clip['videos'][1]['url'])
                clipList2.append(clip['title'])
                print(f"\n{i} - {clip['title']}: {clip['description_long']} (Released on: {clip['premiered_on']}, encored on: {clip['encored_on']}, expires on {str(clip['expirationdate'])[:10]})")
                print(f"Thumbnail: {clip['images']['kids-mezzannine-16x9']['url']}")
                i += 1
            index2 = int(input('Select clip index here: '))
            
            ydl_opts = {}
            os.system('cls') # Clears terminal; replace with os.system('clear') if on Unix/Linux/Mac
            
            # Runs yt-dlp through redirect link, and prints video info if valid link is found,
            # or an error message if link is invalid.
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(videoList[index2], download=False)
                    # ℹ️ ydl.sanitize_info makes the info json-serializable
                    print(json.dumps(ydl.sanitize_info(info)))
                    return
                except:
                    print(f"Episode '{clipList2[index2]}' not currently available.")
                    return

# Retrieves JSON data from producer player, and performs an action based on the selected option
# 1 - Lists all shows in site data, and allows for manual navigation and selection of show info
# 2 - Searches all new episodes via PBS WGTE's data
# 3 - Searches all new episodes in producer player's data
# 4 - Searches all upcoming 'rotated' episodes in producer player's data
def main(navIndex):
    homeResponse = requests.get('https://content.services.pbskids.org/v2/kidspbsorg/home/').json()
    
    showlist = []
    for show in homeResponse['collections']['kids-programs-tier-1']['content']:
        showlist.append([show['title'], show['slug']])
    for show in homeResponse['collections']['kids-programs-tier-2']['content']:
        showlist.append([show['title'], show['slug']])
    for show in homeResponse['collections']['kids-programs-tier-3']['content']:
        showlist.append([show['title'], show['slug']])
        
    os.system('cls') # Clears terminal; replace with os.system('clear') if on Unix/Linux/Mac
    match navIndex:
        case 1: 
            i = 0
            print('Currently active shows on PBS Kids site:')
            for show in showlist:
                print(f'{i} - {show[0]}')
                i += 1
            searchShow(showlist)
        case 2:
            searchStation()
        case 3:
            searchFuture(showlist)
        case 4:
            searchFutureRot(showlist)
        case 5:
            searchFutureClip(showlist)
        case 6:
            searchExpired(showlist)

while True:
    os.system('cls') # Clears terminal; replace with os.system('clear') if on Unix/Linux/Mac
    print("Welcome to the PBS Producer Player navigator! This program is for learning purposes only, and should not be used to 'leak' unreleased materials (outside of episode synopsises/thumbnails). Please support the program(s) when they officially release via the PBS Kids Video App or through station broadcasts.")
    print("\n1 - Search producer list manually")
    print("2 - Search all upcoming episodes (WGTE, yields ~2 months ahead, read only)")
    print("3 - Search all upcoming (new) episodes (Producer, yields ~1 month ahead, read only)")
    print("4 - Search all upcoming (rotated) episodes (Producer, yields ~1 month ahead, read only)")
    print("5 - Search all upcoming (new) clips (Producer, yields ~1 month ahead, read only)")
    print("6 - Search all expired episodes (Producer, yields ~1 month ahead, read only)")
    print("0 - Exit program")
    
    # Option selection, ends program if 0 is entered
    navOption = int(input("Input option here: "))
    if navOption == 0:
        break
    main(navOption)
    
    # Rerun selection, ends program if 'n' is entered
    navContinue = input('Continue program? (y/n): ')
    if navContinue == 'n': break