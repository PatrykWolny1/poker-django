from django.shortcuts import render
from django.core.cache import cache
import time
from classes.Game import Game
import threading
import sys
from home.redis_buffer_singleton import redis_buffer_instance
from home.long_running_task import long_running_task
sys.path.insert(0, '..') # Adds the project root to the system path
from main import main

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

# def long_running_task1():
#     aa = cache.get('shared_variable')
#     print(f'Progress bar: {aa}')  #
        
def start_task(request):
    threading.Thread(target=main).start()
    # threading.Thread(target=mock_writer).start()
    # threading.Thread(target=mock_reader).start()


    # threading.Thread(target=main).start()
    

    return render(request, 'home/progress.html')

from django.http import HttpResponse

from django.http import FileResponse, Http404
import os
def download_saved_file(request):
    file_path = 'permutations_data/carriage.txt'

    # Check if the file exists
    if not os.path.exists(file_path):
        raise Http404("File not found")

    # Serve the file as a download
    response = FileResponse(open(file_path, 'rb'), as_attachment=True)
    response['Content-Disposition'] = f'attachment; filename="carriage.txt"'
    return response