#!/usr/bin/env python
import json
from json import *
import datetime
import urwid
from time import sleep
from threading import Thread 
import re
from os.path import exists
import os

MAX_ALERTS = 20
FRAME_HEADER = "Term-Alert v2.0"
TAB_SIZE = 4
POLLING_RATE = 1

#files = ['user_mod.log']
files = ['/var/log/go-audit.log']

class parsedData:

    def __init__(self):
        self.cwd = ""
        self.cmd = ""
        self.uid = ""
        self.time = ""

    def refresh(self):
        self.cwd = ""
        self.cmd = ""
        self.uid = ""
        self.time = ""
        self.key = ""

    def isValid(self):
        if self.cwd != "" and self.key != "" and self.cmd != "" and self.uid != "" and self.time != "":
            return True
        return False
    
    def toString(self):
        return ("Time: {} \n cwd: {} \n cmd: {} \n uid: {} \n ".format(self.time, self.cwd, self.cmd, self.uid))

class Parser():
    parsed_events = []
    files = {}
    def  __init__(self):
        for entry in files:
            Parser.files.update({entry : 0})
        self.parsedJson = parsedData()
        self.rawJson = []

    def jsonArrayParser(self, jsonArray):
        for item in jsonArray: #the entire json entry aka singular events that are logged
            self.parsedJson.refresh() #flushing the dirt out
            self.parsedJson.time = datetime.datetime.fromtimestamp(float(item.get("timestamp")))
            for messages in item.get("messages"):
                if messages.get("type") == 1327:
                    proctitleHex = messages.get("data")
                    try:
                        self.parsedJson.cmd=bytes.fromhex(proctitleHex.replace("proctitle=", "")).decode("ascii").replace("\x00", " ")
                    except:
                        self.parsedJson.cmd=proctitleHex
                if messages.get("type") == 1307: #self.cwd
                    self.parsedJson.cwd = messages.get("data")
                if messages.get("type") == 1300: #self.key                              
                    self.parsedJson.key = "Key: "
                    try:
                        self.parsedJson.key += messages.get("data").partition("key=")[2]
                    except:
                        self.parsedJson.key += "Unknown"
            if len(item.get("uid_map")) == 2:
                temparr = []
                for user in item.get("uid_map"):
                    temparr.append(user)
                self.parsedJson.uid="{}, originally {}".format(item.get("uid_map").get(temparr[0]), item.get("uid_map").get(temparr[1]))
            elif len(item.get("uid_map")) == 1:
                for user in item.get("uid_map"):
                    self.parsedJson.uid=item.get("uid_map").get("user")
            if self.parsedJson.isValid():
                self.add_event(self.parsedJson)



    def parse(self, file_to_parse):

        if exists(file_to_parse):
            line_count = Parser.files.get(file_to_parse)
            lines = 0
            current_line = 0
            self.rawJson = []
            with open(file_to_parse) as infile:
                #for jsonObj in infile:
                    #deserialized = json.loads(jsonObj)
                for line in infile:
                    if current_line > line_count :
                    #if current_line >= line_count:
                        self.rawJson.append(json.loads(line))
                    elif current_line >= line_count and len(Parser.parsed_events) == 0:
                        self.rawJson.append(json.loads(line))
                        '''
                        event = json.loads(line)
                        self.parsedJson.refresh()
                        self.parsedJson.time = datetime.datetime.fromtimestamp(float(event.get("timestamp")))
                        for messages in event.get("messages"):
                            if messages.get("type") == 1327:
                                proctitleHex = messages.get("data")
                                try:
                                    self.parsedJson.cmd=bytes.fromhex(proctitleHex.replace("proctitle=", "")).decode("ascii").replace("\x00", " ")
                                except:
                                    self.parsedJson.cmd=proctitleHex
                            if messages.get("type") == 1307: #self.cwd
                                self.parsedJson.cwd = messages.get("data")
                            if messages.get("type") == 1300: #self.key                              
                                self.parsedJson.key = "Key: "
                                try:
                                    self.parsedJson.key += messages.get("data").partition("key=")[2]
                                except:
                                    self.parsedJson.key += "Unknown"
                        if len(event.get("uid_map")) == 2:
                            temparr = []
                            for user in event.get("uid_map"):
                                temparr.append(user)
                            self.parsedJson.uid="{}, originally {}".format(event.get("uid_map").get(temparr[0]), event.get("uid_map").get(temparr[1]))
                        elif len(event.get("uid_map")) == 1:
                            for user in event.get("uid_map"):
                                self.parsedJson.uid=event.get("uid_map").get("user")
                    current_line+=1
                
                    if self.parsedJson.isValid():
                        self.add_event(self.parsedJson)
                    '''
                    current_line += 1
            Parser.files.update({file_to_parse : current_line})
            #self.jsonArrayParser(self.rawJson)
            if current_line == line_count:
                return []
            else:
                self.jsonArrayParser(self.rawJson)
                return Parser.parsed_events
            #return [] if current_line == line_count else Parser.parsed_events
        else:
            return []

    def add_event(self, event):
        #key = re.search('(?<= key=)(\w+)', event)
        #event_type = re.search(r'\b(?<=type=)(\w+)', event)
        '''
        try:
            if 'proctitle=grep' in event:
                cmd = 'Command=\''+re.search('(?<= proctitle=)(.+)', event).group(0)+'\''
                uid = re.search('auid=\w+ uid=\w+', event).group(0)
                description = '\n' + uid.replace(' ', ', ') + '\n'
                result = ('GREP Event: '+cmd, cmd+description)
            elif key.group(0) == 'user_modification':
                result = self.user_event(event)
            elif key.group(0) == 'recon':
                result = self.recon_event(event)
            elif event_type.group(0) == 'USER_AUTH':
                result = self.auth_event(event)
            elif key.group(0) == 'rootcmd':
                result = self.rootcmd_event(event)
            else:
                result = (key.group(0), event)
        except AttributeError:
            if event_type and event_type.group(0) == 'USER_AUTH':
                result = self.auth_event(event)
            else:
                result = ('NO KNOWN FORMAT FOR EVENT', event)
        Parser.parsed_events.append( result )
        '''
        result = (event.key, event.toString())
        Parser.parsed_events.append(result)
    '''
    def rootcmd_event(self, event):
        title = 'rootcmd: '
        description = event
        try:
            m = re.search('(?<= proctitle=).+', event)
            title += m.group(0).strip()
        except AttributeError:
            title += 'cannot determine command'
        return (title, description)

    def auth_event(self, event):
        title = 'Unknown auth event'
        description = ''
        try:
            acct = re.search('(?<= acct=)(\S+)', event).group(0)
            exe = re.search('(?<= exe=)(\S+)', event).group(0)
            addr = re.search('(?<= addr=)(\S+)', event).group(0)
            description += 'Account: '+acct+'\n'
            description += 'Command: '+exe+'\n'
            description += 'Address: '
            description += addr if not addr == '?' else 'localhost'+'\n'
            description += 'key=USER_AUTH\n'
            description += '\n'+event+'\n'
            title += ': Acct = '+acct+' | exe = '+exe
        except AttributeError:
            return (title, description)
        return ( title, description )

    def recon_event(self, event):
        key = 'recon'
        pid = int(re.search('(?<= pid=)(\d+)', event).group(0))
        ppid = int(re.search('(?<= ppid=)(\d+)', event).group(0))
        title = 'Uknown RECON event'
        description = ''
        process_tree = [pid]
        is_ssh = False
        is_reverse_shell = False
        found = True
        while not ppid in (0, 1) and found:
            found = False
            for entry in TUI.alerts:
                if entry.pid == ppid: 
                    ppid = entry.ppid
                    found = True
                    TUI.header.contents[1][0].set_text(str(ppid))
                    if '/ssh' in entry.message:
                        is_ssh = True
                    if '/nc' in entry.message:
                        is_reverse_shell = True
                    break;
            process_tree.append(ppid)
        
        description += 'Full Process Tree:\n' + str(process_tree) + '\n'
        description += 'Event info: key=recon\n'
        description += '\n'+event+'\n'

        if is_ssh:
            title = 'Probably an ssh Session'
        elif is_reverse_shell:
            title = 'Probably a reverse Shell'
        else:
            title = 'Probably not a reverse Shell'
        return ( title, description )

    def user_event(self, event):
        title = 'Unknown user event'
        try:
            m = re.search('(?<= proctitle=).+', event)
            result = m.group(0).strip()
            if 'useradd' in result or 'adduser' in result:
                title = 'New user detected \''+ result[result.rindex(' ')+1:]+'\''
            elif 'userdel' in result or 'deluser' in result:
                title = 'User deleted \''+ result[result.rindex(' ')+1:]+'\''
        except AttributeError:
            title = m
        try:
            m = re.search('(?<=type=SYSCALL ).+', event)
            description = m.group(0).strip()
            description += '\n\n'+event+'\n'
        except AttributeError:
            description = m
        return ( title, description )
    '''
