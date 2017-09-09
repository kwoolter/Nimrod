import model
import view
import audio


class Controller:
    def __init__(self):
        self.model = model.Model("Nimrod")
        self.view = view.MainFrame(self.model)
        self.audio = audio.AudioManager()


    def run(self):
        print("Here we go....")
        print(self.model)
