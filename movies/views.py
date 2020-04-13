from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import requests # untuk fetch data api (berbeda dengan "request")
import json
from movies.models import UserMovieList

@login_required
def index(request):
    # ambil data trending today (GET)
    response = requests.get('https://api.themoviedb.org/3/trending/movie/day?api_key=').json()

    # cek hasil fetch api
    movie_data = response['results'] if 'page' in response.keys() else 0
    # query = UserMovieList.objects.get(user=request.user.id)

    return render(request, 'movies/index.html', {
        'movie_data': movie_data
    })


def user_list(request):
    # cek post request
    post_data = request.POST.get('query', 0)

    if(post_data):
        # pisahkan data post [<id movie>, <tombol yang ditekan>]
        item = post_data.split(',')

    user_list = UserMovieList.objects.get(user=request.user.id)
    return render(request, 'movies/user_list.html')


# 'poster': 'https://image.tmdb.org/t/p/w200'+response['poster_path']