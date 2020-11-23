import re
import time
import telepot
import random
import requests
import pyshorteners
from datetime import datetime as dt
from index1 import search
from watchorder import watchsearch
from list_manager import adder, list_search, purge, check, ret
from timer import time_purge, save, ttime, tcheck
from bs4 import BeautifulSoup as soup
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton


def guesser(chat_id):
    url = "https://www.randomanime.org/sitemap.xml"
    req = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    so = soup(req.content, "html.parser")
    links = so.find_all("loc")
    links_filtered = []
    for i in range(len(links)):
        links[i] = links[i].getText()
        if links[i].find("/anime/") != -1:
            links_filtered.append(links[i])
    choose_url = random.choice(links_filtered)
    name = choose_url[34:len(choose_url) - 1]
    name = re.sub(r"-", " ", name)
    req = requests.get(choose_url, headers={'User-Agent': 'Mozilla/5.0'})
    so = soup(req.content, "html.parser")
    image = so.find("picture")
    image = image.find("img")
    image = image.attrs["src"][2:]
    bot.sendPhoto(chat_id, image, caption="OwO, Guess this anime. Type /owo and name to guess")
    now = dt.now()
    now = now.strftime("%H:%M:%S")
    save(chat_id, now)
    adder(chat_id, name)

def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    q = pyshorteners.Shortener(api_key="0043dd9b0dbb97eca53e2fc23b84cfd8a493816b")
    if (content_type == 'text') and ("#request" in msg['text'].lower()):
        if ('reply_to_message' in msg.keys()):
            if str(msg['reply_to_message']['chat']['id']) == "-1001308073740":
                reply = msg['reply_to_message']
                from_id = reply['from']['id']
                name = reply['from']['first_name']
                if 'username' in reply['from'].keys():
                    name = name + " @" + reply['from']['username']
                query = reply['text']
                request_total = "ID: " + str(from_id) + "\nName: " + name + "\nRequest: " + query
                bot.sendMessage("-1001308073740", "Submitted your desires to admins "  + name + " kun!!",
                                reply_to_message_id=msg['message_id'])
                bot.sendMessage("-1001467729523", request_total)
        else:
            if(str(chat_id) == "-1001308073740"):
                from_id = msg['message']['from']['id']
                name = msg['message']['from']['first_name']
                if 'username' in msg['message']['from'].keys():
                    name = name + " @" + msg['message']['from']['username']
                query = msg['text']
                request_total = "ID: " + str(from_id) + "\nName: " + name + "\nRequest: " + query
                bot.sendMessage("-1001308073740",
                                "Submitted your desires to admins " + name + " kun!!",
                                reply_to_message_id=msg['message_id'])
                bot.sendMessage("-1001467729523", request_total)
    if content_type == 'text':
        if msg['text'][:6] == '/guess':
            if (tcheck(chat_id) == True):
                now = dt.now()
                now = now.strftime("%H:%M:%S")
                if (ttime(str(now), chat_id) == True):
                    bot.sendMessage(chat_id, "Already Guessing!!!", reply_to_message_id=msg['message_id'])
                else:
                    bot.sendMessage(chat_id, "last one was '" + str(check(chat_id)) + "' nobody guessed correctly."
                                    + " Sending a new one now!!")
                    guesser(chat_id)
            else:
                guesser(chat_id)

        elif (msg['text'][:4] == '/owo'):
            if (msg['text'][4] == "@"):
                s = msg['text'][17:]
            else:
                s = msg['text'][4:]
            now = dt.now()
            now = now.strftime("%H:%M:%S")
            if (check(chat_id) == True) and (ttime(now, chat_id) == True):
                if list_search(s, chat_id):
                    bot.sendMessage(chat_id, "OwO you got that right!!! \nAnime was " + str(ret(chat_id)),
                                    reply_to_message_id=msg['message_id'])
                    purge(chat_id)
                    time_purge(chat_id)
                else:
                    bot.sendMessage(chat_id, "That's not right!!!", reply_to_message_id=msg['message_id'])
            elif (check(chat_id) == True) and (ttime(now, chat_id) == False):
                bot.sendMessage(chat_id, "Oops you ran out of time... \n Type /guess to play again...",
                                reply_to_message_id=msg['message_id'])
                purge(chat_id)
                time_purge(chat_id)
            else:
                bot.sendMessage(chat_id, "Not guessing anything right now \n Type /guess to play again...")
    group_id = chat_id
    chat_id = msg['from']['id']
    if content_type == 'text':
        if msg['text'][:7] == '/search':
            if ((msg['text'].lower() == '/search') or ((msg['text'].lower()[:7] == '/search')
                                                       and (msg['text'][-13:] == '@Any_Animebot')) or msg[
                                                                                                          'text'].lower()[
                                                                                                      :20] == "/search@Any_Animebot"):
                bot.sendDocument(group_id, "https://i.imgur.com/BhiVTHg.gif", caption="/search     <αηιмє ηαмє>")
            else:
                s = msg['text'][8:]
                s = re.sub('\W+', ' ', s)
                surl2 = 'https://gogoanime.so//search.html?keyword=' + str("%20".join(s.lower().split()))
                r = requests.get(surl2, headers={'User-Agent': 'Mozilla/5.0'})
                page_soup = soup(r.content, "html.parser")
                title = page_soup.find_all('p', class_='name')
                for i in range(len(title)):
                    title[i] = title[i].find('a')
                inl = []
                for tit in title:
                    name = tit.attrs['title']
                    lob = tit.attrs['href']
                    if (len(lob[10:]) > 40):
                        link = q.bitly.short('https://gogoanime.so' + lob)
                        inl.append(
                            [InlineKeyboardButton(text=str(name[:20]) + "...." + str(name[-23:]), parse_mode='Markdown',
                                                  callback_data=link + "%ab#" + str(chat_id))])
                    else:
                        inl.append([InlineKeyboardButton(text=str(name), parse_mode='Markdown',
                                                         callback_data=str(lob)[10:] + "@ab#" + str(chat_id))])
                if ('username' in msg['from']):
                    bot.sendMessage('1152801694',
                                    msg['text'] + " " + msg['from']['first_name'] + " @" + msg['from']['username'])
                else:
                    bot.sendMessage('1152801694', msg['text'] + " " + msg['from']['first_name'])
                bot.sendMessage(group_id, "RESULTS", reply_markup=InlineKeyboardMarkup(inline_keyboard=inl))

        elif msg['text'][:11] == "/watchorder":
            if ((msg['text'].lower() == '/watchorder') or ((msg['text'].lower()[:11] == '/watchorder')
                                                        and (msg['text'][-13:] == '@Any_Animebot')) or msg[
                                                        'text'].lower()[:24] == "/watchorder@Any_Animebot"):
                bot.sendDocument(group_id, "https://i.imgur.com/CsZZEDE.gif",
                                 caption="/watchorder <𝔰𝔥𝔬𝔯𝔱 𝔫𝔞𝔪𝔢>")
            else:
                result = watchsearch(msg['text'][12:])
                if len(result) == 0:
                    bot.sendMessage(group_id, "OwO nothing found")
                else:
                    inl = []
                    for i in result.keys():
                        if (len(inl) > 10):
                            break
                        else:
                            inl.append([InlineKeyboardButton(text=i, url=result[i])])
                    bot.sendMessage(group_id, "Results", reply_markup=InlineKeyboardMarkup(inline_keyboard=inl))


        elif msg['text'][:6] == '/index':
            if ((msg['text'].lower() == '/index') or ((msg['text'].lower()[:6] == '/index')
                                                      and (msg['text'][-13:] == '@Any_Animebot')) or msg[
                                                                                                         'text'].lower()[
                                                                                                     :19] == "/index@Any_Animebot"):
                bot.sendDocument(group_id, "https://i.imgur.com/n7p6W5i.gif", caption="/index  <𝖇𝖊𝖌𝖎𝖓 𝖜𝖎𝖙𝖍>")
            else:
                s = msg['text'][7:]
                if (s.find("#") != -1):
                    bot.sendMessage(group_id, "# in word is forbidden")
                else:
                    result = search(s)
                    if (len(result) == 0):
                        bot.sendMessage(group_id, "OwO nothing with that keyword")
                    else:
                        count = len(result)
                        if (count <= 20):
                            res = ""
                            for i in result:
                                res += i
                            bot.sendMessage(group_id, res)
                        else:
                            res = ""
                            for i in range(20):
                                res += result[i]
                            inl = []
                            inl.append(InlineKeyboardButton(text="N/A", parse_mode='Markdown', callback_data="hshsh"))
                            inl.append(InlineKeyboardButton(text="1", parse_mode='Markdown', callback_data="jsjhs"))
                            inl.append(InlineKeyboardButton(text=">>", parse_mode='Markdown',
                                                            callback_data=s + "*2*#" + str(chat_id)))
                            bot.sendMessage(group_id, res + "\n \n Query:" + s + ", Use the slider to jump pages ",
                                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[inl]))

        elif msg['text'][:8] == '/updates':
            surl4 = 'https://gogoanime.so/'
            r = requests.get(surl4, headers={'User-Agent': 'Mozilla/5.0'})
            souper = soup(r.content, "html.parser")
            tit = souper.find_all('p', class_='name')
            for i in range(len(tit)):
                tit[i] = tit[i].find('a')
            for l in range(len(tit)):
                tit[l] = tit[l].attrs['href'][1:]
            inl = []
            for it in tit:
                cou = 0
                ep = ""
                for i in range(-1, -20, -1):
                    if (cou < 1 and it[i] == "-"):
                        cou += 1
                        ep = it[i + 1:]
                    elif (cou == 1 and it[i] == "-"):
                        cou += 1
                        it = it[:i]
                if (len(it) > 40):
                    link = q.bitly.short('https://gogoanime.so/' + it + "-episode-" + ep)
                    inl.append([InlineKeyboardButton(text=str(it) + "Ep" + ep, parse_mode='Markdown',
                                                     callback_data=link + "%li#" + str(chat_id))])
                else:
                    inl.append([InlineKeyboardButton(text=str(it) + " Ep " + ep, parse_mode='Markdown',
                                                     callback_data=str(it) + "@" + ep + "li#" + str(chat_id))])
            bot.sendMessage(group_id, "Latest Updates in anime world",
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=inl))

        elif msg['text'][:5] == '/help':
            bot.sendMessage(group_id,
                            "Commands: \n /search + plus the name of the anime \n /index + beginning word \n /updates for latest updates in anime \n \nif something doesn't work contact @Ransom_s")


