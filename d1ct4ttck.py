import sys
sys.path.append('../')
from ECU_models.stage6_model_2 import ecu
from story.dict import attack_dict

def dictionaryAttack(target, attack_dict):
    target.ignitionOn()
    response = 0
    while response not in attack_dict:
        response = target.getSeed()
    target.authenticate(attack_dict[response])
    target.enterTesterMode()

dictionaryAttack(ecu, attack_dict)

