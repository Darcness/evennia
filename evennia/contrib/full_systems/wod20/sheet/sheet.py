import evennia

from evennia.contrib.rpg.traits import TraitHandler, TraitProperty, StaticTrait
from evennia.objects.objects import DefaultObject, DefaultCharacter
from evennia.utils import lazy_property, evtable
from typing import List


class SheetManager:
    @staticmethod
    def create_sheet_obj(cls, caller, key_suffix):
        sheet_key = f"{caller.key}::{key_suffix}"

        found_objs = evennia.search_object(sheet_key)
        if found_objs and len(found_objs) == 1:
            return found_objs[0]
        elif len(found_objs) > 1:
            # ... what do we do here?  Fling an error?
            print("Found multiple items for search: " + repr(found_objs))
            pass
            # else we have none, so carry on.

        obj = evennia.create_object(cls, key=sheet_key, location=caller)
        return obj

    @staticmethod
    def get_trait_display(prop: TraitProperty, width) -> str:
        val_display = " " + str(int(prop.base))
        val_display += ((" ({})".format(str(int(prop.value)))) if prop.value != prop.base else "")

        display_width = width - len(val_display) - 3  # 1-space padding and a column border

        # print("get_trait_display: width ({}) - val_display ({}) - name len ({}) display_width ({}), chars ({})".format(
        #     str(width),
        #     str(len(val_display)),
        #     str(len(prop.name)),
        #     str(display_width),
        #     str(len(prop.name.ljust(display_width, ".")))))
        trait_display = prop.name.ljust(display_width, ".") + " " + val_display

        if prop.trait_type == "ability":
            for spec in prop.specializations:
                trait_display += "\n+- " + spec

        return trait_display

    @staticmethod
    def get_formatted_block(sections: List[List[str]], width: int, **tableArgs) -> str:
        col_width = width // len(sections)
        col_mod = (width - len(sections)) % len(sections)

        table = evtable.EvTable(
            table=sections,
            header=False,
            border="cols",
            border_left_char="|m|||n",
            border_right_char="|m|||n",
            valign="t",
            **tableArgs)

        for col in range(len(sections)):
            wid = (col_width + 1) if col_mod > col else col_width
            table.reformat_column(col, width=wid)

        return str(table)

    @staticmethod
    def get_formatted_trait_block(traits: List[List[TraitProperty]], width: int, **tableArgs) -> str:
        col_width = width // len(traits)
        col_mod = (width - (len(traits) + 1)) % len(traits)

        sections = []
        for i, group in enumerate(traits):
            if i <= len(sections):
                sections.append([])

            for _, trait in enumerate(group):
                wid = (col_width + 1) if col_mod >= i else col_width
                # We lose a character on the first column because of borders.
                wid = (wid - 1) if i == 0 else wid

                if hasattr(trait, 'base') and hasattr(trait, 'value'):
                    sections[i].append(SheetManager.get_trait_display(trait, wid))
                else:
                    sections[i].append(trait.name + ": " + trait.value)

        data = []
        for section in sections:
            data.append(["\n".join(section)])

        return SheetManager.get_formatted_block(data, width, **tableArgs)


