from django.shortcuts import render
from django.http import JsonResponse
from .models import LeaderboardEntry
import random

def selection(request):
    last_problems = request.session.get('last_problems', [])
    selected_op = request.session.get('selectedOp', 'add')
    num_digits = request.session.get('num_digits', 1)
    num_questions = request.session.get('num_questions', 3)

    total_time = sum(time_taken for problem, time_taken in last_problems)
    average_time = total_time / len(last_problems) if last_problems else 0

    operation_mapping = {
        'mul': {1: "1×1", 2: "2×1", 3: "3×1", 4: "2×2", 5: "4×1", 6: "3×2", 7: "3×3"},
        'sub': {1: "1-1", 2: "2-2", 3: "3-3", 4: "4-4", 5: "5-5", 6: "6-6", 7: "7-7"},
        'div': {1: "2/1", 2: "3/1", 3: "3/2", 4: "4/1", 5: "4/2", 6: "4/3", 7: "5/1"},
        'add': {1: "1+1", 2: "2+2", 3: "3+3", 4: "4+4", 5: "5+5", 6: "6+6", 7: "7+7"}
    }

    current_mapping = operation_mapping.get(selected_op, operation_mapping['add'])
    mode = current_mapping.get(num_digits, "1+1")

    # Get leaderboard for current settings (will be empty initially)
    try:
        leaderboard = LeaderboardEntry.objects.filter(
            operation=selected_op,
            digits=num_digits,
            num_questions=num_questions
        ).order_by('average_time')[:10]
    except:
        leaderboard = []

    return render(request, 'app/selection.html', {
        'last_problems': last_problems, 
        'mode': mode, 
        'average_time': average_time, 
        'num_questions': num_questions,
        'leaderboard': leaderboard
    })

