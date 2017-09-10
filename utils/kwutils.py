__author__ = 'user'

import logging, sys, time

# Function to ask the user a simple Yes/No confirmation and return a boolean
def confirm(question : str):

    choices = ["Yes", "No"]

    while True:
        print(question)
        for i in range(0, len(choices)):
            print("%i. %s" % (i+1, choices[i]))
        choice = input("Choice?")
        if is_numeric(choice) and int(choice) > 0 and int(choice) <= (len(choices)):
            break
        else:
            print("Invalid choice.  Try again!")

    return (int(choice) == 1)


# Function to present a menu to pick an object from a list of objects
# auto_pick means if the list has only one item then automatically pick that item
def pick(object_type: str, objects: list, auto_pick: bool=False):

    selected_object = None
    choices = len(objects)
    vowels ="AEIOU"
    if object_type[0].upper() in vowels:
        a_or_an = "an"
    else:
        a_or_an = "a"

    # If the list of objects is no good the raise an exception
    if objects is None or choices == 0:
        raise(Exception("No %s to pick from." % object_type))

    # If you selected auto pick and there is only one object in the list then pick it
    if auto_pick is True and choices == 1:
        selected_object = objects[0]

    # While an object has not yet been picked...
    while selected_object == None:

        # Print the menu of available objects to select
        print("Select %s %s:-" % (a_or_an, object_type))

        for i in range(0, choices):
            print("\t%i) %s" % (i + 1, str(objects[i])))

        # Along with an extra option to cancel selection
        print("\t%i) Cancel" % (choices + 1))

        # Get the user's selection and validate it
        choice = input("%s?" % object_type)
        if is_numeric(choice) is not None:
            choice = int(choice)

            if 0 < choice <= choices:
                selected_object = objects[choice -1]
                logging.info("pick(): You chose %s %s." % (object_type, str(selected_object)))
            elif choice == (choices + 1):
                raise (Exception("You cancelled. No %s selected" % object_type))
            else:
                print("Invalid choice '%i' - try again." % choice)
        else:
            print("You choice '%s' is not a number - try again." % choice)

    return selected_object


def is_numeric(s):

    try:
        x = int(s)
    except:
        try:
            x = float(s)
        except:
            x = None
    return x


def type(text : str, wait=0.1):

    for i in range(0,len(text)):
        sys.stdout.write(text[i])
        sys.stdout.flush()
        time.sleep(wait)
