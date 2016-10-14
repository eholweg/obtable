#
#  This is a minimal sample script showing how the individual data
#  are accessed from the decoded report.  To produce the standard text
#  summary of a report, the string() method of the Metar object.
#
#  The parsed data are stored as attributes of a Metar object.
#  Individual attributes are either strings. instances of one of the
#  metar.Datatypes classes, or lists of tuples of these scalars.
#  Here's a summary, adapted from the comments in the Metar.Metar.__init__()
#  method:
#
#    Attribute       Comments [data type]
#    --------------  --------------------
#    code             original METAR code [string]
#    type             METAR (routine) or SPECI (special) [string]
#    mod              AUTO (automatic) or COR (corrected) [string]
#    station_id       4-character ICAO station code [string]
#    time             observation time [datetime]
#    cycle            observation cycle (0-23) [int]
#    wind_dir         wind direction [direction]
#    wind_speed       wind speed [speed]
#    wind_gust        wind gust speed [speed]
#    wind_dir_from    beginning of range for win dir [direction]
#    wind_dir_to      end of range for wind dir [direction]
#    vis              visibility [distance]
#    vis_dir          visibility direction [direction]
#    max_vis          visibility [distance]
#    max_vis_dir      visibility direction [direction]
#    temp             temperature (C) [temperature]
#    dewpt            dew point (C) [temperature]
#    press            barometric pressure [pressure]
#    runway           runway visibility [list of tuples...]
#                        name [string]
#                        low  [distance]
#                        high [distance]
#    weather          present weather [list of tuples...]
#                        intensity     [string]
#                        description   [string]
#                        precipitation [string]
#                        obscuration   [string]
#                        other         [string]
#    recent           recent weather [list of tuples...]
#    sky              sky conditions [list of tuples...]
#                        cover   [string]
#                        height  [distance]
#                        cloud   [string]
#    windshear        runways w/ wind shear [list of strings]
#
#    press_sea_level  sea-level pressure [pressure]
#    wind_speed_peak  peak wind speed in last hour [speed]
#    wind_dir_peak    direction of peak wind speed in last hour [direction]
#    max_temp_6hr     max temp in last 6 hours [temperature]
#    min_temp_6hr     min temp in last 6 hours [temperature]
#    max_temp_24hr    max temp in last 24 hours [temperature]
#    min_temp_24hr    min temp in last 24 hours [temperature]
#    precip_1hr       precipitation over the last hour [precipitation]
#    precip_3hr       precipitation over the last 3 hours [precipitation]
#    precip_6hr       precipitation over the last 6 hours [precipitation]
#    precip_24hr      precipitation over the last 24 hours [precipitation]
#
#    _remarks         remarks [list of strings]
#    _unparsed        unparsed remarks [list of strings]
#
#  The metar.Datatypes classes (temperature, pressure, precipitation,
#  speed, direction) describe an observation and its units.  They provide
#  value() and string() methods to that return numerical and string
#  representations of the data in any of a number of supported units.
#
#  (You're going to have to study the source code for more details,
#  like the available methods and supported unit conversions for the
#  metar.Datatypes objects, etc..)

#  In particular, look at the Metar.string()
#  method, and the functions it calls.
#
#  Feb 4, 2005
#  Tom Pollard
#
from metar import Metar
import urllib
import re
import pytz
import datetime

dtgPat = '\w\w\w\s\d{1,2},\s\d\d\d\d\s-\s(.*)\w\w\w\s/\s.*'
wndPat = 'Wind:(.*):.*'
visPat = 'Vis.*:(.*)\sm.*:.*'
skyPat = 'Sky.*:(.*)'
tmpPat = 'Temp.*:(.*)F.*'
dewPat = 'Dew.*:(.*)F.*'
humPat = 'Relative.*:(.*)%'
prePat = 'Press.*:(.*)\sin.*'

local_tz = pytz.timezone('America/New_York')


def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)


def aslocaltimestr(utc_dt):
    return utc_to_local(utc_dt).strftime('%H:%M')


def getlocaltimezone(utc_dt):
    return utc_to_local(utc_dt).strftime('%Z')


localTZ = getlocaltimezone(datetime.datetime.utcnow())



obtable='<style type="text/css">'+ "\n"
obtable+='<!--'+ "\n"
obtable+='.obtab { font-size: 10px; font-family: Arial,Helvetica,san-serif; text-align:center; }'+ "\n"
obtable+='.obtableft { font-size: 10px; text-align:left; font-family: Arial,Helvetica,san-serif; }'+ "\n"
obtable+='.wht { background-color:#FFF; text-align:center; }'+ "\n"
obtable+='.color { background-color:#EEE; text-align:center; }'+ "\n"
obtable+='.tabbg { background-color: #202cb8; font-size: 120%; }'+ "\n"
obtable+='-->'+ "\n"
obtable+='</style>'+ "\n"

