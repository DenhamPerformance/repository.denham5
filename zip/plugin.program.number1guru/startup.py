################################################################################
#      Copyright (C) 2015 Surfacingx                                           #
#                                                                              #
#  This Program is free software; you can redistribute it and/or modify        #
#  it under the terms of the GNU General Public License as published by        #
#  the Free Software Foundation; either version 2, or (at your option)         #
#  any later version.                                                          #
#                                                                              #
#  This Program is distributed in the hope that it will be useful,             #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of              #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
#  GNU General Public License for more details.                                #
#                                                                              #
#  You should have received a copy of the GNU General Public License           #
#  along with XBMC; see the file COPYING.  If not, write to                    #
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.       #
#  http://www.gnu.org/copyleft/gpl.html                                        #
################################################################################

import os, sys, glob
import re
import uservar
from datetime import date, datetime, timedelta
import six
from kodi_six import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs
# Py2
try:
    from urllib import quote_plus

# Py3:
except ImportError:
    from urllib.parse import quote_plus


from resources.libs import extract, downloader, notify, loginit, debridit, traktit, skinSwitch, uploadLog, wizard as wiz
                                   
if six.PY2:
    reload(sys)
    sys.setdefaultencoding("utf-8")

xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Settings.ResetSettingValue", "params":{"setting":"debug.showloginfo"},"id":1}')
KODIV            = float(xbmc.getInfoLabel("System.BuildVersion")[:4])
transPath  = xbmc.translatePath if KODIV < 19 else xbmcvfs.translatePath
LOGNOTICE = xbmc.LOGNOTICE if KODIV < 19 else xbmc.LOGINFO
ADDON_ID       = uservar.ADDON_ID
ADDONTITLE     = uservar.ADDONTITLE
ADDON          = wiz.addonId(ADDON_ID)
VERSION        = wiz.addonInfo(ADDON_ID,'version')
ADDONPATH      = wiz.addonInfo(ADDON_ID,'path')
ADDONID        = wiz.addonInfo(ADDON_ID,'id')
DIALOG         = xbmcgui.Dialog()
DP             = xbmcgui.DialogProgress()
HOME           = transPath('special://home/')
PROFILE        = transPath('special://profile/')
KODIHOME       = transPath('special://xbmc/')
ADDONS         = os.path.join(HOME,     'addons')
KODIADDONS     = os.path.join(KODIHOME, 'addons')
USERDATA       = os.path.join(HOME,     'userdata')
PLUGIN         = os.path.join(ADDONS,   ADDON_ID)
PACKAGES       = os.path.join(ADDONS,   'packages')
ADDONDATA      = os.path.join(USERDATA, 'addon_data', ADDON_ID)
TEXTCACHE      = os.path.join(ADDONDATA, 'Cache')
FANART         = os.path.join(ADDONPATH,'fanart.jpg')
ICON           = os.path.join(ADDONPATH,'icon.png')
ART            = os.path.join(ADDONPATH,'resources', 'art')
ADVANCED       = os.path.join(USERDATA, 'advancedsettings.xml')
SKIN           = xbmc.getSkinDir()
BUILDNAME      = wiz.getS('buildname')
DEFAULTSKIN    = wiz.getS('defaultskin')
DEFAULTNAME    = wiz.getS('defaultskinname')
DEFAULTIGNORE  = wiz.getS('defaultskinignore')
BUILDVERSION   = wiz.getS('buildversion')
BUILDLATEST    = wiz.getS('latestversion')
BUILDCHECK     = wiz.getS('lastbuildcheck')
DISABLEUPDATE  = wiz.getS('disableupdate')
AUTOCLEANUP    = wiz.getS('autoclean')
AUTOCACHE      = wiz.getS('clearcache')
AUTOPACKAGES   = wiz.getS('clearpackages')
AUTOTHUMBS     = wiz.getS('clearthumbs')
AUTOFEQ        = wiz.getS('autocleanfeq')
AUTONEXTRUN    = wiz.getS('nextautocleanup')
TRAKTSAVE      = wiz.getS('traktlastsave')
REALSAVE       = wiz.getS('debridlastsave')
                                           
