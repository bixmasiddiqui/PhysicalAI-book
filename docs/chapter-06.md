---
sidebar_position: 7
title: Chapter 6 - Machine Learning for Robotics
---

# Chapter 6: Machine Learning for Robotics

<div className="chapter-actions">
  <button className="ai-button chat-button">💬 Ask Questions from This Chapter</button>
  <button className="ai-button personalize-button">✨ Personalize this Chapter for Me</button>
  <button className="ai-button translate-button">🌐 Translate to Urdu</button>
</div>

## Learning Objectives

- Apply supervised learning for robot perception tasks
- Understand reinforcement learning for robot control
- Implement imitation learning from demonstrations
- Use deep learning for computer vision in robotics
- Apply sim-to-real transfer techniques

## 6.1 Supervised Learning for Perception

### Object Classification

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models, transforms
from torch.utils.data import DataLoader, Dataset

class RobotVisionClassifier:
    def __init__(self, num_classes, pretrained=True):
        """Image classifier for robot objects"""
        # Load pretrained ResNet
        self.model = models.resnet18(pretrained=pretrained)

        # Modify final layer for our classes
        num_features = self.model.fc.in_features
        self.model.fc = nn.Linear(num_features, num_classes)

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)

        # Optimizer
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.CrossEntropyLoss()

        # Image preprocessing
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    def train_epoch(self, dataloader):
        """Train for one epoch"""
        self.model.train()
        total_loss = 0

        for images, labels in dataloader:
            images = images.to(self.device)
            labels = labels.to(self.device)

            # Forward pass
            outputs = self.model(images)
            loss = self.criterion(outputs, labels)

            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            total_loss += loss.item()

        return total_loss / len(dataloader)

    def predict(self, image):
        """Predict class for single image"""
        self.model.eval()

        # Preprocess
        image_tensor = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            output = self.model(image_tensor)
            _, predicted = torch.max(output, 1)

        return predicted.item()

# Example usage
classifier = RobotVisionClassifier(num_classes=10)
# Then train with your dataset
```

### Grasp Point Detection

```python
import torch.nn as nn

class GraspPointNet(nn.Module):
    def __init__(self):
        """Neural network to predict grasp points from images"""
        super(GraspPointNet, self).__init__()

        # Encoder (feature extraction)
        self.encoder = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )

        # Decoder (grasp point prediction)
        self.decoder = nn.Sequential(
            nn.Conv2d(256, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Upsample(scale_factor=2),
            nn.Conv2d(128, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Upsample(scale_factor=2),
            nn.Conv2d(64, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Upsample(scale_factor=2),
            nn.Conv2d(32, 1, kernel_size=1)  # Output: grasp quality map
        )

    def forward(self, x):
        features = self.encoder(x)
        grasp_map = self.decoder(features)
        return torch.sigmoid(grasp_map)

# Example usage
model = GraspPointNet()
# Input: RGB image (batch_size, 3, H, W)
# Output: Grasp quality map (batch_size, 1, H, W)
```

## 6.2 Reinforcement Learning for Control

### Q-Learning for Navigation

```python
import numpy as np

class QLearningNavigator:
    def __init__(self, state_space, action_space, learning_rate=0.1, gamma=0.95):
        """
        Q-Learning for robot navigation
        state_space: (grid_width, grid_height)
        action_space: number of actions (e.g., 4 for up, down, left, right)
        """
        self.state_space = state_space
        self.action_space = action_space

        # Q-table
        self.Q = np.zeros((*state_space, action_space))

        self.lr = learning_rate
        self.gamma = gamma
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01

    def get_action(self, state):
        """Epsilon-greedy action selection"""
        if np.random.random() < self.epsilon:
            # Explore
            return np.random.randint(self.action_space)
        else:
            # Exploit
            return np.argmax(self.Q[state])

    def update(self, state, action, reward, next_state, done):
        """Update Q-value"""
        current_q = self.Q[state][action]

        if done:
            target_q = reward
        else:
            max_next_q = np.max(self.Q[next_state])
            target_q = reward + self.gamma * max_next_q

        # Q-learning update
        self.Q[state][action] = current_q + self.lr * (target_q - current_q)

        # Decay epsilon
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

# Example environment
class GridWorld:
    def __init__(self, width=10, height=10):
        self.width = width
        self.height = height
        self.reset()

    def reset(self):
        """Reset to start state"""
        self.robot_pos = (0, 0)
        self.goal_pos = (self.width-1, self.height-1)
        return self.robot_pos

    def step(self, action):
        """
        Execute action
        Actions: 0=up, 1=down, 2=left, 3=right
        """
        x, y = self.robot_pos

        if action == 0:  # up
            y = max(0, y - 1)
        elif action == 1:  # down
            y = min(self.height - 1, y + 1)
        elif action == 2:  # left
            x = max(0, x - 1)
        elif action == 3:  # right
            x = min(self.width - 1, x + 1)

        self.robot_pos = (x, y)

        # Reward
        if self.robot_pos == self.goal_pos:
            reward = 100
            done = True
        else:
            reward = -1  # Small penalty for each step
            done = False

        return self.robot_pos, reward, done

# Training loop
env = GridWorld(10, 10)
agent = QLearningNavigator((10, 10), action_space=4)

num_episodes = 500
for episode in range(num_episodes):
    state = env.reset()
    total_reward = 0

    for step in range(100):
        action = agent.get_action(state)
        next_state, reward, done = env.step(action)

        agent.update(state, action, reward, next_state, done)

        state = next_state
        total_reward += reward

        if done:
            break

    if episode % 50 == 0:
        print(f"Episode {episode}, Total Reward: {total_reward}, Epsilon: {agent.epsilon:.3f}")
```

### Deep Q-Network (DQN)

```python
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random

class DQN(nn.Module):
    def __init__(self, state_dim, action_dim):
        super(DQN, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, action_dim)
        )

    def forward(self, x):
        return self.network(x)

class DQNAgent:
    def __init__(self, state_dim, action_dim, learning_rate=0.001):
        self.state_dim = state_dim
        self.action_dim = action_dim

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Networks
        self.policy_net = DQN(state_dim, action_dim).to(self.device)
        self.target_net = DQN(state_dim, action_dim).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())

        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=learning_rate)

        # Replay buffer
        self.memory = deque(maxlen=10000)
        self.batch_size = 64

        self.gamma = 0.99
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01

    def select_action(self, state):
        """Epsilon-greedy action selection"""
        if random.random() < self.epsilon:
            return random.randint(0, self.action_dim - 1)

        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.policy_net(state_tensor)
            return q_values.argmax().item()

    def store_transition(self, state, action, reward, next_state, done):
        """Store experience in replay buffer"""
        self.memory.append((state, action, reward, next_state, done))

    def train(self):
        """Train on batch from replay buffer"""
        if len(self.memory) < self.batch_size:
            return

        # Sample batch
        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)

        # Current Q-values
        current_q = self.policy_net(states).gather(1, actions.unsqueeze(1))

        # Target Q-values
        with torch.no_grad():
            next_q = self.target_net(next_states).max(1)[0]
            target_q = rewards + (1 - dones) * self.gamma * next_q

        # Loss
        loss = nn.MSELoss()(current_q.squeeze(), target_q)

        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def update_target_network(self):
        """Copy policy network to target network"""
        self.target_net.load_state_dict(self.policy_net.state_dict())
