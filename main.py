from train import *
import curses
from time import time, sleep


waiting_tracks = Platform("WAITING_TRACKS")  # Voies d'attente en entrée de la plateforme

main_tracks = Platform("MAIN_TRACKS")
main_track = main_tracks.add_track(5)       # Voie unique d'entrée/sortie de la plateforme

sidings = Platform("SIDINGS")                # Voies de garage
sidings.add_track()
sidings.add_track()
sidings.add_track()
sidings.add_track()


def train_arrival():
    """Fait arriver un nouveau train en entrée de la plateforme"""

    # S'il n'y a pas de voie libre à l'entrée, en créer une (on modélise les trains en attente comme s'ils étaient sur des voies physiques)
    track = waiting_tracks.free_track()
    if (track == None):
        track = waiting_tracks.add_track()

    # Démarrer le processus du train
    track.train = Train(track, DIRECTION_ENTRY)


# Création des trains en attente d'entrée
train_arrival()
train_arrival()

# On positionne un train en stationnement
track = sidings.free_track()
track.train = Train(track, DIRECTION_EXIT)


stdscr = curses.initscr()

def drawDisplay():
    stdscr.clear()

    sidings.draw(stdscr, 0, 0)
    main_tracks.draw(stdscr, 0, 30)
    waiting_tracks.draw(stdscr, 0, 60)

    stdscr.refresh()


# Main loop
trains_moving = []
next_train_timer_start = time()


def train_move(train):
    # print(str(train.id) + " a reçu une autorisation d'avancer.")
    main_track = main_tracks.free_track()

    # On choisit la voie de destination du mouvement
    if   train.track.platform.name == "WAITING_TRACKS":
        destination_track = sidings.free_track()

    elif train.track.platform.name == "SIDINGS":
        destination_track = waiting_tracks.free_track()
        if (destination_track == None):
            destination_track = waiting_tracks.add_track()

    # Si une voie de destination est libre, on indique au train qu'il peut bouger (sinon il attend et il fait pas chier)
    if destination_track != None:
        trains_moving.append(train)
        train.waiting = False
        train.parent_conn.send([main_track.to_mp_data(), destination_track.to_mp_data()])

def clear_trains_moving():
    trains_moving.clear()


while True:
    # Réception des données des trains
    for train in trains:
        # Traitement des messages envoyés par les trains
        if train.parent_conn.poll():
            train.process_data(train.parent_conn.recv(), clear_trains_moving)


    # Ordonnanceur
    trains_waiting_to_enter = []
    trains_waiting_to_exit = []

    # On classe les trains en fonction de leur destination
    for train in trains:
        if   train.waiting and train.track.platform.name == "WAITING_TRACKS":
            trains_waiting_to_enter.append(train)

        elif train.waiting and train.track.platform.name == "SIDINGS":
            trains_waiting_to_exit.append(train)

    # On traite les départs si aucun train n'est en train de se déplacer
    if len(trains_moving) == 0:
        # Les trains voulant sortir ont la priorité
        if len(trains_waiting_to_exit) > 0:
            train_move(trains_waiting_to_exit[0])

        elif len(trains_waiting_to_enter) > 0:
            train_move(trains_waiting_to_enter[0])


    # Un nouveau train arrive toutes les vingt secondes
    if time() - next_train_timer_start >= 10:
        train_arrival()
        next_train_timer_start = time()


    drawDisplay()
    print(time() - next_train_timer_start)
    sleep(0.25)
