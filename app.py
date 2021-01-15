from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from kt_simulation import * 

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index(): 
    if request.method == 'POST':
        attacker = {'A': None, 'WS/BS': None, 'S': None, 'AP': None, 'D': None}
        defender = {'T': None, 'W': None, 'Sv': None, 'iSv': None, 'FNP':None}
        # Attackers stats
        for stat in attacker.keys():
            attacker[stat] = request.form[stat]
        for stat in defender.keys():
            defender[stat] = request.form[stat]
        
        exception_rules = {}
        for key in request.form:
            if key not in attacker and key not in defender:
                exception_rules[request.form[key]] = True
                print("NOT IN STATS ", key)
                print("VALUE: ", request.form[key])


        try:
            results = simulateAllRolls(attacker, defender, 10**4, **exception_rules)
        except:
            return '''There is something wrong with your inputs.
            Either something is not supported yet, or you forgot to
            put in values for e.g. Attacks. Only the fields AP, Save
            Invulnerable Save and Feel No Pain may be empty.'''
        try:
            return render_template('index.html', results=results)
        except:
            return 'ERROR WITH CALC'
    else:
        return render_template('index.html', results={})

if __name__ == '__main__':
    app.run(debug=True, host='192.168.178.20')