LOGINSAVE      = wiz.getS('loginlastsave')
KEEPTRAKT      = wiz.getS('keeptrakt')
KEEPREAL       = wiz.getS('keepdebrid')
                                       
KEEPLOGIN      = wiz.getS('keeplogin')
INSTALLED      = wiz.getS('installed')
EXTRACT        = wiz.getS('extract')
EXTERROR       = wiz.getS('errors')
NOTIFY         = wiz.getS('notify')
NOTEDISMISS    = wiz.getS('notedismiss')
NOTEID         = wiz.getS('noteid')
BACKUPLOCATION = ADDON.getSetting('path') if not ADDON.getSetting('path') == '' else HOME
MYBUILDS       = os.path.join(BACKUPLOCATION, 'My_Builds', '')
NOTEID         = 0 if NOTEID == "" else int(NOTEID)
AUTOFEQ        = int(AUTOFEQ) if AUTOFEQ.isdigit() else 0
TODAY          = date.today()
TOMORROW       = TODAY + timedelta(days=1)
TWODAYS        = TODAY + timedelta(days=2)
THREEDAYS      = TODAY + timedelta(days=3)
ONEWEEK        = TODAY + timedelta(days=7)
SKINCHECK      = ['skin.aftermath.zephyr', 'skin.aftermath.silvo', 'skin.aftermath.simple', 'skin.ccm.aftermath']
RAM            = int(xbmc.getInfoLabel("System.Memory(total)")[:-2])
KODIV          = float(xbmc.getInfoLabel("System.BuildVersion")[:4])
EXCLUDES       = uservar.EXCLUDES
BUILDFILE      = uservar.BUILDFILE
UPDATECHECK    = uservar.UPDATECHECK if str(uservar.UPDATECHECK).isdigit() else 1
NEXTCHECK      = TODAY + timedelta(days=UPDATECHECK)
NOTIFICATION   = uservar.NOTIFICATION
ENABLE         = uservar.ENABLE
HEADERMESSAGE  = uservar.HEADERMESSAGE
AUTOUPDATE     = uservar.AUTOUPDATE
WIZARDFILE     = uservar.WIZARDFILE
AUTOINSTALL    = uservar.AUTOINSTALL
REPOID         = uservar.REPOID
REPOADDONXML   = uservar.REPOADDONXML
REPOZIPURL     = uservar.REPOZIPURL
COLOR1         = uservar.COLOR1
COLOR2         = uservar.COLOR2
WORKING        = True if wiz.workingURL(BUILDFILE) == True else False
FAILED         = False

##############################################
####SHOW BUILDS DEPENDING THE KODI VERSION####
##############################################
if 16 <= KODIV < 17:
    wiz.setS('show15', 'false')
    wiz.setS('show17', 'false')
    wiz.setS('show18', 'false')
    wiz.setS('show19', 'false')
    wiz.setS('show16', 'true')

elif 17 <= KODIV < 18:
    wiz.setS('show15', 'false')
    wiz.setS('show16', 'false')
    wiz.setS('show18', 'false')
    wiz.setS('show19', 'false')
    wiz.setS('show17', 'true')

elif 18 <= KODIV < 19:
    wiz.setS('show15', 'false')
    wiz.setS('show16', 'false')
    wiz.setS('show17', 'false')
    wiz.setS('show19', 'false')
    wiz.setS('show18', 'true')

elif 19 <= KODIV < 20:
    wiz.setS('show15', 'false')
    wiz.setS('show16', 'false')
    wiz.setS('show17', 'false')
    wiz.setS('show18', 'false')
    wiz.setS('show19', 'true')

else:
    wiz.setS('show16', 'false')
    wiz.setS('show17', 'false')
    wiz.setS('show18', 'false')
    wiz.setS('show19', 'false')
    wiz.setS('show15', 'true')
