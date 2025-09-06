import json
import requests
import os
import yt_dlp

from datetime import datetime, timedelta

def searchFuture(showList):
    os.system('cls') # Clears terminal; replace with os.system('clear') if on Unix/Linux/Mac
    print('All Upcoming Episodes Available on PBS Kids Player:')
    for show in showList:
        showPrint = show.replace ("&", 'and')
        showPrint = showPrint.replace (' ', '-')
        showPrint = showPrint.replace ('!', '')
        showPrint = showPrint.replace ('?', '')
        showPrint = showPrint.replace ("'", '')
        showPrint = showPrint.replace ("Peg + Cat", 'Peg') # After this message thingy, we'll figure out why PBS has this show ID'd like this
        episodeList = requests.get(f'https://producerplayer.services.pbskids.org/show-list/?shows={showPrint}&type=episode')
        if episodeList.status_code == 200 and 'items' in episodeList.json():
            for episode in episodeList.json()['items']:
                date_object = datetime.strptime(episode['premiered_on'], '%Y-%m-%d').date()
                if date_object >= datetime.now().date():
                    print(f"\n{show}: {episode['title']} - {episode['description_long']} (Releases on: {episode['premiered_on']})")
                    print(f"Thumbnail: {episode['images']['kids-mezzannine-16x9']['url']}")

def searchStation():
    os.system('cls') # Clears terminal; replace with os.system('clear') if on Unix/Linux/Mac
    start_date = datetime.now().date()
    episodes = []
    # Reads all dates between now and a year from now
    for i in range(0, 366):
        date = start_date + timedelta(days=i)
        url = f'https://schedule.whro.org/tv?date={date}&station=TVKIDS'

        # Send a GET request to fetch the webpage content (Returns None if page fails)
        schedule = requests.get(url)
        if (schedule.status_code) == 200:
            newDate = True
            response = schedule.text
            # Exits program when no schedule is posted (date limit reached)
            if response.__contains__('Selected date has no programs to display.'):
                break
            
            # Reads every episode detail on PBS WHRO's Kids schedule
            while response.__contains__("<p class='mb0'>"):
                response = response[response.find("<p class='mb0'>")+15:]
                response2 = response[:response.find("<div class='col-md-1 pl2 airtime time'>")]
                showtime = response2[:response2.find('</p>')] # Air time of show
                # Show name
                show = response2[response2.find("<a href='/program?programid=")+28:]
                show = show[show.find("'>")+2:show.find("</a>")+1]
                # Episode name
                episode = 'episode-0'
                if not response2.__contains__("<h3 class='episodeTitle my0'> "):
                    episode = response2[response2.find("<h3 class='episodeTitle my0'>")+29:response2.find('</h3>')]
                episode = episode.replace(' / ', '/')
                show = show[:show.find("</a>")]
                desc = 'No description available.'
                if response2.__contains__("<p class='episodeDesc mb0 mt1 font-light'>"):
                    desc = response2[response2.find("<p class='episodeDesc mb0 mt1 font-light'>")+42:response2.find("</p></div><div class='col-md-2'>")]
                # If new episode is detected, crosscheck with PBS WGTE for potential mislabeling
                # (some already aired episodes labeled as 'new' on WHRO)
                if episode not in episodes and response2.__contains__("<span class='new'>"):
                    crossShow = show.replace(' ', '-')
                    crossShow = crossShow.replace("'", '')
                    crossShow = crossShow.replace(' + ', '')
                    crossShow = crossShow.replace(' & ', '-and-')
                    crossShow = crossShow.replace(':-', '-')
                    crossShow = crossShow.replace('!', '')
                    crossEpisode = episode[:episode.find(' <span')].replace('episode-', 'episode-0')
                    crossEpisode = crossEpisode.replace(' ', '-')
                    crossEpisode = crossEpisode.replace('/', '-')
                    crossEpisode = crossEpisode.replace("'", '')
                    crossEpisode = crossEpisode.replace(',', '')
                    crossDate = date.strftime("%m/%d/%Y").replace('/', '-')
                    crossTime = showtime.replace(':', '-')
                    if crossTime[1] == '-':
                        crossTime = '0' + crossTime
                    crossResponse = requests.get(f'https://www.wgte.org/schedules/program/kids/{crossShow}/{crossEpisode}/{crossDate}/{crossTime}-00')
                    # If page exists on PBS WGTE
                    if crossResponse.text.__contains__('Previous Episodes'):
                        crossText = crossResponse.text[crossResponse.text.find('</td><td>')+9:]
                        crossText = crossText[crossText.find('</td><td>')+9:]
                        # If new episode hasn't aired (according to WGTE)
                        if crossText[:crossText.find('</td>')] == crossDate.replace('-', '/'):
                            # If first new episode entry on date
                            if newDate:
                                print(f'\nNew episodes for {date}:')
                                newDate = False
                            episodes.append(episode)
                            episodeNew = episode[:episode.find(' <span ')]
                            desc = crossResponse.text[crossResponse.text.find('</h2><p>')+8:crossResponse.text.find('</p><p class="channel">')]
                            if crossResponse.text.__contains__(')<p>'):
                                desc = crossResponse.text[crossResponse.text.find(')<p>')+4:crossResponse.text.find('</p><p class="channel">')]
                            desc = desc.replace('&#039;', "'")
                            desc = desc.replace('&quot;', "'")
                            print(f'{show}: {episodeNew} - {desc}')
                    else:
                        crossTime = str(int(crossTime[:crossDate.find(':')-2])+12) + '-' + crossTime[crossDate.find(':')-1:]
                        crossResponse = requests.get(f'https://www.wgte.org/schedules/program/kids/{crossShow}/{crossEpisode}/{crossDate}/{crossTime}-00')
                        # If page exists on PBS WGTE
                        if crossResponse.text.__contains__('Previous Episodes'):
                            crossText = crossResponse.text[crossResponse.text.find('</td><td>')+9:]
                            crossText = crossText[crossText.find('</td><td>')+9:]
                            # If new episode hasn't aired (according to WGTE)
                            if crossText[:crossText.find('</td>')] == crossDate.replace('-', '/'):
                                # If first new episode entry on date
                                if newDate:
                                    print(f'\nNew episodes for {date}:')
                                    newDate = False
                                episodes.append(episode)
                                episodeNew = episode[:episode.find(' <span ')]
                                desc = crossResponse.text[crossResponse.text.find('</h2><p>')+8:crossResponse.text.find('</p><p class="channel">')]
                                if crossResponse.text.__contains__(')<p>'):
                                    desc = crossResponse.text[crossResponse.text.find(')<p>')+4:crossResponse.text.find('</p><p class="channel">')]
                                desc = desc.replace('&#039;', "'")
                                desc = desc.replace('&quot;', "'")
                                print(f'{show}: {episodeNew} - {desc}')
                        # If new episode but page does not exist on WGTE
                        elif episode not in episodes:
                            episodes.append(episode)
                            episodeNew = episode[:episode.find(' <span')]
                            if newDate:
                                newDate = False
                            programID = response2.split("data-program_id='")[1]
                            programID = programID.split("'")[0]
                            response3 = requests.get(f'https://schedule.whro.org/program?programid={programID}')
                            if response3.status_code == 200:
                                response3 = response3.text.split(episodeNew)[1]
                                response3 = response3.split('</p></div>')[0]
                                if not response3.__contains__("<span class='new'>NEW</span></h3></div>"):
                                    continue
                                print(f'\nNew episodes for {date}:')
                                desc = response3.split('<div class="episodeDesc font-light"><p class="mt0">')[1]
                                print(f'{show}: {episodeNew} - {desc}')
                            else:
                                print(f'{show}: {episodeNew} - {desc}')