def check_chat_id(poster, clicker):
    if (poster == clicker):
        return True
    else:
        return False


def about(url, chat_id, group_id, typ):
    q = pyshorteners.Shortener(api_key="0043dd9b0dbb97eca53e2fc23b84cfd8a493816b")
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    so = soup(r.content, 'html.parser')
    abo = so.find_all('p', class_='type')
    abo[0] = str(abo[0].find('span').getText()) + str(abo[0].find('a').attrs['title'])
    abo[1] = str(abo[1].getText())
    x = abo[2].find_all('a')
    s = ""
    for i in range(len(x)):
        s += x[i].getText()
    abo[2] = str(abo[2].find('span').getText()) + s
    s = ""
    abo[3] = str(abo[3].getText())
    abo[4] = str(abo[4].getText())
    abo[5] = str(abo[5].getText())
    img = so.find('div', class_='anime_info_body')
    img = img.find('img')
    img = img.attrs['src']
    abo.append("Episodes: " + str(so.find('a', class_='active').getText()))
    for i in range(len(abo)):
        s = s + abo[i] + '\n' + '\n'
    try:
        bot.sendPhoto(group_id, img)
    except Exception as e:
        print("Oops!", e.__class__, "occurred.")
    bot.sendMessage(group_id, s)
    inl = []
    if (typ == "%"):
        link = q.bitly.short(url)
        inl.append(
            [InlineKeyboardButton(text="Download", parse_mode='Markdown', callback_data=link + "%ep#" + str(chat_id))])
    else:
        link = url[30:]
        inl.append(
            [InlineKeyboardButton(text="Download", parse_mode='Markdown', callback_data=link + "@ep#" + str(chat_id))])
    bot.sendMessage(group_id, "Choose your episode from the list",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=inl))


