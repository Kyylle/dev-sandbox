from django.shortcuts import render

def coming_soon(request, module):
    return render(request, 'coming_soon.html', {'module': module})

def error_404(request, exception):
    return render(request, '404.html', status=404)