obtable += '<table border="0" cellpadding="0" cellspacing="0" width="90%">' + "\n"
obtable += '<tr><td bgcolor="#202CB8"><span style="color: #FFFFFF; font-weight: bold">&nbsp;Current Weather Observations... </span></td></tr>' + "\n"
obtable += '<tr><td>' + "\n"
obtable += '<table border="0" cellpadding="0" cellspacing="0" width="100%">' + "\n"
obtable += '<tr><td bgcolor="#202CB8">' + "\n"
obtable += '<table cellspacing="1" cellpadding="4" border="0" width="100%">' + "\n"
obtable += '<tr bgcolor="#fff2d9">' + "\n"
obtable += '<td class="obtab">Location</td>' + "\n"
obtable += '<td class="obtab">Time<br>(' + localTZ + ')</td>' + "\n"
obtable += '<td class="obtab">Weather</td>' + "\n"
obtable += '<td class="obtab">Vsby.<br>(SM)</td>' + "\n"
obtable += '<td class="obtab">Temp.<br>(&ordm;F)</td>' + "\n"
obtable += '<td class="obtab">Dewpt.<br>(&ordm;F)</td>' + "\n"
obtable += '<td class="obtab">Hum.<br>(%)</td>' + "\n"
obtable += '<td class="obtab">Wind<br>(mph)</td><td class="obtab">Wind<br>Chill (&ordm;F)</td><td class="obtab">Pres.<br>(in)</td></tr>' + "\n"

sites = dict([('KVJI', 'Abingdon VA'),
              ('KRHP', 'Andrews-Murphy NC'),
              ('KCHA', 'Chattanooga TN'),
              ('KCSV', 'Crossville TN'),
              ('KDNN', 'Dalton GA'),
              ('KTYS', 'Knoxville TN'),
              ('K1A6', 'Middlesboro KY'),
              ('KMOR', 'Morristown TN'),
              ('KOQT', 'Oak Ridge TN'),
              ('KJFZ', 'Tazewell Cnty VA'),
              ('KTRI', 'Tri-Cities TN'),
              ('KEKQ', 'Wayne Cnty KY'),
              ('KLNP', 'Wise VA'),
              ])

row = 0

for id, name in sites.items():
    # CAN USE stations IN PLACE OF decoded IF YOU WANT TO GET JUST THE RAW OBSERVATION
    link = "http://tgftp.nws.noaa.gov/data/observations/metar/decoded/" + id + ".TXT"
    observation = urllib.urlopen(link).read(10000)
    observation = observation.split("\n")

    href = 'http://w1.weather.gov/data/obhistory/' + id + '.html'

    for line in observation:
        matchdtg = re.match(dtgPat, line)
        if matchdtg:
            eventTime = matchdtg.group(1).strip()
            in_time = datetime.datetime.strptime(eventTime, "%I:%M %p")
            eventTime = datetime.datetime.strftime(in_time, "%H:%M")

        matchwnd = re.match(wndPat, line)
        if matchwnd:
            wind = matchwnd.group(1).strip()
            print wind
            #Have root wind... now need to break it out and format
            #Calm will not need to be further extracted

            #from pattern
            #With GUSTS    from\sthe\s(\w+)\s.*at\s(\d+)\s.*gusting.*(\d+).*
            wndFrmPat = 'from\sthe\s(\w+)\s.*at(\d+)\sMPH.*'
            matchFrmWnd = re.match(wndFrmPat, wind)
            if matchFrmWnd:
                wind = matchFrmWnd.group(1)+' '+ matchFrmWnd.group(2)

            #Variable pattern
            wndVarPat = 'Variable\sat\s(\d+).*'
            matchVarWnd = re.match(wndVarPat, wind)
            if matchVarWnd:
                wind='Vrbl '+matchVarWnd.group(1)

        matchvis = re.match(visPat, line)
        if matchvis:
            vsby = matchvis.group(1).strip()

        matchsky = re.match(skyPat, line)
        if matchsky:
            sky = matchsky.group(1).strip().title()

        matchtmp = re.match(tmpPat, line)
        if matchtmp:
            temp = int(round(float(matchtmp.group(1).strip())))
            temp = str(temp)

        matchdew = re.match(dewPat, line)
        if matchdew:
            dew = int(round(float(matchdew.group(1).strip())))
            dew = str(dew)

        matchhum = re.match(humPat, line)
        if matchhum:
            rh = matchhum.group(1).strip()

        matchpre = re.match(prePat, line)
        if matchpre:
            pres = matchpre.group(1).strip()

        wcHI = 'NA'

    if (row % 2 == 0):
        obtable += '<tr class="wht">'
    else:
        obtable += '<tr class="color">'

    row+=1

    obtable += '<td class="obtableft"><a href="' + href + '">' + name + '</a></td>'
    obtable += '<td class="obtab">' + eventTime + '</td>'
    obtable += '<td class="obtableft">' + sky + '</td>'
    obtable += '<td class="obtab">' + vsby + '</td>'
    obtable += '<td class="obtab">' + temp + '</td>'
    obtable += '<td class="obtab">' + dew + '</td>'
    obtable += '<td class="obtab">' + rh + '</td>'
    obtable += '<td class="obtableft">' + wind + '</td>'
    obtable += '<td class="obtab">' + wcHI + '</td>'
    obtable += '<td class="obtab">' + pres + '</td>'
    obtable += '</tr>' + "\n"




