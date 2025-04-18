from vgc2.ml.env import BattleEnv
from vgc2.util.encoding import EncodeContext
from vgc2.battle_engine.team import Team, BattlingTeam
from vgc2.agent.battle import RandomBattlePolicy, get_actions
from vgc2.battle_engine.pokemon import Pokemon

from stable_baselines3 import PPO


def test_winrate(agent, num_games = 100, opponent = RandomBattlePolicy):
    wins = []
    for i in range(num_games):
        env = BattleEnv(EncodeContext(), opponent=opponent())
        obs, info = env.reset()
        done = False
        while not done:
            possible_actions = get_actions((env.state_view[0], env.state_view[1]))
            action = agent.predict(obs.reshape(1, -1), deterministic=True)[0]
            obs, reward, done, truncated, info = env.step(action)
            if done:
                wins.append(reward)
    print(f"Winrate: {sum(wins) / len(wins)}")

def train_ppo_agent(agent, episodes = 1000):
    agent.learn(total_timesteps=episodes)
    return agent

if __name__ == '__main__':
    agent = PPO("MlpPolicy", BattleEnv(EncodeContext()), verbose=1)
    test_winrate(agent, num_games=100)
    train_ppo_agent(episodes=100)
    test_winrate(agent, num_games=100)
