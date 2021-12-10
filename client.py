import xmlrpc.client
import sys, os
s = xmlrpc.client.ServerProxy('http://localhost:8000')

if (len(sys.argv) > 2) :
    print("trop grand")
    exit()
if (len(sys.argv) == 1) :
    print("pas d'id")
    exit()


id = sys.argv[1]

enregistrement = s.enregistrer(id)

if enregistrement:
    print("enregistré avec succès")
else:
    print("id déjà utilisé")
    exit()
menu_actions  = {}


def main_menu():
    #os.system('clear')

    print ("Bonjour train n' " + id +",\n")
    print ("Que veux tu faire :")
    print ("1 : entrer en gare ")
    print ("2 : sortir de la gare ")
    print("0 : exit")
    choice = input(" >>  ")
    print(choice)
    exec_menu(choice)

    return

def exec_menu(choice):
    #os.system('clear')
    ch = choice.lower()
    if ch == '':
        main_menu()
    else:
        try:
            menu_actions[choice]()
        except KeyError:
            print ("Invalid selection, please try again.\n")
            main_menu()
    return

def entrer():
    print("entrer")
    s.entrer(id)
    main_menu()
    return

def sortir():
    print("sortir")
    main_menu()
    return

def exit():
    sys.exit()

def etat():
    print("etat")
    return


menu_actions={
    'main_menu':main_menu,
    '1':entrer,
    '2':sortir,
    '3':etat,
    '0':exit,
}

main_menu()
#print(s.pow(2,3))  # Returns 2**3 = 8
#print(s.add(2,3))  # Returns 5
#print(s.mul(5,2))  # Returns 5*2 = 10

# Print list of available methods
#print(s.system.listMethods())