```

## 6.3 Imitation Learning

### Behavioral Cloning

```python
import torch
import torch.nn as nn

class BehavioralCloningPolicy(nn.Module):
    def __init__(self, state_dim, action_dim):
        """Learn policy from expert demonstrations"""
        super(BehavioralCloningPolicy, self).__init__()

        self.network = nn.Sequential(
            nn.Linear(state_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU(),
            nn.Linear(256, action_dim),
            nn.Tanh()  # Continuous actions in [-1, 1]
        )

    def forward(self, state):
        return self.network(state)

class BehavioralCloningTrainer:
    def __init__(self, state_dim, action_dim):
        self.policy = BehavioralCloningPolicy(state_dim, action_dim)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=0.001)
        self.criterion = nn.MSELoss()

    def train_on_demonstrations(self, expert_states, expert_actions, epochs=100):
        """Train policy to mimic expert"""
        expert_states = torch.FloatTensor(expert_states)
        expert_actions = torch.FloatTensor(expert_actions)

        for epoch in range(epochs):
            # Forward pass
            predicted_actions = self.policy(expert_states)
            loss = self.criterion(predicted_actions, expert_actions)

            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            if epoch % 10 == 0:
                print(f"Epoch {epoch}, Loss: {loss.item():.4f}")

    def get_action(self, state):
        """Get action from trained policy"""
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            action = self.policy(state_tensor)
        return action.numpy()[0]

# Example: Collect expert demonstrations
expert_states = []  # States observed by expert
expert_actions = []  # Actions taken by expert

# Collect data...
# trainer = BehavioralCloningTrainer(state_dim=4, action_dim=2)
# trainer.train_on_demonstrations(expert_states, expert_actions)
```

## 6.4 Sim-to-Real Transfer

### Domain Randomization

```python
import numpy as np

