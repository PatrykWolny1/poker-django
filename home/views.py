import os
import json
import uuid
import time
from django.shortcuts import render
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from home.redis_buffer_singleton import redis_buffer_instance, redis_buffer_instance_one_pair_game, redis_buffer_instance_perms_combs
from home.MyThread import MyThread
from home.ThreadVarManagerSingleton import task_manager
from main import main
import uuid

# Global Variables
task_threads = {}
thread_ids = []
task_thread = None

redis_client = redis_buffer_instance_one_pair_game.redis_1

def index(request):
    """Main index view."""
    template_data = {'title': 'Poker Simulation'}
    return render(request, 'home/index.html', {'template_data': template_data})

def cards_permutations(request):
    is_dev = os.getenv('IS_DEV', 'yes')
    _initialize_redis_values_start_task(0)
     # csrf_token = get_token(request)
    return render(request, 'home/cards_permutations.html', {'is_dev': is_dev})

def one_pair_game(request):
    is_dev = os.getenv('IS_DEV', 'yes')
    redis_buffer_instance.redis_1.set('choice_1', '2')
    redis_buffer_instance.redis_1.set('choice', '2')
    if request.method == 'GET':
        print("ONE_PAIR_GAME")
        return render(request, 'home/one_pair_game.html', {'is_dev': is_dev})

def get_session_id(request):
    """Ensure a session exists and return its ID."""
    # Accessing request.session ensures the session exists

    if not request.session.session_key:
        request.session.create()  # Explicitly create a session if it doesn't exist
    session_key = request.session.session_key  # Retrieve the session key
    
    unique_session_id = generate_unique_session_id(session_key)

    print("Session ID in get_session_id: ", unique_session_id)
    redis_buffer_instance.redis_1.set(f'{session_key}', str(unique_session_id))
    choice = redis_buffer_instance.redis_1.get('choice').decode('utf-8')

    if choice == '1':
        redis_buffer_instance.redis_1.set(f'shared_progress_{unique_session_id}', '0')
        redis_buffer_instance.redis_1.set(f'connection_accepted_{unique_session_id}', 'no')
        task_manager.stop_event_combs_perms.clear()
        start_thread_combs_perms(request, unique_session_id)
    elif choice == '2':
        _initialize_redis_values_gra_jedna_para(unique_session_id)
        start_thread_one_pair_game(request, unique_session_id)
    

    return JsonResponse({"status" : f"Started thread combs_perms. ID: {unique_session_id}"})
    
def start_task_combs_perms(request):
    return JsonResponse({"status" : "Starting thread for combs_perms..."})

def stop_task_combs_perms(request):
    """Handle task stopping from POST request."""
    if request.method == 'POST':
        data = json.loads(request.body)
        session_id = data.get('session_id', None)
        print("Session ID in stop_task_combs_perms: ", session_id)
        task_manager.stop_event_combs_perms.set()

        if session_id:
            _stop_thread(request, session_id)
        return JsonResponse({"message": f"Task stopped for session {session_id}"})
    return JsonResponse({"error": "No active session."}, status=400)

