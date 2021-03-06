from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from multiprocessing import *
import curses


#etat du train
ETAT_DEHORS = "dehors"#état ou le train est en dehors de la gare il ne fait rien
ETAT_ATTENTE_ENTRER = "attenteEntrer"#état ou le train est en attente de rentrer
ETAT_ATTENTE_SORTIR = "attenteSortir"#état ou le train est en attente de sortir
ETAT_GARAGE = "garage"#état ou le train est dans le garage
ETAT_VOIE_PRINCIPALE = "voiePrincipale"#état ou le train est sur la voie principale

#fonction de changement d'état des trains

trainEnregistrement = []#enregistrement des trains
trainEnregistrementPipe = []#enregistrement des voies de communications avec les différents trains [writer,reader]
voieGarePrincipale = [] #la ou les voies qui servent à sortir de gare
voieGarage = [] #les différentes voies interne de la gare
garage = 4 #4 places de garage
trainAttenteRentrer = []#train en attente de rentrer
trainAttenteSortir = []#train en attente de sortir
ordonanceurPipe = []#pipe de l'ordonnanceur [writer,reader]


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


stdscr = curses.initscr()

# Affichage
def initAffichage():
    pass
    # curses.noecho()
    # curses.cbreak()
    # stdscr.keypad(True)

def desactiverAffichage():
    pass
    # stdscr.keypad(False)
    # curses.nocbreak()
    # curses.echo()

    curses.endwin()


BLOC_TRAINS_W = 20


def afficherListeTrainsAttenteEntree():
    x = BLOC_TRAINS_W + 10
    y = 0

    stdscr.addstr(y, x, "== En attente d'entrée ==")

    for i in range(len(trainAttenteRentrer)):
        y = y + 1
        stdscr.addstr(y, x, str(trainAttenteRentrer[i]))


def rafraichirAffichage():
    stdscr.clear()

    afficherListeTrainsAttenteEntree()
    # stdscr.addstr(0, 0, "Coucou je suis un texte")

    stdscr.refresh()


#processus des trains
def trainFils(pipeWrite,pipeRead,idTrain):
    while(1):
        etat = ETAT_DEHORS
        action = pipeRead.recv()

        if action == "entrer" :
            etat = ETAT_ATTENTE_ENTRER

            pipeWrite.send()

        elif action == "sortir" :
            etat = ETAT_ATTENTE_SORTIR
            pipeWrite.send()

def ordonanceur(pipeWrite,pipeRead):
    while(1):
        idTrain = pipeRead.recv()
        pipeReadTrain = get_pipeRead(idTrain)
        action = pipeReadTrain.recv()
        if action == "entrer":
            return
        elif action == "sortir":
            return

    return


def voie_libre() :
    return len(voieGarePrincipale) == 0

def reste_place_dans_garage() :
    return len(voieGarage) < garage

def ajoute_train_garage(numero_train):
    if (reste_place_dans_garage()):
        voieGarage.append(numero_train)
        return 1
    else :
        return -1
def ajoute_train_voie_principale(numero_train):
    if (voie_libre()):
        voieGarePrincipale.append(numero_train)
        return 1
    else :
        return -1
def renvoi_place_train_dans_liste(numero_train):
    for i in range(len(trainEnregistrement)):
        if num == trainEnregistrement[i] :
            return i
    return -1
def get_pipeWriter(numero_train):
    place = renvoi_place_train_dans_liste(numero_train)
    if ( place > -1 ):
        return trainEnregistrementPipe[place][0]
    else:
        return -1
def get_pipeRead(numero_train):
    place = renvoi_place_train_dans_liste(numero_train)
    if ( place > -1 ):
        return trainEnregistrementPipe[place][1]
    else:
        return -1

def envoi_messsage_entrer(numero_train):
    pipeWrite = get_pipeWriter(numero_train)
    if pipeWrite != -1 :
        pipeWrite.send("entrer")
        return 1
    else :
        return -1
def envoi_messsage_sortir(numero_train):
    pipeWrite = get_pipeWriter(numero_train)
    if pipeWrite != -1 :
        pipeWrite.send("sortir")
        return 1
    else :
        return -1

def creation_train_processus(idTrain):
    pipeRead, pipeWrite = Pipe()
    trainEnregistrementPipe.append([pipeRead, pipeWrite])
    p = Process( target=trainFils, args=( [pipeWrite,pipeRead,idTrain] ) )
    p.start()

def creation_ordonanceur():
    if len(ordonanceurPipe) == 0:
        pipeRead, pipeWrite = Pipe()
        ordonanceurPipe.append([pipeRead, pipeWrite])
        p = Process( target=ordonanceur, args=( [pipeWrite,pipeRead] ) )
        p.start()


# Create server
with SimpleXMLRPCServer(('localhost', 8000),
                        requestHandler=RequestHandler, logRequests=False) as server:
    server.register_introspection_functions()

    def chercheTrain(num):
        for i in range(len(trainEnregistrement)):
            if num == trainEnregistrement[i] :
                return True
        return False

    def enregistrer_train(num):
        if chercheTrain(num) :
            # print("train présent dans la liste")
            return False
        else:
            trainEnregistrement.append(num)
            creation_train_processus(num)
            # print("train ajouté avec succès")
            return True

    server.register_function(enregistrer_train, 'enregistrer')

    def entrer_en_gare(x):
        # print("le train " + x + "souhaite rentrer en gare" )
        rafraichirAffichage()
        return 1

    server.register_function(entrer_en_gare, 'entrer')

    def sortir_en_gare(x):
        # print("le train " + x + "souhaite sortir de la gare" )
        rafraichirAffichage()
        return 1

    server.register_function(sortir_en_gare, 'sortir')

    # Rafraîchir l'affichage
    initAffichage()
    rafraichirAffichage()

    # Run the server's main loop
    server.serve_forever()
    desactiverAffichage()