class PopUpDialog(urwid.WidgetWrap):
    """A dialog that appears with nothing but a close button """
    signals = ['close']
    close_message = 'close'
    def __init__(self, title, message):
        self.title = title
        self.set_description(message)

    def set_description(self, message):
        close_button = urwid.Button(PopUpDialog.close_message)
        urwid.connect_signal(close_button, 'click',
            lambda button:self._emit("close"))
        pile = urwid.Pile([urwid.Text(self.title, align='center'), urwid.Text(message), close_button])
        fill = urwid.Filler(pile)
        self.__super.__init__(urwid.AttrWrap(fill, 'popbg'))
        self.message = message

    def get_description(self):
        return self.message

class Alert(urwid.PopUpLauncher):
    count = 0
    def __init__(self, title, message):
        Alert.count += 1
        self.id = Alert.count
        self.title = expand_tab(str(self.id) + '.\t'+ title)
        self.__super.__init__(urwid.Button(self.title))
        urwid.connect_signal(self.original_widget, 'click',
            lambda button: self.open_pop_up())
        self.pop_up = PopUpDialog('\n'+title+'\n',message)
        self.message = message
        '''
        try:
            self.pid = int(re.search('(?<= pid=)(\d+)', message).group(0))
        except AttributeError:
            self.pid = 0
        try:
            self.ppid = int(re.search('(?<= ppid=)(\d+)', message).group(0))
        except AttributeError:
            self.ppid = 0
        try:
            self.key = re.search('(?<= key=)(\w+)', message).group(0)
        except AttributeError:
            self.key = ''
        '''    
        TUI.header.contents[1][0].set_text('Last event: '+str(Alert.count))

    def create_pop_up(self):
        urwid.connect_signal(self.pop_up, 'close',
            lambda button: self.close_pop_up())
        return self.pop_up

    def get_pop_up_parameters(self):
        colsrows = urwid.raw_display.Screen().get_cols_rows()
        cols = colsrows[0]-4
        rows = max(7, urwid.Text(self.message).pack((cols,))[1]+5)
        return {'left':0, 'top':1, 'overlay_width':cols, 'overlay_height':rows}

    def set_description(self, message):
        self.pop_up.set_description(message)
        self.message = self.pop_up.get_description()

