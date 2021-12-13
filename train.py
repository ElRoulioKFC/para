from math import floor
from random import uniform
from multiprocessing import *
from time import sleep


last_track_id = -1
tracks = []

def TrackFromMPData(data):
    return tracks[data["id"]]

class Track:
    """Une voie sur laquelle un train peut se situer"""

    def __init__(self, platform, travel_time):
        global last_track_id, tracks

        last_track_id = last_track_id + 1
        self.id = last_track_id
        tracks.append(self)

        self.platform = platform        # Plateforme dans laquelle la voie se situe
        self.travel_time = travel_time  # Temps qu'un train met pour entrer ou sortir de cette voie
        self.train = None

    def has_train(self):
        self.train != None

    def remove_train(self):
        self.train = None

    def to_mp_data(self):
        return {"id": self.id, "platform_name": self.platform.name, "travel_time": self.travel_time}

    def draw(self, stdscr, i, y, x):
        if self.train:
            self.train.draw(stdscr, y, x)

        stdscr.addstr(y + 4, x, str(i) + "-------------------")


class Platform():
    """Un ensemble de voies"""

    def __init__(self, name):
        self.name = name  # Nom de la plateforme (permet à un train d'identifier sa position à partir de la voie sur laquelle il est)
        self.tracks = []

    def add_track(self, travel_time = 0):
        track = Track(self, travel_time)
        self.tracks.append(track)

        return track

    def remove_track(self, track):
        if track.train != None:
            raise Exception("A train is still sitting on this track!")

        self.tracks.remove(track)

    def free_track(self):
        """Retourne la première voie libre de la plateforme"""
        for track in self.tracks:
            if not track.train:
                return track

        return None

    def draw(self, stdscr, y, x):
        stdscr.addstr(y, x, self.name)

        i = 1
        y = y + 1
        for track in self.tracks:
            track.draw(stdscr, i, y, x + 1)
            i = i + 1
            y = y + 6


DIRECTION_ENTRY = 1  # Entrée dans la plateforme
DIRECTION_EXIT  = 2  # Sortie de la plateforme

trains = []

class Train:
    """Un train"""

    def __init__(self, initial_track, initial_direction):
        self.id = floor(uniform(1000, 9000))
        self.track = initial_track            # Voie sur laquelle le train se situe
        self.direction = initial_direction    # Direction vers le train se dirige (entrée ou sortie de la plateforme)
        self.waiting = False

        self.parent_conn, self.child_conn = Pipe()

        self.process = Process(target=train_process, args=(self.id, self.track, self.direction, self.child_conn,))
        self.process.start()

        trains.append(self)

    def destroy(self):
        self.track.train = None
        trains.remove(self)

    def process_data(self, data, clear_trains_moving):
        """Traite les données reçues par le processus du train"""

        # Le train a effectué une demande
        if ("demand" in data) and (data["demand"] == "MOVE"):
            # if   self.track.platform.name == "WAITING_TRACKS":
            #     print(str(self.id) + " requiert un accès à la plateforme.")
            # elif self.track.platform.name == "SIDINGS":
            #     print(str(self.id) + " requiert une sortie de la plateforme.")

            self.waiting = True

        # Le train s'est déplacé sur une nouvelle voie
        if "moved" in data:
            moved = data["moved"]
            track = TrackFromMPData(moved["track"])

            if track.has_train():  # <== Pas normal !
                raise Exception("Track already has a train on it (you just caused a deadly accident :( )!")

            # print(str(self.id) + " se déplace sur " + track.platform.name)

            self.track.remove_train()

            self.track = track
            self.direction = moved["direction"]

            self.track.train = self

        # Le train est arrivé à sa destination
        if ("arrived" in data) and data["arrived"]:
            # print(str(self.id) + " est arrivé à " + self.track.platform.name)
            clear_trains_moving()

            if self.track.platform.name == "WAITING_TRACKS":  # Le train est parti, arrêter son processus
                self.destroy()

    def draw(self, stdscr, y, x):
        direction = "<==" if self.direction == DIRECTION_ENTRY else "==>"
        waiting = "X" if self.waiting else " "

        stdscr.addstr(y,     x, " ------------------")
        stdscr.addstr(y + 1, x, "/ " + str(self.id) + "  " + waiting + "  " + direction + "     \\")
        stdscr.addstr(y + 2, x, "__@_@__________@_@__")


def train_process(id, initial_track, initial_direction, conn):
    """Processus fils de chaque train"""

    active = True
    track = initial_track.to_mp_data()
    direction = initial_direction


    def train_process_move():
        """Instructions de déplacement d'un processus fils de train"""
        nonlocal track, direction

        # Indiquer à l'opérateur que l'on souhaite bouger
        conn.send({"demand": "MOVE"})

        # Attendre la réponse de l'opérateur
        instructions = conn.recv()

        # Choix de la direction du train
        if   track["platform_name"] == "WAITING_TRACKS":
            direction = DIRECTION_ENTRY
        elif track["platform_name"] == "SIDINGS":
            direction = DIRECTION_EXIT

        conn.send({"moved": {"track": track, "direction": direction}})

        # Exécution des instructions données par l'opérateur
        for to_track in instructions:
            sleep(track["travel_time"])

            track = to_track
            conn.send({"moved": {"track": track, "direction": direction}})

        conn.send({"arrived": True})

        # Si arrivé en sortie de la plateforme, supprimer le train du système
        if track["platform_name"] == "WAITING_TRACKS":
            active = False


    while active:
        if track["platform_name"] == "SIDINGS":
            # On simule le temps de stationnement à quai (aléatoirement de 10 à 20s)
            sleep(floor(uniform(5, 20)))

        train_process_move()
        sleep(0.01)
