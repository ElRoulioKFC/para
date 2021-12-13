from math import floor
from random import uniform
from multiprocessing import *


class Track:
    """Une voie sur laquelle un train peut se situer"""

    def __init__(self, platform, travel_time):
        self.platform = platform        # Plateforme dans laquelle la voie se situe
        self.travel_time = travel_time  # Temps qu'un train met pour entrer ou sortir de cette voie
        self.train = None

    def has_train(self):
        self.train != None


class Platform():
    """Un ensemble de voies"""

    def __init__(self, name):
        self.name = name  # Nom de la plateforme (permet à un train d'identifier sa position à partir de la voie sur laquelle il est)
        self.tracks = []

    def add_track(self, travel_time = 0):
        track = Track(self.name, travel_time)
        self.tracks.append(track)

        return track

    def remove_track(self, track):
        if track.has_train():
            raise Exception("A train is still sitting on this track!")

        self.tracks.remove(track)

    def free_track(self):
        for track in self.tracks:
            if not track.has_train():
                return track

        return None


DIRECTION_ENTRY = 1  # Entrée dans la plateforme
DIRECTION_EXIT  = 2  # Sortie de la plateforme

class Train:
    """Un train"""

    def __init__(self, initial_position, initial_direction):
        self.id = floor(uniform(1000, 9000))
        self.track = initial_position         # Voie sur laquelle le train se situe
        self.direction = initial_direction    # Direction vers le train se dirige (entrée ou sortie de la plateforme)

        self.parent_conn, self.child_conn = Pipe()

        self.process = Process(target=train_process, args=(self.id, self.track, self.direction, self.child_conn,))
        self.process.start()


def train_process(id, track, direction, conn):
    """Processus fils de chaque train"""
    pass
