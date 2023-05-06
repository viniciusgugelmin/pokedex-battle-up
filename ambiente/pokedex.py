from flask import Flask, render_template, make_response, jsonify
from flask.globals import request
from models.pokemon import Pokemon
import json
import requests
import random

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

@app.route("/battle", methods = ["POST"])
def battle():
    data =  request.get_json()
    pokemonId1 = data['pokemonId1']
    pokemonId2 = data['pokemonId2']
    token1 = data['token1']
    token2 = data['token2']

    res = requests.get(f"http://localhost:5000/users/pokemons/{pokemonId1}", headers = {"Authorization": token1}).text
    pokemon1 = json.loads(res)["data"]

    res2 = requests.get(f"http://localhost:5000/users/pokemons/{pokemonId2}", headers = {"Authorization": token2}).text
    pokemon2 = json.loads(res2)["data"]

    pokemon1Atk = random.randint(0, pokemon1['attack'])
    pokemon1Def = random.randint(0, pokemon1['defense'])

    pokemon2Atk = random.randint(0, pokemon2['attack'])
    pokemon2Def = random.randint(0, pokemon2['defense'])

    if pokemon1Atk > pokemon2Def:
        pokemon2['life'] -= pokemon1Atk - pokemon2Def

    if pokemon2Atk > pokemon1Def:
        pokemon1['life'] -= pokemon2Atk - pokemon1Def

    battle1Res = requests.patch(f"http://localhost:5000/users/pokemons/{pokemonId1}/battle", headers={"Authorization": token1}).text
    battle2Res = requests.patch(f"http://localhost:5000/users/pokemons/{pokemonId2}/battle", headers={"Authorization": token2}).text

    pokemon1 = json.loads(battle1Res)["data"]
    pokemon2 = json.loads(battle2Res)["data"]

    return make_response(
        jsonify({
            "pokemon1": {
                "data": pokemon1,
                "atk": pokemon1Atk,
                "def": pokemon1Def
            },
            "pokemon2": {
                "data": pokemon2,
                "atk": pokemon2Atk,
                "def": pokemon2Def
            }
        }),
        200
    )

    
if __name__=="__main__":
    app.run(debug=True)


