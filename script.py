# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('ggplot')
from random import randrange 

def diceroll():
    return randrange(1,7)

def roll_dices(n):
    rolls = []
    for dice in range(0,n):
        roll = diceroll()
        rolls.append(roll)
    return rolls

def hit(attacks, ws_bs):
    # Determine what dice is hit
    to_hit = ws_bs
    if OBSCURED:
        to_hit += 1
    
    # Roll Dice
    rolls = roll_dices(attacks)

    # Rerolls
    if RR_HIT_1:
        for index, dice in enumerate(rolls):
            if dice == 1:
                rolls[index] = diceroll()
    if RR_HIT_ALL:
        for index, dice in enumerate(rolls):
            if dice < to_hit:
                rolls[index] = diceroll()

    # Check if hitted
    hitted = [dice >= to_hit for dice in rolls]
    hits = sum(hitted)  
    return hits

def wound(hits, strength, toughness):
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
    if RR_WOUND_1:
        for index, dice in enumerate(rolls):
            if dice == 1:
                rolls[index] = diceroll()
    if RR_WOUND_ALL:
        for index, dice in enumerate(rolls):
            if dice < to_wound:
                rolls[index] = diceroll()

    # Check if wounded
    wounded = [dice >= to_wound for dice in rolls]
    wounds = sum(wounded)  
    return wounds

        
def save(wounds, ap, inv_save, save):
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

def make_dmg(damage, unsaved_wounds):
    if FEEL_NO_PAIN:
        rolls = roll_dices(damage*unsaved_wounds)
        saved = sum([dice >= FEEL_NO_PAIN for dice in rolls])
        return unsaved_wounds * damage - saved
    return unsaved_wounds * damage

def injury_roll(damage):
    to_kill = 4
    if OBSCURED:
        to_kill += 1
        
    # Roll Dice
    rolls = roll_dices(damage)

    # Check if killed
    if NECRONS and (6 in rolls):
        return False
    would_kill = [dice >= to_kill for dice in rolls]
    return sum(would_kill)>0


    

def simulateAllRolls(attacker, defender, n_simulations, n_attackers=1):
    results = {'hits': [], 'wounds': [], 'unsaved_wounds': [], 
               'damage_inflicted': [], 'injury_rolled': [], 'killed_model': []}
    for i in range(0,n_simulations):
        # Determine weapon attributes if random
        attacks = attacker['A']
        if isinstance(attacks, str):
            random_attacks = int(attacks.strip('D'))
            attacks = randrange(1,random_attacks+1)
        
        damage = attacker['D']
        if isinstance(damage, str):
            random_damage = int(damage.strip('D'))
            damage = randrange(1,random_damage+1)
        
            
        # Hit roll
        hits = hit(attacks, attacker['WS/BS'])
        results['hits'].append(hits)
        
        # Wound roll
        wounds = wound(hits, attacker['S'], defender['T'])
        results['wounds'].append(wounds)
        
        # Save roll
        unsaved_wounds = save(wounds, attacker['AP'], inv_save = defender['iSv'], 
                              save = defender['Sv'])
        results['unsaved_wounds'].append(unsaved_wounds)
        
        # Inflict damage
        damage_inflicted = make_dmg(damage, unsaved_wounds)
        wounds_left = defender['W'] - damage_inflicted
        results['damage_inflicted'].append(damage_inflicted)
        
        # Injury roll
        if wounds_left > 0:
            results['injury_rolled'].append(False)
            results['killed_model'].append(False)
        else:
            results['injury_rolled'].append(True)
            killed = injury_roll(damage)
            results['killed_model'].append(killed)
    return results       


# default characteristics
MEQ = {'T': 4, 'W': 1, 'Sv': 3, 'iSv': 7} # Space Marine equivalent
P_kiss = {'A': 4, 'WS/BS': 3, 'S': 4, 'AP': -1, 'D': 'D3'} # Player with Harlequins Kiss



# Globals
N = 10**4

attacker = {'A': 3, 'WS/BS': 3, 'S': 7, 'AP': -4, 'D': 2}
defender = {'T': 5, 'W': 1, 'Sv': 3, 'iSv': 7}


OBSCURED = False
NECRONS = False
FEEL_NO_PAIN = 5

# Rerolls possible?
RR_HIT_1 = False
RR_HIT_ALL = True
RR_WOUND_1 = False
RR_WOUND_ALL = False

    
if __name__ == '__main__':
    result_dict = simulateAllRolls(attacker, defender, N)
    df = pd.DataFrame(data=result_dict)
    print(df.mean())

        
        
        
        
        