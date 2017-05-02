import urllib
import re
import pytz
import datetime
from collections import OrderedDict
from AppT import *

dtgPat = '\w\w\w\s\d{1,2},\s\d\d\d\d\s-\s(.*)\w\w\w\s/\s.*'
wndPat = 'Wind:(.*):.*'
visPat = 'Vis.*:(.*)\sm.*:.*'
skyPat = 'Sky.*:(.*)'
wxPat = 'Weather.*:(.*)'
tmpPat = 'Temp.*:(.*)F.*'
dewPat = 'Dew.*:(.*)F.*'
humPat = 'Relative.*:(.*)%'
prePat = 'Press.*altimeter.*:(.*)\sin.*'

local_tz = pytz.timezone('America/New_York')


def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)


def aslocaltimestr(utc_dt):
    return utc_to_local(utc_dt).strftime('%H:%M')


def getlocaltimezone(utc_dt):
    return utc_to_local(utc_dt).strftime('%Z')


localTZ = getlocaltimezone(datetime.datetime.utcnow())

obtable = '<div class="boxit">' + "\n"
obtable += '<style type="text/css">' + "\n"
obtable += '<!--' + "\n"
obtable += '.obtab { font-size: 90%; font-family: Arial,Helvetica,san-serif; text-align:center; padding:3px; }' + "\n"
obtable += '.obtableft { font-size: 90%; text-align:left; font-family: Arial,Helvetica,san-serif; padding-left:6px; }' + "\n"
obtable += '.obtabrght { font-size: 90%; text-align:right; font-family: Arial,Helvetica,san-serif; padding-right:6px; }' + "\n"
obtable += '.wht { background-color:#FFF; text-align:center; }' + "\n"
obtable += '.color { background-color:#EEE; text-align:center; }' + "\n"
obtable += '.tabbg { background-color: #0071bc; font-size: 120%; }' + "\n"
obtable += '.tabhdr { color: #FFFFFF; font-weight: bold; font-family: Arial,Helvetica,san-serif; padding: 8px; }' + "\n"
obtable += '-->' + "\n"
obtable += '</style>' + "\n"

obtable += '<table border="0" cellpadding="0" cellspacing="0" width="100%">' + "\n"
obtable += '<tr><td bgcolor="#0071bc"><div class="title">&nbsp;Current Weather Observations... </div></td></tr>' + "\n"
obtable += '<tr><td>' + "\n"
obtable += '<table border="0" cellpadding="0" cellspacing="0" width="100%">' + "\n"
obtable += '<tr><td bgcolor="#202CB8">' + "\n"
obtable += '<table cellspacing="0" cellpadding="4" border="1" width="100%">' + "\n"
obtable += '<tr bgcolor="#fff2d9">' + "\n"
obtable += '<td class="obtab">Location</td>' + "\n"
obtable += '<td class="obtab">Time<br>(' + localTZ + ')</td>' + "\n"
obtable += '<td class="obtab">Weather</td>' + "\n"
obtable += '<td class="obtab">Vsby.<br>(SM)</td>' + "\n"
obtable += '<td class="obtab">Temp.<br>(&ordm;F)</td>' + "\n"
obtable += '<td class="obtab">Dewpt.<br>(&ordm;F)</td>' + "\n"
obtable += '<td class="obtab">Hum.<br>(%)</td>' + "\n"
obtable += '<td class="obtab">Wind<br>(mph)</td><td class="obtab">Wind Chill / Heat Index<br>(&ordm;F)</td><td class="obtab">Pres.<br>(in)</td></tr>' + "\n"

sites = OrderedDict([('KVJI', 'Abingdon VA'),
              ('KRHP', 'Andrews-Murphy NC'),
              ('KMMI', 'Athens TN'),
              ('KCHA', 'Chattanooga TN'),
              ('KRZR', 'Cleveland TN'),
              ('KCSV', 'Crossville TN'),
              ('KDNN', 'Dalton GA'),
              ('K0A9', 'Elizabethton TN'),
              ('KGKT', 'Gatlinburg-Pigeon Forge TN'),
              ('KJAU', 'Jacksboro TN'),
              ('KTYS', 'Knoxville TN (McGhee-Tyson)'),
              ('KDKX', 'Knoxville TN (Downtown)'),
              ('K0VG', 'Lee County VA'),
              ('K1A6', 'Middlesboro KY'),
              ('KMOR', 'Morristown TN'),
              ('KOQT', 'Oak Ridge TN'),
              ('KJFZ', 'Tazewell Cnty VA'),
              ('KTRI', 'Tri-Cities TN'),
              ('KEKQ', 'Wayne Cnty KY'),
              ('KBYL', 'Whitley County KY'),
              ('KLNP', 'Wise VA'),
              #('K', ''),
              #('KMFR', 'Test Site ND'),
              #('KCDR', 'Test New Site ND'),
              ])

row = 0
# CAN USE stations IN PLACE OF decoded IF YOU WANT TO GET JUST THE RAW OBSERVATION
obLink = 'http://tgftp.nws.noaa.gov/data/observations/metar/decoded/'
obHistory='http://www.wrh.noaa.gov/zoa/getobext.php?sid='

