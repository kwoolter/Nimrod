__author__ = 'KeithW'

from .RPGCharacter import *
import random


class RPGCheck(object):

    # Constants for storing a player's state of a check
    NOT_ATTEMPTED = 0
    FAILED = -1
    SUCCEEDED = 1
    SILENT_REWARD = "***"
    STAT_NOT_FOUND_DEFAULT = -19680926

    # Construct a basic check
    # A name, optional description and optional completion message
    def __init__(self, name : str, type : str, description : str = "", completion_msg : str=""):

        self.name = name
        self.type = type
        self.description = description
        self.completion_msg = completion_msg

        self._rewards = []
        self._prerequisites = []
        self._checks = []

        self.is_rewarded = False

    # Convert a check to a str
    def __str__(self):
        text = "%s:%s:%s" % (self.name, self.type, self.description)
        # text += (" - pre-reqs(%i), checks(%i), rewards(%i)" % (len(self._prerequisites), len(self._checks), len(self._rewards)))

        return text

    #  Add a reward stat if you succeed the check
    def add_reward(self, new_reward : BaseStat):
        self._rewards.append(new_reward)

    # Return the list of rewards only if they have been earned!
    def get_rewards(self):
        if self.is_rewarded == True:
            return self._rewards.copy()
        else:
            return set()

    # Add pre-requisite stat that must be met before you can attempt the check
    def add_pre_requisite(self, new_prerequisite : BaseStat):
        self._prerequisites.append(new_prerequisite)

    # Add a check stat that is made when you attempt this challenge
    # Optional randomiser parameter to randomly increase the provided stat
    def add_check(self, new_check : BaseStat, randomiser : int = 0):
        new_check.value += random.randint(0, randomiser )
        self._checks.append(new_check)

    # See if the check is available based on a character's current stats
    def is_available(self, character :  RPGCharacter):

        available = True

        # Loop through all of the check's prerequisite stats
        for stat in self._prerequisites:

            # If the stat has no scope defined then default is that the stat belongs to the Character
            if hasattr(stat,"scope") is False:
                stat.scope = False

            # Get what the player's equivalent stat is
            player_stat = character.get_stat(stat.name, global_stat=stat.scope)

            # If the player does not have this stat then use a special default value
            # This is because some pre-reqs might require the absence of a stat
            if player_stat is None:
                player_stat = BaseStat(stat.name, "AUTO",RPGCheck.STAT_NOT_FOUND_DEFAULT)
                logging.info("%s.is_available():Check %s: Player %s does not have stat %s", \
                             __class__, self.name, character.name, stat.name)

            #compare the prerequisite vs player_stat
            logging.info("%s.is_available():Check %s: Player %s %s going to compare - %i vs %i", \
                         __class__, self.name, character.name, stat.name, \
                         player_stat.value, stat.value)

            available = self.compare(player_stat, stat)

            if available is False:
                logging.info("%s.is_available():Check %s: Player %s %s FAILED compare - %i vs %i", \
                         __class__, self.name, character.name, stat.name, \
                         player_stat.value, stat.value)

                break

        logging.info("%s.is_available: Check %s available = %r", __class__, self.name, available)

        return available

    # Check if a check has been completed based on the current player stats
    def is_completed(self, character : RPGCharacter):

        completed = True

        # Attempt to get this challenge stat from the player's stats
        stat = character.get_stat(self.name)

        # If we couldn't find it or it was marked as anything but succeeded the flag as incomplete
        if stat is None or stat.value != RPGCheck.SUCCEEDED:
            completed = False
        else:
            logging.info("Check %s completed %s",stat.name, stat.update_time.strftime("%Y-%m-%d %H:%M"))

        return completed

    #  Attempt a check
    def attempt(self, character :  RPGCharacter):

        # Assume we are going to succeed
        succeed = True

        self.is_rewarded = False

        # See if there is a stat for this challenge already
        stat = character.get_stat(self.name)

        # If not then create one and add it to the supplied engine
        if stat is None:
            stat = CoreStat(self.name,self.type,RPGCheck.NOT_ATTEMPTED)
            character.add_stat(stat)

        # If we have already successfully completed the check then we are done
        if stat.value == RPGCheck.SUCCEEDED:
            logging.info("%s.attempt(). Check %s already completed.", __class__, self.name)
            return succeed

        # Else check that the player meets the prerequisites...
        elif self.is_available(character) == True:

            # Now compare the check stats with those of the player
            for check_stat in self._checks:

                compare_stat = character.get_stat(check_stat.name, global_stat=check_stat.scope)

                # If the player does not have this stat then use a special default value
                # This is because some checks might require the absence of a stat
                if compare_stat is None:
                    compare_stat = BaseStat(check_stat.name, "AUTO",RPGCheck.STAT_NOT_FOUND_DEFAULT)
                    logging.info("%s.attempt(): Player stat not found %s %s.", \
                              __class__, self.name, check_stat.name)
                    # raise Exception(check_stat.failure_msg)

                logging.info("%s.attempt(): Check %s checking %s %i vs player %i", \
                             __class__, self.name, check_stat.name, check_stat.value, compare_stat.value)

                # Make the check comparison of the check stat vs. the player's stat
                # and raise an exception if the check fails
                if self.compare(compare_stat, check_stat) is False:
                    logging.info("%s.attempt(): Check %s %s failed", \
                             __class__, self.name, check_stat.name)
                    raise Exception(check_stat.failure_msg)

            # OK, we have been through the check stats, now see if we succeeded...
            if succeed == True:

                # Set the flag to indicate we succeeded the challenge
                character.update_stat(self.name, RPGCheck.SUCCEEDED)
                logging.info("%s.attempt(): Check %s completed", __class__, self.name)

                #.. and that we are going to get rewarded...
                self.is_rewarded = True

                # and dish out the rewards...
                for stat in self._rewards:
                    current_stat = character.get_stat(stat.name, global_stat=stat.scope)
                    if current_stat is not None:
                        if stat.operator is None or stat.operator == "eq":
                            character.update_stat(stat.name, stat.value, global_stat=stat.scope)
                        else:
                            character.increment_stat(stat.name, stat.value, global_stat=stat.scope)
                    else:
                        new_stat = CoreStat(stat.name,"Reward", stat.value)
                        character.add_stat(new_stat, global_stat=stat.scope)
                    logging.info("%s.attempt(): Reward %s +%i", __class__, stat.name, stat.value)

        # Challenge pre-requisites not met - attempt FAIL
        else:
            succeed = False
            logging.info("%s.attempt(): Challenge %s failed as player did not meet prerequisites", __class__, self.name)

        # After all see if we failed the attempt and log this
        if succeed == False:
            character.update_stat(self.name, RPGCheck.FAILED)

        return succeed

    def compare(self, stat1, stat2):

        result = False
        text = ""

        if hasattr(stat2, "comparator"):
            comparator = stat2.comparator
        else:
            comparator = "gte"

        if comparator == "eq":
            result = (stat1.value == stat2.value)
            if result is False:
                text = "Your %s needs to be equal to %i." % (stat1.name, stat2.value)
        elif comparator == "neq":
            result = (stat1.value != stat2.value)
            if result is False:
                text = "Your %s needs to be not equal to %i." % (stat1.name, stat2.value)
        elif comparator == "gte":
            result = (stat1.value >= stat2.value)
            if result is False:
                text = "Your %s is too low.  Needs to be higher than %i." % (stat1.name, stat2.value)
        elif comparator == "lte":
            result = (stat1.value <= stat2.value)
            if result is False:
                text = "Your %s is too high.  Needs to be lower than %i." % (stat1.name, stat2.value)
        else:
            result = (stat1.value >= stat2.value)

        if result is False and (hasattr(stat2, "failure_msg") is False or stat2.failure_msg is None):
            stat2.failure_msg = text

        logging.info("compare():'%s' compare - %i vs %i = %r", comparator,stat1.value, stat2.value, result)

        return result