###########################
#### Check Updates   ######
###########################
def checkUpdate():
    BUILDNAME      = wiz.getS('buildname')
    BUILDVERSION   = wiz.getS('buildversion')
    bf             = wiz.textCache(BUILDFILE)
    if bf == False: return
    link           = bf.decode('utf-8').replace('\n','').replace('\r','').replace('\t','')
    match          = re.compile('name="%s".+?ersion="(.+?)".+?con="(.+?)".+?anart="(.+?)"' % BUILDNAME).findall(link)
    if len(match) > 0:
        version = match[0][0]
        icon    = match[0][1]
        fanart  = match[0][2]
        wiz.setS('latestversion', version)
        if version > BUILDVERSION:
            if DISABLEUPDATE == 'false':
                wiz.log("[Check Updates] [Installed Version: %s] [Current Version: %s] Opening Update Window" % (BUILDVERSION, version), LOGNOTICE)
                notify.updateWindow(BUILDNAME, BUILDVERSION, version, icon, fanart)
            else: wiz.log("[Check Updates] [Installed Version: %s] [Current Version: %s] Update Window Disabled" % (BUILDVERSION, version), LOGNOTICE)
        else: wiz.log("[Check Updates] [Installed Version: %s] [Current Version: %s]" % (BUILDVERSION, version), LOGNOTICE)
    else: wiz.log("[Check Updates] ERROR: Unable to find build version in build text file", xbmc.LOGERROR)

def checkInstalled():
    current = ''
    for skin in SKINCHECK:
        skinpath = os.path.join(ADDONS,skin)
        if os.path.exists(skinpath):
            current = skin
    if current == SKINCHECK[0]:
        yes_pressed = DIALOG.yesno(ADDONTITLE,"[COLOR orchid]Aftermath[/COLOR] Zephyr is currently outdated and is no longer being updated.", "Please download one of the newer community builds.", yeslabel="Build Menu", nolabel="Ignore")
        if yes_pressed: xbmc.executebuiltin('ActivateWindow(10025 , "plugin://%s/?mode=builds", return)' % ADDON_ID)
        else: DIALOG.ok(ADDONTITLE, 'You can still install a community build from the [COLOR orchid]Aftermath[/COLOR] Wizard.')
    elif current == SKINCHECK[1]:
        yes_pressed = DIALOG.yesno(ADDONTITLE,"[COLOR orchid]Aftermath[/COLOR] Silvo is currently outdated and is no longer being updated.", "Please download one of the newer community builds.", yeslabel="Build Menu", nolabel="Ignore")
        if yes_pressed: xbmc.executebuiltin('ActivateWindow(10025 , "plugin://%s/?mode=builds", return)' % ADDON_ID)
        else: DIALOG.ok(ADDONTITLE, 'You can still install a community build from the [COLOR orchid]Aftermath[/COLOR] Wizard.')
    elif current == SKINCHECK[2]:
        if KODIV >= 16:
            gui   = os.path.join(ADDOND, SKINCHECK[2], 'settings.xml')
            f     = xbmcvfs.File(gui); g = f.read(); f.close()
            match = re.compile('<setting id=\"SubSettings.3.Label\" type=\"string\">(.+?)<\/setting>').findall(g)
            if len(match):
                name, build, ver = match[0].replace('[COLOR orchid]','').replace('[/COLOR]','').split(' ')
            else:
                build = "Simple"
                ver = "v0.1"
        else:
            gui   = os.path.join(USERDATA,'guisettings.xml')
            f     = xbmcvfs.File(gui); g = f.read(); f.close()
            match = re.compile('<setting type=\"string\" name=\"skin.aftermath.simple.SubSettings.3.Label\">(.+?)<\/setting>').findall(g)
            name, build, ver = match[0].replace('[COLOR orchid]','').replace('[/COLOR]','').split(' ')
        wiz.setS('buildname', 'Aftermath %s' % build)
        wiz.setS('buildversion', ver[1:])
        wiz.setS('lastbuildcheck', str(NEXTCHECK))
        checkUpdate()
    elif current == SKINCHECK[3]:
        yes_pressed = DIALOG.yesno(ADDONTITLE,"[COLOR orchid]Aftermath[/COLOR] CCM is currently outdated and is no longer being updated.", "Please download one of the newer community builds.", yeslabel="Build Menu", nolabel="Ignore")
        if yes_pressed: xbmc.executebuiltin('ActivateWindow(10025 , "plugin://%s/?mode=builds", return)' % ADDON_ID)
        else: DIALOG.ok(ADDONTITLE, 'You can still install a community build from the [COLOR orchid]Aftermath[/COLOR] Wizard.')
    else:
        notify.firstRunSettings()
        notify.firstRun()

