from django.shortcuts import render

def point_list(request):
    return render(request, 'point/point_list.html')
