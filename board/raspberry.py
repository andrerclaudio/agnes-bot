import logging
import time

import RPi.GPIO as GPIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class DigitalFinger(object):
    """
    Control a remote server turning on/off its state by controlling its power button.
    """

    def __init__(self):

        # Define the GPIO pin where the Server is connected
        self.__SERVER_PIN = 6
        # Define how many times it will hold the pin state
        self.__HOLD_DELAY = 0.5
        self.__initialized = False
        GPIO.setmode(GPIO.BCM)
        # Call the initializer function
        self.__pin_init()

    def digital_finger(self):
        """
        Turn On and Off a given raspberry pi pin.
        :return: 1 = successful, 0 = fail
        """

        try:
            if not self.__initialized:
                self.__pin_init()

            # Take the action (0 means ON)
            GPIO.output(self.__SERVER_PIN, GPIO.LOW)
            # Wait for HOLD_DELAY seconds
            time.sleep(self.__HOLD_DELAY)
            # Take the action (1 means OFF)
            GPIO.output(self.__SERVER_PIN, GPIO.HIGH)
            logging.info('Server turned on/off control successful!')
            return 1  # Return a status code for success

        except Exception as e:
            logging.exception(f"An error occurred: {e}", exc_info=False)
            return 0  # Return a status code for failure

    def __pin_init(self):
        """
        Initialize the default state.
        :return: none
        """
        try:
            # Set up the GPIO pin as an output
            GPIO.setup(self.__SERVER_PIN, GPIO.OUT)
            # Make the default state (1 means OFF)
            GPIO.output(self.__SERVER_PIN, GPIO.HIGH)

            logging.info('Pin initialized (OFF).')
            self.__initialized = True

        except Exception as e:
            logging.exception(f"An error occurred during PIN initialization: {e}", exc_info=False)
