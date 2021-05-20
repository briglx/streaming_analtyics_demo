#!/usr/bin/python
"""Main script for json convert."""
import argparse
import asyncio
import logging
import os
import random
import signal
import sys
import uuid
from datetime import datetime, timedelta, timezone

from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient

import template_jinja as template


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)



def generate_guid():
    """Generate a UUID string."""
    return str(uuid.uuid4())


def generate_id():
    """Generate Hexadecimal 32 length id."""
    return "%032x" % random.randrange(16 ** 32)


def get_date_now_isoformat():
    """Generate Iso Formatted Date based on Now."""
    cur_time = datetime.utcnow()
    return get_date_isoformat(cur_time)


def get_date_isoformat(date):
    """Format Iso Formatted Date."""
    cur_time = date.replace(tzinfo=timezone.utc, microsecond=0)
    return cur_time.isoformat().replace("+00:00", "Z")

def create_device_list(count=50):
    device_list = []
    for i in range(count):
        device_list.append(generate_id())
    return device_list

def get_random_device_id(device_list):
    return random.choice(device_list)

def create_sample_data(device_list):
    """Generate Sample Data."""
    device_id = get_random_device_id(device_list)
    period_start_time = datetime.utcnow()
    period_count = random.randint(0, 30)
    period_end_time = period_start_time + timedelta(0, period_count)
    max_value = 50
    start_value = random.uniform(20, max_value)
    delta_value = random.uniform(-1, 1) * max_value

    values = []
    cur_value = start_value
    for i in range(period_count):
        start_interval = period_start_time + timedelta(0, i)
        end_interval = period_start_time + timedelta(0, i + 1)
        values.append(
            {
                "start_interval": get_date_isoformat(start_interval),
                "end_interval": get_date_isoformat(end_interval),
                "value": cur_value,
            }
        )
        cur_value = cur_value + delta_value

    sample_data = {
        "device_id": generate_id(),
        "create_datetime": get_date_isoformat(period_start_time),
        "SystemGuid": generate_guid(),
        "period_start_time": get_date_isoformat(period_start_time),
        "period_end_time": get_date_isoformat(period_end_time),
        "values": values,
    }

    return sample_data


def get_template_string(path):
    """Load Message Template."""
    with open(path, "r") as template_file:
        src = Template(template_file.read())
        return src


async def run():
    """Create sample messages."""
    async with PRODUCER:

        device_list = create_device_list()

        # Loop Forever
        while True:
            # Create a batch.
            event_data_batch = await PRODUCER.create_batch()

            data = create_sample_data(device_list)
            message = template.render_json(data, TEMPLATE_PATH, TEMPLATE_SOURCE_MESSAGE)

            # Add event to the batch.
            logging.info("Sending Event %s", message)
            event_data_batch.add(EventData(message))

            # Send the batch of events to the event hub.
            await PRODUCER.send_batch(event_data_batch)

            logging.info("waiting...")
            # await asyncio.sleep(1)


if __name__ == "__main__":
    logging.info("Starting script")

    parser = argparse.ArgumentParser(
        description="Provision Analytics Workspaces.",
        add_help=True,
    )
    parser.add_argument(
        "--connection_string",
        "-c",
        help="Eventhubs Connection String",
    )
    parser.add_argument(
        "--eventhubs_name",
        "-n",
        help="EventHubs Name",
    )
    parser.add_argument(
        "--template_path",
        "-t",
        help="Template Path",
    )
    parser.add_argument(
        "--template_source_message",
        "-ts",
        help="Template to create the Source Message",
    )

    args = parser.parse_args()

    CONNECTION_STRING = args.connection_string or os.environ.get(
        "EVENT_HUB_CONNECTION_STRING"
    )
    EVENT_HUB_NAME = args.eventhubs_name or os.environ.get("EVENT_HUB_NAME")
    TEMPLATE_PATH = args.template_path or os.environ.get("TEMPLATE_PATH")
    TEMPLATE_SOURCE_MESSAGE = args.template_source_message or os.environ.get(
        "TEMPLATE_SOURCE_MESSAGE"
    )

    if not CONNECTION_STRING:
        raise ValueError(
            "Event hub connection string is required."
            "Have you set the EVENT_HUB_CONNECTION_STRING env variable?"
        )

    if not EVENT_HUB_NAME:
        raise ValueError(
            "Event hub name is required."
            "Have you set the EVENT_HUB_NAME env variable?"
        )

    if not TEMPLATE_PATH:
        raise ValueError(
            "Template path is required." "Have you set the TEMPLATE_PATH env variable?"
        )

    if not TEMPLATE_SOURCE_MESSAGE:
        raise ValueError(
            "Template source message is required."
            "Have you set the TEMPLATE_SOURCE_MESSAGE env variable?"
        )

    # This restores the default Ctrl+C signal handler, which just kills the process
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Create a producer client to send messages to the event hub.
    # Specify a connection string to your event hubs namespace and
    # the event hub name.
    PRODUCER = EventHubProducerClient.from_connection_string(
        conn_str=CONNECTION_STRING, eventhub_name=EVENT_HUB_NAME
    )

    # Start Message Generator
    loop = asyncio.get_event_loop()
    loop.create_task(run())
    loop.run_forever()