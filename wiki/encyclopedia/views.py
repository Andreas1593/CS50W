import secrets

from re import M
from django import forms
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from . import util

class NewPageForm(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={"class": "form-control col-sm-4 col-md-4 col-lg-4"}))
    content = forms.CharField(label="Description", widget=forms.Textarea(attrs={"class": "form-control col-sm-8 col-md-8 col-lg-8", "rows": 25}))


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, entry):
    # Retrieve entry in markdown and convert to HTML
    content = util.get_entry(entry)
    convertedContent = util.convertEntry(content)

    if request.method == "GET":
        if entry == "noResult":
            return render(request, "encyclopedia/entry.html", {
                "entryContent": convertedContent,
                "title": "No Result",
            })

        else:
            return render(request, "encyclopedia/entry.html", {
                "entryContent": convertedContent,
                "title": entry
            })

    else:
        return HttpResponseRedirect(reverse("edit", kwargs={"entry": entry}))

def search(request):
    title = request.GET.get('q')
    entries = util.list_entries()
    
    # If the queried entry exists
    if util.get_entry(title):

        # Fix lower- / uppercase writing of the query
        for entry in entries:
            if title.lower() == entry.lower():
                title = entry
                
        # 'kwargs' puts the variable into the URL (<str:entry>)
        return HttpResponseRedirect(reverse("entry", kwargs={"entry": title}))

    # Queried entry doesn't exist
    else:
        # Find all entries that have the query as a substring
        matches = []
        for entry in entries:
            if title.lower() in entry.lower():
                matches.append(entry)

        # Show substring results if existing
        return render(request, "encyclopedia/entry.html", {
            "title": "No Result",
            "matches": matches,
            })

def newPage(request):
    # Submit newly created page
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            entries = util.list_entries()

            # Check if a page with the same title exists
            for entry in entries:
                # Case insensitive
                if title.lower() == entry.lower():
                    return render(request, "encyclopedia/layout.html", {
                        "error": "Page with this title already exists",
                    })

                # Save new page and redirect
                else:
                    util.save_entry(title, content)
                    return HttpResponseRedirect(reverse("entry", kwargs={"entry": title}))

    # Render 'create new entry' page
    else:
        return render(request, "encyclopedia/newPage.html", {
            "form": NewPageForm(),
        })

def editPage(request, entry):
    content = util.get_entry(entry)

    # Create new form, hide the title and prefill the content
    if request.method == "GET":
        form = NewPageForm()
        form.fields["title"].widget = forms.HiddenInput()
        form.fields["content"].initial = content
        return render(request, "encyclopedia/editPage.html", {
            "form": form,
            "title": entry,
        })

    # Submit edited page
    else:
        # The replace function prevents strange behavior of line breaks being inserted
        content = request.POST.get("content").replace("\r", "")
        util.save_entry(entry, content)
        return HttpResponseRedirect(reverse("entry", kwargs={"entry": entry}))

def randomPage(request):
    entries = util.list_entries()
    randomEntry = secrets.choice(entries)
    return HttpResponseRedirect(reverse("entry", kwargs={"entry": randomEntry}))