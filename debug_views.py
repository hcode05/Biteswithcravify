from django.shortcuts import render

def debug_paypal(request):
    return render(request, 'debug_paypal.html')
