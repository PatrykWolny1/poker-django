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
import os
from classes.Player import Player
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
    # Force session creation
    if not request.session.session_key:
        request.session.save()  # This ensures a session key is generated
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
    
    redis_buffer_instance.redis_1.set('session_key', session_key)

    unique_session_id = generate_unique_session_id(session_key)

    redis_buffer_instance.redis_1.set(f'choice_1_{unique_session_id}', '2')
    redis_buffer_instance.redis_1.set(f'choice_{unique_session_id}', '1')
    redis_buffer_instance.redis_1.set(f'when_one_pair_{unique_session_id}', '0')
    redis_buffer_instance.redis_1.set(f'prog_when_fast_{unique_session_id}', '-1')
    redis_buffer_instance.redis_1.set(f'min_{unique_session_id}', '-1')
    redis_buffer_instance.redis_1.set(f'max_{unique_session_id}', '-1')
    redis_buffer_instance.redis_1.set(f'count_arrangements_{unique_session_id}', '-1')
    redis_buffer_instance.redis_1.set(f'count_arrangements_stop_{unique_session_id}', '-1')
    redis_buffer_instance.redis_1.set(f'print_gen_combs_perms_{unique_session_id}', '-1')
    redis_buffer_instance.redis_1.set(f'shared_progress_{unique_session_id}', '0')
    redis_buffer_instance.redis_1.set(f'connection_accepted_{unique_session_id}', 'no')

    print("Session ID in get_session_id: ", unique_session_id)
    redis_buffer_instance.redis_1.set(f'{session_key}', str(unique_session_id))
    choice = redis_buffer_instance.redis_1.get(f'choice_{unique_session_id}').decode('utf-8')

    _add_id_to_redis(request, f'perms_combs', unique_session_id)
    _add_id_to_redis(request, f'arrangement', unique_session_id)

    if redis_buffer_instance.redis_1.get(f'arrangement_{unique_session_id}').decode('utf-8') == '1':
        _add_id_to_redis(request, f'straight_royal_flush', unique_session_id)   
    
    print("Choice: ", choice)
    if choice == '1':
        name = "thread_perms_combs"
        task_manager.add_session(unique_session_id, name)
        task_manager.session_threads[unique_session_id][name].add_event("stop_event_progress")
        task_manager.session_threads[unique_session_id][name].add_event("stop_event_immediately")
        task_manager.session_threads[unique_session_id][name].event["stop_event_progress"].clear()
        task_manager.session_threads[unique_session_id][name].event["stop_event_immediately"].clear()
        print(task_manager.session_threads[unique_session_id][name].event)
        redis_buffer_instance.redis_1.set(f'{unique_session_id}_thread_name', name)
        start_thread_combs_perms(request, unique_session_id, name)
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
        task_manager.session_threads[session_id]["thread_perms_combs"].event["stop_event_progress"].set()
        task_manager.session_threads[session_id]["thread_perms_combs"].event["stop_event_immediately"].set()

        if session_id:
            _stop_thread(request, session_id, "thread_perms_combs")
        return JsonResponse({"message": f"Task stopped for session {session_id}"})
    return JsonResponse({"error": "No active session."}, status=400)

@csrf_exempt
def stop_task(request):
    """Handle task stopping from POST request."""
    if request.method == 'POST':
        data = json.loads(request.body)

        csrf_token = data.get('csrfmiddlewaretoken')

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
    unique_session_id = redis_buffer_instance.redis_1.get(f'{request.session.session_key}').decode('utf-8')
    print(unique_session_id)
    file_path = f'permutations_data/data_perms_combs_ID_{unique_session_id}.txt'
    if not os.path.exists(file_path):
        raise Http404("File not found")
    response = FileResponse(open(file_path, 'rb'), as_attachment=True)
    response['Content-Disposition'] = f'attachment; filename="collected_data_perms_combs_{unique_session_id}.txt"'
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
    redis_buffer_instance.redis_1.set(f'choice_1_{session_id}', '2')
    redis_buffer_instance.redis_1.set(f'choice_{session_id}', '1')
    redis_buffer_instance.redis_1.set(f'when_one_pair_{session_id}', '0')
    redis_buffer_instance.redis_1.set(f'prog_when_fast_{session_id}', '-1')
    redis_buffer_instance.redis_1.set(f'min_{session_id}', '-1')
    redis_buffer_instance.redis_1.set(f'max_{session_id}', '-1')
    redis_buffer_instance.redis_1.set(f'count_arrangements_{session_id}', '-1')
    redis_buffer_instance.redis_1.set(f'count_arrangements_stop_{session_id}', '-1')
    redis_buffer_instance.redis_1.set(f'print_gen_combs_perms_{session_id}', '-1')


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

