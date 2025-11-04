'''
This is a placeholder file for the actual effects in the game.
It's used to stop errors in files like Entity.py which require variables like allEffects
'''

allEffects = {}

allItems = {
    0: {
        "imgPath": "Sprites/DefaultSprite.png",
        "name": "TestItem",
        "replaces": "None",
        "description": "A test item... Should make you move really fast",
        "effects": "speed * 10",
    }
}

allWeapons = {
    0: {
        "imgPath": "Sprites/DefaultSprite.png",
        "damage": 10
    }
}