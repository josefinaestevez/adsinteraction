from django.shortcuts import render

# Create your views here.

def generate_refresh_token(request):
  return render(request, 'generate_refresh_token.html')