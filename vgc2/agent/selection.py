from random import shuffle

from vgc2.agent import SelectionPolicy, SelectionCommand
from vgc2.battle_engine import Team


class BasicSelectionPolicy(SelectionPolicy):
    """
    Policy that selects team members in order.
    """

    def decision(self,
                 teams: tuple[Team, Team],
                 max_size: int) -> SelectionCommand:
        return list(set(range(len(teams[0].members))))[:max_size]


class RandomSelectionPolicy(SelectionPolicy):
    """
    Policy that selects team members in a random order.
    """

    def decision(self,
                 teams: tuple[Team, Team],
                 max_size: int) -> SelectionCommand:
        ids = list(set(range(len(teams[0].members))))[:max_size]
        shuffle(ids)
        return ids


class TerminalSelection(SelectionPolicy):
    """
    Terminal selection interface.
    """

    def decision(self, teams: tuple[Team, Team], max_size: int) -> SelectionCommand:
        print('~ Opponent ~')
        for p in teams[1].members:
            print(p)
        print('~ My Team ~')
        for i, p in enumerate(teams[0].members):
            print(i, '->', p)
        print('Select action in the format p p p... with p in {0, 1, ...}')
        while True:
            valid = True
            try:
                t = input('Team: ')
                m = t.split()
                if len(m) < min(max_size, len(teams[0].members)):
                    print('Invalid action. Select again.')
                    continue
                for d in m:
                    if not d.isdigit() and 0 < int(d) < len(teams[0].members):
                        print('Invalid action. Select again.')
                        valid = False
                        break
                if valid:
                    break
            except:
                print('Invalid action. Select again.')
        print()
        return list({int(x) for x in t.split()})
