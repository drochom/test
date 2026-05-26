import numpy as np
import matplotlib.pyplot as plt


class MultiArmedBandit:
    def __init__(self, n_arms=10, seed=None):
        rng = np.random.default_rng(seed)
        self.q_true = rng.normal(0, 1, n_arms)
        self.n_arms = n_arms

    def pull(self, arm):
        return np.random.normal(self.q_true[arm], 1)

    def optimal_arm(self):
        return np.argmax(self.q_true)


class EpsilonGreedy:
    def __init__(self, n_arms=10, epsilon=0.1):
        self.n_arms = n_arms
        self.epsilon = epsilon
        self.q_est = np.zeros(n_arms)
        self.counts = np.zeros(n_arms, dtype=int)

    def select_action(self):
        if np.random.random() < self.epsilon:
            return np.random.randint(self.n_arms)
        return np.argmax(self.q_est)

    def update(self, arm, reward):
        self.counts[arm] += 1
        self.q_est[arm] += (reward - self.q_est[arm]) / self.counts[arm]


def run_experiment(epsilon, n_arms=10, n_steps=1000, n_runs=2000, seed=42):
    np.random.seed(seed)
    rewards = np.zeros((n_runs, n_steps))
    optimal_actions = np.zeros((n_runs, n_steps))

    for run in range(n_runs):
        bandit = MultiArmedBandit(n_arms=n_arms)
        agent = EpsilonGreedy(n_arms=n_arms, epsilon=epsilon)
        optimal = bandit.optimal_arm()

        for step in range(n_steps):
            arm = agent.select_action()
            reward = bandit.pull(arm)
            agent.update(arm, reward)
            rewards[run, step] = reward
            optimal_actions[run, step] = (arm == optimal)

    return rewards.mean(axis=0), optimal_actions.mean(axis=0)


def plot_results(results, epsilons):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    for eps, (avg_reward, pct_optimal) in zip(epsilons, results):
        label = f"ε = {eps}"
        ax1.plot(avg_reward, label=label)
        ax2.plot(pct_optimal * 100, label=label)

    ax1.set_xlabel("Steps")
    ax1.set_ylabel("Average Reward")
    ax1.set_title("10-Arm Bandit: Average Reward over Time")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.set_xlabel("Steps")
    ax2.set_ylabel("% Optimal Action")
    ax2.set_title("10-Arm Bandit: % Optimal Action over Time")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("bandit_results.png", dpi=150)
    print("Plot saved to bandit_results.png")


def main():
    n_arms = 10
    n_steps = 10000
    n_runs = 2000
    epsilons = [0.0, 0.01, 0.1]

    print(f"Running {n_runs} independent runs, {n_steps} steps each...")
    print(f"Epsilons: {epsilons}\n")

    results = []
    for eps in epsilons:
        avg_reward, pct_optimal = run_experiment(eps, n_arms, n_steps, n_runs)
        results.append((avg_reward, pct_optimal))
        final_reward = avg_reward[-100:].mean()
        final_optimal = pct_optimal[-100:].mean() * 100
        print(f"ε={eps:4.2f}  last-100-step avg reward: {final_reward:.4f}  % optimal: {final_optimal:.1f}%")

    plot_results(results, epsilons)


if __name__ == "__main__":
    main()
