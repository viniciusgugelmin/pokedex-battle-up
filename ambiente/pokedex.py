from flask import Flask, render_template
from flask.globals import request
from models.pokemon import Pokemon
import json
import requests
app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/buscar", methods = ["GET", "POST"])
def buscar():
    pokemon = Pokemon(request.form["nome"].lower(), "")
    try:
        res = json.loads(requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon.nome}").text)
        result = res['sprites']
        result = result['front_default']
        pokemon.foto = result
    except:
        return "Pokemon não encontrando"         
    return render_template("index.html",
    nome = pokemon.nome,
    foto = pokemon.foto,   
    
    )
    
if __name__=="__main__":
    app.run(debug=True)


