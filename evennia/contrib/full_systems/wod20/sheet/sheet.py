import evennia

from evennia.contrib.rpg.traits import TraitHandler, TraitProperty
from evennia.objects.objects import DefaultObject, DefaultCharacter
from evennia.utils import lazy_property, evtable


def create_sheet_obj(cls, caller, key_suffix):
    sheet_key = f"{caller.key}::{key_suffix}"

    talents = evennia.search_object(sheet_key)
    if talents and len(talents) == 1:
        return talents[0]
    elif len(talents) > 1:
        # ... what do we do here?  Fling an error?
        pass
        # else we have none, so carry on.

    obj = cls(db_key=sheet_key, db_location=caller)
    obj.save()
    return obj


class Sheet(DefaultObject):

    @staticmethod
    def create(caller: DefaultCharacter) -> 'Sheet':
        return create_sheet_obj(Sheet, caller, "Sheet")

    @lazy_property
    def attribs(self) -> TraitHandler:
        return TraitHandler(self, db_attribute_key="attribs")

    def at_object_creation(self):
        # Add the attributes
        self.attribs.add('strength', 'Strength', type="static", base=1)
        self.attribs.add('dexterity', 'Dexterity', type="static", base=1)
        self.attribs.add('stamina', 'Stamina', type="static", base=1)
        self.attribs.add('charisma', 'Charisma', type="static", base=1)
        self.attribs.add('manipulation', 'Manipulation', type="static", base=1)
        self.attribs.add('appearance', 'Appearance', type="static", base=1)
        self.attribs.add('perception', 'Perception', type="static", base=1)
        self.attribs.add('intelligence', 'Intelligence', type="static", base=1)
        self.attribs.add('wits', 'Wits', type="static", base=1)

    @lazy_property
    def abilities(self) -> 'SheetAbilities':
        return SheetAbilities.create(self)

    def get_trait_display(self, prop: TraitProperty) -> str:
        return f"{prop.name}: {str(int(prop.base))}" + ((" ({})".format(str(int(prop.value)))) if prop.value != prop.base else "")

    def get_formatted_display(self, width: int) -> str:
        physicals = list(map(self.attribs.get, ["strength", "dexterity", "stamina"]))
        str_physicals = "\n".join(list(map(self.get_trait_display, physicals)))

        socials = list(map(self.attribs.get, ["charisma", "manipulation", "appearance"]))
        str_socials = "\n".join(list(map(self.get_trait_display, socials)))

        mentals = list(map(self.attribs.get, ["perception", "intelligence", "wits"]))
        str_mentals = "\n".join(list(map(self.get_trait_display, mentals)))

        abil_blocks = self.abilities.get_formatted_blocks()

        return str(evtable.EvTable(
            table=[
                [str_physicals, "Talents", abil_blocks[0]],
                [str_socials, "Skills", abil_blocks[1]],
                [str_mentals, "Knowledges", abil_blocks[2]]
            ],
            width=width,
            header=False,
            corner_char="+",
            border="cells",
            border_left_char="|c|||n",
            border_right_char="|c|||n",
            pad_top=0,
            valign="t",
            vpad_char=""))


class SheetAbilities(DefaultObject):
    @staticmethod
    def create(caller: Sheet) -> 'SheetAbilities':
        return create_sheet_obj(SheetAbilities, caller, "Abilities")

    @lazy_property
    def talents(self) -> TraitHandler:
        return TraitHandler(self, db_attribute_key="talents")

    @lazy_property
    def skills(self) -> TraitHandler:
        return TraitHandler(self, db_attribute_key="skills")

    @lazy_property
    def knowledges(self) -> TraitHandler:
        return TraitHandler(self, db_attribute_key="knowledges")

    def get_trait_display(self, prop: TraitProperty) -> str:
        return f"{prop.name}: {str(int(prop.base))}" + ((" ({})".format(str(int(prop.value)))) if prop.value != prop.base else "")

    def get_formatted_blocks(self) -> list:
        return [
            "\n".join(list(map(self.get_trait_display, list(map(self.talents.get, self.talents.all()))))),
            "\n".join(list(map(self.get_trait_display, list(map(self.skills.get, self.skills.all()))))),
            "\n".join(list(map(self.get_trait_display, list(map(self.knowledges.get, self.knowledges.all())))))
            ]

    def at_object_creation(self):
        # Add Talents
        self.talents.add("alertness", "Alertness", type="static", base=0)
        self.talents.add("art", "Art", type="static", base=0)
        self.talents.add("athletics", "Athletics", type="static", base=0)
        self.talents.add("awareness", "Awareness", type="static", base=0)
        self.talents.add("brawl", "Brawl", type="static", base=0)
        self.talents.add("empathy", "Empathy", type="static", base=0)
        self.talents.add("expression", "Expression", type="static", base=0)
        self.talents.add("intimidation", "Intimidation", type="static", base=0)
        self.talents.add("leadership", "Leadership", type="static", base=0)
        self.talents.add("streetwise", "Streetwise", type="static", base=0)
        self.talents.add("subterfuge", "Subterfuge", type="static", base=0)

        # Notes: Awareness = Primal Urge / Kenning

        # Add Skills
        self.skills.add("animal_ken", "Animal Ken", type="static", base=0)
        self.skills.add("crafts", "Crafts", type="static", base=0)
        self.skills.add("drive", "Drive", type="static", base=0)
        self.skills.add("etiquette", "Etiquette", type="static", base=0)
        self.skills.add("firearms", "Firearms", type="static", base=0)
        self.skills.add("larceny", "Larceny", type="static", base=0)
        self.skills.add("meditation", "Meditation", type="static", base=0)
        self.skills.add("melee", "Melee", type="static", base=0)
        self.skills.add("research", "Research", type="static", base=0)
        self.skills.add("stealth", "Stealth", type="static", base=0)
        self.skills.add("survival", "Survival", type="static", base=0)

        # Notes: Performance = Art (in Talents), Buh bye Martial Arts

        # add Knowledges
        self.knowledges.add("academics", "Academics", type="static", base=0)
        self.knowledges.add("computer", "Computer", type="static", base=0)
        self.knowledges.add("enigmas", "Enigmas", type="static", base=0)
        self.knowledges.add("esoterica", "Esoterica", type="static", base=0)
        self.knowledges.add("investigation", "Investigation", type="static", base=0)
        self.knowledges.add("law", "Law", type="static", base=0)
        self.knowledges.add("medicine", "Medicine", type="static", base=0)
        self.knowledges.add("occult", "Occult", type="static", base=0)
        self.knowledges.add("politics", "Politics", type="static", base=0)
        self.knowledges.add("science", "Science", type="static", base=0)
        self.knowledges.add("technology", "Technology", type="static", base=0)

        # Notes: Esoterica = Rituals / Gremayre, Buh bye Cosmology and Finance
