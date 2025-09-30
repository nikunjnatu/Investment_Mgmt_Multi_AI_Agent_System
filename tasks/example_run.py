
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.example_agent import ExampleAgent
from protocols.message import Message

if __name__ == "__main__":
    agent = ExampleAgent("Agent1")
    msg = Message(sender="system", content="Hello, agent!")
    response = agent.handle_message(msg)
    print(f"Response: {response.content}")
