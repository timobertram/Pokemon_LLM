from numpy.random import choice, multinomial

from vgc2.agent import TeamBuildPolicy, TeamBuildCommand
from vgc2.battle_engine.modifiers import Nature
from vgc2.meta import Meta, Roster


class RandomTeamBuildPolicy(TeamBuildPolicy):
    """
    random team builder.
    """

    def decision(self,
                 roster: Roster,
                 meta: Meta | None,
                 max_team_size: int,
                 max_pkm_moves: int,
                 n_active: int) -> TeamBuildCommand:
        ivs = (31,) * 6
        ids = choice(len(roster), 3, False)
        cmds: TeamBuildCommand = []
        for i in range(len(ids)):
            n_moves = len(roster[i].moves)
            moves = list(choice(n_moves, min(max_pkm_moves, n_moves), False))
            evs = tuple(multinomial(510, [1 / 6] * 6, size=1)[0])
            nature = Nature(choice(len(Nature), 1, False))
            cmds += [(i, evs, ivs, nature, moves)]
        return cmds


class TerminalTeamBuild(TeamBuildPolicy):
    """
    Terminal interface.
    """

    def decision(self,
                 roster: Roster,
                 meta: Meta | None,
                 max_team_size: int,
                 max_pkm_moves: int,
                 n_active: int) -> TeamBuildCommand:
        pass  # TODO terminal team build
