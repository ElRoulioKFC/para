from train import *


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