def writeAdvanced():
    if RAM > 1536: buffer = '209715200'
    else: buffer = '104857600'
    with xbmcvfs.File(ADVANCED, 'w') as f:
        f.write('<advancedsettings>\n')
        f.write('   <network>\n')
        f.write('       <buffermode>2</buffermode>\n')
        f.write('       <cachemembuffersize>%s</cachemembuffersize>\n' % buffer)
        f.write('       <readbufferfactor>5</readbufferfactor>\n')
        f.write('       <curlclienttimeout>10</curlclienttimeout>\n')
        f.write('       <curllowspeedtime>10</curllowspeedtime>\n')
        f.write('   </network>\n')
        f.write('</advancedsettings>\n')
    f.close()

def checkSkin():
    wiz.log("[Build Check] Invalid Skin Check Start")
    DEFAULTSKIN   = wiz.getS('defaultskin')
    DEFAULTNAME   = wiz.getS('defaultskinname')
    DEFAULTIGNORE = wiz.getS('defaultskinignore')
    gotoskin = False
    if not DEFAULTSKIN == '':
        if os.path.exists(os.path.join(ADDONS, DEFAULTSKIN)):
            if DIALOG.yesno(ADDONTITLE, "[COLOR %s]It seems that the skin has been set back to [COLOR %s]%s[/COLOR][CR]Would you like to set the skin back to:[/COLOR][CR][COLOR %s]%s[/COLOR]" % (COLOR2, COLOR1, SKIN[5:].title(), COLOR1, DEFAULTNAME)):
                gotoskin = DEFAULTSKIN
                gotoname = DEFAULTNAME
            else: wiz.log("Skin was not reset", LOGNOTICE); wiz.setS('defaultskinignore', 'true'); gotoskin = False
        else: wiz.setS('defaultskin', ''); wiz.setS('defaultskinname', ''); DEFAULTSKIN = ''; DEFAULTNAME = ''
    if DEFAULTSKIN == '':
        skinname = []
        skinlist = []
        for folder in glob.glob(os.path.join(ADDONS, 'skin.*/')):
            xml = "%s/addon.xml" % folder
            if os.path.exists(xml):
                f  = xbmcvfs.File(xml); g = f.read().replace('\n','').replace('\r','').replace('\t',''); f.close();
                match  = wiz.parseDOM(g, 'addon', ret='id')
                match2 = wiz.parseDOM(g, 'addon', ret='name')
                wiz.log("%s: %s" % (folder, str(match[0])), LOGNOTICE)
                if len(match) > 0: skinlist.append(str(match[0])); skinname.append(str(match2[0]))
                else: wiz.log("ID not found for %s" % folder, LOGNOTICE)
            else: wiz.log("ID not found for %s" % folder, LOGNOTICE)
        if len(skinlist) > 0:
            if len(skinlist) > 1:
                if DIALOG.yesno(ADDONTITLE, "[COLOR %s]It seems that the skin has been set back to [COLOR %s]%s[/COLOR] Would you like to view a list of avaliable skins?[/COLOR]" % (COLOR2, COLOR1, SKIN[5:].title())):
                    choice = DIALOG.select("Select skin to switch to!", skinname)
                    if choice == -1: wiz.log("Skin was not reset", LOGNOTICE); wiz.setS('defaultskinignore', 'true')
                    else:
                        gotoskin = skinlist[choice]
                        gotoname = skinname[choice]
                else: wiz.log("Skin was not reset", LOGNOTICE); wiz.setS('defaultskinignore', 'true')
            else:
                if DIALOG.yesno(ADDONTITLE, "[COLOR %s]It seems that the skin has been set back to [COLOR %s]%s[/COLOR][CR]Would you like to set the skin back to:[/COLOR][CR][COLOR %s]%s[/COLOR]" % (COLOR2, COLOR1, SKIN[5:].title(), COLOR1, skinname[0])):
                    gotoskin = skinlist[0]
                    gotoname = skinname[0]
                else: wiz.log("Skin was not reset", LOGNOTICE); wiz.setS('defaultskinignore', 'true')
        else: wiz.log("No skins found in addons folder.", LOGNOTICE); wiz.setS('defaultskinignore', 'true'); gotoskin = False
    if gotoskin:
        if wiz.swapSkins(gotoskin):
            wiz.lookandFeelData('restore')
    wiz.log("[Build Check] Invalid Skin Check End", LOGNOTICE)

