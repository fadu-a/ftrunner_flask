import csv
import datetime
import json
import os
import subprocess
from subprocess import Popen, PIPE
import time
import threading
from flask import request, Flask, Response, redirect, url_for
import requests
import app

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
GLOBAL_CONFIGS_DIR = os.path.join(RESULTS_DIR, "configs")


class Scenario(object):
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.jobs = data['jobs']
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.dirname = os.path.join(RESULTS_DIR, self.timestamp)
        self.job_files = []

    def create_job_files(self):
        os.makedirs(self.dirname)
        print(GLOBAL_CONFIGS_DIR)
        for job in self.jobs:
            id = job.pop('id')
            name = job.pop('name')
            order = job.pop('order')
            global_config = job.pop('global')

            file_path = os.path.join(self.dirname, f"{order}_{name}.job")
            with open(file_path, "w") as f:
                f.write("[global]\n")
                f.write(f"include {GLOBAL_CONFIGS_DIR}/global-{global_config}.fio\n\n")
                f.write("[job1]\n")
                f.write(f"description=[{self.id}] {order}_{name}\n")
                for key in job.keys():
                    f.write(f"{key}={job[key]}\n")
            self.job_files.append(file_path)

    def run_test(self):
        global fio_process, fio_thread

        for job_file in self.job_files:
            cmd = [
                "fio",
                f"{job_file}",
                "--status-interval=1",
                "--minimal"
            ]
            fio_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, preexec_fn=os.setpgrp)
            fio_thread = threading.Thread(target=self.read_test_log(), args=())
            fio_thread.daemon = True
            fio_thread.start()
        print("kjy")

    def read_test_log(self):
        print("Test")
        while fio_process.poll() == None:
            std_line = fio_process.stdout.readline()
            print(std_line)
            rt = requests.get('http://192.168.0.28:8000/api/fio/results')
            rt.status_code
            rt.text
            if std_line is None:
                fio_status = {'status': '2'}
                r = requests.post('http://192.168.0.28:8000/api/fio/results',data=fio_status)
                r.text
            re = requests.post('http://192.168.0.28:8000/api/fio/results',data=std_line)
            re.text
            re.status_code
            print(re.text)


    def do_test(self):
        self.create_job_files()
        self.run_test()




