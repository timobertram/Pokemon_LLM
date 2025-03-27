from enum import IntEnum

Stats = tuple[int, int, int, int, int, int]
MutableStats = list[int]


class Type(IntEnum):
    NORMAL = 0
    FIRE = 1
    WATER = 2
    ELECTRIC = 3
    GRASS = 4
    ICE = 5
    FIGHT = 6
    POISON = 7
    GROUND = 8
    FLYING = 9
    PSYCHIC = 10
    BUG = 11
    ROCK = 12
    GHOST = 13
    DRAGON = 14
    DARK = 15
    STEEL = 16
    FAIRY = 17
    TYPELESS = 18


class Category(IntEnum):
    OTHER = 0
    PHYSICAL = 1
    SPECIAL = 2


class Stat:
    # perm
    MAX_HP = 0
    ATTACK = 1
    DEFENSE = 2
    SPECIAL_ATTACK = 3
    SPECIAL_DEFENSE = 4
    SPEED = 5
    # temp
    EVASION = 6
    ACCURACY = 7


class Status(IntEnum):
    NONE = 0
    SLEEP = 1
    BURN = 2
    FROZEN = 3
    PARALYZED = 4
    POISON = 5
    TOXIC = 6


class Weather(IntEnum):
    CLEAR = 0
    RAIN = 1
    SUN = 2
    SAND = 3
    SNOW = 4


class Hazard(IntEnum):
    NONE = 0
    STEALTH_ROCK = 1
    TOXIC_SPIKES = 2


class Terrain(IntEnum):
    NONE = 0
    ELECTRIC_TERRAIN = 1
    GRASSY_TERRAIN = 2
    MISTY_TERRAIN = 3
    PSYCHIC_TERRAIN = 4


class Nature(IntEnum):
    HARDY = 0
    LONELY = 1
    BRAVE = 2
    ADAMANT = 3
    NAUGHTY = 4
    BOLD = 5
    DOCILE = 6
    RELAXED = 7
    IMPISH = 8
    LAX = 9
    TIMID = 10
    HASTY = 11
    SERIOUS = 12
    JOLLY = 13
    NAIVE = 14
    MODEST = 15
    MILD = 16
    QUIET = 17
    BASHFUL = 18
    RASH = 19
    CALM = 20
    GENTLE = 21
    SASSY = 22
    CAREFUL = 23
    QUIRKY = 24