while xbmc.Player().isPlayingVideo():
    xbmc.sleep(1000)

if KODIV >= 17:
    NOW = datetime.now()
    temp = wiz.getS('kodi17iscrap')
    if not temp == '':
        if temp > str(NOW - timedelta(minutes=2)):
            wiz.log("Killing Start Up Script")
            sys.exit()
    wiz.log("%s" % (NOW))
    wiz.setS('kodi17iscrap', str(NOW))
    xbmc.sleep(1000)
    if not wiz.getS('kodi17iscrap') == str(NOW):
        wiz.log("Killing Start Up Script")
        sys.exit()
    else:
        wiz.log("Continuing Start Up Script")

wiz.log("[Path Check] Started", LOGNOTICE)
path = os.path.split(os.path.dirname(ADDONPATH))
if not ADDONID == path[1]: DIALOG.ok(ADDONTITLE, '[COLOR %s]Please make sure that the plugin folder is the same as the ADDON_ID.[/COLOR][CR][COLOR %s]Plugin ID:[/COLOR] [COLOR %s]%s[/COLOR][CR][COLOR %s]Plugin Folder:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR2, COLOR2, COLOR1, ADDONID, COLOR2, COLOR1, path)); wiz.log("[Path Check] ADDON_ID and plugin folder doesnt match. %s / %s " % (ADDONID, path))
else: wiz.log("[Path Check] Good!", LOGNOTICE)

if KODIADDONS in ADDONPATH:
    wiz.log("Copying path to addons dir", LOGNOTICE)
    if not os.path.exists(ADDONS): os.makedirs(ADDONS)
    newpath = transPath(os.path.join('special://home/addons/', ADDONID))
    if os.path.exists(newpath):
        wiz.log("Folder already exists, cleaning House", LOGNOTICE)
        wiz.cleanHouse(newpath)
        wiz.removeFolder(newpath)
    try:
        wiz.copytree(ADDONPATH, newpath)
    except Exception as e:
        pass
    wiz.forceUpdate(True)

try:
    mybuilds = transPath(MYBUILDS)
    if not os.path.exists(mybuilds): xbmcvfs.mkdirs(mybuilds)
except:
    pass

wiz.log("Flushing Aged Cached Text Files")
wiz.flushOldCache()

wiz.log("[Auto Install Repo] Started", LOGNOTICE)
if AUTOINSTALL == 'Yes' and not os.path.exists(os.path.join(ADDONS, REPOID)):
    workingxml = wiz.workingURL(REPOADDONXML)
    if workingxml == True:
        ver = wiz.parseDOM(wiz.openURL(REPOADDONXML), 'addon', ret='version', attrs = {'id': REPOID})
        if len(ver) > 0:
            installzip = '%s-%s.zip' % (REPOID, ver[0])
            workingrepo = wiz.workingURL(REPOZIPURL+installzip)
            if workingrepo == True:
                DP.create(ADDONTITLE,'Downloading Repo...','', 'Please Wait')
                if not os.path.exists(PACKAGES): os.makedirs(PACKAGES)
                lib=os.path.join(PACKAGES, installzip)
                try: xbmcvfs.delete(lib)
                except: pass
                downloader.download(REPOZIPURL+installzip,lib, DP)
                extract.all(lib, ADDONS, DP)
                try:
                    f = xbmcvfs.File(os.path.join(ADDONS, REPOID, 'addon.xml')); g = f.read(); f.close()
                    name = wiz.parseDOM(g, 'addon', ret='name', attrs = {'id': REPOID})
                    wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, name[0]), "[COLOR %s]Add-on updated[/COLOR]" % COLOR2, icon=os.path.join(ADDONS, REPOID, 'icon.png'))
                except:
                    pass
                if KODIV >= 17: wiz.addonDatabase(REPOID, 1)
                DP.close()
                xbmc.sleep(500)
                wiz.forceUpdate(True)
                wiz.log("[Auto Install Repo] Successfully Installed", LOGNOTICE)
            else:
                wiz.LogNotify("[COLOR %s]Repo Install Error[/COLOR]" % COLOR1, "[COLOR %s]Invalid url for zip![/COLOR]" % COLOR2)
                wiz.log("[Auto Install Repo] Was unable to create a working url for repository. %s" % workingrepo, xbmc.LOGERROR)
        else:
            wiz.log("Invalid URL for Repo Zip", xbmc.LOGERROR)
    else:
        wiz.LogNotify("[COLOR %s]Repo Install Error[/COLOR]" % COLOR1, "[COLOR %s]Invalid addon.xml file![/COLOR]" % COLOR2)
        wiz.log("[Auto Install Repo] Unable to read the addon.xml file.", xbmc.LOGERROR)
