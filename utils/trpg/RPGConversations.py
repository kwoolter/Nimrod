__author__ = 'KeithW'

from xml.dom.minidom import *
from .RPGXMLUtilities import *


class ConversationLine(object):

    NOT_ATTEMPTED = 0
    SUCCEEDED = 1
    FAILED = -1
    REWARDED = 2

    def __init__(self, text : str):

        self.text = text
        self.completed = False

    def is_completed(self):
        return self.completed

    def attempt(self):
        self.completed = True
        return self.completed

class Conversation(object):

    def __init__(self, owner : str, linear: bool = True):
        self.owner = owner
        self._lines = []
        self.linear = linear
        self.current_line = 0

    def add_line(self, new_line : ConversationLine):
        self._lines.append(new_line)

    def is_completed(self):

        completed = True

        for line in self._lines:
            if line.is_completed() is False:
                completed = False
                break

        return completed

    # Get the next line in the conversation
    def get_next_line(self):

        # If this conversation has been completed...
        if self.is_completed():
            # then just pick a line at random that is still available
            line = self._lines[random.randint(0,len(self._lines)-1)]

        # Else cycle through the lines in sequence
        else:
            line = self._lines[self.current_line]

            # Move to the next line of the conversation
            self.current_line += 1

            # If you have reached the end of the conversation then go back to the beginning
            if self.current_line >= len(self._lines):
                self.current_line = 0

        return line

    def print(self):
        print("%s conversation." % self.owner)
        for line in self._lines:
            print(str(line))


class ConversationFactory(object):

    def __init__(self, file_name : str):

        self.file_name = file_name
        self._dom = None
        self._conversations = {}

    def get_conversation(self, npc_name : str):
        if npc_name in self._conversations.keys():
            return self._conversations[npc_name]
        else:
            return None

    def print(self):
        for conversation in self._conversations.values():
            conversation.print()

    # Load in the quest contained in the quest file
    def load(self):

        self._dom = parse(self.file_name)

        assert self._dom.documentElement.tagName == "conversations"

        logging.info("%s.load(): Loading in %s", __class__, self.file_name)

        # Get a list of all conversations
        conversations = self._dom.getElementsByTagName("conversation")

        # for each conversation...
        for conversation in conversations:

            # Get the main tags that describe the conversation
            npc_name = xml_get_node_text(conversation, "npc_name")
            linear = (xml_get_node_text(conversation, "linear") == "True")

            # ...and create a basic conversation object
            new_conversation = Conversation(npc_name, linear = linear)

            logging.info("%s.load(): Loading Conversation for NPC '%s'...", __class__, new_conversation.owner)

            # Next get a list of all of the lines
            lines = conversation.getElementsByTagName("line")

            # For each line...
            for line in lines:

                # Get the basic details of the line
                text = xml_get_node_text(line, "text")

                # ... and create a basic line object which we add to the owning conversation
                new_line = ConversationLine(text)
                new_conversation.add_line(new_line)

                logging.info("%s.load(): Loading line '%s'...", __class__, new_line.text)

            logging.info("%s.load(): Conversation '%s' loaded", __class__, new_conversation.owner)

            # Add the new conversation to the dictionary
            self._conversations[new_conversation.owner] = new_conversation

        self._dom.unlink()




