import os
import json
import uuid
import time
from django.shortcuts import render
from django.http import JsonResponse, FileResponse, Http404
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.core.cache import cache
from home.redis_buffer_singleton import redis_buffer_instance, redis_buffer_instance_one_pair_game
from home.MyThread import MyThread
from home.ThreadVarManagerSingleton import task_manager
from main import main
import threading
import traceback

# Global Variables
task_threads = {}
thread_ids = []
task_thread = None
THREAD_METADATA_FILE = "threads.json"
# Views

def index(request):
    """Main index view."""
    template_data = {'title': 'Poker Simulation'}
    return render(request, 'home/index.html', {'template_data': template_data})

def cards_permutations(request):
    is_dev = os.getenv('IS_DEV', 'yes')
    """Initialize values and render the permutacje_kart template."""
    # csrf_token = get_token(request)
    _initialize_redis_values_permutacje()
    return render(request, 'home/cards_permutations.html', {'is_dev': is_dev})

def one_pair_game(request):
    """Start thread if not already running, for one-pair game."""
    is_dev = os.getenv('IS_DEV', 'yes')
    if request.method == 'GET':
        _initialize_redis_values_gra_jedna_para()
        response = _handle_thread(request, subsite_specific=True, template='home/one_pair_game.html', context={'is_dev': is_dev})
        print(response['status'])
        return response
    print("ONE_PAIR_GAME")
    return render(request, 'home/one_pair_game.html', {'is_dev': is_dev})

def start_task(request):
    """Handle task initiation from POST request."""
    if request.method == 'POST':
        _initialize_redis_values_start_task()
        return _handle_thread(request, subsite_specific=False)
    return JsonResponse({'status': 'Invalid request'}, status=400)

def stop_task(request):
    """Handle task stopping from POST request."""
    if request.method == 'POST':
        redis_buffer_instance_one_pair_game.redis_1.set('stop_event_send_updates', '1')
        redis_buffer_instance_one_pair_game.redis_1.set('wait_buffer', '1')
        return _stop_thread(request)
    return JsonResponse({'status': 'Invalid request'}, status=400)

def download_saved_file(request):
    """Serve a saved file as an attachment download."""
    file_path = 'permutations_data/data_permutations_combinations.txt'
    if not os.path.exists(file_path):
        raise Http404("File not found")
    response = FileResponse(open(file_path, 'rb'), as_attachment=True)
    response['Content-Disposition'] = 'attachment; filename="collected_data_perms_combs.txt"'
    return response

def submit_number(request):
    """Submit a number from JSON data in POST request to Redis."""
    if request.method == "POST":
        data = json.loads(request.body)
        number = data.get("value")
        redis_buffer_instance.redis_1.set("entered_value", str(number))
        return JsonResponse({"message": "Number received successfully", "value": number})
    return JsonResponse({"error": "Invalid request"}, status=400)

