import fs_nmea
import fs_serial
import fs_database
import time
import curses
import subprocess
import sys
import com
from dicts import *

'''
Farmstar screen module
Takes a dictionary of dictionaries with processed nmea data (from fs_nmea)
{'gga':{'fix':'012345','age':'3'},'rmc':{key:val}}
Prints to a terminal screen statically, i.e. not scrolling
needs to be initiated from a terminal not IDE
'''


class display():

    def __init__(self):
        self.stdscr = curses.initscr()
        self.stdscr.border(0)
        self.box1 = curses.newwin(3, 80, 1, 1)
        self.box2 = curses.newwin(3, 18, 1, 81)
        self.box3 = curses.newwin(3, 20, 1, 99)
        self.box4 = curses.newwin(10, 22, 4, 1)
        self.box5 = curses.newwin(10, 30, 4, 23)
        self.box1.box()
        self.box2.box()
        self.box3.box()
        self.box4.box()
        self.box5.box()
        self.stdscr.addstr(0,50,"Farmstar Boiiii")
        self.box1.addstr(0,40,"Sentence")
        self.box2.addstr(0,5,"Checksum")
        self.box3.addstr(0,7,"Errors")
        self.box4.addstr(0,10,"GGA")
        self.box5.addstr(0,13,"GSA")


    def screen(self,GPS=None):
        if GPS == None:
            self.GPS = GPS.GPS
        else:
            self.GPS = GPS
            
        self.STATUS = self.GPS['STATUS']
        self.SPACETIME = self.GPS['SPACETIME']
        self.GGA = self.GPS['GGA']
        self.GSAALL = self.GPS['GSA']



        try:
            
            #Box 1
            self.box1.addstr(1,1,' '*78)
            self.box1.addstr(1,1,self.STATUS['string'].center(78, ' '))
            
            #Box 2
            self.check = '{}/{} - {}'.format(self.STATUS['checksum'],self.STATUS['calculated'],self.STATUS['check'])
            self.box2.addstr(1,1,str(' '*16))
            self.box2.addstr(1,1,self.check)

            #Box 3
            self.errper = int(round((int(self.STATUS['count_bad'])/int(self.STATUS['count_total']))*100))
            self.errors = '{}/{} - {}%'.format(self.STATUS['count_bad'],self.STATUS['count_total'],self.errper)
            self.box3.addstr(1,1,str(' '*18))
            self.box3.addstr(1,1,self.errors.center(18, ' '))

            #Box 4
            self.box4.addstr(1,1,str(' '*20))
            self.box4.addstr(1,1,'Lat: {} {}'.format(self.GGA['Latitude'],self.GGA['North/South']))
            self.box4.addstr(2,1,str(' '*20))
            self.box4.addstr(2,1,'Lon: {} {}'.format(self.GGA['Longitude'],self.GGA['East/West']))
            self.box4.addstr(3,1,str(' '*20))
            self.box4.addstr(3,1,'Alt: {} {}'.format(self.GGA['Altitude'],self.GGA['Altitude_Units']))
            self.box4.addstr(4,1,str(' '*20))
            self.box4.addstr(4,1,'Sat: {}'.format(self.GGA['Satellites']))
            self.box4.addstr(5,1,str(' '*20))
            self.box4.addstr(5,1,'Qua: {} - {}'.format(self.GGA['Quality'],self.GGA['Type']))
            self.box4.addstr(6,1,str(' '*20))
            self.box4.addstr(6,1,'Acc: {}'.format(self.GGA['Accuracy']))
            self.box4.addstr(7,1,str(' '*20))
            self.box4.addstr(7,1,'Geo: {} {}'.format(self.GGA['GeoID_Height'],self.GGA['GeoID_Units']))
            self.box4.addstr(8,1,str(' '*20))
            self.box4.addstr(8,1,'Fix: {} UTC'.format(self.GGA['Fix']))

            #Box 5
            try:
                GSA0 = self.GSAALL['list'][0]
                GSA1 = self.GSAALL['list'][1]
                GSA2 = self.GSAALL['list'][2]
                
                self.box5.addstr(1,1,str(' '*20))
                self.box5.addstr(1,1,'Talker: {}|{}|{}'.format(GSA0,
                                                               GSA1,
                                                               GSA2))
                
                self.box5.addstr(2,1,str(' '*20))
                self.box5.addstr(2,1,'  Mode: {} |{} |{}'.format(self.GSAALL[GSA0]['selection'],
                                                                 self.GSAALL[GSA1]['selection'],
                                                                 self.GSAALL[GSA2]['selection']))
                self.box5.addstr(3,1,str(' '*20))
                self.box5.addstr(3,1,'  Type:  {}  | {}  | {} '.format(self.GSAALL[GSA0]['mode'],
                                                                       self.GSAALL[GSA1]['mode'],
                                                                       self.GSAALL[GSA2]['mode']))
                self.box5.addstr(4,1,str(' '*20))
                self.box5.addstr(4,1,'  PDOP:  {} | {} | {}'.format(self.GSAALL[GSA0]['PDOP'],
                                                                    self.GSAALL[GSA1]['PDOP'],
                                                                    self.GSAALL[GSA2]['PDOP']))
                self.box5.addstr(5,1,str(' '*20))
                self.box5.addstr(5,1,'  HDOP:  {} | {} | {}'.format(self.GSAALL[self.GSAALL['list'][0]]['HDOP'],
                                                               self.GSAALL[self.GSAALL['list'][1]]['HDOP'],
                                                               self.GSAALL[self.GSAALL['list'][2]]['HDOP'],))
                self.box5.addstr(6,1,str(' '*20))
                self.box5.addstr(6,1,'  VDOP:  {} | {} | {}'.format(self.GSAALL[self.GSAALL['list'][0]]['VDOP'],
                                                               self.GSAALL[self.GSAALL['list'][1]]['VDOP'],
                                                               self.GSAALL[self.GSAALL['list'][2]]['VDOP'],))
            except:
                self.box5.addstr(1,3,'Failed to get GSA data.')

            
            self.stdscr.refresh()
            self.box1.refresh()
            self.box2.refresh()
            self.box3.refresh()
            self.box4.refresh()
            self.box5.refresh()
        except:
            curses.endwin()
            print("Give it a sec...")

        