@csrf_exempt
def stop_task(request):
    """Handle task stopping from POST request."""
    if request.method == 'POST':
        data = json.loads(request.body)

        csrf_token = data.get('csrfmiddlewaretoken')

        # task_manager.stop_event.set()
        if csrf_token != request.META.get('CSRF_COOKIE'):
            return JsonResponse({'error': 'Invalid CSRF token'}, status=403)
        
        # session_id = redis_buffer_instance_one_pair_game.redis_1.get(request.session.session_key).decode('utf-8')
        session_id = data.get("session_id")

        # session_id = request.session.session_key
        task_manager.stop_event_main.set()
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
        
        return JsonResponse({'status': 'Game started'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def _initialize_redis_values_gra_jedna_para(session_id):
    """Initialize Redis values specific to gra_jedna_para."""
    redis_buffer_instance.redis_1.set('prog_when_fast', '-1')
    redis_buffer_instance.redis_1.set('choice_1', '2')
    redis_buffer_instance.redis_1.set('choice', '2')
    redis_buffer_instance.redis_1.set('when_one_pair', '1')
    redis_buffer_instance.redis_1.set("entered_value", '10982') #one_pair 1098240
    redis_buffer_instance.redis_1.set('game_si_human', '2')
    redis_buffer_instance.redis_1.set('player_number', '0')
    redis_buffer_instance.redis_1.set('wait_buffer', '0')
    redis_buffer_instance.redis_1.set('stop_event_send_updates', '0')
    redis_buffer_instance_one_pair_game.redis_1.set('thread_status', 'not_ready')
    redis_buffer_instance.redis_1.set(f'connection_accepted_{session_id}', 'no')    
    task_manager.stop_event_main.clear()
    task_manager.stop_event.clear()

def _initialize_redis_values_start_task(session_id):
    """Initialize Redis values specific to start_task."""
    redis_buffer_instance.redis_1.set('choice_1', '2')
    redis_buffer_instance.redis_1.set('choice', '1')
    redis_buffer_instance.redis_1.set('when_one_pair', '0')
    redis_buffer_instance.redis_1.set('prog_when_fast', '-1')
    redis_buffer_instance.redis_1.set('min', '-1')
    redis_buffer_instance.redis_1.set('max', '-1')
    redis_buffer_instance.redis_1.set('count_arrangements', '-1')
    redis_buffer_instance.redis_1.set('count_arrangements_stop', '-1')
    redis_buffer_instance.redis_1.set('print_gen_combs_perms', '-1')


def generate_unique_session_id(session_id):
    """Generate a unique identifier by combining session ID and UUID."""
    return f"{session_id}_{uuid.uuid4().hex}"

def fetch_session_id(request):
    unique_session_id = redis_buffer_instance.redis_1.get(f'{request.session.session_key}').decode('utf-8')
    return JsonResponse({'session_id': unique_session_id})

def start_thread_one_pair_game(request, unique_session_id):
    global task_manager
    """Start a new thread and store it in Redis and session."""
    # Generate a unique identifier for this session/thread
    _initialize_redis_values_gra_jedna_para(unique_session_id)

    if unique_session_id not in task_manager.session_threads:
        task_manager.session_threads[unique_session_id] = {}

    print("Session ID in start_thread: ", unique_session_id, "############################################################")
    my_thread = MyThread(
        target=main,
        session_id=unique_session_id,
        stop_event=task_manager.stop_event_game,
    )
    # Store thread details using the unique session ID
    task_manager.session_threads[unique_session_id]["thread"] = my_thread
    task_manager.session_threads[unique_session_id]["stop_event"] = task_manager.stop_event_game

    my_thread.daemon = True

    my_thread.start()
    return {'task_status': 'Thread started', 'thread_id': unique_session_id}

def start_thread_combs_perms(request, session_id):
    global task_manager
    """Start a new thread and store it in Redis and session."""
    # Generate a unique identifier for this session/thread
    unique_session_id = session_id
    if session_id not in task_manager.session_threads:
        task_manager.session_threads[unique_session_id] = {}

    print("Session ID in start_thread: ", session_id, "############################################################")
    my_thread = MyThread(
        target=main,
        session_id=unique_session_id,
        stop_event=task_manager.stop_event_combs_perms,
    )
    # Store thread details using the unique session ID
    task_manager.session_threads[unique_session_id]["thread"] = my_thread
    task_manager.session_threads[unique_session_id]["stop_event"] = None
    task_manager.session_threads[unique_session_id]["stop_event_progress"] = task_manager.stop_event_combs_perms

    my_thread.daemon = True

    my_thread.start()
    return {'task_status': 'Thread started', 'thread_id': session_id}

def _stop_thread(request, session_id):
    """Stop the thread based on the unique session ID."""

    # Ensure the session ID is unique per thread
    print("Session ID in stop_thread: ", session_id)
    print("Keys in session_threads:", task_manager.session_threads.keys())
    if session_id in task_manager.session_threads:
        if task_manager.session_threads[session_id]["stop_event"] is not None:
            task_manager.session_threads[session_id]["stop_event"].set()  # Signal the thread to stop
        if task_manager.session_threads[session_id]["stop_event_progress"] is not None:
            task_manager.session_threads[session_id]["stop_event_progress"].set()
        task_manager.session_threads[session_id]["thread"].join()  # Wait for the thread to terminate
        print(f"Thread {session_id} stopped")
        del task_manager.session_threads[session_id]  # Remove from the dictionary
        return JsonResponse({'status': 'Success on stopping thread', 'message': 'Thread stopped successfully'}, status=200)
    else:
        print(f"Thread not managed by session_threads: {session_id}")
        return JsonResponse({'status': 'Failure on stopping thread', 'message': 'Thread not managed by session_threads'}, status=500)

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