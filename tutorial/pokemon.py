from vgc2.battle_engine import Move, Type
from vgc2.battle_engine.modifiers import Category, Status, Nature
from vgc2.battle_engine.pokemon import PokemonSpecies, Pokemon


def main():
    move_set = [Move(Type.PSYCHIC, 0, 1., 5, Category.OTHER, toggle_trickroom=True),
                Move(Type.FIRE, 100, .95, 10, Category.SPECIAL, status=Status.BURN)]
    ps = PokemonSpecies((100,) * 6, [Type.PSYCHIC], move_set)
    p = Pokemon(ps, [1, 0], nature=Nature.TIMID)
    print("~ Moves ~")
    for i, m in enumerate(move_set):
        print("Move " + str(i) + ": " + str(m))
    print("~ Pokemon Species ~")
    print(ps)
    print("~ Pokemon ~")
    print(p)


if __name__ == '__main__':
    main()
