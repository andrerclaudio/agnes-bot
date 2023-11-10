"""
MQTT application in general.
"""

import logging
import traceback
import paho.mqtt.client as mqtt


# Define the MQTT broker information
BROKER_ADDRESS = "mqtt.eclipseprojects.io"
PORT = 1883
TOPIC = "my_topic"
CLIENT_ID = "my_client"

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


def on_connect(client, userdata, flags, rc) -> None:
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
        client.subscribe(TOPIC)
    else:
        error_msg = f"Connection failed with code {rc}"
        logging.error(error_msg)
        raise MQTTConnectionError(error_msg)


def on_message(client, userdata, message) -> None:
    """
    Parse the incoming messages.
    """
    
    _ = client
    _ = userdata
    logging.info("Received message: %s", message.payload.decode())


# MQTT client setup
mqttc = mqtt.Client(CLIENT_ID)
mqttc.on_connect = on_connect
mqttc.on_message = on_message


def mqtt_client():
    """" All application has its initialization from here """
    logging.info('Main application is running!')

    try:

        mqttc.connect(BROKER_ADDRESS, PORT)
        mqttc.loop_start()

        while True:
            pass

            # message = "message to publish!"
            # mqttc.publish(TOPIC, message)
            # logging.info("Published message: %s", message)

    except mqtt as e:
        logging.exception("An error occurred: %s", str(e), exc_info=False)
        traceback.print_exc()

    finally:
        mqttc.disconnect()
        logging.info("Disconnected from MQTT broker")