from train import *
from multiprocessing import Manager
from time import sleep


waiting_tracks = Platform("WAITING_TRACKS")  # Voies d'attente en entrée de la plateforme

main_tracks = Platform("MAIN_TRACKS")
main_track = main_tracks.add_track(10)       # Voie unique d'entrée/sortie de la plateforme

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


# Main loop
manager = Manager()

while True:
    for train in trains:
        # Traitement des messages envoyés par les trains
        if train.parent_conn.poll():
            train.process_data(train.parent_conn.recv())

        # Si un train est attente, on regarde si toute les conditions sont réunies pour le faire partir
        if train.waiting:
            main_track = main_tracks.free_track()

            if   train.track.platform.name == "WAITING_TRACKS":
                destination_track = sidings.free_track()

            elif train.track.platform.name == "SIDINGS":
                destination_track = waiting_tracks.free_track()
                if (destination_track == None):
                    destination_track = waiting_tracks.add_track()

            if main_track and destination_track:  # Si la voie est libre, on envoie le train !
                print(str(train.id) + " a reçu une autorisation d'avancer.")

                train.waiting = False
                train.parent_conn.send([main_track.to_mp_data(), destination_track.to_mp_data()])

                break  # Permet d'éviter certains conflits


    sleep(0.25)
