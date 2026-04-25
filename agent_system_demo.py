"""
What's an Agent - educational demo
Part of the "What's" series

© 2026 Quan Ying | MIT License
"""

import tkinter as tk
import random
from tkinter import messagebox

# =====================================================
# Decision Strategy (Policy / 策略)
# =====================================================

class DecisionStrategy:
    """Policy interface / 决策策略接口"""
    def decide(self, dx, dy):
        raise NotImplementedError


class GreedyStrategy(DecisionStrategy):
    """Greedy policy: always reduce distance to goal / 贪心策略"""
    def decide(self, dx, dy):
        if abs(dx) > abs(dy):
            return "right" if dx > 0 else "left"
        return "down" if dy > 0 else "up"


class NoisyStrategy(DecisionStrategy):
    """
    Suboptimal policy with noise
    带噪声的次优策略（有时会选错）
    """
    def __init__(self, mistake_prob=0.35):
        self.mistake_prob = mistake_prob
        self.base = GreedyStrategy()

    def decide(self, dx, dy):
        if random.random() < self.mistake_prob:
            return random.choice(["up", "down", "left", "right"])
        return self.base.decide(dx, dy)


# =====================================================
# Agent (智能体)
# =====================================================

class Agent:
    """
    Agent core loop:
    Perceive → Decide → Act
    智能体核心循环：感知 → 决策 → 行动
    """

    def __init__(self, x, y, name, color, strategy, speed=4):
        self.start_x = x
        self.start_y = y

        # Internal state (agent state) / 内部状态
        self.x = x
        self.y = y

        self.name = name
        self.color = color
        self.strategy = strategy  # Policy / 策略
        self.speed = speed

        self.last_observation = None  # Observation / 观察
        self.last_action = None       # Action / 动作
        self.reached = False
        self.path = [(x, y)]

    def reset(self):
        """Reset agent to initial state / 重置智能体状态"""
        self.x = self.start_x
        self.y = self.start_y
        self.reached = False
        self.last_observation = None
        self.last_action = None
        self.path = [(self.x, self.y)]

    def perceive(self, target):
        """
        Perception step: observe environment
        感知步骤：从环境中获取观察
        """
        dx = target.x - self.x
        dy = target.y - self.y
        self.last_observation = (dx, dy)
        return dx, dy

    def decide(self, observation):
        """
        Decision step: choose action via policy
        决策步骤：通过策略选择动作
        """
        self.last_action = self.strategy.decide(*observation)
        return self.last_action

    def act(self, action):
        """
        Action step: execute action & change state
        行动步骤：执行动作并更新状态
        """
        if action == "right":
            self.x += self.speed
        elif action == "left":
            self.x -= self.speed
        elif action == "down":
            self.y += self.speed
        elif action == "up":
            self.y -= self.speed

        self.path.append((self.x, self.y))


# =====================================================
# Environment (环境)
# =====================================================

class Target:
    """Goal state in environment / 环境中的目标状态"""
    def __init__(self):
        self.x = None
        self.y = None


# =====================================================
# GUI World (可视化环境)
# =====================================================

class AgentWorldGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("What is an Agent? — Concept + Visualization")

        self.canvas = tk.Canvas(self.root, width=760, height=560, bg="white")
        self.canvas.pack()

        self.label = tk.Label(
            self.root,
            text="Click anywhere to set the GOAL and start the agents ▶",
            font=("Arial", 12)
        )
        self.label.pack()

        self.target = Target()
        self.running = False
        self.notified = set()

        # Same initial state for fair comparison
        START_X, START_Y = 90, 280

        self.agents = [
            Agent(START_X, START_Y, "Good Agent", "green", GreedyStrategy()),
            Agent(START_X, START_Y, "Bad Agent", "orange", NoisyStrategy())
        ]

        # Visual offset (GUI only, not agent state)
        self.offset = {
            "Good Agent": -7,
            "Bad Agent": +7
        }

        self.canvas.bind("<Button-1>", self.set_target)
        self.root.after(100, self.loop)

    # -------------------------
    # Interaction
    # -------------------------

    def set_target(self, event):
        self.target.x = event.x
        self.target.y = event.y
        self.running = True
        self.notified.clear()
        for agent in self.agents:
            agent.reset()

    # -------------------------
    # Simulation Step
    # -------------------------

    def step(self):
        for agent in self.agents:
            if agent.reached:
                continue

            obs = agent.perceive(self.target)
            action = agent.decide(obs)
            agent.act(action)

            if abs(obs[0]) < agent.speed * 2 and abs(obs[1]) < agent.speed * 2:
                agent.x = self.target.x
                agent.y = self.target.y
                agent.reached = True

                if agent.name not in self.notified:
                    self.notified.add(agent.name)
                    messagebox.showinfo(
                        "Goal Reached ✅",
                        f"{agent.name} reached the goal.\n\n"
                        "Same environment.\n"
                        "Same start state.\n"
                        "Different policy → different behavior."
                    )

    # -------------------------
    # Drawing
    # -------------------------

    def draw_agent(self, agent):
        dx = self.offset[agent.name]

        for i in range(1, len(agent.path)):
            x1, y1 = agent.path[i - 1]
            x2, y2 = agent.path[i]
            self.canvas.create_line(
                x1 + dx, y1,
                x2 + dx, y2,
                fill=agent.color,
                width=3
            )

        x, y = agent.x + dx, agent.y

        self.canvas.create_oval(
            x - 8, y - 8,
            x + 8, y + 8,
            fill=agent.color,
            outline="black"
        )

        self.canvas.create_text(
            x + 85, y - 14,
            text=f"{agent.name}  (Agent)",
            fill=agent.color,
            font=("Arial", 10, "bold")
        )

        if agent.last_observation:
            dx_obs, dy_obs = agent.last_observation
            self.canvas.create_text(
                x + 85, y + 4,
                text=f"Observation (dx, dy)",
                fill="gray",
                font=("Arial", 9)
            )

        if agent.last_action:
            self.canvas.create_text(
                x + 85, y + 20,
                text=f"Action: {agent.last_action}",
                fill="gray",
                font=("Arial", 9)
            )

    # -------------------------
    # Main Draw
    # -------------------------

    def draw(self):
        self.canvas.delete("all")

        # Core formula
        self.canvas.create_text(
            380, 18,
            text="Agent = Perceive → Decide → Act",
            font=("Helvetica", 16, "bold")
        )

        # Simple explanation
        self.canvas.create_text(
            520, 90,
            anchor="nw",
            font=("Arial", 10),
            fill="black",
            text=(
                "MAIN IDEA\n\n"
                "• Agents live in a world\n"
                "• They have a goal\n"
                "• They move step by step\n\n"
                "They repeat:\n"
                "Look → Decide → Move"
            )
        )

        # Side notes with core concepts
        self.canvas.create_text(
            520, 250,
            anchor="nw",
            font=("Arial", 10),
            fill="gray",
            text=(
                "AGENT CONCEPT NOTES\n\n"
                "Agent: decision-making entity\n"
                "Environment: the world (canvas)\n"
                "Observation: (dx, dy)\n"
                "Policy: how decisions are made\n"
                "Action: up / down / left / right\n"
                "Goal: target state\n"
                "Termination: goal reached"
            )
        )

        # Target
        if self.target.x is not None:
            self.canvas.create_oval(
                self.target.x - 10, self.target.y - 10,
                self.target.x + 10, self.target.y + 10,
                fill="red"
            )
            self.canvas.create_text(
                self.target.x,
                self.target.y - 18,
                text="GOAL (Environment State)",
                fill="red",
                font=("Arial", 10, "bold")
            )

        for agent in self.agents:
            self.draw_agent(agent)

    # -------------------------
    # Loop
    # -------------------------

    def loop(self):
        if self.running:
            self.step()
        self.draw()
        self.root.after(100, self.loop)


# =====================================================
# Entry
# =====================================================

if __name__ == "__main__":
    AgentWorldGUI().root.mainloop()