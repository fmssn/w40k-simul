# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import pandas as pd
from random import randrange 

def diceroll():
    return randrange(1,7)

def roll_dices(n):
    rolls = []
    for dice in range(0,n):
        roll = diceroll()
        rolls.append(roll)
    return rolls

def hit(attacks, ws_bs, **kwargs):
    # Determine what dice is hit
    to_hit = ws_bs
    if "OBSCURED" in kwargs and kwargs["OBSCURED"]:
        to_hit += 1
    
    # Roll Dice
    rolls = roll_dices(attacks)

    # Rerolls
    if "RR_HIT_1" in kwargs and kwargs["RR_HIT_1"]:
        for index, dice in enumerate(rolls):
            if dice == 1:
                rolls[index] = diceroll()
    if "RR_HIT_ALL" in kwargs and kwargs["RR_HIT_ALL"]:
        for index, dice in enumerate(rolls):
            if dice < to_hit:
                rolls[index] = diceroll()

    # Check if hitted
    hitted = [dice >= to_hit for dice in rolls]
    hits = sum(hitted)  
    return hits

def wound(hits, strength, toughness, **kwargs):
    if strength >= 2*toughness:
        to_wound = 2
    elif strength > toughness:
        to_wound = 3
    elif strength == toughness:
        to_wound = 4
    elif strength < toughness:
        to_wound = 5
    elif 2*strength <= toughness:
        to_wound = 6
    else:
        raise ValueError('Strength or toughness not valid.')
    
    # Roll Dice
    rolls = roll_dices(hits)

    # Rerolls
    if "RR_WOUND_1" in kwargs and kwargs["RR_WOUND_1"]:
        for index, dice in enumerate(rolls):
            if dice == 1:
                rolls[index] = diceroll()
    if "RR_WOUND_ALL" in kwargs and kwargs["RR_WOUND_ALL"]:
        for index, dice in enumerate(rolls):
            if dice < to_wound:
                rolls[index] = diceroll()

    # Check if wounded
    wounded = [dice >= to_wound for dice in rolls]
    wounds = sum(wounded)  
    return wounds
      
def save(wounds, ap, inv_save, save, **kwargs):
    if abs(ap) + save > inv_save:
        to_save = inv_save
    else:
        to_save = save + abs(ap)
    unsaved_wounds = 0
    
    # Roll Dice
    rolls = roll_dices(wounds)

    # Check if saved
    unsaved = [dice < to_save for dice in rolls]
    unsaved_wounds = sum(unsaved)  
    return unsaved_wounds

def make_dmg(damage, feel_no_pain, unsaved_wounds, **kwargs):
    if feel_no_pain != 7:
        rolls = roll_dices(damage*unsaved_wounds)
        saved = sum([dice >= feel_no_pain for dice in rolls])
        return unsaved_wounds * damage - saved
    return unsaved_wounds * damage

def injury_roll(damage, **kwargs):
    to_kill = 4
    print(kwargs)
    if "OBSCURED" in kwargs and kwargs["OBSCURED"]:
        to_kill += 1
        
    # Roll Dice
    rolls = roll_dices(damage)

    # Check if killed
    if "NECRONS" in kwargs and kwargs["NECRONS"] and (6 in rolls):
        return False
    would_kill = [dice >= to_kill for dice in rolls]
    return sum(would_kill)>0

def random_stat(stat_string):
    roll_value = int(stat_string.strip('D'))
    return randrange(1, roll_value+1)
    

def formatAttacker(attackerArg):
    '''Formats the attackers stats to int. Strips + for e.g. WS 3+
    and sets random value for e.g. "D6".''' # TODO Major Perfomance Issues
    attacker = dict(attackerArg)
    # Attacks
    if 'D' in attacker['A']:
        attacker['A'] = random_stat(attacker['A'])
    else:
        attacker['A'] = int(attacker['A'])
    # Weapon Skill / Ballistic Skill
    if '+' in attacker['WS/BS']:
        attacker['WS/BS'] = int(attacker['WS/BS'].strip('+'))
    else:
        attacker['WS/BS'] = int(attacker['WS/BS'])
    # Strength
    attacker['S'] = int(attacker['S'])
    # Armor Penetration
    if attacker['AP'] == '':
        attacker['AP'] = 0
    else:
        attacker['AP'] = -abs(int(attacker['AP']))
    # Damage
    if 'D' in attacker['D']:
        attacker['D'] = random_stat(attacker['D'])
    else:
        attacker['D'] = int(attacker['D'])
    return attacker

def formatDefender(defenderArg):
    '''Formats the defenders stats to int. Strips + for e.g. Sv 3+
    and sets random value for e.g. "D6".'''
    defender = dict(defenderArg)
    # Toughness
    defender['T'] = int(defender['T'])
    # Wounds
    defender['W'] = int(defender['W'])
    # Save (normal)
    if '+' in defender['Sv']:
        defender['Sv'] = int(defender['Sv'].strip('+'))
    elif defender['Sv'] == '':
        defender['Sv'] = 7
    else:
        defender['Sv'] = int(defender['Sv'])
    # Invulnerable Save
    if '+' in defender['iSv']:
        defender['iSv'] = int(defender['iSv'].strip('+'))
    elif defender['iSv'] == '':
        defender['iSv'] = 7
    else:
        defender['iSv'] = int(defender['iSv'])
    # Feel No Pain
    if '+' in defender['FNP']:
        defender['FNP'] = int(defender['FNP'].strip('+'))
    elif defender['FNP'] == '':
        defender['FNP'] = 7
    else:
        defender['FNP'] = int(defender['FNP'])
    return defender

def simulateAllRolls(attackerArg, defenderArg, n_simulations, **kwargs):
    results = {'hits': [], 'wounds': [], 'unsaved_wounds': [], 
               'damage_inflicted': [], 'injury_rolled': [], 'killed_model': []}
    for i in range(0,n_simulations):
        # Format dicts to int
        attacker = formatAttacker(attackerArg)
        defender = formatDefender(defenderArg)
        # Hit roll
        hits = hit(attacker['A'], attacker['WS/BS'], **kwargs)
        results['hits'].append(hits)
        
        # Wound roll
        wounds = wound(hits, attacker['S'], defender['T'], **kwargs)
        results['wounds'].append(wounds)
        
        # Save roll
        unsaved_wounds = save(wounds, attacker['AP'], inv_save = defender['iSv'], 
                              save = defender['Sv'], **kwargs)
        results['unsaved_wounds'].append(unsaved_wounds)
        
        # Inflict damage
        damage_inflicted = make_dmg(attacker['D'], defender['FNP'], unsaved_wounds, **kwargs)
        wounds_left = defender['W'] - damage_inflicted
        results['damage_inflicted'].append(damage_inflicted)
        
        # Injury roll
        if wounds_left > 0:
            results['injury_rolled'].append(False)
            results['killed_model'].append(False)
        else:
            results['injury_rolled'].append(True)
            killed = injury_roll(attacker['D'], **kwargs)
            results['killed_model'].append(killed)
    df_results = pd.DataFrame(data=results).mean() # Get average over all results
    return df_results.to_dict()       

# default characteristics
MEQ = {'T': 4, 'W': 1, 'Sv': 3, 'iSv': 7, 'FNP':7} # Space Marine equivalent
P_kiss = {'A': 4, 'WS/BS': 3, 'S': 4, 'AP': -1, 'D': 'D3'} # Player with Harlequins Kiss



# Globals
N = 10**4


    
if __name__ == '__main__':
    print(simulateAllRolls(attacker, defender, N))
    #df = pd.DataFrame(data=result_dict)
    #print(df.mean())
