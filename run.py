#Run
import controller
import logging

def main():

    logging.basicConfig(level = logging.WARN)

    c = controller.Controller()
    c.run()


if __name__ == "__main__":
    main()
