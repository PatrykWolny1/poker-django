import os
import json
import uuid
from django.shortcuts import render
from django.http import JsonResponse, FileResponse, Http404
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from home.redis_buffer_singleton import redis_buffer_instance, redis_buffer_instance_one_pair_game
from home.MyThread import MyThread
from home.ThreadVarManagerSingleton import task_manager
from main import main



# Global Variables
task_threads = {}
task_thread = None
# Views

def index(request):
    """Main index view."""
    template_data = {'title': 'Poker Simulation'}
    return render(request, 'home/index.html', {'template_data': template_data})

def cards_permutations(request):
    """Initialize values and render the permutacje_kart template."""
    csrf_token = get_token(request)
    _initialize_redis_values_permutacje()
    return render(request, 'home/cards_permutations.html', {'csrf_token': csrf_token})

def one_pair_game(request):
    """Start thread if not already running, for one-pair game."""
    if request.method == 'GET':
        _initialize_redis_values_gra_jedna_para()
        return _handle_thread(request, subsite_specific=True, template='home/one_pair_game.html')
    return render(request, 'home/one_pair_game.html', {'message': 'No thread running'})

def start_task(request):
    """Handle task initiation from POST request."""
    if request.method == 'POST':
        _initialize_redis_values_start_task()
        return _handle_thread(request, subsite_specific=False)
    return JsonResponse({'status': 'Invalid request'}, status=400)

def stop_task(request):
    """Handle task stopping from POST request."""
    print("CSRF token:", request.META.get('HTTP_X_CSRFTOKEN'))  # Log the CSRF token received.
    print("AAAAAAAAAAAAAAAAAAAAA")
    if request.method == 'POST':
        print("in AAAAAAAAAAAAAAAAAAAAA")
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
    if request.method == 'POST':
        data = json.loads(request.body)
        # player1_name = data.get('player1Name')
        # player2_name = data.get('player2Name')

        # # Set Redis variable (e.g., game state or progress)
        # redis_client.set('game_in_progress', 'true')
        # redis_client.set('player1_name', player1_name)
        # redis_client.set('player2_name', player2_name)

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
    redis_buffer_instance.redis_1.set('min', '-1')
    redis_buffer_instance.redis_1.set('max', '-1')
    

def _initialize_redis_values_gra_jedna_para():
    """Initialize Redis values specific to gra_jedna_para."""
    redis_buffer_instance_one_pair_game.redis_1.flushdb()
    redis_buffer_instance.redis_1.set('choice_1', '2')
    redis_buffer_instance.redis_1.set('choice', '2')
    redis_buffer_instance.redis_1.set('when_one_pair', '1')
    redis_buffer_instance.redis_1.set("entered_value", '10982') #one_pair 1098240
    redis_buffer_instance.redis_1.set('game_si_human', '2')
    redis_buffer_instance.redis_1.set('min', '-1')
    redis_buffer_instance.redis_1.set('max', '-1')
    # for player in range(0, 2):
    #     redis_buffer_instance.redis_1.delete(f'arr_{player}')
    #     redis_buffer_instance.redis_1.delete(f'cards_{player}')
        
    redis_buffer_instance.redis_1.set('player_number', '0')
    redis_buffer_instance.redis_1.set('wait_buffer', '0')
    # redis_buffer_instance.redis_1.delete('arrangement')
    # redis_buffer_instance.redis_1.delete('exchange_cards')
    # redis_buffer_instance.redis_1.delete('type_arrangement')
    # redis_buffer_instance.redis_1.delete('chance')
    # redis_buffer_instance.redis_1.delete('amount')
    

def _initialize_redis_values_start_task():
    """Initialize Redis values specific to start_task."""
    redis_buffer_instance.redis_1.set('choice_1', '2')
    redis_buffer_instance.redis_1.set('choice', '1')
    redis_buffer_instance.redis_1.set('when_one_pair', '0')
    redis_buffer_instance.redis_1.set('prog_when_fast', '-1')
    redis_buffer_instance.redis_1.set('count_arrangements', '-1')
    redis_buffer_instance.redis_1.set('count_arrangements_stop', '-1')
    redis_buffer_instance.redis_1.set('print_gen_combs_perms', '-1')
    
def _handle_thread(request, subsite_specific=False, template=None):
    """Handle the starting and managing of threads for different requests."""
    thread_key = f'thread_data_{request.path.split("/")[1]}' if subsite_specific else 'thread_id'
    existing_thread_id = request.session.get(thread_key)
    if existing_thread_id:
        thread_status = redis_buffer_instance.redis_1.get(f'thread_data_{existing_thread_id}')
        if thread_status and thread_status.decode('utf-8') == 'running':
            task_manager.stop_event.set()
            redis_buffer_instance.redis_1.set(f'thread_data_{existing_thread_id}', 'stopped')
            request.session.pop(thread_key, None)
    task_manager.stop_event.clear()
    task_manager.data_ready_event.clear()
    thread_result = start_thread(request)
    request.session[thread_key] = thread_result['thread_id']
    return render(request, template, {'message': 'Thread already running'}) if template else JsonResponse({'status': 'arrangement started'})

def start_thread(request):
    """Start a new thread and store it in Redis and session."""
    task_manager.stop_event.clear()
    thread_id = str(uuid.uuid4())
    request.session['thread_id'] = thread_id
    try:
        # Start threads or tasks
        my_thread = MyThread(target=main, thread_id=thread_id)
        my_thread.start()
        redis_buffer_instance.redis_1.set(f'thread_data_{thread_id}', 'running')
    except KeyboardInterrupt:
        print("KeyboardInterrupt caught. Cleaning up...")
        redis_buffer_instance.redis_1.set('wait_buffer', '1')
        task_manager.stop_event.set()
        my_thread.join()
    
    return {'task_status': 'Thread started', 'thread_id': thread_id}

def _stop_thread(request):
    """Stop the thread based on the thread ID stored in session."""
    thread_key = 'thread_id'
    thread_id = request.session.get(thread_key)
    task_manager.stop_event.set()
    if thread_id:
        thread_status = redis_buffer_instance.redis_1.get(f'thread_data_{thread_id}')
        if thread_status and thread_status.decode('utf-8') == 'running':
            task_manager.stop_event.set()
            task_thread = task_threads.get(thread_id)
            if task_thread and task_thread.is_alive():
                task_thread.join()
            redis_buffer_instance.redis_1.set(f'thread_data_{thread_id}', 'stopped')
            request.session.pop(thread_key, None)
            task_threads.pop(thread_id, None)
            return JsonResponse({'status': 'Task stopped successfully', 'thread_id': thread_id})
    return JsonResponse({'status': 'No running task found for this sub-site'}, status=400)

# Game State Management Views

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

#ONE PAIR GAME

def play_button(request):
    pass

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