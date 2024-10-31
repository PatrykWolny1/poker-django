from django.shortcuts import render
from django.core.cache import cache
import time
from classes.Game import Game
import threading
import sys
from home.redis_buffer_singleton import redis_buffer_instance
from home.long_running_task import long_running_task
from main import main
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse  # Import JsonResponse
import config

# from arrangements.LoadingBar import stop_event, task_thread

stop_event = threading.Event()
task_thread = None
    
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
        
def start_task(request): ###################################
    stop_event.clear()  # Clear the stop event if it was previously set
    task_thread = threading.Thread(target=main)  # Create a new thread for the task
    task_thread.start()  # Start the long-running task
    
    return render(request, 'home/progress.html')

@csrf_exempt
def stop_task_view(request):
    if stop_event is not None:
        stop_event.set()  # Set the stop event to stop the thread
    if task_thread is not None:
        task_thread.join()  # Wait for the thread to finish
    return JsonResponse({'status': 'Task stopped'})
        
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