elif not AUTOINSTALL == 'Yes': wiz.log("[Auto Install Repo] Not Enabled", LOGNOTICE)
elif os.path.exists(os.path.join(ADDONS, REPOID)): wiz.log("[Auto Install Repo] Repository already installed")

wiz.log("[Auto Update Wizard] Started", LOGNOTICE)
if AUTOUPDATE == 'Yes':
    wiz.wizardUpdate('startup')
else: wiz.log("[Auto Update Wizard] Not Enabled", LOGNOTICE)

wiz.log("[Notifications] Started", LOGNOTICE)
if ENABLE == 'Yes':
    if not NOTIFY == 'true':
        url = wiz.workingURL(NOTIFICATION)
        if url == True:
            id, msg = wiz.splitNotify(NOTIFICATION)
            if not id == False:
                try:
                    id = int(id); NOTEID = int(NOTEID)
                    if id == NOTEID:
                        if NOTEDISMISS == 'false':
                            notify.notification(msg)
                        else: wiz.log("[Notifications] id[%s] Dismissed" % int(id), LOGNOTICE)
                    elif id > NOTEID:
                        wiz.log("[Notifications] id: %s" % str(id), LOGNOTICE)
                        wiz.setS('noteid', str(id))
                        wiz.setS('notedismiss', 'false')
                        notify.notification(msg=msg)
                        wiz.log("[Notifications] Complete", LOGNOTICE)
                except Exception as e:
                    wiz.log("Error on Notifications Window: %s" % str(e), xbmc.LOGERROR)
            else: wiz.log("[Notifications] Text File not formated Correctly")
        else: wiz.log("[Notifications] URL(%s): %s" % (NOTIFICATION, url), LOGNOTICE)
    else: wiz.log("[Notifications] Turned Off", LOGNOTICE)
else: wiz.log("[Notifications] Not Enabled", LOGNOTICE)