class DomainRandomizer:
    def __init__(self):
        """Randomize simulation parameters for better real-world transfer"""
        pass

    def randomize_lighting(self, scene):
        """Randomize lighting conditions"""
        light_intensity = np.random.uniform(0.5, 1.5)
        light_color = np.random.uniform([0.8, 0.8, 0.8], [1.0, 1.0, 1.0])
        # Apply to scene...

    def randomize_textures(self, objects):
        """Randomize object textures"""
        for obj in objects:
            texture = self.generate_random_texture()
            # Apply to object...

    def randomize_physics(self, simulator):
        """Randomize physics parameters"""
        friction = np.random.uniform(0.3, 0.9)
        mass_scale = np.random.uniform(0.8, 1.2)
        # Apply to simulator...

    def randomize_camera(self, camera):
        """Randomize camera parameters"""
        noise_std = np.random.uniform(0.0, 0.05)
        position_offset = np.random.uniform(-0.1, 0.1, size=3)
        # Apply to camera...
```

## 6.5 Practical Task: Train Navigation Policy

```python
import gym
import numpy as np
import torch

class RobotNavigationEnv:
    """Custom navigation environment"""
    def __init__(self):
        self.robot_pos = np.array([0.0, 0.0])
        self.goal_pos = np.array([5.0, 5.0])
        self.max_steps = 200
        self.step_count = 0

    def reset(self):
        self.robot_pos = np.random.uniform(-1, 1, size=2)
        self.goal_pos = np.random.uniform(4, 6, size=2)
        self.step_count = 0
        return self._get_state()

    def _get_state(self):
        """State: [robot_x, robot_y, goal_x, goal_y, distance, angle]"""
        diff = self.goal_pos - self.robot_pos
        distance = np.linalg.norm(diff)
        angle = np.arctan2(diff[1], diff[0])
        return np.array([*self.robot_pos, *self.goal_pos, distance, angle])

    def step(self, action):
        """Action: [velocity_x, velocity_y]"""
        self.robot_pos += action * 0.1
        self.step_count += 1

        distance = np.linalg.norm(self.goal_pos - self.robot_pos)

        # Reward
        if distance < 0.5:
            reward = 100
            done = True
        elif self.step_count >= self.max_steps:
            reward = -10
            done = True
        else:
            reward = -distance * 0.1  # Reward for getting closer
            done = False

        return self._get_state(), reward, done

# Train DQN agent
env = RobotNavigationEnv()
agent = DQNAgent(state_dim=6, action_dim=4)  # 4 discrete actions

episodes = 1000
for episode in range(episodes):
    state = env.reset()
    total_reward = 0

    for step in range(200):
        action = agent.select_action(state)

        # Convert discrete action to continuous
        action_map = {
            0: [1, 0],   # right
            1: [-1, 0],  # left
            2: [0, 1],   # up
            3: [0, -1]   # down
        }
        continuous_action = action_map[action]

        next_state, reward, done = env.step(np.array(continuous_action))

        agent.store_transition(state, action, reward, next_state, done)
        agent.train()

        state = next_state
        total_reward += reward

        if done:
            break

    if episode % 10 == 0:
        agent.update_target_network()
        print(f"Episode {episode}, Reward: {total_reward:.2f}")
```

## Glossary

- **Supervised Learning**: Learning from labeled examples
- **Reinforcement Learning**: Learning from rewards
- **Imitation Learning**: Learning from demonstrations
- **Q-Learning**: Value-based RL algorithm
- **DQN**: Deep Q-Network using neural networks
- **Behavioral Cloning**: Supervised imitation learning
- **Sim-to-Real**: Transferring from simulation to reality
- **Domain Randomization**: Randomizing simulation for robustness

## Checkpoint Quiz

<div className="quiz-container">

### Question 1
What is the main challenge of supervised learning for robotics?

A) Too slow
B) Requires large labeled datasets
C) Cannot work with images
D) Only works in simulation

<details>
<summary>Show Answer</summary>
**Answer: B** - Supervised learning requires extensive labeled training data.
</details>

### Question 2
What does the "Q" in Q-Learning represent?

A) Quantity of data
B) Quality of action-state pairs
C) Quick learning rate
D) Quantum state

<details>
<summary>Show Answer</summary>
**Answer: B** - Q-value represents expected future reward for action-state pairs.
</details>

### Question 3
Why is sim-to-real transfer challenging?

A) Simulations are too slow
B) Reality gap between simulation and real world
C) Simulations cannot model physics
D) Real robots are too expensive

<details>
<summary>Show Answer</summary>
**Answer: B** - The reality gap causes policies to fail when transferred to real robots.
</details>

</div>

## AI Assistant Prompts for Deep Learning

1. "Explain the difference between supervised, reinforcement, and imitation learning for robots."
2. "How does Q-learning work? Walk me through the algorithm with a robot example."
3. "What is the reality gap in sim-to-real transfer and how can we overcome it?"
4. "Compare behavioral cloning vs reinforcement learning for robot manipulation tasks."
5. "Explain domain randomization and why it helps with sim-to-real transfer."

---

**Previous**: [Chapter 5: Actuators and Control](./chapter-05.md) | **Next**: [Chapter 7: Motion Planning](./chapter-07.md)
