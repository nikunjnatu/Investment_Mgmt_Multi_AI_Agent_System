from protocols.message import Message

class ExampleAgent:
    def __init__(self, name):
        self.name = name

    def handle_message(self, message: Message):
        print(f"{self.name} received: {message.content}")
        # Example: echo the message
        return Message(sender=self.name, content=f"Echo: {message.content}")
