from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404

from .models import Topic, Entry
from .forms import TopicForm, EntryForm
from .task_tracker import load_tasks, add_task, complete_task

# Create your views here.

def index(request):
    """The home page for Learning Log."""
    return render(request, "learning_logs/index.html")

@login_required
def topics(request):
    """Show all topics."""
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics' : topics}
    return render(request, 'learning_logs/topics.html', context)

@login_required
def topic(request, topic_id):
    """Show a single topic and all its entries."""
    topic = Topic.objects.get(id=topic_id)
    # Make sure the topic belongs to the current user.
    if topic.owner != request.user:
        raise Http404

    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'learning_logs/topic.html', context)

@login_required
def new_topic(request):
    """Add a new topic."""
    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = TopicForm()
    else:
        # POST data submitted; process data.
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect('learning_logs:topics')

    # Display a blank or invalid form.
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)

@login_required
def new_entry(request, topic_id):
    """Add a new entry for a particular topic."""
    topic = Topic.objects.get(id=topic_id)

    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = EntryForm()
    else:
        # POST data submitted; process data.
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect('learning_logs:topic', topic_id=topic_id)

    # Display a blank or invalid form.
    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)

@login_required
def edit_entry(request, entry_id):
    """Edit an existing entry."""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    if topic.owner != request.user:
        raise Http404

    if request.method != 'POST':
        # Initial request; pre-fill form with the current entry.
        form = EntryForm(instance=entry)
    else:
        # POST data submitted; process data.
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topic', topic_id=topic.id)

    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context)

@login_required
def task_list(request):
    """Display all tasks and handle assing new ones via POST."""

    #Load all existing tasks from the JOSN file.
    tasks = load_tasks()

    #Check if the request is a POST
    if request.method == "POST":

        # If the submitted form contains "new_task", the user is adding a task
        if "new_task" in request.POST:
            #Add the task using the text submitted
            add_task(request.POST["new_task"])
        #If the submitted form contains "complete", the user clicked the 'Complete Task' button
        elif "complete" in request.POST:
            # Convert ID from string to int before passing it
            complete_task(int(request.POST["complete"]))

        #Redirect back to the same page so refreshing doesn't resubmit the form
        return redirect("learning_logs:task_list")
    
    # Render the page with all tasks passed into the template context
    return render(request, "learning_logs/task_list.html", {"tasks": tasks})

@login_required
def add_task_view(request):
    """Add a new task with a title and estimated hours."""
    
    #When form is submitted
    if request.method == "POST":
        #Retrieve fields from the form
        title = request.POST["title"]
        hours = float(request.POST["est_hours"])

        #Pass values to add_task
        add_task(title, hours)

        #Redirect to main task list
        return redirect("learning_logs:task_list")

    #Otherwise, show the "add task" form
    return render(request, "learning_logs/add_task.html")

@login_required
def complete_task_view(request, index):
    """Mark a task as complete and log hours spent."""

    #Check if visitor submitted the form
    if request.method == "POST":
        hours = float(request.POST["hours_spent"])

        #Mark the task as complete
        complete_task(index, hours)

        #Return to task list after updating
        return redirect("learning_logs:task_list")

