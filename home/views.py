from django.shortcuts import render
from .forms import ScriptForm
import subprocess
import json
from django.http import JsonResponse

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import time
from .hello import long_running_task
from django.core.cache import cache

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
    for i in range(101):
        time.sleep(0.1)
        cache.set('task_progress', i)
        print(f"Progress: {i}%")  # Check if this prints in the console
        
def start_task(request):
    import threading
    threading.Thread(target=long_running_task).start()
    return render(request, 'home/progress.html')

# def data(request):
#     return render(request, 'home/input_form.html')