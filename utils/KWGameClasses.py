__author__ = 'user'


from operator import itemgetter
import pickle
import logging


class HighScoreTable():

    def __init__(self, name = "default", max_size = 10, prefix = ""):
        self.name = name
        self.max_size = max_size
        self.prefix = prefix
        self.table = []

    def add(self, name : str, score : float, auto_save = False):

        added = False

        # If the specified score makes it into the high score table...
        if self.is_high_score(score):

            # Add it and re-sort the table
            self.table.append((name, score))
            self.table.sort(key=itemgetter(1,0), reverse=True)
            added = True

        # Trim the size of the table to be the maximum size
        while len(self.table) > self.max_size:
            del self.table[-1]

        if auto_save is True:
            self.save()

        return added

    def is_high_score(self, score):
        if len(self.table) < self.max_size:
            return True
        else:
            name, lowest_score = self.table[len(self.table) - 1]
            if score > lowest_score:
                return True
            elif score == lowest_score and len(self.table) < self.max_size:
                return True
            else:
                return False

    def save(self):
        file_name = self.name + ".hst"
        game_file = open(file_name, "wb")
        pickle.dump(self, game_file)
        game_file.close()

        logging.info("%s saved." % file_name)

    def load(self):

        file_name = self.name + ".hst"

        try:
            game_file = open(file_name, "rb")

            new_table = pickle.load(game_file)

            self.table = new_table.table
            self.max_size = new_table.max_size

            game_file.close()

            logging.info("\n%s loaded.\n" % file_name)

        except IOError:

            logging.warning("High Score Table file %s not found." % file_name)


    def print(self):
        print("%s High Score Table - top %i scores" % (self.name, self.max_size))

        if len(self.table) == 0:
            print("No high scores recorded.")
        else:
            for i in range(len(self.table)):
                name, score = self.table[i]
                print("%i. %s - %s%s" % (i + 1, name, self.prefix, format(score,",d")))