class main():
    #main for testing this module

    def __init__(self, comports=''):
        if comports == '':
            print("No serial port specified")
            self.comports = com.Ports().valid
            if self.comports == []:
                print("Unable to find valid gps port")
            else:
                self.comport_1 = self.comports[0]
        else:
            self.comport_1 = comports[0]

    def run(self):
        self.serial_stream_1 = fs_serial.stream(self.comport_1)
        self.Display = display()
        self.db = fs_database.logging()
        self.data = ['','','','']

        while True:
            self.serial_stream_1.data()
            self.line_1 = self.serial_stream_1.line
            self.status_1 = self.serial_stream_1.status
            self.GPS_1 = fs_nmea.parse(self.line_1).GPS
            self.Display.screen(self.GPS_1)
        
            self.SPACETIME = self.GPS_1['SPACETIME']
            self.GGA = self.GPS_1['GGA']

            #This is a stupid way of doing this, the normal way isn't working.
            for key in self.SPACETIME:
                if key == 'unix':
                    self.data[0] = self.SPACETIME[key]
            for key in self.GGA:
                if key == 'Latitude':
                    self.data[1] = self.GGA[key]
                elif key == 'Longitude':
                    self.data[2] = self.GGA[key]
                elif key == 'Altitude':
                    self.data[3] = self.GGA[key]

            self.db.data(self.data)
                    


if __name__ == '__main__':
    #Uses com module to scan for valid ports if a port isn't specified
    #main()
    Main = main(['COM5'])
    Main.run()
    

 