# matchOb=re.match(obPattern, line)
#
# result = re.search(r'my name is (\S+)', line)
#
# if matchOb:
#   code=line
#   # Initialize a Metar object with the coded report
#   obs = Metar.Metar(code)
#
#   print name
#   print "-----------------------------------------------------------------------"
#   print "METAR: ",code
#   print "-----------------------------------------------------------------------"
#
#   if(row%2==0):
#       obtable+='<tr class="wht">'
#   else:
#       obtable+='<tr class="color">'
#
#   eventTime=aslocaltimestr(obs.time)
#   href='http://w1.weather.gov/data/obhistory/'+id+'.html'
#   #vsby=obs.visibility()
#  #print obs.temp
#   #temp=int(round(obs.temp.string()))
#   #dew=int(round(obs.dewpt.string()))
#   #rh=int(round( (dew/temp) ))
#   #wind=obs.wind_dir+' '+obs.wind_speed
#   #wcHI='NA'
#   #pres=obs.press_sea_level
#
#
#   # Print the individual data
#   # obtable+='<td class="obtableft"><a href="'+href+'">'+name+'</a></td>'
#   # obtable+='<td class="obtab">'+eventTime+'</td>'
#   # obtable+='<td class="obtableft">&nbsp;</td>'
#   # obtable+='<td class="obtab">'+vsby+'</td>'
#   # obtable+='<td class="obtab">'+temp+'</td>'
#   # obtable+='<td class="obtab">'+dew+'</td>'
#   # obtable+='<td class="obtab">'+rh+'</td>'
#   # obtable+='<td class="obtableft">'+wind+'</td>'
#   # obtable+='<td class="obtab">'+wcHI+'</td>'
#   # obtable+='<td class="obtab">'+pres+'</td>'
#   # obtable+='</tr>'
#
#   # The 'station_id' attribute is a string.
#   print "station: %s" % obs.station_id
#
#   if obs.type:
#     print "type: %s" % obs.report_type()
#
#   # The 'time' attribute is a datetime object
#   if obs.time:
#     print "time: %s" % obs.time.ctime()
#
#   # The 'temp' and 'dewpt' attributes are temperature objects
#   if obs.temp:
#     print "temperature: %s" % obs.temp.string("C")
#
#   if obs.dewpt:
#     print "dew point: %s" % obs.dewpt.string("C")
#
#   # The wind() method returns a string describing wind observations
#   # which may include speed, direction, variability and gusts.
#   if obs.wind_speed:
#     print "wind: %s" % obs.wind()
#
#   # The peak_wind() method returns a string describing the peak wind
#   # speed and direction.
#   if obs.wind_speed_peak:
#     print "wind: %s" % obs.peak_wind()
#
#   # The visibility() method summarizes the visibility observation.
#   if obs.vis:
#     print "visibility: %s" % obs.visibility()
#
#   # The runway_visual_range() method summarizes the runway visibility
#   # observations.
#   if obs.runway:
#     print "visual range: %s" % obs.runway_visual_range()
#
#   # The 'press' attribute is a pressure object.
#   if obs.press:
#     print "pressure: %s" % obs.press.string("mb")
#
#   # The 'precip_1hr' attribute is a precipitation object.
#   if obs.precip_1hr:
#     print "precipitation: %s" % obs.precip_1hr.string("in")
#
#   # The present_weather() method summarizes the weather description (rain, etc.)
#   print "weather: %s" % obs.present_weather()
#
#   # The sky_conditions() method summarizes the cloud-cover observations.
#   print "sky: %s" % obs.sky_conditions("\n     ")
#
#   # The remarks() method describes the remark groups that were parsed, but
#   # are not available directly as Metar attributes.  The precipitation,
#   # min/max temperature and peak wind remarks, for instance, are stored as
#   # attributes and won't be listed here.
#   if obs._remarks:
#     print "remarks:"
#     print "- "+obs.remarks("\n- ")
#
#   print "-----------------------------------------------------------------------\n"
#

obtable += '</table>'
obtable += '</td></tr></table>'
obtable += '</td></tr></table>'

# OUTPUT THE TABLE TO FILE
print obtable

html = open('./obstable.html', 'w')
html.write(obtable)
html.close()
