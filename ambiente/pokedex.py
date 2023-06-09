from flask import Flask, render_template, make_response, jsonify
from flask.globals import request
from models.pokemon import Pokemon
import json
import requests
import random
import pika

app = Flask(__name__)
credentials = pika.PlainCredentials('admin', 'admin')
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', credentials=credentials))
channel = connection.channel()
exchange_name = 'default'


@app.route('/')
def index():
    return render_template("index.html")


@app.route("/buscar", methods=["GET", "POST"])
def buscar():
    pokemon = Pokemon(request.form["nome"].lower(), "")
    routing_key = 'hello'
    try:
        res = json.loads(requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon.nome}").text)
        result = res['sprites']
        result = result['front_default']
        pokemon.foto = result
        channel.basic_publish(exchange=exchange_name, routing_key=routing_key,
                              body=bytes(json.dumps(pokemon.__dict__), 'utf-8'))
    except:
        return "Pokemon não encontrado"
    return render_template("index.html",
                           nome=pokemon.nome,
                           foto=pokemon.foto,

                           )


@app.route("/battle", methods=["POST"])
def battle():
    data = request.get_json()
    routing_key = 'battle'
    if not data:
        return make_response(
            jsonify({"message": "No data found", "status": "BAD_REQUEST", "status_code": 400, "data": None}), 400)

    if not data.get("pokemonId1") or not data.get("pokemonId2") or not data.get("token1") or not data.get("token2"):
        return make_response(
            jsonify({"message": "Missing data", "status": "BAD_REQUEST", "status_code": 400, "data": None}), 400)

    pokemonId1 = data['pokemonId1']
    pokemonId2 = data['pokemonId2']
    token1 = data['token1']
    token2 = data['token2']

    res = requests.get(f"http://localhost:5000/users/pokemons/{pokemonId1}", headers={"Authorization": token1}).text
    pokemon1 = json.loads(res)["data"]

    if not pokemon1:
        return make_response(
            jsonify({"message": "Pokemon not found", "status": "BAD_REQUEST", "status_code": 400, "data": None}), 400)

    if pokemon1 is None:
        return make_response(
            jsonify({"message": "Pokemon not found", "status": "NOT_FOUND", "status_code": 404, "data": None}), 404)

    res2 = requests.get(f"http://localhost:5000/users/pokemons/{pokemonId2}", headers={"Authorization": token2}).text
    pokemon2 = json.loads(res2)["data"]

    if not pokemon2:
        return make_response(
            jsonify({"message": "Pokemon not found", "status": "BAD_REQUEST", "status_code": 400, "data": None}), 400)

    if pokemon2 is None:
        return make_response(
            jsonify({"message": "Pokemon not found", "status": "NOT_FOUND", "status_code": 404, "data": None}), 404)

    if pokemon1['life'] == 0 or pokemon2['life'] == 0:
        return make_response(
            jsonify({
                "message": "One of the pokemons is dead",
                "status": "BAD_REQUEST",
                "status_code": 400,
                "data": None
            }),
            400
        )

    pokemon1Atk = random.randint(0, pokemon1['attack'])
    pokemon1Def = random.randint(0, pokemon1['defense'])

    pokemon2Atk = random.randint(0, pokemon2['attack'])
    pokemon2Def = random.randint(0, pokemon2['defense'])

    if pokemon1Atk > pokemon2Def:
        damage = pokemon1Atk - pokemon2Def
        if damage > pokemon2['life']:
            pokemon2['life'] = 0
        else:
            pokemon2['life'] -= damage

    if pokemon2Atk > pokemon1Def:
        damage = pokemon2Atk - pokemon1Def
        if damage > pokemon1['life']:
            pokemon1['life'] = 0
        else:
            pokemon1['life'] -= damage

    channel.basic_publish(exchange=exchange_name, routing_key=routing_key,
                          body=bytes(json.dumps({
                              "pokemon1": pokemon1,
                              "pokemon2": pokemon2,
                          }), 'utf-8'))

    return make_response(
        jsonify({
            "message": "Battle result",
            "status": "SUCCESS",
            "status_code": 200,
            "data": {
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
            }
        }),
        200
    )


if __name__ == '__main__':
    app.run(debug=True, port=5001)
