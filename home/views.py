from django.shortcuts import render
from .forms import ScriptForm
import subprocess
import json
from django.http import JsonResponse

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import time
import threading

def index(request):
    template_data = {}
    template_data['title'] = 'Poker Game'
    return render(request, 'home/index.html', {'template_data': template_data})

def permutacje(request):
    template_data = {}
    template_data['title'] = 'Permutacje'
    return render(request, 'home/permutacje.html', {'template_data': template_data, })

# def run_script(request):
#     result = subprocess.run(['python', 'main.py'], stdout=subprocess.PIPE)
#     output = result.stdout.decode('utf-8')
#     return render(request, 'home/run_script.html', {'output': output})

def long_running_task():
    channel_layer = get_channel_layer()
    while True:
        time.sleep(5)  # Simulate time-consuming work
        async_to_sync(channel_layer.group_send)(
            "data",
            {
                'type': 'send_update',
                'data': 'Update at {}'.format(time.strftime('%X'))
            }
        )

def start_long_running_task():
    thread = threading.Thread(target=long_running_task)
    thread.daemon = True
    thread.start()


def data(request):
    return render(request, 'home/input_form.html')