def start_thread_combs_perms(request, session_id, name):
    global task_manager
    """Start a new thread and store it in Redis and session."""
    # Generate a unique identifier for this session/thread
    unique_session_id = session_id
    if session_id not in task_manager.session_threads:
        task_manager.session_threads[unique_session_id] = {}

    print("Session ID in start_thread: ", session_id, "############################################################")
    perms_combs = redis_buffer_instance.redis_1.get(f'{'perms_combs'}_{session_id}').decode('utf-8')
    
    if perms_combs == '1':
        perms_combs = True
    elif perms_combs == '0':
        perms_combs = False

    my_thread = MyThread(target=Player().cards_permutations, 
                        flag1=False, 
                        flag2=perms_combs, 
                        session_id=unique_session_id)
    
    task_manager.session_threads[unique_session_id][name].set_thread(my_thread)

    my_thread.daemon = True

    my_thread.start()
    return {'task_status': 'Thread started', 'thread_id': session_id}

def _stop_thread(request, session_id, name):
    """Stop the thread based on the unique session ID."""

    # Ensure the session ID is unique per thread
    print("Session ID in stop_thread: ", session_id)
    print("Keys in session_threads:", task_manager.session_threads.keys())
    if session_id in task_manager.session_threads:
        task_manager.session_threads[session_id][name].event["stop_event_progress"].set()
        task_manager.session_threads[session_id][name].thread.join()  # Wait for the thread to terminate
        print(f"Thread {session_id} stopped")
        del task_manager.session_threads[session_id][name]  # Remove from the dictionary
        return JsonResponse({'status': 'Success on stopping thread', 'message': 'Thread stopped successfully'}, status=200)
    else:
        print(f"Thread not managed by session_threads: {session_id}")
        return JsonResponse({'status': 'Failure on stopping thread', 'message': 'Thread not managed by session_threads'}, status=500)

def permutacje(request):
    session_id = request.session.session_key
    print("Session ID in permutacje: ", session_id)
    return _toggle_redis_value(request, f'perms_combs_{session_id}', '0', 'Permutacje is ON')

def kombinacje(request):
    session_id = request.session.session_key
    print("Session ID in kombinacje: ", session_id)
    return _toggle_redis_value(request, f'perms_combs_{session_id}', '1', 'Kombinacje is ON')

def high_card(request):
    session_id = request.session.session_key
    print("Session ID in high_card: ", session_id)
    return _toggle_redis_value(request, f'arrangement_{session_id}', '9', 'High Card is ON')

def one_pair(request):
    session_id = request.session.session_key
    print("Session ID in one_pair: ", session_id)
    return _toggle_redis_value(request, f'arrangement_{session_id}', '8', 'One Pair is ON')

def two_pairs(request):
    session_id = request.session.session_key
    print("Session ID in two_pairs: ", session_id)
    return _toggle_redis_value(request, f'arrangement_{session_id}', '7', 'Two Pairs are ON')

def three_of_a_kind(request):
    session_id = request.session.session_key
    print("Session ID in three_of_a_kind: ", session_id)
    return _toggle_redis_value(request, f'arrangement_{session_id}', '6', 'Three of a Kind is ON')

def straight(request):
    session_id = request.session.session_key
    print("Session ID in straight: ", session_id)
    return _toggle_redis_value(request, f'arrangement_{session_id}', '5', 'Straight is ON')

def color(request):
    session_id = request.session.session_key
    print("Session ID in color: ", session_id)
    return _toggle_redis_value(request, f'arrangement_{session_id}', '4', 'Color is ON')

def full(request):
    session_id = request.session.session_key
    print("Session ID in full: ", session_id)
    return _toggle_redis_value(request, f'arrangement_{session_id}', '3', 'Full is ON')

def carriage(request):
    session_id = request.session.session_key
    print("Session ID in carriage: ", session_id)
    return _toggle_redis_value(request, f'arrangement_{session_id}', '2', 'Carriage is ON')

def straight_flush(request):
    session_id = request.session.session_key
    print("Session ID in straight_flush: ", session_id)
    redis_buffer_instance.redis_1.set(f'arrangement_{session_id}', '1')
    redis_buffer_instance.redis_1.set(f'straight_royal_flush_{session_id}', '0')
    return JsonResponse({'status': 'Straight Flush is ON'})

def straight_royal_flush(request):
    session_id = request.session.session_key
    print("Session ID in straight_royal_flush: ", session_id)
    redis_buffer_instance.redis_1.set(f'arrangement_{session_id}', '1')
    redis_buffer_instance.redis_1.set(f'straight_royal_flush_{session_id}', '1')
    return JsonResponse({'status': 'Straight Royal Flush is ON'})

# Utility function to toggle Redis values
def _toggle_redis_value(request, key, value, status_message):
    if request.method == 'POST':
        redis_buffer_instance.redis_1.set(key, value)
        return JsonResponse({'status': status_message})
    return JsonResponse({'status': 'Invalid request'}, status=400)

def _add_id_to_redis(request, key, session_id):
    print(key, session_id)
    value = redis_buffer_instance.redis_1.get(f'{key}_{request.session.session_key}').decode('utf-8')
    print("################################", value)
    redis_buffer_instance.redis_1.set(f'{key}_{session_id}', value)
    print("################################",f'{key}_{session_id}')
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