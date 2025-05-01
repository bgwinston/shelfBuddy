from django.shortcuts import render, redirect, get_object_or_404
from .models import ReadingPlan, ReadingProgress, ReadingGoal, ReadingPlan
from .forms import ReadingPlanForm, ReadingProgressForm
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from .forms import ReadingGoalForm
from math import ceil
from datetime import date
from django.shortcuts import get_object_or_404, redirect
from .models import ReadingGoal

@login_required
def create_reading_plan(request):
    if request.method == 'POST':
        form = ReadingPlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.user = request.user
            plan.save()
            return redirect('reading_dashboard')
    else:
        form = ReadingPlanForm()
    return render(request, 'reading/create_plan.html', {'form': form})

# @login_required
# def reading_plan_detail(request, plan_id):
#     plan = get_object_or_404(ReadingPlan, id=plan_id, user=request.user)
#     progress = ReadingProgress.objects.filter(plan=plan).order_by('-date')
#     total_read = sum(p.pages_read for p in progress)

#     # ✅ Calculate the percent complete
#     total_days = (plan.target_end_date - plan.start_date).days + 1
#     total_goal_pages = plan.daily_target_pages * total_days

#     if total_goal_pages > 0:
#         percent_complete = (total_read / total_goal_pages) * 100
#     else:
#         percent_complete = 0

#     if percent_complete > 100:
#         percent_complete = 100  # ✅ cap it at 100%

#     plan.percent_complete = round(percent_complete, 1)  # round to 1 decimal if you want

#     return render(request, 'reading/plan_detail.html', {
#         'plan': plan,
#         'progress': progress,
#         'total_read': total_read,
#     })
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

@login_required
def weekly_report(request):
    plans = ReadingPlan.objects.filter(user=request.user, is_active=True)
    report_data = []
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    for plan in plans:
        weekly_progress = ReadingProgress.objects.filter(
            plan=plan, date__range=[week_start, today]
        )
        pages_this_week = sum(p.pages_read for p in weekly_progress)
        days_so_far = (today - week_start).days + 1  # Include today

        report_data.append({
            'book': plan.book.title,
            'pages_this_week': pages_this_week,
            'daily_target': plan.daily_target_pages,
            'weekly_target': plan.daily_target_pages * 7,
            'expected_by_now': plan.daily_target_pages * days_so_far,
            'on_track': pages_this_week >= plan.daily_target_pages * days_so_far,
        })

    return render(request, 'reading/weekly_report.html', {
        'report_data': report_data,
        'week_start': week_start,
        'week_end': today
    })

@login_required
def check_falling_behind(request):
    plans = ReadingPlan.objects.filter(user=request.user, is_active=True)
    behind = []
    today = date.today()

    for plan in plans:
        total_days = (today - plan.start_date).days + 1
        expected_pages = plan.daily_target_pages * total_days
        actual_pages = sum(p.pages_read for p in ReadingProgress.objects.filter(plan=plan))
        if actual_pages < expected_pages:
            behind.append({
                'book': plan.book.title,
                'expected': expected_pages,
                'actual': actual_pages,
                'difference': expected_pages - actual_pages
            })

    return render(request, 'reading/behind_alerts.html', {'behind': behind})


@login_required
def reading_dashboard(request):
    plans = ReadingPlan.objects.filter(user=request.user, is_active=True)
    goals = ReadingGoal.objects.filter(user=request.user)

    today = date.today()
    behind_alerts = []

    for plan in plans:
        total_read = sum(p.pages_read for p in ReadingProgress.objects.filter(plan=plan))

        # ✅ Calculate percentage complete
        total_days = (plan.target_end_date - plan.start_date).days + 1
        total_goal_pages = plan.daily_target_pages * total_days

        if total_goal_pages > 0:
            percent_complete = (total_read / total_goal_pages) * 100
        else:
            percent_complete = 0

        # Cap at 100%
        if percent_complete > 100:
            percent_complete = 100

        plan.percent_complete = round(percent_complete, 1)

        # ✅ Handle behind alerts
        expected_pages = plan.daily_target_pages * (today - plan.start_date).days + 1
        if total_read < expected_pages:
            behind_alerts.append(plan)

    return render(request, 'reading/reading_dashboard.html', {
        'plans': plans,
        'goals': goals,
        'behind_alerts': behind_alerts,
    })
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

from .models import ReadingProgress

@login_required
def check_falling_behind(request):
    today = date.today()
    plans = ReadingPlan.objects.filter(user=request.user, is_active=True)
    behind = []

    for plan in plans:
        # Dynamically calculate total pages read
        total_pages_read = sum(progress.pages_read for progress in ReadingProgress.objects.filter(plan=plan))
        
        # Calculate how many days have passed
        days_passed = (today - plan.start_date).days + 1  # +1 to include today

        expected_pages = plan.daily_target_pages * days_passed

        if total_pages_read < expected_pages:
            remaining_days = (plan.target_end_date - today).days
            total_pages = plan.book.total_pages or 0
            remaining_pages = total_pages - total_pages_read

            revised_target = (
                ceil(remaining_pages / remaining_days) if remaining_days > 0 else None
            )

            behind.append({
                'book': plan.book.title,
                'expected': expected_pages,
                'actual': total_pages_read,
                'difference': expected_pages - total_pages_read,
                'revised_target': revised_target,
            })

    return render(request, 'reading/behind_alerts.html', {'behind': behind})



def delete_goal(request, goal_id):
    goal = get_object_or_404(ReadingGoal, id=goal_id, user=request.user)
    goal.delete()
    return redirect('reading_dashboard')  # or whatever your dashboard page is

def about_shelfbuddy(request):
    return render(request, 'reading/about_shelfbuddy.html')

@login_required
def edit_reading_plan(request, plan_id):
    plan = get_object_or_404(ReadingPlan, id=plan_id, user=request.user)
    if request.method == 'POST':
        form = ReadingPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            return redirect('reading_dashboard')
    else:
        form = ReadingPlanForm(instance=plan)
    return render(request, 'reading/edit_plan.html', {'form': form})

@login_required
def apply_suggested_target(request, plan_id):
    plan = get_object_or_404(ReadingPlan, id=plan_id, user=request.user)
    revised_target = request.GET.get('revised_target')
    if revised_target and revised_target.isdigit():
        plan.daily_target_pages = int(revised_target)
        plan.save()
    return redirect('plan_detail', plan_id=plan.id)

@login_required
def reading_plan_detail(request, plan_id):
    plan = get_object_or_404(ReadingPlan, id=plan_id, user=request.user)
    progress = ReadingProgress.objects.filter(plan=plan).order_by('-date')

    total_read = sum(p.pages_read for p in progress)
    plan.total_pages_read = total_read

    # Avoid division by zero and use .total_pages from the related book
    if plan.book and plan.book.total_pages:
        percent_complete = (total_read / plan.book.total_pages) * 100
    else:
        percent_complete = 0

    plan.percent_complete = round(min(percent_complete, 100), 1)  # cap at 100% and round

    return render(request, 'reading/plan_detail.html', {
        'plan': plan,
        'progress': progress,
        'total_read': total_read
    })