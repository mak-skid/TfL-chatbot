class Identity():
    def __init__(self) -> None:
        self.name = ""

    def askName(self):
        print("Oh, but firstly what is your name?")
        self.name = input("Type your name: ")
        print(f"Nice to meet you, {self.name}.")
    
    def getName(self):
        return self.name