wiz.log("[Installed Check] Started", LOGNOTICE)
if INSTALLED == 'true':
    if KODIV >= 17:
        wiz.kodi17Fix()
        if SKIN in ['skin.confluence', 'skin.estuary']:
            checkSkin()
        FAILED = True
    elif not EXTRACT == '100' and not BUILDNAME == "":
        wiz.log("[Installed Check] Build was extracted %s/100 with [ERRORS: %s]" % (EXTRACT, EXTERROR), LOGNOTICE)
        yes=DIALOG.yesno(ADDONTITLE, '[COLOR %s]%s[/COLOR] [COLOR %s]was not installed correctly![CR]Installed: [COLOR %s]%s[/COLOR] / Error Count: [COLOR %s]%s[/COLOR][CR]Would you like to try again?[/COLOR]' % (COLOR1, COLOR2, BUILDNAME, COLOR1, EXTRACT, COLOR1, EXTERROR), nolabel='[B]No Thanks![/B]', yeslabel='[B]Retry Install[/B]')
        wiz.clearS('build')
        FAILED = True
        if yes:
            wiz.ebi("PlayMedia(plugin://%s/?mode=install&name=%s&url=fresh)" % (ADDON_ID, quote_plus(BUILDNAME)))
            wiz.log("[Installed Check] Fresh Install Re-activated", LOGNOTICE)
        else: wiz.log("[Installed Check] Reinstall Ignored")
    elif SKIN in ['skin.confluence', 'skin.estuary']:
        wiz.log("[Installed Check] Incorrect skin: %s" % SKIN, LOGNOTICE)
        defaults = wiz.getS('defaultskin')
        if not defaults == '':
            if os.path.exists(os.path.join(ADDONS, defaults)):
                if wiz.swapSkins(defaults):
                    wiz.lookandFeelData('restore')
        if not wiz.currSkin() == defaults and not BUILDNAME == "":
            gui = wiz.checkBuild(BUILDNAME, 'gui')
            FAILED = True
            if gui == 'http://':
                wiz.log("[Installed Check] Guifix was set to http://", LOGNOTICE)
                DIALOG.ok(ADDONTITLE, "[COLOR %s]It looks like the skin settings was not applied to the build." % COLOR2, "Sadly no gui fix was attatched to the build", "You will need to reinstall the build and make sure to do a force close[/COLOR]")
            elif wiz.workingURL(gui):
                yes=DIALOG.yesno(ADDONTITLE, '%s was not installed correctly![CR]It looks like the skin settings was not applied to the build.[CR]Would you like to apply the GuiFix?' % BUILDNAME, nolabel='[B]No, Cancel[/B]', yeslabel='[B]Apply Fix[/B]')
                if yes: wiz.ebi("PlayMedia(plugin://%s/?mode=install&name=%s&url=gui)" % (ADDON_ID, quote_plus(BUILDNAME))); wiz.log("[Installed Check] Guifix attempting to install")
                else: wiz.log('[Installed Check] Guifix url working but cancelled: %s' % gui, LOGNOTICE)
            else:
                DIALOG.ok(ADDONTITLE, "[COLOR %s]It looks like the skin settings was not applied to the build." % COLOR2, "Sadly no gui fix was attatched to the build", "You will need to reinstall the build and make sure to do a force close[/COLOR]")
                wiz.log('[Installed Check] Guifix url not working: %s' % gui, LOGNOTICE)
    else:
        wiz.log('[Installed Check] Install seems to be completed correctly', LOGNOTICE)
    if not wiz.getS('pvrclient') == "":
        wiz.toggleAddon(wiz.getS('pvrclient'), 1)
        wiz.ebi('StartPVRManager')
    wiz.addonUpdates('reset')
    if KEEPTRAKT == 'true': traktit.traktIt('restore', 'all'); wiz.log('[Installed Check] Restoring Trakt Data', LOGNOTICE)
                                                                                                                      
    if KEEPREAL  == 'true': debridit.debridIt('restore', 'all'); wiz.log('[Installed Check] Restoring Real Debrid Data', LOGNOTICE)
    if KEEPLOGIN == 'true': loginit.loginIt('restore', 'all'); wiz.log('[Installed Check] Restoring Login Data', LOGNOTICE)
    wiz.clearS('install')
else: wiz.log("[Installed Check] Not Enabled", LOGNOTICE)

if FAILED == False:
    wiz.log("[Build Check] Started", LOGNOTICE)
    if not WORKING:
        wiz.log("[Build Check] Not a valid URL for Build File: %s" % BUILDFILE, LOGNOTICE)
    elif BUILDCHECK == '' and BUILDNAME == '':
        wiz.log("[Build Check] First Run", LOGNOTICE)
        checkInstalled()
        wiz.setS('lastbuildcheck', str(NEXTCHECK))
    elif not BUILDNAME == '':
        wiz.log("[Build Check] Build Installed", LOGNOTICE)
        if SKIN in ['skin.confluence', 'skin.estuary'] and not DEFAULTIGNORE == 'true':
            checkSkin()
            wiz.log("[Build Check] Build Installed: Checking Updates", LOGNOTICE)
            wiz.setS('lastbuildcheck', str(NEXTCHECK))
            checkUpdate()
        elif BUILDCHECK <= str(TODAY):
            wiz.log("[Build Check] Build Installed: Checking Updates", LOGNOTICE)
            wiz.setS('lastbuildcheck', str(NEXTCHECK))
            checkUpdate()
        else:
            wiz.log("[Build Check] Build Installed: Next check isn't until: %s / TODAY is: %s" % (BUILDCHECK, str(TODAY)), LOGNOTICE)

