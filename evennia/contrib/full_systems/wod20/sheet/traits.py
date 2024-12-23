from evennia.contrib.rpg.traits import StaticTrait

class AbilityTrait(StaticTrait):
    trait_type = "ability"

    default_keys = {"base": 0, "mod": 0, "mult": 1.0, 'specializations': []}