def start_game(request):
    _initialize_redis_values_gra_jedna_para()
    redis_buffer_instance.redis_1.set('when_one_pair', '0')

    if request.method == 'POST':
        _handle_thread(request, subsite_specific=True, template='home/one_pair_game.html')
        
        return JsonResponse({'status': 'Game started'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

# Helper Functions

def _initialize_redis_values_permutacje():
    """Initialize Redis values specific to permutacje_kart."""
    redis_buffer_instance.redis_1.set('choice_1', '2')
    redis_buffer_instance.redis_1.set('choice', '1')
    redis_buffer_instance.redis_1.set('when_one_pair', '0')
    redis_buffer_instance.redis_1.set('prog_when_fast', '-1')
    redis_buffer_instance.redis_1.set('count_arrangements', '-1')
    redis_buffer_instance.redis_1.set('count_arrangements_stop', '-1')
    redis_buffer_instance.redis_1.set('print_gen_combs_perms', '-1')
    redis_buffer_instance.redis_1.set('shared_progress', '0')
    redis_buffer_instance.redis_1.set('min', '-1')
    redis_buffer_instance.redis_1.set('max', '-1')
    redis_buffer_instance_one_pair_game.redis_1.set('connection_accepted', 'yes')    
    
def _initialize_redis_values_gra_jedna_para():
    """Initialize Redis values specific to gra_jedna_para."""
    redis_buffer_instance.redis_1.set('prog_when_fast', '-1')
    redis_buffer_instance.redis_1.set('choice_1', '2')
    redis_buffer_instance.redis_1.set('choice', '2')
    redis_buffer_instance.redis_1.set('when_one_pair', '1')
    redis_buffer_instance.redis_1.set("entered_value", '10982') #one_pair 1098240
    redis_buffer_instance.redis_1.set('game_si_human', '2')
    # redis_buffer_instance.redis_1.set('min', '-1')
    # redis_buffer_instance.redis_1.set('max', '-1')
    # redis_buffer_instance.redis_1.set('shared_progress', '0')
    redis_buffer_instance.redis_1.set('player_number', '0')
    redis_buffer_instance.redis_1.set('wait_buffer', '0')
    redis_buffer_instance.redis_1.set('stop_event_send_updates', '0')
    redis_buffer_instance_one_pair_game.redis_1.set('thread_status', 'not_ready')
    redis_buffer_instance_one_pair_game.redis_1.set('connection_accepted', 'no')    

def _initialize_redis_values_start_task():
    """Initialize Redis values specific to start_task."""
    redis_buffer_instance.redis_1.set('choice_1', '2')
    redis_buffer_instance.redis_1.set('choice', '1')
    redis_buffer_instance.redis_1.set('when_one_pair', '0')
    redis_buffer_instance.redis_1.set('prog_when_fast', '-1')
    redis_buffer_instance.redis_1.set('count_arrangements', '-1')
    redis_buffer_instance.redis_1.set('count_arrangements_stop', '-1')
    redis_buffer_instance.redis_1.set('print_gen_combs_perms', '-1')
    
def _handle_thread(request, subsite_specific=False, template=None, context=None):
    """Handle the starting and managing of threads for different requests."""
    thread_key = f'thread_data_{request.path.split("/")[1]}' if subsite_specific else 'thread_id'
   
    _stop_thread(request)
    
    thread_result = start_thread(request)
    request.session[thread_key] = thread_result['thread_id']
    
    print("Before rendering the response...")

    if template:
        response = render(request, template, context)
        response['status'] = 'Threads started...'
        return response
    else:
        return JsonResponse({'status': 'Threads started...'})

def start_thread(request):
    """Start a new thread and store it in Redis and session."""
    global task_threads, thread_ids

    task_manager.stop_event.clear()
        
    my_thread = MyThread(target=main)
    my_thread.start()
    
    for thread_id, thread in threading._active.items(): 
        print("Active items (threads): ", thread_id) 
        thread_ids.append(thread_id)
        task_threads[thread_id] = thread
        
    return {'task_status': 'Thread started', 'thread_id': thread_id}

# Function to save thread metadata
def save_thread_metadata(thread_data):
    with open(THREAD_METADATA_FILE, "w") as file:
        json.dump(thread_data, file)

# Function to load thread metadata
def load_thread_metadata():
    try:
        with open(THREAD_METADATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    
def _stop_thread(request, connection_count=None):
    global task_threads, thread_ids
    """Stop the thread based on the thread ID stored in session."""

    redis_buffer_instance_one_pair_game.redis_1.set('stop_event_send_updates', '1')
    task_manager.stop_event.set()

    keys = list(task_threads.keys())
    
    c_threads = 0
        
    while c_threads < len(keys):
        print(c_threads)
        for thread_id in thread_ids:
            try:
                if thread_id == keys[c_threads]:
                    print(isinstance(task_threads[keys[c_threads]], MyThread))
                    if isinstance(task_threads[keys[c_threads]], MyThread):
                        print("Stopping thread ID: ", keys[c_threads])
                        when_game_one_pair = redis_buffer_instance.redis_1.get('when_one_pair').decode('utf-8')
                        print("One pair game or not: ", when_game_one_pair)
                        when_on_refresh = redis_buffer_instance_one_pair_game.redis_1.get('on_refresh').decode('utf-8')
                        if when_on_refresh == '1':
                            task_threads[keys[c_threads]].raise_exception()
                            # task_threads[keys[c_threads]].join()
                        else:
                            task_threads[keys[c_threads]].raise_exception()   
                            # task_threads[keys[c_threads]].join()
                
            except Exception as e:
                # Display full exception details
                print("Exception occurred:")
                print("Type:", type(e).__name__)  # Type of the exception
                print("Message:", e)  # Exception message
                print("Traceback:")
                
                traceback.print_exc()  # Full traceback
                return JsonResponse({'status': f'Raised exception {e}', 'message': 'Threads not stopped'}, status=500)
        c_threads += 1
    return JsonResponse({'status': 'Success on stoping threads', 'message': 'Task stopped successfully'}, status=200)

def permutacje(request):
    return _toggle_redis_value(request, 'perms_combs', '0', 'Permutacje is ON')

def kombinacje(request):
    return _toggle_redis_value(request, 'perms_combs', '1', 'Kombinacje is ON')

def high_card(request):
    return _toggle_redis_value(request, 'arrangement', '9', 'High Card is ON')

def one_pair(request):
    return _toggle_redis_value(request, 'arrangement', '8', 'One Pair is ON')

def two_pairs(request):
    return _toggle_redis_value(request, 'arrangement', '7', 'Two Pairs are ON')

def three_of_a_kind(request):
    return _toggle_redis_value(request, 'arrangement', '6', 'Three of a Kind is ON')

def straight(request):
    return _toggle_redis_value(request, 'arrangement', '5', 'Straight is ON')

def color(request):
    return _toggle_redis_value(request, 'arrangement', '4', 'Color is ON')

def full(request):
    return _toggle_redis_value(request, 'arrangement', '3', 'Full is ON')

def carriage(request):
    return _toggle_redis_value(request, 'arrangement', '2', 'Carriage is ON')

def straight_flush(request):
    redis_buffer_instance.redis_1.set('arrangement', '1')
    redis_buffer_instance.redis_1.set('straight_royal_flush', '0')
    return JsonResponse({'status': 'Straight Flush is ON'})

def straight_royal_flush(request):
    redis_buffer_instance.redis_1.set('arrangement', '1')
    redis_buffer_instance.redis_1.set('straight_royal_flush', '1')
    return JsonResponse({'status': 'Straight Royal Flush is ON'})

# Utility function to toggle Redis values
def _toggle_redis_value(request, key, value, status_message):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set(key, value)
        return JsonResponse({'status': status_message})
    return JsonResponse({'status': 'Invalid request'}, status=400)

def get_redis_value(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        body = json.loads(request.body)
        key = body.get("key")  # Extract the key from the JSON body
        if not key:
            return JsonResponse({"error": "Key is missing"}, status=400)

        redis_buffer_instance.redis_1.set(key, '1')

        
        # Use the value (key) as needed
        print(f"Received key: {key}")

        # Example response
        return JsonResponse({"message": f"Key '{key}' received successfully"})
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
def goodbye(request):
    return render(request, 'home/goodbye.html', {'message': 'We’re sorry, but cookies are required to use this site. Przepraszamy, ale pliki cookie są niezbędne do korzystania z tej strony.'})