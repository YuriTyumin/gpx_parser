from typing import Union, IO, Callable
from xml.etree.ElementTree import ElementTree as ET

from gpx_parser.GPX import GPX
from gpx_parser.GPXTrack import GPXTrack as Track
from gpx_parser.GPXTrackPoint import GPXTrackPoint as TrackPoint
from gpx_parser.GPXTrackSegment import GPXTrackSegment as TrackSegment
from gpx_parser.xml_loader import load_xml


class GPXParser:

    def __init__(self, xml_or_file:Union[str, IO]):
       #print("Init: ", xml_or_file)
        self.init(xml_or_file)
        self.gpx:GPX = GPX()

    def init(self, xml_or_file:Union[str, IO], loader:Callable = load_xml):
        #print('parser.init: ', xml_or_file)
        text:str = xml_or_file.read() if hasattr(xml_or_file, 'read') else xml_or_file
        #print('text: ', text, type(text))
        self.xml:ET = loader(text)

    def parse(self) ->GPX:
        for track in self.xml.iterfind('trk'):
            new_track = Track(track[0].text, track[1].text)
            for segment in track.iterfind('trkseg'):
                new_segment = TrackSegment()
                for point in segment.iterfind('trkpt'):
                    values = point.attrib
                    t = point.find('time').text
                    values['time'] = t if t else None                   #print('PARSER: ', point[0].text)
                    #print(values, '###')
                    new_point = TrackPoint(point.attrib) # attrib is a dictionary
                    new_segment.append(new_point)
                new_track.append(new_segment)
            #print('Name: ' + track[0].text)
            #print('Number: ' + track[1].text)
            self.gpx.append(new_track)
        return self.gpx



if __name__ == '__main__':
    fn = '/home/olga/Documents/GPX/test1.gpx'
    with open(fn, 'r') as xml_file:
        parser = GPXParser(xml_file)
    gpx = parser.parse()
    print(gpx)
    print(len(gpx))
    for track in gpx:
        print(track)
        for seg in track:
            print(seg)
            for pt in seg:
                print(pt)
                print(pt.latitude, pt.longitude,pt.time)
