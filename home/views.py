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
from threading import Thread, Event
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor, TimeoutError

# Global Variables
task_threads = {}
session_threads = {}
thread_ids = []
task_thread = None
# Views
redis_client = redis_buffer_instance_one_pair_game.redis_1

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
    is_dev = os.getenv('IS_DEV', 'yes')
    if request.method == 'GET':
        # Ensure a session is created
        print("ONE_PAIR_GAME")
        return render(request, 'home/one_pair_game.html', {'is_dev': is_dev})
        # _initialize_redis_values_gra_jedna_para()

        # # Log all query parameters for debugging
        # print("Query parameters:", request.GET)

        # # Get channel_name from the query parameters
        # channel_name = request.GET.get("channel_name")
        # if not channel_name:
        #     print("Error: Channel name not provided in the query string.")
        #     return JsonResponse({"error": "Channel name not provided in the query string"}, status=400)

        # # Get session_id from Redis using channel_name
        # session_id = redis_client.get(f"ws_session_{channel_name}")
        # if session_id:
        #     session_id = session_id.decode('utf-8')
        #     print("SESSION ID CHANNEL", session_id)

        #     # Start the thread with the session ID
        #     start_thread(request, session_id)

def get_session_id(request):
    """Return the current session ID."""
    # Ensure the session exists
    if not request.session.session_key:
        request.session.create()
    start_thread(request, request.session.session_key)
    return JsonResponse({"session_id": request.session.session_key})
    
def start_task(request):
    """Handle task initiation from POST request."""
    if request.method == 'POST':
        _initialize_redis_values_start_task()
        return _handle_thread(request, subsite_specific=False)
    return JsonResponse({'status': 'Invalid request'}, status=400)

def stop_task(request):
    """Handle task stopping from POST request."""
    if request.method == 'POST':
        data = json.loads(request.body)
        session_id = data.get("session_id")


        task_manager.stop_event_main.set()
        # task_manager.stop_event.set()
        
        # session_id = request.session.session_key
        redis_buffer_instance_one_pair_game.redis_1.set(f'stop_event_send_updates', '1')
        redis_buffer_instance_one_pair_game.redis_1.set(f'wait_buffer', '1')
        if session_id:
            _stop_thread(request, session_id)
        return JsonResponse({"message": f"Task stopped for session {session_id}"})
    return JsonResponse({"error": "No active session."}, status=400)

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
    task_manager.stop_event_main.clear()
    task_manager.stop_event.clear()

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
    
    when_on_refresh = redis_buffer_instance_one_pair_game.redis_1.get('on_refresh').decode('utf-8')
    print("On refresh", when_on_refresh)
    # if when_on_refresh == '1':
    #     _stop_thread(request)
    task_manager.stop_event_main.clear()
    thread_result = start_thread(request)
    request.session[thread_key] = thread_result['thread_id']
    
    print("Before rendering the response...")

    if template:
        response = render(request, template, context)
        response['status'] = 'Threads started...'
        return response
    else:
        return JsonResponse({'status': 'Threads started...'})

def start_thread(request, session_id):
    """Start a new thread and store it in Redis and session."""
    global task_threads, thread_ids
    print("START THREAD", session_id)
    # task_manager.stop_event.clear()
    # task_manager.stop_event_main.clear()
    if session_id not in session_threads:  # Avoid starting duplicate threads
        stop_event = Event()  # Stop signal for the thread
        my_thread = MyThread(target=main, session_id=session_id, stop_event=stop_event, thread_name="thread_main")
        session_threads[session_id] = {"thread": my_thread, "stop_event": stop_event}
        my_thread.start()
    # task_threads["thread_main"] = my_thread

    
        
    return {'task_status': 'Thread started', 'thread_id': "thread_main"}
    
def _stop_thread(request, session_id):
    global task_threads, thread_ids
    """Stop the thread based on the thread ID stored in session."""

    redis_buffer_instance_one_pair_game.redis_1.set('stop_event_send_updates', '1')
    # task_manager.stop_event_main.set()
    print("STOP THREAD$$$$$$$$$$$$$$$$$$$$$$$$$$")
    

    print("Keys in session_threads:", session_threads.keys())
    for thread in threading.enumerate():
        # Skip MainThread and other critical threads
        if thread.name == "MainThread" or thread.name.startswith("django"):
            print(f"Skipping critical thread: {thread.name}")
            continue

        if session_id in session_threads:
            task_manager.stop_event_main.set()
            task_manager.stop_event.set()
            session_threads[session_id]["stop_event"].set()  # Signal the thread to stop
            session_threads[session_id]["thread"].join()  # Wait for the thread to terminate
            print(f"Thread {session_id} stopped")
            del session_threads[session_id]  # Remove from the dictionary
        else:
            print(f"Thread not managed by task_threads: {thread.name}")
            return JsonResponse({'status': f'Failure on stoping threads', 'message': 'Thread not managed by task_threads'}, status=500)
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