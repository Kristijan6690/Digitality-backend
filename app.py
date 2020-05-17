from flask import Flask, jsonify , request, json
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
import datetime

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb+srv://Kristijan_10:Messi123@digitality-4hkuh.mongodb.net/Digitality?retryWrites=true&w=majority'


mongo = PyMongo(app)
bcrypt = Bcrypt(app)
CORS(app)

@app.route('/')
def index():
    return "Hello World"


@app.route('/register', methods=['POST'])
def registracija():
    
    ime = request.get_json()['ime']
    prezime = request.get_json()['prezime']
    email = request.get_json()['email']
    password = bcrypt.generate_password_hash(request.get_json()['password'])

    mongo.db.Korisnik.insert({
        'ime' : ime,
        'prezime' : prezime,
        'email' : email,
        'password' : password
    })

    return "Poslano"


# Dovršiti access token da vraća sve potrebne atribute uključujući authenticated
@app.route('/login', methods=['POST'])
def login():

    access = ""

    if (mongo.db.Korisnik.count() == 0):
        access = False
        return jsonify(access)

    else:
        email = request.get_json()['email']
        password = request.get_json()['password']

        for x in mongo.db.Korisnik.find():
            if (x['email'] == email):
                if bcrypt.check_password_hash(x['password'],password):
                    access = {
                        'ID' : str(x['_id']),
                        'ime' : x['ime'],
                        'prezime' : x['prezime'],
                        'email' : x['email']
                    }     
                else:
                    access = False

        return jsonify(access)


# Dovršiti da vraća arhive za određenog usera/arhive kojima ima pristup(PUBLIC)
@app.route('/archives')
def getarhive():

    if (mongo.db.Lista_arhiva.count()== 0):
        provjera = False
        return provjera

    else:
        arhive = {}
        i = 0
        
        for x in mongo.db.Lista_arhiva.find():
            arhive[i] = {
                'ID' : str(x['_id']),
                'naziv' : x['naziv'].capitalize(),
                'datum_dodavanja' : x['datum_dodavanja']
            }
            i += 1

        return jsonify(arhive)


# Dovršiti da vraća dokumente za određenog usera
@app.route('/documents', methods=['POST'])
def getdocument():

    naziv_arhive = request.get_json()['naziv'].lower()
    dokumenti = {}
    i = 0

    for x in mongo.db.Lista_arhiva.find():
        if (naziv_arhive == x['naziv']):
            if (not x['documents']):
                dokumenti = False
                break
            else:
                for y in x['documents']:    
                    # staviti if da se nađe id korisnika
                    dokumenti[i] = {
                        'id' : str(y['id']),
                        'naziv' : y['naziv_doc'].capitalize()
                    }
                    i += 1

    return jsonify(dokumenti)


# Proces spremanje dokumenta u bazu nakon skeniranja. Još u razradi za sada sprema samo blob i ime dokumenta u bazu
@app.route('/send_document', methods=['POST'])
def sendDocument():
    docfile = request.get_json()['docfile']
    docname = request.get_json()['docname']
    mongo.db.test_loadImage.insert({
        'docfile' : docfile,
        'docname' : docname
    })

    return "Poslano u bazu"


@app.route('/search/lista_arhiva', methods=['POST'])
def searchArchives():

    searchTerm = str(request.get_json()['searchTerm'])
    searchTerm = searchTerm.lower()
    rezultat = {}
    i = 0

    if(searchTerm):

        cursor = mongo.db.Lista_arhiva.find({'naziv':{'$regex':'^(%s)' % searchTerm}})
        result = list(cursor)
        
        for x in result:
            rezultat[i] = {
                'ID' : str(x['_id']),
                'naziv' : x['naziv'].capitalize()
            }
            i += 1
            
        return jsonify(rezultat)

    else:
        for x in mongo.db.Lista_arhiva.find():
            rezultat[i] = {
                'ID' : str(x['_id']),
                'naziv' : x['naziv'].capitalize()
            }
            i += 1  
            
        return jsonify(rezultat)  


@app.route('/archives/createSubarchive', methods=['POST'])
def createSubarchive():
    archive_name = request.get_json()['archive_name']
    archive_access_user_ID = request.get_json()['archive_access_user_ID']

    mongo.db.Lista_arhiva.insert({
        'naziv' : archive_name,
        'datum_dodavanja' : datetime.datetime.utcnow(),
        'access_user_id' : [archive_access_user_ID],
        'documents' : []
    })


    return "radi"


if __name__ == "__main__":
    app.run(port=5000, debug=True)