def get_leaderboard(request):
    """AJAX endpoint to get leaderboard data for specific settings"""
    if request.method == 'GET':
        operation = request.GET.get('operation', 'add')
        digits = int(request.GET.get('digits', 1))
        num_questions = int(request.GET.get('num_questions', 3))
        
        try:
            leaderboard = LeaderboardEntry.objects.filter(
                operation=operation,
                digits=digits,
                num_questions=num_questions
            ).order_by('average_time')[:10]
            
            # Convert to list of dictionaries for JSON response
            leaderboard_data = [
                {
                    'rank': idx + 1,
                    'average_time': entry.average_time
                }
                for idx, entry in enumerate(leaderboard)
            ]
            
            return JsonResponse({
                'success': True,
                'leaderboard': leaderboard_data
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def store_selected_op(request):
    if request.method == 'POST':
        request.session['selectedOp'] = request.POST.get('selected_op')
        request.session['num_questions'] = request.POST.get('num_questions')
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def generate_numbers(num_digits, operation):
    if operation in ('add', 'sub'):
        min_val = 10**(num_digits - 1) if num_digits > 1 else 1
        max_val = (10**num_digits) - 1
        num1 = random.randint(min_val, max_val)
        num2 = random.randint(min_val, max_val)
        if operation == 'sub' and num2 > num1:
            num1, num2 = num2, num1
        return num1, num2

    elif operation == 'mul':
        # Mapping: for a given num_digits, determine the digit-lengths of factors.
        digit_mapping = {1: (1, 1), 2: (2, 1), 3: (3, 1), 4: (2, 2), 5: (4, 1), 6: (3, 2), 7: (3, 3)}
        num1_digits, num2_digits = digit_mapping.get(num_digits, (1, 1))
        # If one-digit factors, set range to 2-9 (exclude 1); otherwise, use standard range.
        if num1_digits == 1:
            min_val1, max_val1 = 2, 9
        else:
            min_val1 = 10**(num1_digits - 1)
            max_val1 = (10**num1_digits) - 1

        if num2_digits == 1:
            min_val2, max_val2 = 2, 9
        else:
            min_val2 = 10**(num2_digits - 1)
            max_val2 = (10**num2_digits) - 1

        # Loop until neither factor is divisible by 10.
        while True:
            num1 = random.randint(min_val1, max_val1)
            num2 = random.randint(min_val2, max_val2)
            if num1 % 10 != 0 and num2 % 10 != 0:
                break
        return num1, num2

    elif operation == 'div':
        # For division, the mapping assigns num1 a higher digit count than num2 by design.
        digit_mapping = {1: (2, 1), 2: (3, 1), 3: (3, 2), 4: (4, 1), 5: (4, 2), 6: (4, 3), 7: (5, 1)}
        num1_digits, num2_digits = digit_mapping.get(num_digits, (1, 1))
        if num1_digits == 1:
            min_val1, max_val1 = 10, 99
        else:
            min_val1 = 10**(num1_digits - 1)
            max_val1 = (10**num1_digits) - 1

        # For divisor, ensure it's not 1.
        if num2_digits == 1:
            min_val2, max_val2 = 2, 9
        else:
            min_val2 = 10**(num2_digits - 1)
            max_val2 = (10**num2_digits) - 1

        # Loop until a valid division is found and neither number is divisible by 10.
        while True:
            num1 = random.randint(min_val1, max_val1)
            num2 = random.randint(min_val2, max_val2)
            if num2 != 0 and num1 % num2 == 0:
                if num1 % 10 != 0 and num2 % 10 != 0:
                    return num1, num2
    return None, None

def start_game(request, operation, problem):
    request.session['last_problems'] = []
    num_digits = problem
    request.session['num_digits'] = num_digits
    num1, num2 = generate_numbers(num_digits, operation)
    num_questions = request.session.get('num_questions')
    selectedOp = request.session.get('selectedOp')
    context = {'num1': num1, 'num2': num2, 'operation': operation, 'num_questions': num_questions, 'selectedOp': selectedOp}
    return render(request, 'app/index.html', context)

def addition(request, problem):
    return start_game(request, 'add', problem)

def subtraction(request, problem):
    return start_game(request, 'sub', problem)

def multiplication(request, problem):
    return start_game(request, 'mul', problem)

def division(request, problem):
    return start_game(request, 'div', problem)

def check_answer(request):
    if request.method != "POST":
        return JsonResponse({'correct': False})

    try:
        answer = int(request.POST.get('answer'))
        num1 = int(request.POST.get('num1'))
        num2 = int(request.POST.get('num2'))
        time_taken = float(request.POST.get('timeTaken')) / 1000
    except (ValueError, TypeError):
        return JsonResponse({'correct': False})

    operation = request.GET.get('operation', 'add')
    num_digits = request.session.get('num_digits', 1)
    
    # Retrieve user's stats data
    last_problems = request.session.get('last_problems', [])
    # Canonical forms for preventing repeats
    last_problems_set = set(request.session.get('last_problems_set', []))

    # Decide min_val and max_val for add/sub
    if operation in ('add', 'sub'):
        min_val = 10**(num_digits - 1) if num_digits > 1 else 1
        max_val = (10**num_digits) - 1
    else:
        min_val, max_val = None, None

    correct_answer = {
        'add': num1 + num2,
        'sub': num1 - num2,
        'mul': num1 * num2,
        'div': num1 / num2 if num2 and num1 % num2 == 0 else None
    }.get(operation)

    if correct_answer is None or answer != correct_answer:
        return JsonResponse({'correct': False})

    # -------------------------------------------------------
    # 1) Store the old problem so it won't repeat
    symbol_map = {'add': '+', 'sub': '-', 'mul': '×', 'div': '÷'}
    symbol = symbol_map.get(operation, operation)
    if operation in ('add', 'mul'):
        old_canonical = f"{min(num1, num2)}{symbol}{max(num1, num2)}"
    else:
        old_canonical = f"{num1}{symbol}{num2}"
    last_problems_set.add(old_canonical)
    request.session['last_problems_set'] = list(last_problems_set)

    # 2) Save the old question for display/stats
    last_problems.insert(0, (f"{num1}{symbol}{num2}", time_taken))
    request.session['last_problems'] = last_problems
    # -------------------------------------------------------

    # Check if a set of problems is complete (based on Q setting) and save to leaderboard
    num_questions = int(request.session.get('num_questions', 3))
    set_completed = False
    
    if len(last_problems) >= num_questions:
        print("Set completed! Calculating average and saving to leaderboard.")
        
        # Calculate average time for this completed set
        total_time = sum(time for problem, time in last_problems[:num_questions])
        average_time = total_time / num_questions
        
        # Save to leaderboard
        try:
            LeaderboardEntry.objects.create(
                operation=operation,
                digits=num_digits,
                num_questions=num_questions,
                average_time=average_time
            )
            print(f"Saved to leaderboard: {operation} {num_digits}D {num_questions}Q - {average_time:.3f}s")
        except Exception as e:
            print(f"Error saving to leaderboard: {e}")
        
        # Reset the canonical set after completing a set
        last_problems_set = set()
        request.session['last_problems_set'] = []
        set_completed = True

    MAX_ATTEMPTS = 1000
    attempts = 0

    # Now generate a fresh problem that isn't in the canonical set
    while attempts < MAX_ATTEMPTS:
        if operation in ('add', 'sub'):
            new_num1 = random.randint(min_val, max_val)
            new_num2 = random.randint(min_val, max_val)
            if operation == 'sub' and new_num2 > new_num1:
                new_num1, new_num2 = new_num2, new_num1
        elif operation in ('mul', 'div'):
            new_num1, new_num2 = generate_numbers(num_digits, operation)
            if not new_num1 or not new_num2:
                return JsonResponse({'correct': False})
        else:
            return JsonResponse({'correct': False})

        # Build canonical form for the new question
        displayed_problem = f"{new_num1}{symbol}{new_num2}"
        if operation in ('add', 'mul'):
            canonical_problem = f"{min(new_num1, new_num2)}{symbol}{max(new_num1, new_num2)}"
        else:
            canonical_problem = displayed_problem

        if canonical_problem not in last_problems_set:
            # Mark the newly generated question as used
            last_problems_set.add(canonical_problem)
            request.session['last_problems_set'] = list(last_problems_set)
            print(f"Generated new question after {attempts + 1} attempts")
            break
        attempts += 1
    else:
        # Fallback if no unique question found
        print(f"Warning: Could not generate a unique {operation} problem after multiple attempts. Trying fallback...")
        FALLBACK_RETRIES = 100
        fallback_attempts = 0
        while fallback_attempts < FALLBACK_RETRIES:
            if operation in ('add', 'sub'):
                new_num1 = random.randint(min_val, max_val)
                new_num2 = random.randint(min_val, max_val)
                if operation == 'sub' and new_num2 > new_num1:
                    new_num1, new_num2 = new_num2, new_num1
            elif operation in ('mul', 'div'):
                new_num1, new_num2 = generate_numbers(num_digits, operation)
                if not new_num1 or not new_num2:
                    return JsonResponse({'correct': False})
            else:
                return JsonResponse({'correct': False})

            displayed_problem = f"{new_num1}{symbol}{new_num2}"
            if operation in ('add', 'mul'):
                canonical_problem = f"{min(new_num1, new_num2)}{symbol}{max(new_num1, new_num2)}"
            else:
                canonical_problem = displayed_problem

            if canonical_problem not in last_problems_set:
                last_problems_set.add(canonical_problem)
                request.session['last_problems_set'] = list(last_problems_set)
                print(f"Generated new question after {attempts + 1 + fallback_attempts} attempts (fallback)")
                break
            fallback_attempts += 1
        else:
            new_num1, new_num2 = generate_numbers(num_digits, operation)
            displayed_problem = f"{new_num1}{symbol}{new_num2}"
            if operation in ('add', 'mul'):
                canonical_problem = f"{min(new_num1, new_num2)}{symbol}{max(new_num1, new_num2)}"
            else:
                canonical_problem = displayed_problem
            print(f"Warning: Could not generate a unique {operation} problem after all attempts, returning duplicate.")
            last_problems_set.add(canonical_problem)
            request.session['last_problems_set'] = list(last_problems_set)

    return JsonResponse({
        'correct': True,
        'num1': new_num1,
        'num2': new_num2,
        'operation': operation,
        'set_completed': set_completed  # Let frontend know if a set was completed
    })