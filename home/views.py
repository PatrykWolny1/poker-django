from django.shortcuts import render
from django.http import FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse  # Import JsonResponse
from django.middleware.csrf import get_token
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
task_threads = {}
task_thread = None
    
def index(request):
    template_data = {}
    template_data['title'] = 'Poker Simulation'
    return render(request, 'home/index.html', {'template_data': template_data})

def permutacje_kart(request):
    csrf_token = get_token(request)
    redis_buffer_instance.redis_1.set('choice_1', '2')
    redis_buffer_instance.redis_1.set('choice', '1')
    redis_buffer_instance.redis_1.set('when_one_pair', '0')
    redis_buffer_instance.redis_1.set('prog_when_fast', '-1')
    redis_buffer_instance.redis_1.set('count_arrangements', '-1')
    redis_buffer_instance.redis_1.set('count_arrangements_stop', '-1')
    redis_buffer_instance.redis_1.set('print_gen_combs_perms', '-1')
    return render(request, 'home/permutacje_kart.html', {'csrf_token': csrf_token})

def gra_jedna_para(request):
    redis_buffer_instance.redis_1.set('choice_1', '2')
    redis_buffer_instance.redis_1.set('choice', '2')
    redis_buffer_instance.redis_1.set('when_one_pair', 1)
    
    one_pair_combs_max = '10982'
    
    redis_buffer_instance.redis_1.set("entered_value", one_pair_combs_max)
    redis_buffer_instance.redis_1.set('game_si_human', '2')
    
    global stop_event
    stop_event.clear()  # Clear the stop event if it was previously set
    
    thread_result = None
    
    if request.method == 'POST':
        # Get the sub-site identifier from the path
        subsite_id = request.path.split('/')[1]  # Assuming subsite_id is in the path

        # Check if a thread is already running for this sub-site
        thread_key = f'thread_data_{subsite_id}'
        # print(f"Session before: {request.session}")
        
        # If the thread is already running, we want to restart the process
        if thread_key in request.session:
            existing_thread_id = request.session[thread_key]
            # print(f"Existing thread ID: {existing_thread_id}")
            thread_status = redis_buffer_instance.redis_1.get(f'thread_data_{existing_thread_id}')
            # print(f"Thread status in Redis: {thread_status}")

            # If the thread is already running, stop it and restart the process
            if thread_status is not None and thread_status.decode('utf-8') == 'running':
                # print(f"Stopping existing thread: {existing_thread_id}")
                stop_event.set()  # Stop the running thread if any
                redis_buffer_instance.redis_1.set(f'thread_data_{existing_thread_id}', 'stopped')  # Mark the thread as stopped
                request.session.pop(thread_key, None)  # Clear the session key for the old thread

        # Continue thread creation
        stop_event.clear()  # Clear the stop event if previously set
        data_ready_event.clear()

        if task_thread is not None and task_thread.is_alive():
            stop_event.set()
            redis_buffer_instance_stop.redis_1.set('stop_event_var', '1')

        redis_buffer_instance_stop.redis_1.set('stop_event_var', '0')
        # Start the thread and store the result
        thread_result = start_thread(request)

        # Store the thread ID in session for the current sub-site
        request.session[thread_key] = thread_result['thread_id']
        # print(f"Session after storing thread_id: {request.session}")

        if thread_result['task_status'] == 'Thread started':
            return render(request, 'home/gra_jedna_para.html', {'message': 'Thread already running'})
        
    return render(request, 'home/gra_jedna_para.html', {'thread_id': thread_result['thread_id']})


def start_thread(request):
    # Check if a thread is already running for this session
    if 'thread_id' in request.session:
        existing_thread_id = request.session['thread_id']
        thread_status = redis_buffer_instance.redis_1.get(f'thread_data_{existing_thread_id}')
        
        # Ensure thread_status is not None and decoded only if exists
        if thread_status is not None and thread_status.decode('utf-8') == 'running':
            stop_event.set()  # Stop the running thread if any
            redis_buffer_instance.redis_1.set(f'thread_data_{existing_thread_id}', 'stopped')  # Mark the thread as stopped
            request.session.pop('thread_id', None)  # Remove thread_id from session

    stop_event.clear()
    
    # Generate a new thread ID and store it in session
    thread_id = str(uuid.uuid4())
    request.session['thread_id'] = thread_id

    # Check path to determine thread target
    if request.path.startswith("/gra_jedna_para") or request.path.startswith("/start_task"):
        my_thread = MyThread(target=main, thread_id=thread_id)
        my_thread.start()

    # Store thread status in Redis and return result
    redis_buffer_instance.redis_1.set(f'thread_data_{thread_id}', 'running')
    
    return {'task_status': 'Thread started', 'thread_id': thread_id}

