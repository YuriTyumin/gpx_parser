from datetime import datetime
from typing import Optional, List, Union, Iterator, Iterable, Tuple
import math as mod_math
import copy
from gpx_parser.GPXTrack import GPXTrack as Track


class GPX:
    """
    
    """

    __slots__ = ('_version', '_creator', '_tracks')

    def __init__(self, version:Optional[str]=None, creator:Optional[str]=None, tracks:Optional[List[Track]]=None):
        self._version:Optional[str] = version
        self._creator:Optional[str] = creator
        self._tracks:List[Track] = tracks if tracks else []


    def __repr__(self)->str:
        return 'GPX(%s)(tracks=%s)' % (len(self._tracks), self._tracks)

    def __getitem__(self, key:Union[int, slice])-> Union[Track,List[Track]]:
        if isinstance(key, int):
            return self._tracks[key]
        elif isinstance(key, slice):
            return self._tracks[key.start:key.stop:key.step]
        else:
            raise TypeError('Index must be int, not {}'.format(type(key).__name__))

    def __len__(self)->int:
        return len(self._tracks)

    def __contains__(self, item:Track)->bool:
        return item in self._tracks

    def __iter__(self)-> Iterator[Track]:
        return iter(self._tracks)

    @property
    def tracks(self):
        return self._tracks

    @tracks.setter
    def tracks(self, tracks:List[Track]):
        self._tracks = tracks

    @property
    def version(self)->str:
        return self._version

    @version.setter
    def version(self, ver:str):
        self._version = ver

    @property
    def creator(self)->str:
        return self._creator

    @creator.setter
    def creator(self, creator:str):
        self._creator = creator

    def append(self, item:Track):
        self._tracks.append(item)

    def extend(self, items:Iterable[Track]):
        self._tracks.extend(items)

    def remove(self, item:Track):
        self._tracks.remove(item)

    def to_xml(self)->str:

        version:str = self.version if self.version else '1.1'
        creator:str = self.creator if self.creator else 'gpx_parser.py'
        result = ['<?xml version="1.0" encoding="UTF-8"?>',]
        result.append('\n<gpx xmlns="http://www.topografix.com/GPX/{}" '.format(version.replace('.','/')))
        result.append('xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ')
        result.append('xsi:schemaLocation="http://www.topografix.com/GPX/{} '.format(version.replace('.','/')))
        result.append('http://www.topografix.com/GPX/{}/gpx.xsd" '.format(version.replace('.','/')))
        result.extend(['version="%s" '% version, 'creator="%s">'% creator])

        result.extend(map(lambda t : t.to_xml(), self._tracks))
        result.append('\n</gpx>')
        return  ''.join(result)



    def reduce_points(self, max_points_no=None, min_distance=None)->None:
        """
        Reduces the number of points. Points will be updated in place.

        Parameters
        ----------

        max_points : int
            The maximum number of points to include in the GPX
        min_distance : float
            The minimum separation in meters between points
        """
        if max_points_no is None and min_distance is None:
            raise ValueError("Either max_point_no or min_distance must be supplied")

        if max_points_no is not None and max_points_no < 2:
            raise ValueError("max_points_no must be greater than or equal to 2")

        points_no = len(list(self.walk()))
        if max_points_no is not None and points_no <= max_points_no:
            # No need to reduce points only if no min_distance is specified:
            if not min_distance:
                return

        length = self.length_2d()

        min_distance = min_distance or 0
        max_points_no = max_points_no or 1000000000

        min_distance = max(min_distance, mod_math.ceil(length / float(max_points_no)))

        for track in self.tracks:
            track.reduce_points(min_distance)

    def length_2d(self)->float:
        return sum(map(lambda tr: tr.length_2d(), self._tracks))


    def get_time_bounds(self)->Tuple[datetime, datetime]:
        """
        Gets the time bounds (start and end) of the GPX file.

        Returns
        ----------
        time_bounds : TimeBounds named tuple
            start_time : datetime
                Start time of the first segment in track
            end time : datetime
                End time of the last segment in track
        """
        start_time = None
        end_time = None

        for track in self.tracks:
            track_start_time, track_end_time = track.get_time_bounds()
            if not start_time:
                start_time = track_start_time
            if track_end_time:
                end_time = track_end_time

        return start_time, end_time

    def get_bounds(self)->Tuple[float, float, float, float]:

        all_points = [pt for tr in self._tracks for seg  in tr.segments for pt in seg.points]
        min_lat = min(map(lambda pt :pt.latitude, all_points))
        max_lat = max(map(lambda pt :pt.latitude, all_points))
        min_lon = min(map(lambda pt :pt.longitude, all_points))
        max_lon = max(map(lambda pt :pt.longitude, all_points))

        return min_lat, max_lat, min_lon, max_lon


    def get_points_no(self):
        return sum(map(lambda tr: tr.get_points_no(), self._tracks))



    def walk(self, only_points=False):
        """
        Generator used to iterates through points in GPX file

        Parameters
        ----------
        only_point s: boolean
            Only yield points while walking

        Yields
        ----------
        point : GPXTrackPoint
            Point in the track
        track_no : integer
            Index of track containint point. This is suppressed if only_points
            is True.
        segment_no : integer
            Index of segment containint point. This is suppressed if only_points
            is True.
        point_no : integer
            Index of point. This is suppressed if only_points is True.
        """
        for track_no, track in enumerate(self.tracks):
            for segment_no, segment in enumerate(track.segments):
                for point_no, point in enumerate(segment.points):
                    if only_points:
                        yield point
                    else:
                        yield point, track_no, segment_no, point_no


    def clone(self):
        return copy.deepcopy(self)


if __name__ == '__main__':

    from gpx_parser.GPXTrackPoint import GPXTrackPoint as TrackPoint
    from gpx_parser.GPXTrackSegment import GPXTrackSegment as TrackSegment

    x = "50.0164596"
    y = "14.4547907"
    p1 = TrackPoint(x, y, '2017-11-22T07:03:36Z')
    p2 = TrackPoint(y, x)
    p3 = TrackPoint(y, y, '2617-11-13T08:11:09Z')
    p4 = TrackPoint(x, x)
    seg1 = TrackSegment([p1, p2, p3])
    seg2 = TrackSegment([p2, p3, p4])
    seg3 = TrackSegment([p4, p1])
    track1 = Track('800003627_337', '0', [seg1, seg2, seg3])
    track2 = Track('800003627_908', None, [seg2, seg3])
    track3 = Track(None, '2', [TrackSegment([p4])])
    print('Track with name, number, 3 segments: ',track1)
    print('Track with name,no number, 2 segments: ',track2)
    print('Track with no name, number, 1 segment: ', track3)

    gpx = GPX('1.0','gpx.py -- https://github.com/tkrajina/gpxpy')
    print('Empty gpx with version and creator: ', gpx)
    gpx.append(track1)
    print('1 track added: ', gpx)
    gpx.extend([track2,track3])
    print('2 more tracks added, len = ', gpx)

    print('Slice: ', gpx[0:1])
    print('third track: ', gpx[2])

    print('Iterator')
    for t in gpx:
        print(t)

    gpx.remove(track3)
    print('.tracks after 1 track removed: ', gpx.tracks)


