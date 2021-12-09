from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

trainEnregistrement = []
listTrains ={}
voiePassage = True
# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create server
with SimpleXMLRPCServer(('localhost', 8000),
                        requestHandler=RequestHandler) as server:
    server.register_introspection_functions()

    # Register pow() function; this will use the value of
    # pow.__name__ as the name, which is just 'pow'.
    server.register_function(pow)

    # Register a function under a different name
    def adder_function(x, y):
        return x + y
    server.register_function(adder_function, 'add')

    def chercheTrain(num):
        for i in range(len(trainEnregistrement)):
            if num == trainEnregistrement[i] :
                return True
        return False

    def enregistrer_train(num):
        if chercheTrain(num) :
            print("train présent dans la liste")
            return False
        else:
            trainEnregistrement.append(num)
            print("train ajouté avec succès")
            return True
    server.register_function(enregistrer_train, 'enregistrer')

    def entrer_en_gare(x):
        print("le train " + x + "souhaite rentrer en gare" )
        return 1
    server.register_function(entrer_en_gare, 'entrer')

    def sortir_en_gare(x):
        print("le train " + x + "souhaite sortir de la gare" )
        return 1

    server.register_function(sortir_en_gare, 'sortir')

    # Register an instance; all the methods of the instance are
    # published as XML-RPC methods (in this case, just 'mul').
    class MyFuncs:
        def mul(self, x, y):
            return x * y

    server.register_instance(MyFuncs())

    # Run the server's main loop
    server.serve_forever()