def searchShow(showList):
    show = showList[int(input('Select show index here: '))]
    show = show.replace ("&", 'and')
    show = show.replace (' ', '-')
    show = show.replace ('!', '')
    show = show.replace ('?', '')
    show = show.replace ("'", '')
    show = show.replace ("Peg + Cat", 'Peg') # After this message thingy, we'll figure out why PBS has this show ID'd like this
    
    episodeList = requests.get(f'https://producerplayer.services.pbskids.org/show-list/?shows={show}&type=episode').json()
    os.system('cls') # Clears terminal; replace with os.system('clear') if on Unix/Linux/Mac
    IDList = []
    prodIDList = []
    videoList = []
    i = 0
    print('Episode List:')
    for episode in episodeList['items']:
        IDList.append(episode['id'])
        prodIDList.append(episode['nola_episode'])
        videoList.append(episode['videos'][1]['url'])
        print(f"{i} - {episode['title']}: {episode['description_long']}")
        i += 1
    index2 = int(input('Select show index here: '))
    
    ydl_opts = {}
    # Runs yt-dlp through each link, printing an error message if link is invalid,
    # and prints info and breaks if valid link is found
    os.system('cls') # Clears terminal; replace with os.system('clear') if on Unix/Linux/Mac
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(videoList[index2], download=False)
            # ℹ️ ydl.sanitize_info makes the info json-serializable
            print(json.dumps(ydl.sanitize_info(info)))
            return
        except:
            secretID = int(input('Video not found, input secret ID here): '))
            while True:
                print(id)
                newURL = f'https://kids.pbs-video.pbs.org/videos//{show}/{id}/{secretID}/hd-16x9-mezzanine-1080p/{prodID}-ep-dvi-en-'
                ydl_opts = {}
                # Runs yt-dlp through each link, printing an error message if link is invalid,
                # and prints info and breaks if valid link is found
                try:
                    info = ydl.extract_info(newURL, download=False)
                    # ℹ️ ydl.sanitize_info makes the info json-serializable
                    print(json.dumps(ydl.sanitize_info(info)))
                    break
                except:
                    print("Error.")
                id += 1   

def main(navIndex):
    homeResponse = requests.get('https://content.services.pbskids.org/v2/kidspbsorg/home/').json()
    
    showlist = []
    for show in homeResponse['collections']['kids-programs-tier-1']['content']:
        showlist.append(show['title'])
    for show in homeResponse['collections']['kids-programs-tier-2']['content']:
        showlist.append(show['title'])
    for show in homeResponse['collections']['kids-programs-tier-3']['content']:
        showlist.append(show['title'])
        
    match navIndex:
        case 0: 
            i = 0
            print('\nCurrently active shows on PBS Kids site:')
            for show in showlist:
                print(f'{i} - {show}')
                i += 1
            searchShow(showlist)
        case 1:
            searchStation()
            print("\nNote: Some episodes may not have descriptions on WHRO, please double-check listings via WGTE to find descriptions, as they are usually the samr between stations.")
        case 2:
            searchFuture(showlist)

os.system('cls') # Clears terminal; replace with os.system('clear') if on Unix/Linux/Mac
print("Welcome to the PBS Producer Player navigator! This program is for learning purposes only, and should not be used to 'leak' unreleased materials (outside of episode synopsises/thumbnails). Please support the program(s) when they officially release via the PBS Kids Video App or through station broadcasts.")
print("\n0 - Search producer list manually")
print("1 - Search all upcoming episodes (Station, yields ~2 months ahead, read only)")
print("2 - Search all upcoming episodes (Producer, yields ~1 month ahead, read only)")
main(int(input("Input option here: ")))
input("\nClick any button to finish the program:")