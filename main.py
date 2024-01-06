import json
import os
import socket
import time
from typing import Callable

import pystray
from pystray import MenuItem as item
from PIL import Image


class Messages:
    def __init__(self, path: str):
        self.path = path
        self.temp = None
        self.message_objects = {}

    def load_messages(self):
        for filename in os.listdir(self.path):
            if filename.endswith('.json'):
                file_path = os.path.join(self.path, filename)

                with open(file_path, 'r') as file:
                    json_data = json.load(file)

                for item in json_data:
                    self.message_objects[item] = json_data[item]

        return self.message_objects


class Govee(Messages):
    def __init__(self, config):
        self.messages_path = ""
        self.ip, self.port = None, None
        self.brightness = 100

        for index, (key, value) in enumerate(config.items()):
            setattr(self, key, value)
            print(f"Setting self data config {key} = '{value}'")

        instance_messages = Messages(path=self.messages_path)
        self.messages = instance_messages.load_messages()

        super().__init__(path=self.messages_path)
        (pystray.Icon("Govee Compact Control (by szymczakovv)", Image.open("assets/logo.png"),
                      "Govee Compact Control (by szymczakovv)", (
                          item('Włącz Pasek Led', self.turn_on),
                          item('Wyłącz Pasek Led', self.turn_off),
                          item('Wyłącz Aplikację', self.on_exit_app)
                      ))).run()

    @staticmethod
    def on_exit_app(icon):
        icon.stop()

    @staticmethod
    def send_udp_command(self, command: object):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as lanSocket:
            lanSocket.sendto(json.dumps(command).encode(), (self.ip, self.port))

    def try_action(self, action: str, function: Callable):
        if not self.ip:
            print('Ip is not configured properly!')
        elif not self.port:
            print('Port is not configured properly!')
        elif not self.messages_path:
            print('Messages Path is not configured properly!')
        else:
            function()
            print(f'Action "{action}" resolved without any error')

    def turn_on(self):
        def send_message():
            self.send_udp_command(self, self.messages["TURN_ON"])

        self.try_action("TURN_ON", send_message)

    def turn_off(self):
        def send_message():
            self.send_udp_command(self, self.messages["TURN_OFF"])

        self.try_action("TURN_OFF", send_message)

    def increase_brightness(self, brightness_level):
        def send_message():
            if self.brightness >= 100:
                return print("Cannot increase brightness of led stripes because it's equals to 100 already")

            self.brightness += brightness_level
            self.messages["DECREASE_BRIGHTNESS"]["msg"]["data"]["value"] = self.brightness
            self.send_udp_command(self, self.messages["DECREASE_BRIGHTNESS"])
            print(self.brightness)

        self.try_action("INCREASE_BRIGHTNESS", send_message)

    def decrease_brightness(self, brightness_level):
        def send_message():
            if self.brightness <= 1:
                return print("Cannot increase brightness of led stripes because it's equals to 1 already")

            self.brightness -= brightness_level
            self.messages["DECREASE_BRIGHTNESS"]["msg"]["data"]["value"] = self.brightness
            self.send_udp_command(self, self.messages["DECREASE_BRIGHTNESS"])
            print(self.brightness)

        self.try_action("DECREASE_BRIGHTNESS", send_message)


instance = Govee(config=json.load(open("config.json")))
instance.turn_on()

# instance.decrease_brightness(50)

# time.sleep(3)

# instance.increase_brightness(50)
