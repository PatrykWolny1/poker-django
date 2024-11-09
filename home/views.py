from django.shortcuts import render
from django.http import FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse  # Import JsonResponse
from home.redis_buffer_singleton import redis_buffer_instance_stop, redis_buffer_instance
from home.MyThread import MyThread
from classes.Game import Game
from main import main
import os
import threading
import json
import queue
import uuid

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
    redis_buffer_instance.redis_1.set('when_one_pair', '0')
    redis_buffer_instance.redis_1.set('prog_when_fast', '-1')
    return render(request, 'home/permutacje_kart.html')

def gra_jedna_para(request):
    redis_buffer_instance.redis_1.set('choice_1', '2')
    redis_buffer_instance.redis_1.set('choice', '2')
    redis_buffer_instance.redis_1.set('when_one_pair', 1)
    one_pair_combs_max = '10982'
    redis_buffer_instance.redis_1.set("entered_value", one_pair_combs_max)
    redis_buffer_instance.redis_1.set('game_si_human', '2')
    global stop_event
    stop_event.clear()  # Clear the stop event if it was previously set
    
    # Initialize and start a new thread for the task
    data_queue_combinations = queue.Queue()
    
    # Call start_thread and check the result
    thread_result = start_thread(request)
    if thread_result['task_status'] == 'Thread started':
        # Handle any specific message or notification in the template if needed
        return render(request, 'home/gra_jedna_para.html', {'message': 'Thread already running'})
    
    # If thread starts successfully, render the page with the thread ID or any additional context
    return render(request, 'home/gra_jedna_para.html', {'thread_id': thread_result['thread_id']})

def start_thread(request):
    # Check if a thread is already running for this session
    if 'thread_id' in request.session:
        existing_thread_id = request.session['thread_id']
        thread_status = redis_buffer_instance.redis_1.get(f'thread_data_{existing_thread_id}').decode('utf-8')

        if thread_status == 'running':
            return {'task_status': 'Thread already running', 'thread_id': existing_thread_id}

    # Create a new thread for this session
    thread_id = str(uuid.uuid4())
    request.session['thread_id'] = thread_id
    my_thread = MyThread(target=main, thread_id=thread_id)
    my_thread.start()

    result = {'task_status': 'Thread started', 'thread_id': thread_id}
    return result

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
        redis_buffer_instance.redis_1.set('arrangement', '9')  # Binary code for High Card
        return JsonResponse({'status': 'High Card is ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

@csrf_exempt
def one_pair(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('arrangement', '8')  # Binary code for One Pair
        return JsonResponse({'status': 'One Pair is ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

@csrf_exempt
def two_pairs(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('arrangement', '7')  # Binary code for Two Pairs
        return JsonResponse({'status': 'Two Pairs are ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

@csrf_exempt
def three_of_a_kind(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('arrangement', '6')  # Binary code for Three of a Kind
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
        redis_buffer_instance.redis_1.set('arrangement', '4')  # Binary code for Color
        return JsonResponse({'status': 'Color is ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

@csrf_exempt
def full(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('arrangement', '3')  # Binary code for Full
        return JsonResponse({'status': 'Full is ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

@csrf_exempt
def carriage(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('arrangement', '2')  # Binary code for Carriage
        return JsonResponse({'status': 'Carriage is ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

@csrf_exempt
def straight_flush(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('arrangement', '1')  # Binary code for Straight Flush
        redis_buffer_instance.redis_1.set('straight_royal_flush', '0')
        return JsonResponse({'status': 'Straight Flush is ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

@csrf_exempt
def straight_royal_flush(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('arrangement', '1')  # Binary code for Straight Royal Flush
        redis_buffer_instance.redis_1.set('straight_royal_flush', '1')
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
        redis_buffer_instance.redis_1.set('when_one_pair', '0')

        # Call start_thread to handle thread initialization and starting
        thread_result = start_thread(request)

        if thread_result['task_status'] == 'Thread started':
            # If thread is already running, optionally handle this case (e.g., log or notify)
            return JsonResponse({'status': 'Thread already running', 'thread_id': thread_result['thread_id']})
        
        return JsonResponse({'status': 'arrangement started'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

# @csrf_exempt
def stop_task(request):    
    global stop_event, task_thread

    # Check if a thread is currently running for this session
    if 'thread_id' in request.session:
        existing_thread_id = request.session['thread_id']
        thread_status = str(redis_buffer_instance.redis_1.get(f'thread_data_{existing_thread_id}').decode('utf-8'))

        if thread_status == 'running':
            # Stop the thread
            if stop_event is not None:
                stop_event.set()  # Signal the thread to stop

            # Wait for the thread to finish
            if task_thread is not None and task_thread.is_alive():
                task_thread.join()  # Wait for the thread to finish

            # Optionally, update the thread status in Redis or session
            redis_buffer_instance.redis_1.set(f'thread_data_{existing_thread_id}', 'stopped')

            # Reset stop_event and task_thread
            stop_event.clear()
            task_thread = None

            return JsonResponse({'status': 'Task stopped successfully', 'thread_id': existing_thread_id})

    # If no thread is running, return an error message
    return JsonResponse({'status': 'No running task found'}, status=400)
 
def download_saved_file(request):
    file_path = 'permutations_data/data_permutations_combinations.txt'

    # Check if the file exists
    if not os.path.exists(file_path):
        raise Http404("File not found")

    # Serve the file as a download
    response = FileResponse(open(file_path, 'rb'), as_attachment=True)
    response['Content-Disposition'] = f'attachment; filename="collected_data_perms_combs.txt"'
    return response

@csrf_exempt  # Use only if you’re not sending the CSRF token (recommended for testing only)
def submit_number(request):
    if request.method == "POST":
        data = json.loads(request.body)
        number = data.get("value")
        
        redis_buffer_instance.redis_1.set("entered_value", str(number))
        
        # Perform any processing with the number here
        # print("Received number:", number)  # Example action
        
        return JsonResponse({"message": "Number received successfully", "value": number})
    
    return JsonResponse({"error": "Invalid request"}, status=400)
    