def start_task(request):
    global task_thread, task_threads, stop_event, data_ready_event

    # Set up Redis initial values
    redis_buffer_instance.redis_1.set('choice_1', '2')
    redis_buffer_instance.redis_1.set('choice', '1')
    redis_buffer_instance.redis_1.set('when_one_pair', '0')
    redis_buffer_instance.redis_1.set('prog_when_fast', '-1')
    redis_buffer_instance.redis_1.set('count_arrangements', '-1')
    redis_buffer_instance.redis_1.set('count_arrangements_stop', '-1')
    redis_buffer_instance.redis_1.set('print_gen_combs_perms', '-1')

    if request.method == 'POST':
        # Get the sub-site identifier from the path
        subsite_id = request.path.split('/')[1]  # Assuming subsite_id is in the path

        # Check if a thread is already running for this sub-site
        thread_key = f'thread_data_{subsite_id}'
        # print(f"Session before: {request.session}")
        
        # If the thread is already running, we want to restart the process
        if thread_key in request.session:
            existing_thread_id = request.session[thread_key]
            # print(f"Existing thread ID: {existing_thread_id}")
            thread_status = redis_buffer_instance.redis_1.get(f'thread_data_{existing_thread_id}')
            # print(f"Thread status in Redis: {thread_status}")

            # If the thread is already running, stop it and restart the process
            if thread_status is not None and thread_status.decode('utf-8') == 'running':
                # print(f"Stopping existing thread: {existing_thread_id}")
                stop_event.set()  # Stop the running thread if any
                redis_buffer_instance.redis_1.set(f'thread_data_{existing_thread_id}', 'stopped')  # Mark the thread as stopped
                request.session.pop(thread_key, None)  # Clear the session key for the old thread

        # Continue thread creation
        stop_event.clear()  # Clear the stop event if previously set
        data_ready_event.clear()

        if task_thread is not None and task_thread.is_alive():
            stop_event.set()
            redis_buffer_instance_stop.redis_1.set('stop_event_var', '1')

        redis_buffer_instance_stop.redis_1.set('stop_event_var', '0')
        # Start the thread and store the result
        thread_result = start_thread(request)

        # # Store the thread ID in session for the current sub-site
        # request.session[thread_key] = thread_result['thread_id']
        # # print(f"Session after storing thread_id: {request.session}")

        # task_thread = MyThread(target=main, thread_id=thread_result['thread_id'])  # Assign to global task_thread
        # task_threads[thread_result['thread_id']] = task_thread  # Store the thread in the dictionary

        if thread_result['task_status'] == 'Thread started':
            return JsonResponse({'status': 'arrangement started'})
        
        return JsonResponse({'status': 'Task stopped successfully'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

def stop_task(request):
    global stop_event, task_threads

    if request.method == 'POST':
        thread_key = 'thread_id'

        # Check if a thread is running for this sub-site
        # print(thread_key, dict(request.session))
        
        if thread_key in request.session:
            thread_id = request.session[thread_key]
            thread_status = redis_buffer_instance.redis_1.get(f'thread_data_{thread_id}')
                        
            if thread_status and thread_status.decode('utf-8') == 'running':
                # Stop the thread
            
                stop_event.set()  # Signal the thread to stop
                
                # Wait for the thread to finish
                task_thread = task_threads.get(thread_id)
                
                if task_thread and task_thread.is_alive():
                    task_thread.join()  # Wait for the thread to finish
                    
                # Update thread status in Redis to 'stopped'
                redis_buffer_instance.redis_1.set(f'thread_data_{thread_id}', 'stopped')
                request.session.pop('thread_id', None)  # This clears the session

                # Clear session and task_threads dictionary
                request.session.pop(thread_key, None)
                task_threads.pop(thread_id, None)

                return JsonResponse({'status': 'Task stopped successfully', 'thread_id': thread_id})
            else:
                return JsonResponse({'status': 'No running task found for this sub-site'}, status=400)
    
    return JsonResponse({'status': 'POST is not working'}, status=200)
 
def download_saved_file(request):
    file_path = 'permutations_data/data_permutations_combinations.txt'

    # Check if the file exists
    if not os.path.exists(file_path):
        raise Http404("File not found")

    # Serve the file as a download
    response = FileResponse(open(file_path, 'rb'), as_attachment=True)
    response['Content-Disposition'] = f'attachment; filename="collected_data_perms_combs.txt"'
    return response

def submit_number(request):
    if request.method == "POST":
        data = json.loads(request.body)
        number = data.get("value")
        
        redis_buffer_instance.redis_1.set("entered_value", str(number))
        
        # Perform any processing with the number here
        # print("Received number:", number)  # Example action
        
        return JsonResponse({"message": "Number received successfully", "value": number})
    
    return JsonResponse({"error": "Invalid request"}, status=400)

def permutacje(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('perms_combs', '0')
        return JsonResponse({'status': 'Permutacje is ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

def kombinacje(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('perms_combs', '1')
        return JsonResponse({'status': 'Kombinacje is ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

def high_card(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('arrangement', '9')  # Binary code for High Card
        return JsonResponse({'status': 'High Card is ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

def one_pair(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('arrangement', '8')  # Binary code for One Pair
        return JsonResponse({'status': 'One Pair is ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

def two_pairs(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('arrangement', '7')  # Binary code for Two Pairs
        return JsonResponse({'status': 'Two Pairs are ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

def three_of_a_kind(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('arrangement', '6')  # Binary code for Three of a Kind
        return JsonResponse({'status': 'Three of a Kind is ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

def straight(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('arrangement', '5')  # Binary code for Straight
        return JsonResponse({'status': 'Straight is ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

def color(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('arrangement', '4')  # Binary code for Color
        return JsonResponse({'status': 'Color is ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

def full(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('arrangement', '3')  # Binary code for Full
        return JsonResponse({'status': 'Full is ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

def carriage(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('arrangement', '2')  # Binary code for Carriage
        return JsonResponse({'status': 'Carriage is ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

def straight_flush(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('arrangement', '1')  # Binary code for Straight Flush
        redis_buffer_instance.redis_1.set('straight_royal_flush', '0')
        return JsonResponse({'status': 'Straight Flush is ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)

def straight_royal_flush(request):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set('arrangement', '1')  # Binary code for Straight Royal Flush
        redis_buffer_instance.redis_1.set('straight_royal_flush', '1')
        return JsonResponse({'status': 'Straight Royal Flush is ON'})
    return JsonResponse({'status': 'Invalid request'}, status=400)