from django.shortcuts import render
from django.http import FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse  # Import JsonResponse
from home.redis_buffer_singleton import redis_buffer_instance_stop, redis_buffer_instance
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
    template_data['title'] = 'Poker Simulation'
    return render(request, 'home/index.html', {'template_data': template_data})

def permutacje_kart(request):
    redis_buffer_instance.redis_1.set('choice_1', '2')
    redis_buffer_instance.redis_1.set('choice', '1')
    redis_buffer_instance.redis_1.set('prog_when_fast', '-1')
    return render(request, 'home/permutacje_kart.html')

@csrf_exempt
def permutacje(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('perms_combs', '0')
        return JsonResponse({'status': 'Permutacje is ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

@csrf_exempt
def kombinacje(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('perms_combs', '1')
        return JsonResponse({'status': 'Kombinacje is ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

@csrf_exempt
def high_card(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('arrangement', '1')  # Binary code for High Card
        return JsonResponse({'status': 'High Card is ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

@csrf_exempt
def one_pair(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('arrangement', '2')  # Binary code for One Pair
        return JsonResponse({'status': 'One Pair is ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

@csrf_exempt
def two_pairs(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('arrangement', '3')  # Binary code for Two Pairs
        return JsonResponse({'status': 'Two Pairs are ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

@csrf_exempt
def three_of_a_kind(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('arrangement', '4')  # Binary code for Three of a Kind
        return JsonResponse({'status': 'Three of a Kind is ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

@csrf_exempt
def straight(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('arrangement', '5')  # Binary code for Straight
        return JsonResponse({'status': 'Straight is ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

@csrf_exempt
def color(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('arrangement', '6')  # Binary code for Color
        return JsonResponse({'status': 'Color is ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

@csrf_exempt
def full(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('arrangement', '7')  # Binary code for Full
        return JsonResponse({'status': 'Full is ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

@csrf_exempt
def carriage(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('arrangement', '8')  # Binary code for Carriage
        return JsonResponse({'status': 'Carriage is ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

@csrf_exempt
def straight_flush(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('arrangement', '9')  # Binary code for Straight Flush
        return JsonResponse({'status': 'Straight Flush is ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

@csrf_exempt
def straight_royal_flush(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('arrangement', '10')  # Binary code for Straight Royal Flush
        return JsonResponse({'status': 'Straight Royal Flush is ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

@csrf_exempt
def start_task(request):
    global task_thread, stop_event, data_ready_event
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('prog_when_fast', '-1')

        stop_event.clear()  # Clear the stop event if it was previously set
        data_ready_event.clear()
        if task_thread is not None and task_thread.is_alive():
            stop_event.set()
            redis_buffer_instance_stop.redis_1.set('stop_event_var', '1')
            
        redis_buffer_instance_stop.redis_1.set('stop_event_var', '0')
        
        redis_buffer_instance.redis_1.set('choice_1', '2')
        redis_buffer_instance.redis_1.set('choice', '1')
        
        task_thread = threading.Thread(target=main)  # Create a new thread for the arrangement
        task_thread.start()  # Start the long-running arrangement
        
        return JsonResponse({'status': 'arrangement started'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

@csrf_exempt
def stop_task(request):
    global stop_event, task_thread
    if stop_event is not None:
        stop_event.set()  # Set the stop event to stop the thread
    if task_thread is not None:
        task_thread.join()  # Wait for the thread to finish
    
    return JsonResponse({'status': 'arrangement stopped'})

def download_saved_file(request):
    file_path = 'permutations_data/data_permutations_combinations.txt'

    # Check if the file exists
    if not os.path.exists(file_path):
        raise Http404("File not found")

    # Serve the file as a download
    response = FileResponse(open(file_path, 'rb'), as_attachment=True)
    response['Content-Disposition'] = f'attachment; filename="collected_data_perms_combs.txt"'
    return response
    