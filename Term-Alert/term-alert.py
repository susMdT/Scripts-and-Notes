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
                if messages.get("type") == 1327: #proctitle stuff
                    proctitleHex = messages.get("data")
                    try:
                        self.parsedJson.cmd=bytes.fromhex(proctitleHex.replace("proctitle=", "")).decode("ascii").replace("\x00", " ")
                    except:
                        self.parsedJson.cmd=proctitleHex
                if messages.get("type") == 1307: #self.cwd
                    self.parsedJson.cwd = messages.get("data")
                if messages.get("type") == 1300: #self.key     and uid                         
                    self.parsedJson.key = "Key: " #key
                    try:
                        self.parsedJson.key += messages.get("data").partition("key=")[2]
                    except:
                        self.parsedJson.key += "Unknown"
                    try:#uid
                        #euid = re.findall(r'\beuid=+\w{4}\b', messages.get("data"))
                        euid = messages.get("data").partition("euid=")[2].split()[0]
                    except:
                        euid = "N/A"
                    try:
                        #auid = re.findall(r'\bauid=+\w{4}\b', messages.get("data"))
                        auid = messages.get("data").partition("auid=")[2].split()[0]
                    except:
                        auid = "N/A"
                    try:
                        self.parsedJson.uid = "{}, originally {}".format(item.get("uid_map").get(euid), item.get("uid_map").get(auid))
                    except:
                        self.parsedJson.uid = "N/A"

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
        result = (event.key, event.toString())
        Parser.parsed_events.append(result)

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
                    break
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
