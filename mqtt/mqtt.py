"""
MQTT application in general.
"""

import logging
import requests
from config import CHAT_ID, MQTT_CLIENT_ID, MQTT_TOPIC, TOKEN
import paho.mqtt.client as mqtt

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")


class MQTTConnectionError(Exception):
    """
    Custom exception for MQTT connection errors.

    This exception is raised when there is a failure to establish a connection
    with an MQTT broker.

    Args:
        message (str): An optional custom error message to describe the specific
        connection issue. If not provided, a default message is used.

    Attributes:
        message (str): The error message describing the connection issue.

    Example:
        You can raise this exception with a custom message when handling MQTT
        connection errors to provide more context about the issue.

    """

    def __init__(self, message="MQTT connection failed"):
        self.message = message
        super().__init__(self.message)


class AgnesMqttClient(object):
    """
    AgnesMqttClient class for handling MQTT communication.

    This class encapsulates an MQTT client with specific configurations for the Agnes
    application. It provides methods and attributes for setting up and interacting
    with the MQTT broker.

    Attributes:
        TOPIC (str): The MQTT topic to subscribe to ("agnes.mqtt").
        CLIENT_ID (str): The client ID for the MQTT broker ("bridge").
        mqttc (paho.mqtt.client.Client): The MQTT client instance.

    Example:
        # Create an instance of AgnesMqttClient
        agnes_client = AgnesMqttClient()

        # Perform further configuration if needed

    """

    def __init__(self) -> None:
        """
        Initialize an instance of AgnesMqttClient.

        This constructor sets up the MQTT client with predefined configurations,
        including the topic and client ID.

        """

        # Define the MQTT broker client ID and Topic to subscribe        
        self.TOPIC = MQTT_TOPIC
        self.CLIENT_ID = MQTT_CLIENT_ID

        # MQTT client setup
        self.mqttc = mqtt.Client(self.CLIENT_ID)
        self.mqttc.on_connect = self.__on_connect
        self.mqttc.on_message = self.__on_message


    def __on_connect(self, client, userdata, flags, rc) -> None:
        """
        MQTT on_connect callback function.

        This function is called when the MQTT client successfully connects to the broker
        or encounters an error during connection.

        Args:
            client (paho.mqtt.client.Client): The MQTT client instance.
            userdata (Any): User-defined data passed to the client.
            flags (dict): Flags indicating specific MQTT connection flags.
            rc (int): The connection result code.

        Returns:
            None

        Raises:
            Exception: If the MQTT connection fails (rc is not 0).

        Example:
            This function is typically set as the on_connect callback when configuring
            an MQTT client. It handles the logic for successful and failed connections.

        """

        if rc == 0:

            _ = client
            _ = userdata
            _ = flags

            logging.info("Connected to MQTT broker")
            client.subscribe(self.TOPIC)
        else:
            error_msg = f"Connection failed with code {rc}"
            logging.error(error_msg)
            raise MQTTConnectionError(error_msg)


    def __on_message(self, client, userdata, message) -> None:
        """
        Parse the incoming messages.
        """
        
        _ = client
        _ = userdata

        # This method is called when a message is received on the MQTT topic
        message = message.payload.decode('utf-8')
        logging.info("Received MQTT message: %s", message)

        try:
            # Send the message to the specified chat ID
            send_text = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage?chat_id=' + CHAT_ID + '&parse_mode=Markdown&text=' + message
            response = requests.get(send_text)
            logging.debug(response)

        except Exception as e:
            logging.error(f"Error sending message to Telegram: {str(e)}", exc_info=False)