class Sheet(DefaultObject):

    @staticmethod
    def construct(caller: DefaultCharacter) -> 'Sheet':
        return SheetManager.create_sheet_obj(Sheet, caller, "Sheet")

    @lazy_property
    def vitals(self) -> TraitHandler:
        return TraitHandler(self, db_attribute_key="vitals")

    @lazy_property
    def attribs(self) -> TraitHandler:
        return TraitHandler(self, db_attribute_key="attribs")

    @lazy_property
    def abilities(self) -> 'SheetAbilities':
        return SheetAbilities.construct(self)
    


    # Object runtime handlers
    def at_object_creation(self):
        # Add common vitals
        self.vitals.add('fullname', "Full Name", trait_type="trait", value="")
        self.vitals.add('concept', "Concept", trait_type="trait", value="")

        # Add the attributes
        self.attribs.add('strength', 'Strength', trait_type="ability", base=1)
        self.attribs.add('dexterity', 'Dexterity', trait_type="ability", base=1)
        self.attribs.add('stamina', 'Stamina', trait_type="ability", base=1)
        self.attribs.add('charisma', 'Charisma', trait_type="ability", base=1)
        self.attribs.add('manipulation', 'Manipulation', trait_type="ability", base=1)
        self.attribs.add('appearance', 'Appearance', trait_type="ability", base=1)
        self.attribs.add('perception', 'Perception', trait_type="ability", base=1)
        self.attribs.add('intelligence', 'Intelligence', trait_type="ability", base=1)
        self.attribs.add('wits', 'Wits', trait_type="ability", base=1)

    def at_object_delete(self):
        # kill any sub objects
        self.abilities.delete()
        return True

    # Methods
    def get_formatted_display(self, target: DefaultCharacter,  width: int) -> str:
        # We add 8 for all of the color characters being stripped out, -2 for the edges.
        top = "|m+" + (f"|n|h[ {target.name} ]|n|m").center(width + 6, "=") + "+|n"
        separator = "|m+" + ("-" * (width - 2)) + "+|n"

        vitals = self.vitals.all()
        vitals_mid = (len(vitals) // 2) + (len(vitals) % 2)
        vital_blocks = [list(map(self.vitals.get, vitals[0:vitals_mid])), list(map(self.vitals.get, vitals[vitals_mid:]))]

        physicals = list(map(self.attribs.get, ["strength", "dexterity", "stamina"]))
        socials = list(map(self.attribs.get, ["charisma", "manipulation", "appearance"]))
        mentals = list(map(self.attribs.get, ["perception", "intelligence", "wits"]))

        abil_blocks = self.abilities.get_trait_blocks()

        blocks = []
        blocks.append(top)
        blocks.append(SheetManager.get_formatted_trait_block(vital_blocks, width))
        blocks.append(separator)
        blocks.append(SheetManager.get_formatted_block(
            [["Physical"], ["Social"], ["Mental"]], width, align="c"))
        blocks.append(SheetManager.get_formatted_trait_block([physicals, socials, mentals], width))
        blocks.append(separator)
        blocks.append(SheetManager.get_formatted_block(
            [["Talents"], ["Skills"], ["Knowledges"]], width, align="c"))
        blocks.append(SheetManager.get_formatted_trait_block(abil_blocks, width))
        blocks.append(separator)

        return "\n".join(blocks)


class SheetAbilities(DefaultObject):
    @staticmethod
    def construct(caller: Sheet) -> 'SheetAbilities':
        return SheetManager.create_sheet_obj(SheetAbilities, caller, "Abilities")

    @lazy_property
    def talents(self) -> TraitHandler:
        return TraitHandler(self, db_attribute_key="talents")

    @lazy_property
    def skills(self) -> TraitHandler:
        return TraitHandler(self, db_attribute_key="skills")

    @lazy_property
    def knowledges(self) -> TraitHandler:
        return TraitHandler(self, db_attribute_key="knowledges")

    def get_trait_blocks(self) -> list:
        return [
            list(map(self.talents.get, self.talents.all())),
            list(map(self.skills.get, self.skills.all())),
            list(map(self.knowledges.get, self.knowledges.all()))
        ]

    def at_object_creation(self):
        # Add Talents
        self.talents.add("alertness", "Alertness", trait_type="ability", base=0)
        self.talents.add("art", "Art", trait_type="ability", base=0)
        self.talents.add("athletics", "Athletics", trait_type="ability", base=0)
        self.talents.add("awareness", "Awareness", trait_type="ability", base=0)
        self.talents.add("brawl", "Brawl", trait_type="ability", base=0)
        self.talents.add("empathy", "Empathy", trait_type="ability", base=0)
        self.talents.add("expression", "Expression", trait_type="ability", base=0)
        self.talents.add("intimidation", "Intimidation", trait_type="ability", base=0)
        self.talents.add("leadership", "Leadership", trait_type="ability", base=0)
        self.talents.add("streetwise", "Streetwise", trait_type="ability", base=0)
        self.talents.add("subterfuge", "Subterfuge", trait_type="ability", base=0)

        # Notes: Awareness = Primal Urge / Kenning

        # Add Skills
        self.skills.add("animal_ken", "Animal Ken", trait_type="ability", base=0)
        self.skills.add("crafts", "Crafts", trait_type="ability", base=0)
        self.skills.add("drive", "Drive", trait_type="ability", base=0)
        self.skills.add("etiquette", "Etiquette", trait_type="ability", base=0)
        self.skills.add("firearms", "Firearms", trait_type="ability", base=0)
        self.skills.add("larceny", "Larceny", trait_type="ability", base=0)
        self.skills.add("meditation", "Meditation", trait_type="ability", base=0)
        self.skills.add("melee", "Melee", trait_type="ability", base=0)
        self.skills.add("research", "Research", trait_type="ability", base=0)
        self.skills.add("stealth", "Stealth", trait_type="ability", base=0)
        self.skills.add("survival", "Survival", trait_type="ability", base=0)

        # Notes: Performance = Art (in Talents), Buh bye Martial Arts

        # add Knowledges
        self.knowledges.add("academics", "Academics", trait_type="ability", base=0)
        self.knowledges.add("computer", "Computer", trait_type="ability", base=0)
        self.knowledges.add("enigmas", "Enigmas", trait_type="ability", base=0)
        self.knowledges.add("esoterica", "Esoterica", trait_type="ability", base=0)
        self.knowledges.add("investigation", "Investigation", trait_type="ability", base=0)
        self.knowledges.add("law", "Law", trait_type="ability", base=0)
        self.knowledges.add("medicine", "Medicine", trait_type="ability", base=0)
        self.knowledges.add("occult", "Occult", trait_type="ability", base=0)
        self.knowledges.add("politics", "Politics", trait_type="ability", base=0)
        self.knowledges.add("science", "Science", trait_type="ability", base=0)
        self.knowledges.add("technology", "Technology", trait_type="ability", base=0)

        # Notes: Esoterica = Rituals / Gremayre, Buh bye Cosmology and Finance
