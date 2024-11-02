from django.shortcuts import render
from django.http import FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse  # Import JsonResponse
from home.redis_buffer_singleton import redis_buffer_instance_stop
from classes.Game import Game
from main import main
import os
import threading

stop_event = threading.Event()
data_ready_event = threading.Event()  # Signals data is ready

cache_lock_progress = threading.Lock()
cache_lock_event_var = threading.Lock()
task_thread = None
    
def index(request):
    template_data = {}
    template_data['title'] = 'Poker Game'
    return render(request, 'home/index.html', {'template_data': template_data})

def permutacje(request):
    template_data = {}
    template_data['title'] = 'Permutacje'
    return render(request, 'home/permutacje.html', {'template_data': template_data, })

def kareta(request):
    return render(request, 'home/kareta.html')

@csrf_exempt
def start_task(request): ###################################
    global task_thread, stop_event, data_ready_event
    if request.method == 'POST':
        redis_buffer_instance_stop.redis_1.set('stop_event_var', '1')
        stop_event.clear()  # Clear the stop event if it was previously set
        data_ready_event.clear()
        if task_thread is not None and task_thread.is_alive():
            stop_event.set()
            redis_buffer_instance_stop.redis_1.set('stop_event_var', '1')
        

        task_thread = threading.Thread(target=main)  # Create a new thread for the task
        task_thread.start()  # Start the long-running task

        return JsonResponse({'status': 'Task started'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

@csrf_exempt
def stop_task_view(request):
    global stop_event, task_thread
    if stop_event is not None:
        stop_event.set()  # Set the stop event to stop the thread
    if task_thread is not None:
        task_thread.join()  # Wait for the thread to finish
        
    redis_buffer_instance_stop.redis_1.set('stop_event_var', '1')

    return JsonResponse({'status': 'Task stopped'})
        
def download_saved_file(request):
    file_path = 'permutations_data/data_permutations_combinations.txt'

    # Check if the file exists
    if not os.path.exists(file_path):
        raise Http404("File not found")

    # Serve the file as a download
    response = FileResponse(open(file_path, 'rb'), as_attachment=True)
    response['Content-Disposition'] = f'attachment; filename="collected_data_perms_combs.txt"'
    return response