for id, name in sites.items():
    print id
    # CAN USE stations IN PLACE OF decoded IF YOU WANT TO GET JUST THE RAW OBSERVATION
    link = obLink + id + ".TXT"
    observation = urllib.urlopen(link).read(10000)
    observation = observation.split("\n")

    href = obHistory + id

    tableWx=''

    for line in observation:
        matchdtg = re.match(dtgPat, line)
        if matchdtg:
            eventTime = matchdtg.group(1).strip()
            in_time = datetime.datetime.strptime(eventTime, "%I:%M %p")
            eventTime = datetime.datetime.strftime(in_time, "%H:%M")

        matchwnd = re.match(wndPat, line)
        if matchwnd:
            wind = matchwnd.group(1).strip()
            #print wind
            wndSpd = '0'
            # Have root wind... now need to break it out and format
            # Calm will not need to be further extracted
            if wind.startswith('Calm'):
                wind = "CALM"
                wndSpd = 0
            elif wind.startswith('Variable'):
                #print("Going into wind var")
                wndVarPat = 'Variable\sat\s(\d+).*'
                matchVarWnd = re.match(wndVarPat, wind)
                if matchVarWnd:
                    wind = 'VRB ' + matchVarWnd.group(1)
                    wndSpd = matchVarWnd.group(1)
                else:
                    wnd = 'NA'
                    wndSpd = '0'
            else:
                wndFrmGustPat = 'from\sthe\s(\w+)\s.*at\s(\d+)\s.*gusting\sto.*\s(\d+)\sMPH.*'
                matchFrmGustWnd = re.match(wndFrmGustPat, wind)
                if matchFrmGustWnd:
                    wind = matchFrmGustWnd.group(1) + ' ' + matchFrmGustWnd.group(2) + 'G' + matchFrmGustWnd.group(3)
                    wndSpd=matchFrmGustWnd.group(2)
                else:
                    # NO GUST INFO IS AVAILABLE
                    wndFrmPat = 'from\sthe\s(\w+)\s.*at\s(\d+)\sMPH.*'
                    matchFrmWnd = re.match(wndFrmPat, wind)
                    if matchFrmWnd:
                        wind = matchFrmWnd.group(1) + ' ' + matchFrmWnd.group(2)
                        wndSpd = matchFrmWnd.group(2)
                    else:
                        # CANNOT PARSE WIND DATA
                        wind = 'NA'
                        wndSpd = '0'
            windSpeed=int(wndSpd)

        matchvis = re.match(visPat, line)
        if matchvis:
            vsby = matchvis.group(1).strip()

        matchwx = re.match(wxPat, line)
        if matchwx:
            wx = matchwx.group(1).strip().title()
            wx = wx.replace("; ", "&nbsp;&bsol;&nbsp;")
            #print(wx)

        matchsky = re.match(skyPat, line)
        if matchsky:
            sky = matchsky.group(1).strip().title()

        matchtmp = re.match(tmpPat, line)
        if matchtmp:
            appT_t=float(matchtmp.group(1))
            temp = str(int(round(float(matchtmp.group(1)))))

        matchdew = re.match(dewPat, line)
        if matchdew:
            #print(matchdew.group(1))
            appT_d=float(matchdew.group(1))
            dew = str(int(round(float(matchdew.group(1)))))

        matchhum = re.match(humPat, line)
        if matchhum:
            rh = matchhum.group(1).strip()

        matchpre = re.match(prePat, line)
        if matchpre:
            #print(line)
            pval=matchpre.group(1).strip()
            #print(pval)
            if len(pval) < 3:
                pval = pval + ".00"
            elif len(pval) < 5:
                pval = pval + "0"
            pres = pval

    try:
        tableWx=wx
        del wx
    except NameError:
        try:
            tableWx=sky
            del sky
        except NameError:
            tableWx=''

    if (row % 2 == 0):
        obtable += '<tr class="wht">'
    else:
        obtable += '<tr class="color">'

    #Calculate Wind Chill or Heat Index
    W=array([int(windSpeed)])
    T=array([float(appT_t)])
    TD=array([float(appT_d)])

    apparentT = AppT(T, TD, W, T)
    # print(apparentT[0])
    # print(round(apparentT[0],0))
    # print("\n----\n")
    appTVal=int(round(apparentT[0],0))
    if appTVal>90:
        wcHI=str(appTVal) + " [HI]"
    elif appTVal<45 and windSpeed>4:
        wcHI=str(appTVal) + " [WC]"
    else:
        wcHI="-"

    row += 1
    obtable += '<td class="obtableft"><a href="' + href + '">' + name + '</a></td>'
    obtable += '<td class="obtab">' + eventTime + '</td>'
    obtable += '<td class="obtableft">' + tableWx + '</td>'
    obtable += '<td class="obtab">' + vsby + '</td>'
    obtable += '<td class="obtab">' + temp + '</td>'
    obtable += '<td class="obtab">' + dew + '</td>'
    obtable += '<td class="obtab">' + rh + '</td>'
    obtable += '<td class="obtabrght">' + wind + '</td>'
    obtable += '<td class="obtab">' + wcHI + '</td>'
    obtable += '<td class="obtab">' + pres + '</td>'
    obtable += '</tr>' + "\n"

# Finalize The Ob Table
obtable += '</table>'
obtable += '</td></tr></table>'
obtable += '</td></tr></table>'
obtable += '</div>'

# OUTPUT THE OB TABLE TO FILE
# print obtable

html = open('./obstable.html', 'w')
html.write(obtable)
html.close()