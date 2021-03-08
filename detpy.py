# detect and copy --> detpy
import pyudev
import os
import subprocess
import re
import time
from slack import Slack
from threading import Thread
from dotenv import load_dotenv
import shutil


class UsbDetector:
    def __init__(self, slack):
        load_dotenv()
        self.context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(self.context)
        self.monitor.filter_by('block', device_type='partition')
        self.slack = slack

    def watch(self):
        print("Watching has started")
        for device in iter(self.monitor.poll, None):

            if device.action == 'add' and device['ID_SERIAL_SHORT'] == os.environ["ID_SERIAL_SHORT"]:
                self.mount_point = self.mount(device.device_node)
                self.slack.post(
                    f"Device Mounted at {self.mount_point}", 'info')

                worker = Worker(self.mount_point)
                worker.start()

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


class Worker(Thread):
    def __init__(self, destination_path):
        Thread.__init__(self)
        self.source_path = os.environ["SOURCE_PATH"]
        self.destination_path = destination_path

    def run(self):
        files_list = self.list_files(self.source_path)
        for f in files_list:
            shutil.copy(os.path.join(self.source_path, f),
                        self.destination_path)

    def list_files(self, path):
        return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]


if __name__ == "__main__":
    slack = Slack()

    detector = UsbDetector(slack)
    detector.watch()
