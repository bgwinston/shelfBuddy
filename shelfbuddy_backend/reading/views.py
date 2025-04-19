from django.shortcuts import render, redirect, get_object_or_404
from .models import ReadingPlan, ReadingProgress, ReadingGoal
from .forms import ReadingPlanForm, ReadingProgressForm
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta

@login_required
def create_reading_plan(request):
    if request.method == 'POST':
        form = ReadingPlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.user = request.user
            plan.save()
            return redirect('reading_plan_detail', plan.id)
    else:
        form = ReadingPlanForm()
    return render(request, 'reading/create_plan.html', {'form': form})

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

from django.contrib.auth.decorators import login_required
from .models import ReadingPlan

@login_required
def reading_dashboard(request):
    plans = ReadingPlan.objects.filter(user=request.user, is_active=True)
    return render(request, 'reading/reading_dashboard.html', {'plans': plans})
