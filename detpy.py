# detect and copy --> detpy
import pyudev
import os
import subprocess
import re
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import time


class UsbDetector:
    def __init__(self, slack):
        self.context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(self.context)
        self.monitor.filter_by('block', device_type='partition')
        self.slack = slack

    def watch(self):
        print("Watching has started")
        for device in iter(self.monitor.poll, None):
            if device.action == 'add' and device['ID_SERIAL_SHORT'] == "0022CFF6B88BC320D78C1E59":
                self.mount_point = self.mount(device.device_node)
                self.slack.post(
                    f"Device Mounted at {self.mount_point}", 'info')
                for x in range(10):
                    time.sleep(3)
                    self.slack.update(f"Copied {x} of 10 files", 'info')

    def mount(self, device_node):
        cmd = ["udisksctl", "mount", "-b", device_node]
        completed_process = self.run_command(cmd)
        if completed_process.returncode == 1:
            # mount is already present
            # get its path
            return self.extract_path(completed_process, r".`(.*)'")
        return self.extract_path(completed_process, r"at\s(/.*)\.")

    def extract_path(self, completed_process, reg_expression):
        output = completed_process.stdout.decode()
        path_object = re.search(reg_expression, output)
        return path_object.group(1)

    def unmount(self, device_node):
        cmd = ["udisksctl", "unmount", "-b", device_node]
        self.run_command(cmd)

    def copy(self):
        pass

    def notify(self):
        pass

    def run_command(self, command):
        return subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def slack(self, message, mtype):
        blocks = []
        message = self.generate_block(message, mtype)
        blocks.append(message)
        client = WebClient(
            token='xoxb-1046320327431-1844711994913-sAu6XkHJQZKUSRADK5waRvSY')
        response = client.chat_postMessage(
            channel='#general', blocks=blocks)


if __name__ == "__main__":
    slack = Slack()
    detector = UsbDetector(slack)
    detector.watch()