wiz.log("[Trakt Data] Started", LOGNOTICE)
if KEEPTRAKT == 'true':
    if TRAKTSAVE <= str(TODAY):
        wiz.log("[Trakt Data] Saving all Data", LOGNOTICE)
        traktit.autoUpdate('all')
        wiz.setS('traktlastsave', str(THREEDAYS))
    else:
        wiz.log("[Trakt Data] Next Auto Save isn't until: %s / TODAY is: %s" % (TRAKTSAVE, str(TODAY)), LOGNOTICE)
else: wiz.log("[Trakt Data] Not Enabled", LOGNOTICE)

wiz.log("[Debrid Data] Started", LOGNOTICE)
if KEEPREAL == 'true':
    if REALSAVE <= str(TODAY):
        wiz.log("[Debrid Data] Saving all Data", LOGNOTICE)
        debridit.autoUpdate('all')
        wiz.setS('debridlastsave', str(THREEDAYS))
    else:
        wiz.log("[Debrid Data] Next Auto Save isn't until: %s / TODAY is: %s" % (REALSAVE, str(TODAY)), LOGNOTICE)
else: wiz.log("[Real Debrid Data] Not Enabled", LOGNOTICE)

wiz.log("[Login Info] Started", LOGNOTICE)

if KEEPLOGIN == 'true':
    if LOGINSAVE <= str(TODAY):
        wiz.log("[Login Info] Saving all Data", LOGNOTICE)
        loginit.autoUpdate('all')
        wiz.setS('loginlastsave', str(THREEDAYS))
    else:
        wiz.log("[Login Info] Next Auto Save isn't until: %s / TODAY is: %s" % (LOGINSAVE, str(TODAY)), LOGNOTICE)
else: wiz.log("[Login Info] Not Enabled", LOGNOTICE)

wiz.log("[Auto Clean Up] Started", LOGNOTICE)
if AUTOCLEANUP == 'true':
    service = False
    days = [TODAY, TOMORROW, THREEDAYS, ONEWEEK]
    feq = int(float(AUTOFEQ))
    if AUTONEXTRUN <= str(TODAY) or feq == 0:
        service = True
        next_run = days[feq]
        wiz.setS('nextautocleanup', str(next_run))
    else: wiz.log("[Auto Clean Up] Next Clean Up %s" % AUTONEXTRUN, LOGNOTICE)
    if service == True:
        AUTOCACHE      = wiz.getS('clearcache')
        AUTOPACKAGES   = wiz.getS('clearpackages')
        AUTOTHUMBS     = wiz.getS('clearthumbs')
        if AUTOCACHE == 'true': wiz.log('[Auto Clean Up] Cache: On', LOGNOTICE); wiz.clearCache(True)
        else: wiz.log('[Auto Clean Up] Cache: Off', LOGNOTICE)
        if AUTOTHUMBS == 'true': wiz.log('[Auto Clean Up] Old Thumbs: On', LOGNOTICE); wiz.oldThumbs()
        else: wiz.log('[Auto Clean Up] Old Thumbs: Off', LOGNOTICE)
        if AUTOPACKAGES == 'true': wiz.log('[Auto Clean Up] Packages: On', LOGNOTICE); wiz.clearPackagesStartup()
        else: wiz.log('[Auto Clean Up] Packages: Off', LOGNOTICE)
else: wiz.log('[Auto Clean Up] Turned off', LOGNOTICE)

wiz.setS('kodi17iscrap', '')
