from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

attacker = {'A': 3, 'WS/BS': 3, 'S': 7, 'AP': -4, 'D': 2}
defender = {'T': 5, 'W': 1, 'Sv': 3, 'iSv': 7}

@app.route('/', methods=['POST', 'GET'])
def index(): 
    if request.method == 'POST':
        for stat in attacker.keys():
            attacker[stat] = request.form[stat]
        for stat in defender.keys():
            defender[stat] = request.form[stat]
        print(attacker)
        print(defender)
        try:
            return render_template('index.html')
        except:
            return 'There was an issue adding your task'
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='192.168.178.20')