def episode_matrix(url_main, chat_id, ide, typ):
    q = pyshorteners.Shortener(api_key="0043dd9b0dbb97eca53e2fc23b84cfd8a493816b")
    r = requests.get(url_main, headers={'User-Agent': 'Mozilla/5.0'})
    so = soup(r.content, 'html.parser')
    abo = so.find('a', class_='active')
    abo = abo.attrs['ep_end']
    inl = []
    if (typ == "%"):
        if (int(abo) <= 28):
            temp = []
            for i in range(1, int(abo) + 1):
                if (i % 7 == 0):
                    url = "https://gogoanime.so/" + url_main[30:] + "-episode-" + str(i)
                    url = q.bitly.short(url)
                    temp.append(InlineKeyboardButton(text=str(i), parse_mode='Markdown',
                                                     callback_data=url + "%li#" + str(chat_id)))
                    inl.append(temp)
                    temp = []
                else:
                    url = "https://gogoanime.so/" + url_main[30:] + "-episode-" + str(i)
                    url = q.bitly.short(url)
                    temp.append(InlineKeyboardButton(text=str(i), parse_mode='Markdown',
                                                     callback_data=url + "%li#" + str(chat_id)))
                    if (i == int(abo)):
                        inl.append(temp)
            bot.editMessageReplyMarkup(ide, reply_markup=InlineKeyboardMarkup(inline_keyboard=inl))

        elif (int(abo) // 28 == 1):
            temp = []
            for i in range(1, 26):
                if (i % 7 == 0):
                    url = "https://gogoanime.so/" + url_main[30:] + "-episode-" + str(i)
                    url = q.bitly.short(url)
                    temp.append(InlineKeyboardButton(text=str(i), parse_mode='Markdown',
                                                     callback_data=url + "%li#" + str(chat_id)))
                    inl.append(temp)
                    temp = []
                else:
                    url = "https://gogoanime.so/" + url_main[30:] + "-episode-" + str(i)
                    url = q.bitly.short(url)
                    temp.append(InlineKeyboardButton(text=str(i), parse_mode='Markdown',
                                                     callback_data=url + "%li#" + str(chat_id)))
                    if (i == 25):
                        inl.append(temp)
            url_main = q.bitly.short(url_main)
            inl[3].append(InlineKeyboardButton(text="26-" + str(abo), parse_mode='Markdown',
                                               callback_data=url_main + "%26-" + str(abo) + "/#" + str(chat_id)))
            bot.editMessageReplyMarkup(ide, reply_markup=InlineKeyboardMarkup(inline_keyboard=inl))

        else:
            temp = []
            rem = int(abo) // 16
            for i in range(1, 16):
                low = rem * i - (rem - 1)
                high = rem * i
                if (i % 4 == 0):
                    url_main = q.bitly.short(url_main)
                    temp.append(InlineKeyboardButton(text=str(low) + "-" + str(high), parse_mode='Markdown',
                                                     callback_data=url_main + "%" + str(low) + "-" + str(
                                                         high) + "/#" + str(chat_id)))
                    inl.append(temp)
                    temp = []
                else:
                    url_main = q.bitly.short(url_main)
                    temp.append(InlineKeyboardButton(text=str(low) + "-" + str(high), parse_mode='Markdown',
                                                     callback_data=url_main + "%" + str(low) + "-" + str(
                                                         high) + "/#" + str(chat_id)))
                    if (i == 15):
                        inl.append(temp)
            inl[3].append(InlineKeyboardButton(text=str(rem * 15 + 1) + "-" + str(abo), parse_mode='Markdown',
                                               callback_data=url_main + "%" + str(rem * 15 + 1) + "-" + str(abo) +
                                                             "/#" + str(chat_id)))
            bot.editMessageReplyMarkup(ide, reply_markup=InlineKeyboardMarkup(inline_keyboard=inl))
    else:
        if (int(abo) <= 28):
            temp = []
            for i in range(1, int(abo) + 1):
                if (i % 7 == 0):
                    url = url_main[30:]
                    temp.append(InlineKeyboardButton(text=str(i), parse_mode='Markdown',
                                                     callback_data=url + "@" + str(i) + "li#" + str(chat_id)))
                    inl.append(temp)
                    temp = []
                else:
                    url = url_main[30:]
                    temp.append(InlineKeyboardButton(text=str(i), parse_mode='Markdown',
                                                     callback_data=url + "@" + str(i) + "li#" + str(chat_id)))
                    if (i == int(abo)):
                        inl.append(temp)
            bot.editMessageReplyMarkup(ide, reply_markup=InlineKeyboardMarkup(inline_keyboard=inl))
        elif (int(abo) // 28 == 1):
            temp = []
            for i in range(1, 26):
                if (i % 7 == 0):
                    url = url_main[30:]
                    temp.append(InlineKeyboardButton(text=str(i), parse_mode='Markdown',
                                                     callback_data=url + "@" + str(i) + "li#" + str(chat_id)))
                    inl.append(temp)
                    temp = []
                else:
                    url = url_main[30:]
                    temp.append(InlineKeyboardButton(text=str(i), parse_mode='Markdown',
                                                     callback_data=url + "@" + str(i) + "li#" + str(chat_id)))
                    if (i == 25):
                        inl.append(temp)
            inl[3].append(InlineKeyboardButton(text="26-" + str(abo), parse_mode='Markdown',
                                               callback_data=url_main[30:] + "@26-" + str(abo) + "/#" + str(chat_id)))
            bot.editMessageReplyMarkup(ide, reply_markup=InlineKeyboardMarkup(inline_keyboard=inl))

        else:
            temp = []
            rem = int(abo) // 16
            for i in range(1, 16):
                low = rem * i - (rem - 1)
                high = rem * i
                if (i % 4 == 0):
                    temp.append(InlineKeyboardButton(text=str(low) + "-" + str(high), parse_mode='Markdown',
                                                     callback_data=url_main[30:] + "@" + str(low) + "-" + str(
                                                         high) + "/#" + str(chat_id)))
                    inl.append(temp)
                    temp = []
                else:
                    temp.append(InlineKeyboardButton(text=str(low) + "-" + str(high), parse_mode='Markdown',
                                                     callback_data=url_main[30:] + "@" + str(low) + "-" + str(
                                                         high) + "/#" + str(chat_id)))
                    if (i == 15):
                        inl.append(temp)
            inl[3].append(InlineKeyboardButton(text=str(rem * 15 + 1) + "-" + str(abo), parse_mode='Markdown',
                                               callback_data=url_main[30:] + "@" + str(rem * 15 + 1) + "-" + str(abo) +
                                                             "/#" + str(chat_id)))
            bot.editMessageReplyMarkup(ide, reply_markup=InlineKeyboardMarkup(inline_keyboard=inl))


def range_expand(url_main, low, high, typ, chat_id, ide):
    q = pyshorteners.Shortener(api_key="0043dd9b0dbb97eca53e2fc23b84cfd8a493816b")
    if (typ == "%"):
        url = q.bitly.expand(url_main)
        inl = []
        if (high - low + 1 <= 16):
            temp = []
            for i in range(1, high - low + 2):
                if (i % 4 == 0):
                    url = "https://gogoanime.so/" + url[30:] + "-episode-" + str(i)
                    url = q.bitly.short(url)
                    temp.append(InlineKeyboardButton(text=str(low - 1 + i), parse_mode='Markdown',
                                                     callback_data=url + "%li#" + str(chat_id)))
                    inl.append(temp)
                    temp = []
                else:
                    url = "https://gogoanime.so/" + url[30:] + "-episode-" + str(i)
                    url = q.bitly.short(url)
                    temp.append(InlineKeyboardButton(text=str(low - 1 + i), parse_mode='Markdown',
                                                     callback_data=url + "%li#" + str(chat_id)))
            inl.append(temp)
            inl.append(
                [InlineKeyboardButton(text="Back", parse_mode='Markdown',
                                      callback_data=url_main + "%ep#" + str(chat_id))])
            bot.editMessageReplyMarkup(ide, reply_markup=InlineKeyboardMarkup(inline_keyboard=inl))


        elif ((high - low + 1) // 16 == 1):
            temp = []
            for i in range(1, 16):
                if (i % 4 == 0):
                    url = "https://gogoanime.so/" + url[30:] + "-episode-" + str(i)
                    url = q.bitly.short(url)
                    temp.append(InlineKeyboardButton(text=str(low - 1 + i), parse_mode='Markdown',
                                                     callback_data=url + "%li#" + str(chat_id)))
                    inl.append(temp)
                    temp = []
                else:
                    url = "https://gogoanime.so/" + url[30:] + "-episode-" + str(i)
                    url = q.bitly.short(url)
                    temp.append(InlineKeyboardButton(text=str(low - 1 + i), parse_mode='Markdown',
                                                     callback_data=url + "%li#" + str(chat_id)))
                    if (i == 15):
                        inl.append(temp)
            inl[3].append(InlineKeyboardButton(text=str(low + 15) + "-" + str(high), parse_mode='Markdown',
                                               callback_data=url_main + "%" + str(low + 15) + "-" + str(
                                                   high) + "/#" + str(chat_id)))
            inl.append(
                [InlineKeyboardButton(text="Back", parse_mode='Markdown',
                                      callback_data=url_main + "%ep#" + str(chat_id))])
            bot.editMessageReplyMarkup(ide, reply_markup=InlineKeyboardMarkup(inline_keyboard=inl))

        else:
            temp = []
            rem = (high - low + 1) // 16
            slow = shigh = 0
            for i in range(1, 16):
                slow = low + rem * i - (rem - 1) - 1
                shigh = low + rem * i - 1
                if (i % 4 == 0):
                    temp.append(InlineKeyboardButton(text=str(slow) + "-" + str(shigh), parse_mode='Markdown',
                                                     callback_data=url_main + "%" + str(slow) + "-" + str(
                                                         shigh) + "/#" + str(chat_id)))
                    inl.append(temp)
                    temp = []
                else:
                    temp.append(InlineKeyboardButton(text=str(slow) + "-" + str(shigh), parse_mode='Markdown',
                                                     callback_data=url_main + "%" + str(slow) + "-" + str(
                                                         shigh) + "/#" + str(chat_id)))
                    if (i == 15):
                        inl.append(temp)
            inl[3].append(InlineKeyboardButton(text=str(low + rem * 15) + "-" + str(high), parse_mode='Markdown',
                                               callback_data=url_main
                                                             + "%" + str(low + rem * 15) + "-" + str(high) + "/#" + str(
                                                   chat_id)))
            inl.append(
                [InlineKeyboardButton(text="Back", parse_mode='Markdown',
                                      callback_data=url_main + "%ep#" + str(chat_id))])
            bot.editMessageReplyMarkup(ide, reply_markup=InlineKeyboardMarkup(inline_keyboard=inl))
    else:
        inl = []
        if (high - low + 1 <= 16):
            temp = []
            for i in range(1, high - low + 2):
                if (i % 4 == 0):
                    temp.append(InlineKeyboardButton(text=str(low - 1 + i), parse_mode='Markdown',
                                                     callback_data=url_main + "@" + str(
                                                         low - 1 + i) + "li#" + str(chat_id)))
                    inl.append(temp)
                    temp = []
                else:
                    temp.append(InlineKeyboardButton(text=str(low - 1 + i), parse_mode='Markdown',
                                                     callback_data=url_main + "@" + str(
                                                         low - 1 + i) + "li#" + str(chat_id)))
            inl.append(temp)
            inl.append(
                [InlineKeyboardButton(text="Back", parse_mode='Markdown',
                                      callback_data=url_main + "@ep#" + str(chat_id))])
            bot.editMessageReplyMarkup(ide, reply_markup=InlineKeyboardMarkup(inline_keyboard=inl))


        elif ((high - low + 1) // 16 == 1):
            temp = []
            for i in range(1, 16):
                if (i % 4 == 0):
                    temp.append(InlineKeyboardButton(text=str(low - 1 + i), parse_mode='Markdown',
                                                     callback_data=url_main + "@" + str(
                                                         low - 1 + i) + "li#" + str(chat_id)))
                    inl.append(temp)
                    temp = []
                else:
                    temp.append(InlineKeyboardButton(text=str(low - 1 + i), parse_mode='Markdown',
                                                     callback_data=url_main + "@" + str(
                                                         low - 1 + i) + "li#" + str(chat_id)))
                    if (i == 15):
                        inl.append(temp)
            inl[3].append(InlineKeyboardButton(text=str(low + 15) + "-" + str(high), parse_mode='Markdown',
                                               callback_data=url_main + "@" + str(low + 15) + "-" + str(
                                                   high) + "/#" + str(chat_id)))
            inl.append(
                [InlineKeyboardButton(text="Back", parse_mode='Markdown',
                                      callback_data=url_main + "@ep#" + str(chat_id))])
            bot.editMessageReplyMarkup(ide, reply_markup=InlineKeyboardMarkup(inline_keyboard=inl))

        else:
            temp = []
            rem = (high - low + 1) // 16
            slow = shigh = 0
            for i in range(1, 16):
                slow = low + rem * i - (rem - 1) - 1
                shigh = low + rem * i - 1
                if (i % 4 == 0):
                    temp.append(InlineKeyboardButton(text=str(slow) + "-" + str(shigh), parse_mode='Markdown',
                                                     callback_data=url_main + "@" + str(slow) + "-" + str(
                                                         shigh) + "/#" + str(chat_id)))
                    inl.append(temp)
                    temp = []
                else:
                    temp.append(InlineKeyboardButton(text=str(slow) + "-" + str(shigh), parse_mode='Markdown',
                                                     callback_data=url_main + "@" + str(slow) + "-" + str(
                                                         shigh) + "/#" + str(chat_id)))
                    if (i == 15):
                        inl.append(temp)
            inl[3].append(InlineKeyboardButton(text=str(low + rem * 15) + "-" + str(high), parse_mode='Markdown',
                                               callback_data=url_main
                                                             + "@" + str(low + rem * 15) + "-" + str(high) + "/#" + str(
                                                   chat_id)))
            inl.append(
                [InlineKeyboardButton(text="Back", parse_mode='Markdown',
                                      callback_data=url_main + "@ep#" + str(chat_id))])
            bot.editMessageReplyMarkup(ide, reply_markup=InlineKeyboardMarkup(inline_keyboard=inl))


def on_callback_query(msg):
    query_id, chat_id, query_data = telepot.glance(msg, flavor='callback_query')
    group_id = msg['message']['chat']['id']
    ide = (group_id, msg['message']['message_id'])
    q = pyshorteners.Shortener(api_key="0043dd9b0dbb97eca53e2fc23b84cfd8a493816b")
    # query_data = s.bitly.expand(query_data)
    hash_position = query_data.find("#")
    if (check_chat_id(query_data[hash_position + 1:], str(chat_id)) == False):
        bot.answerCallbackQuery(query_id, text="Not your query!!", show_alert=True)
    else:
        if (query_data[hash_position - 2:hash_position] == "ab"):
            bot.editMessageReplyMarkup(ide, reply_markup=None)
            if (query_data[hash_position - 3] == "%"):
                url = q.bitly.expand(query_data[:hash_position - 3])
                about(url, chat_id, group_id, "%")
            else:
                url = "https://gogoanime.so/category/" + query_data[:hash_position - 3]
                about(url, chat_id, group_id, "@")
        elif (query_data[hash_position - 2:hash_position] == "ep"):
            if (query_data[hash_position - 3] == "%"):
                url = q.bitly.expand(query_data[:hash_position - 3])
                episode_matrix(url, chat_id, ide, "%")
            else:
                url = "https://gogoanime.so/category/" + query_data[:hash_position - 3]
                episode_matrix(url, chat_id, ide, "@")
        elif (query_data[hash_position - 1] == "/"):
            s = query_data[:hash_position - 1]
            m = s
            low = high = pos = 0
            q = ""
            for i in range(-2, -13, -1):
                if (s[i] == "@" or s[i] == "%"):
                    pos = i
                    typ = s[i]
            s = s[pos + 1:]
            for i in s:
                if (i == "-"):
                    low = int(q)
                    q = ""
                else:
                    q = q + i
            high = int(q)
            range_expand(m[:pos], low, high, typ, chat_id, ide)

        elif (query_data[hash_position - 1] == "*"):
            s = query_data[:hash_position - 1]
            num = ""
            for i in range(-1, -5, -1):
                if (s[i] == "*"):
                    pos = i
                    break
                else:
                    num += s[i]
            num = int(num[::-1])
            result = search(s[:pos])
            res = ""
            if (20 * num >= len(result)):
                end = len(result)
            else:
                end = 20 * num
            for i in range(20 * (num - 1), end):
                res += result[i]
            bot.editMessageText((group_id, msg['message']['message_id']), res)
            inl = []
            if (num == 1):
                inl.append(InlineKeyboardButton(text="N/A", parse_mode='Markdown', callback_data="hshsh"))
                inl.append(InlineKeyboardButton(text=str(num), parse_mode='Markdown', callback_data="jsjhs"))
            else:
                inl.append(InlineKeyboardButton(text="<< " + str(num - 1), parse_mode='Markdown',
                                                callback_data=s[:pos] + "*" + str(num - 1) + "*#" + str(chat_id)))
                inl.append(InlineKeyboardButton(text=str(num), parse_mode='Markdown', callback_data="jsjhs"))
            if (end == len(result)):
                inl.append(InlineKeyboardButton(text="end", parse_mode='Markdown', callback_data="dhddh"))
            else:
                inl.append(InlineKeyboardButton(text=str(num + 1) + " >>", parse_mode='Markdown',
                                                callback_data=s[:pos] + "*" + str(num + 1) + "*#" + str(chat_id)))
            bot.editMessageReplyMarkup(ide, reply_markup=InlineKeyboardMarkup(inline_keyboard=[inl]))

        elif (query_data[hash_position - 2:hash_position] == "li"):
            if (query_data[hash_position - 3] == "%"):
                url = query_data[:hash_position - 3]
                url_gogo = q.bitly.expand(url)
                m = url_gogo.find("episode")
                back_url = "https://gogoanime.so/category/" + url_gogo[21:m - 1]
                back_url = q.bitly.short(back_url)
                num = ""
                for i in range(-1, -6, -1):
                    if (url_gogo[i] == "-"):
                        break
                    else:
                        num += url_gogo[i]
                num = num[::-1]
                inl = []
                login = {'_csrf': 0,
                         'email': 'ransomsumit@aol.com',
                         'password': 'Beluga#44'}
                with requests.Session() as s:
                    url1 = "https://gogoanime.so/login.html"
                    r = s.get(url1, headers={'User-Agent': 'Mozilla/5.0'})
                    soupy = soup(r.content, 'html.parser')
                    t = soupy.find('meta', attrs={'name': "csrf-token"})['content']
                    login['_csrf'] = t
                    r = s.post(url1, data=login, headers={'User-Agent': 'Mozilla/5.0'})
                    r = r.text
                    req = s.get(url_gogo, headers={'User-Agent': 'Mozilla/5.0'})
                    page_soup = soup(req.content, "html.parser")
                    title = page_soup.find_all('div', class_='cf-download')
                    if (len(title) > 0):
                        title = title[0].find_all('a')

                        for i in range(len(title)):
                            tex = title[i].getText()
                            title[i] = title[i].attrs['href']
                            inl.append([InlineKeyboardButton(text="Ep " + num + " " + tex, url=title[i])])
                    inl.append([InlineKeyboardButton(text="Back", parse_mode='Markdown',
                                                     callback_data=back_url + "%ep#" + str(chat_id))])
                    bot.editMessageReplyMarkup(ide, reply_markup=InlineKeyboardMarkup(inline_keyboard=inl))

            else:
                s = query_data[:hash_position - 2]
                num = ""
                pos = 0
                for i in range(-1, -6, -1):
                    if (s[i] == "@"):
                        pos = i
                        break
                    else:
                        num += s[i]
                num = num[::-1]
                url = "https://gogoanime.so/" + s[:pos] + "-episode-" + str(num)
                back_url = s[:pos]
                inl = []
                login = {'_csrf': 0,
                         'email': 'ransomsumit@aol.com',
                         'password': 'Beluga#44'}
                with requests.Session() as s:
                    url1 = "https://gogoanime.so/login.html"
                    r = s.get(url1, headers={'User-Agent': 'Mozilla/5.0'})
                    soupy = soup(r.content, 'html.parser')
                    t = soupy.find('meta', attrs={'name': "csrf-token"})['content']
                    login['_csrf'] = t
                    r = s.post(url1, data=login, headers={'User-Agent': 'Mozilla/5.0'})
                    r = r.text
                    req = s.get(url, headers={'User-Agent': 'Mozilla/5.0'})
                    page_soup = soup(req.content, "html.parser")
                    title = page_soup.find_all('div', class_='cf-download')
                    if (len(title) > 0):
                        title = title[0].find_all('a')

                        for i in range(len(title)):
                            tex = title[i].getText()
                            title[i] = title[i].attrs['href']
                            inl.append([InlineKeyboardButton(text="Ep " + num + " " + tex, url=title[i])])
                    inl.append([InlineKeyboardButton(text="Back", parse_mode='Markdown',
                                                     callback_data=back_url + "@ep#" + str(chat_id))])
                    bot.editMessageReplyMarkup(ide, reply_markup=InlineKeyboardMarkup(inline_keyboard=inl))


TOKEN = '1382346231:AAFovu38e6OnV0qRqAg7wMmgmw9MZ6ImVUk'

bot = telepot.Bot(TOKEN)
MessageLoop(bot, {'chat': on_chat_message,
                  'callback_query': on_callback_query}).run_as_thread()
print('Listening ...')

while 1:
    time.sleep(10)
