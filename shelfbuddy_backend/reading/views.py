from datetime import date, timedelta
from math import ceil
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ReadingPlanForm, ReadingProgressForm, ReadingGoalForm
from .models import ReadingPlan, ReadingProgress, ReadingGoal
from shelfbuddy_backend.books.models import Book

# View to create a new reading plan for the logged-in user
@login_required
def create_reading_plan(request):
    if request.method == 'POST':
        form = ReadingPlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.user = request.user
            plan.save()

            if request.POST.get('create_goal'):
                book = plan.book
                total_pages = book.total_pages or 0
                total_days = (plan.target_end_date - plan.start_date).days + 1

                goal = ReadingGoal(
                    user=request.user,
                    plan=plan,  
                    name=f"Finish {book.title}",
                    goal_type='pages',
                    target_amount=total_pages,
                    time_period='monthly',  
                    start_date=plan.start_date,
                    end_date=plan.target_end_date,
                )
                goal.save()

            return redirect('reading_dashboard')
    else:
        form = ReadingPlanForm()

    return render(request, 'reading/create_plan.html', {'form': form})

# View to show details of a specific reading plan, including percent complete
@login_required
@login_required
def reading_plan_detail(request, plan_id):
    plan = get_object_or_404(ReadingPlan, id=plan_id, user=request.user)
    progress = ReadingProgress.objects.filter(plan=plan).order_by('-date')
    total_read = sum(p.pages_read for p in progress)

    return render(request, 'reading/plan_detail.html', {
        'plan': plan,
        'progress': progress,
        'total_read': total_read,
    })

# View for logging reading progress to a specific plan
@login_required
def log_progress(request, plan_id):
    plan = get_object_or_404(ReadingPlan, id=plan_id, user=request.user)
    if request.method == 'POST':
        form = ReadingProgressForm(request.POST)
        if form.is_valid():
            progress = form.save(commit=False)
            progress.plan = plan
            progress.save()
            return redirect('reading_plan_detail', plan.id)
    else:
        form = ReadingProgressForm()
    return render(request, 'reading/log_progress.html', {'form': form, 'plan': plan})

# Generates a weekly report of progress toward active reading plans
def weekly_report(request):
    user = request.user
    today = date.today()
    week_start = today - timedelta(days=today.weekday())  # Monday
    week_end = week_start + timedelta(days=6)  # Sunday

    plans = ReadingPlan.objects.filter(user=user)
    report_data = []

    for plan in plans:
        # Calculate how many pages the user read this week
        progress_qs = ReadingProgress.objects.filter(
            plan=plan,
            date__range=[week_start, week_end]
        )
        pages_this_week = sum(p.pages_read for p in progress_qs)

        # Calculate weekly target
        total_days = (plan.target_end_date - plan.start_date).days + 1
        total_weeks = max(total_days // 7, 1)
        weekly_target = plan.book.total_pages // total_weeks if plan.book.total_pages else plan.daily_target_pages * 7

        # Determine reading status
        if today < plan.start_date and pages_this_week > 0:
            status = "📈 Ahead of Schedule"
        elif pages_this_week >= weekly_target:
            status = "✅ On Track"
        else:
            status = "⚠️ Behind Schedule"

        report_data.append({
            'book': plan.book.title,
            'pages_this_week': pages_this_week,
            'weekly_target': weekly_target,
            'status': status,
        })

    return render(request, 'reading/weekly_report.html', {
        'week_start': week_start,
        'week_end': week_end,
        'report_data': report_data,
    })

# Checks which reading plans are falling behind based on expected vs actual pages read
@login_required
def check_falling_behind(request):
    today = date.today()
    plans = ReadingPlan.objects.filter(user=request.user, is_active=True)
    behind = []

    for plan in plans:
        total_pages_read = sum(progress.pages_read for progress in ReadingProgress.objects.filter(plan=plan))
        days_passed = (today - plan.start_date).days + 1
        expected_pages = plan.daily_target_pages * days_passed

        if total_pages_read < expected_pages:
            remaining_days = (plan.target_end_date - today).days
            total_pages = plan.book.total_pages or 0
            remaining_pages = total_pages - total_pages_read
            revised_target = ceil(remaining_pages / remaining_days) if remaining_days > 0 else None

            behind.append({
                'book': plan.book.title,
                'expected': expected_pages,
                'actual': total_pages_read,
                'difference': expected_pages - total_pages_read,
                'revised_target': revised_target,
            })

    return render(request, 'reading/behind_alerts.html', {'behind': behind})

# Main reading dashboard that shows active plans, goals, and behind alerts
@login_required
def reading_dashboard(request):
    user = request.user

    active_plans = ReadingPlan.objects.filter(user=user, is_active=True)
    currently_reading = [
        plan.book for plan in active_plans
        if plan.readingprogress_set.exists()
    ]

    recent_books = Book.objects.filter(user=user).order_by('-date_added')[:5]
    wishlist_books = Book.objects.filter(user=user, is_wishlist=True)
    overdue_books = Book.objects.filter(user=user, due_date__lt=date.today())
    goals = ReadingGoal.objects.filter(user=user)

    behind_alerts = []
    today = date.today()
    for plan in active_plans:
        total_read = sum(p.pages_read for p in plan.readingprogress_set.all())
        expected_pages = plan.daily_target_pages * (today - plan.start_date).days
        if total_read < expected_pages:
            behind_alerts.append(plan)

    return render(request, 'reading/reading_dashboard.html', {
        'plans': active_plans,  
        'currently_reading': currently_reading,
        'recent_books': recent_books,
        'wishlist_books': wishlist_books,
        'overdue_books': overdue_books,
        'goals': goals,
        'behind_alerts': behind_alerts,
    })

# View to create a new reading goal for the user
@login_required
def create_goal_view(request):
    if request.method == 'POST':
        form = ReadingGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            return redirect('reading_dashboard')
    else:
        form = ReadingGoalForm()
    return render(request, 'reading/create_goal.html', {'form': form})

# Deletes a reading goal for the logged-in user
def delete_goal(request, goal_id):
    goal = get_object_or_404(ReadingGoal, id=goal_id, user=request.user)
    goal.delete()
    return redirect('reading_dashboard')

# Static informational page about ShelfBuddy
def about_shelfbuddy(request):
    return render(request, 'reading/about_shelfbuddy.html')

# View to edit an existing reading plan
@login_required
def edit_reading_plan(request, plan_id):
    plan = get_object_or_404(ReadingPlan, id=plan_id, user=request.user)
    goal = plan.goals.first()  

    if request.method == 'POST':
        plan_form = ReadingPlanForm(request.POST, instance=plan)
        goal_form = ReadingGoalForm(request.POST, instance=goal) if goal else None

        if plan_form.is_valid() and (goal_form is None or goal_form.is_valid()):
            plan_form.save()
            if goal_form:
                goal_form.save()
            return redirect('reading_dashboard')
    else:
        plan_form = ReadingPlanForm(instance=plan)
        goal_form = ReadingGoalForm(instance=goal) if goal else None

    return render(request, 'reading/edit_plan.html', {
        'form': plan_form,
        'goal_form': goal_form,
        'goal': goal,
    })
    
@login_required
def delete_reading_plan(request, plan_id):
    plan = get_object_or_404(ReadingPlan, id=plan_id, user=request.user)
    plan.delete()
    return redirect('reading_dashboard')