class TUI():
    status = False
    animate_alarm = None
    palette = []
    placeholder = urwid.SolidFill()
    show_list = []
    alerts = [] 
    filtered = []
    show_mode = False
    lb = None
    frame = None
    content = None
    loop = None
    footer_search = None 
    header = urwid.Columns([urwid.Text(FRAME_HEADER, align='left'), urwid.Text('Last event: '+str(Alert.count), align='center'), urwid.Text('', align='right')], dividechars=2)
    search_text = urwid.Edit('Search: ')
    search_button = urwid.Button('Search')


    def __init__(self):
        self.p = Parser()
        urwid.connect_signal(TUI.search_button, 'click', self.search)
        search_widgets = [('weight', 3, TUI.search_text), ('weight', 1, TUI.search_button)] 
        TUI.footer_search = urwid.Columns(search_widgets, dividechars=3, min_width=4)
        self.draw()

    def search(self, state):
        query = TUI.search_text.get_edit_text()
        message = ''
        success_msg = ' Search success '
        filtered = False
        if TUI.show_mode:
            TUI.show_mode = False
            self.update_ui()
        try:
            m = re.findall(r'\b(\w+)=(\S+)\b', query)
            if len(m) == 0:
                raise AttributeError
            for term in m:
                key = term[0]
                value = term[1]
                message = ('nomatch', ' No match found ')
                jump_index = TUI.lb.get_focus()[1]

                if(key in ('j', 'jump')):
                    jump_index = int(value)-1
                    if 0 <= jump_index and jump_index < Alert.count:
                        TUI.frame.focus_position = 'body'
                        TUI.lb.body.set_focus(jump_index)
                        message = ('success', success_msg)
                elif(key in ('k', 'key')):
                    for alert in TUI.alerts[jump_index+1:]:
                        if alert.key == value:
                            jump_index = alert.id -1
                            TUI.frame.focus_position = 'body'
                            TUI.lb.body.set_focus(jump_index)
                            if filtered:
                                success_msg = ' Search filtered '
                                TUI.filtered.append(TUI.alerts[jump_index])
                            message = ('success', success_msg)
                            if not filtered:
                                break
                elif(key in ('s', 'search')):
                    for alert in TUI.alerts[jump_index+1:]:
                        if value in alert.message or value in alert.title:
                            jump_index = alert.id-1
                            TUI.frame.focus_position = 'body'
                            TUI.lb.body.set_focus(jump_index)
                            if filtered:
                                success_msg = ' Search filtered '
                                TUI.filtered.append(TUI.alerts[jump_index])
                            message = ('success', success_msg)
                            if not filtered:
                                break
                elif(key in ('f', 'filter')):
                    if value in ('true', 't', 'y', 'yes'):
                        TUI.filtered = []
                        filtered = True

        except (AttributeError, ValueError) as e:
            message = ('invalid', ' Invalid search ')
        except TypeError:
            message = ('invalid', ' Cannot search ')
        if message:
            TUI.header.contents[2][0].set_text(message)
        if filtered:
            TUI.show_mode = True 
        else:
            TUI.show_mode = False

    def handle_input(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()
        elif key in ('/', 's', 'S'):
            TUI.frame.focus_position = 'footer'
            TUI.footer_search.focus_position = 0
        elif key == 'esc':
            TUI.frame.focus_position = 'body'
        else:
            if not TUI.status:
                TUI.status = True
                self.update_ui()

    def draw(self):
        TUI.palette = [
        ('popbg', 'white', 'dark blue'),
        ('a_banner', '', '', '', '#ffa', '#60d'),
        ('a_streak', '', '', '', 'g50', '#60a'),
        ('a_inside', '', '', '', 'g38', '#808'),
        ('a_outside', '', '', '', 'g27', '#a06'),
        ('a_bg', '', '', '', 'g7', '#d06'),
        ('c_banner', '', '', '', '#ffa', '#066'),
        ('c_streak', '', '', '', '#066', '#066'),
        ('c_inside', '', '', '', '#076', '#076'),
        ('c_outside', '', '', '', '#0a5', '#0a5'),
        ('c_bg', '', '', '', '#0c5', '#0c5'),
        ('warning', '', '', '', '#111', 'brown'),
        ('success', 'white', 'dark green'),
        ('invalid', 'yellow', 'dark red'),
        ('nomatch', 'white', 'dark blue')
        ]
        TUI.content = urwid.SimpleFocusListWalker(TUI.show_list)
        TUI.lb = urwid.ListBox(TUI.content)
        self.change_screen()
        TUI.loop = urwid.MainLoop(
            TUI.frame,
            TUI.palette,
            pop_ups=True, 
            unhandled_input=self.handle_input)
        TUI.loop.screen.set_terminal_properties(colors=256)
        TUI.loop.run()

    def change_screen(self):
        TUI.show_list = TUI.filtered if TUI.show_mode else TUI.alerts
        warning =  False if len(TUI.show_list) == 0 else True
        bg_color = 'a_bg' if warning else 'c_bg'
        if warning:
            streak = urwid.AttrMap(urwid.BoxAdapter(TUI.lb, height=min(len(TUI.show_list), MAX_ALERTS)), 'a_streak' if warning else 'c_streak')
        elif TUI.status:
            streak = urwid.AttrMap(urwid.Text(('c_banner', u'No valid files to parse!'), align='center'), 'c_streak')
            bg_color = 'warning'
            for check in files:
                if exists(check):
                    bg_color = 'c_bg'
                    streak = urwid.AttrMap(urwid.Text(('c_banner', u'nothing detected'), align='center'), 'c_streak')
                    break;
        else:
            streak = urwid.AttrMap(urwid.Text(('warning', u'Press any button...'), align='center'), 'warning')
        background = urwid.AttrMap(TUI.placeholder,  bg_color)
        background.original_widget = urwid.Filler(urwid.Pile([]))
        pile = background.base_widget
        div = urwid.Divider()
        outside = urwid.AttrMap(div, 'a_outside' if warning else 'c_outside')
        inside = urwid.AttrMap(div, 'a_inside' if warning else 'c_inside')
        pile.contents.clear()
        for item in [ outside, inside, streak, inside, outside ]:
            pile.contents.append((item, pile.options()))
        if not TUI.status or TUI.frame.get_focus() == 'body':
            pile.focus_position = 2

        pos = TUI.frame.focus_position if TUI.status else 'body'
        TUI.frame = urwid.Frame(background, header=TUI.header, footer=TUI.footer_search, focus_part=pos)
        if TUI.loop:
            TUI.loop.screen.clear()
            TUI.loop.widget = TUI.frame


    def update_ui(self, loop=None, user_data=None):
        self.change_screen() 
        TUI.content[:] = TUI.show_list
        TUI.animate_alarm = TUI.loop.set_alarm_in(0.1, self.update_ui)

def expand_tab(text: str, width: int = TAB_SIZE):
    width = max(2, width)
    result = []
    for line in text.splitlines():
        try:
            while True:
                i = line.index('\t')
                pad = ' ' * (width - (i % width))
                line = line.replace('\t', pad, 1)
        except ValueError:
            result.append(line)
    return '\n'.join(result)

def main():
    side_thread = Thread(target=start_parser, daemon=True)
    side_thread.start()
    start_tui()

def start_tui():
   TUI() 

def start_parser():
    p = Parser()
    while True:
        for infile in files:
            entry = 0
            if TUI.status: 
                res = p.parse(infile)
                for alert in res:
                    if entry >= len(TUI.alerts):
                        TUI.alerts.append(Alert(alert[0], alert[1]))
                    entry += 1
                sleep(POLLING_RATE)

if __name__=='__main__':
    main()