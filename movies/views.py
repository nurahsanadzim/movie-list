from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import requests  # untuk fetch data api (berbeda dengan "request")
import json
from movies.models import UserMovieList


@login_required
def index(request):
    # cek post request, jika tidak ada, set ke 0 (Falsy value)
    post_add = request.POST.get('add', 0)

    # jika ada request post (penambahan data list movie user)
    if post_add : 
        # pisahkan data post [<movie id>, <ptw/w/d>]
        item = post_add.split(',')

        # tambahkan ke list user yang sesuai dengan status movie [[ptw], [w], [d]]
        query = UserMovieList.objects.get(user=request.user.id)
        user_list = json.loads(query.user_list)
        if item[1] == 'ptw':
            user_list[0].append(int(item[0]))
        elif item[1] == 'w':
            user_list[1].append(int(item[0]))
        elif item[1] == 'd':
            user_list[2].append(int(item[0]))

        # simpan ke db
        query.user_list = json.dumps(user_list)
        query.save()

    # ambil data trending today (GET)
    response = requests.get(
        'https://api.themoviedb.org/3/trending/movie/day?api_key=').json()
    # cek hasil fetch api
    movie_data = response['results'] if 'page' in response.keys() else 0

    query = UserMovieList.objects.get(user=request.user.id)
    user_list = json.loads(query.user_list)
    
    if movie_data:
        for movie in movie_data:
            # plan to watch
            if movie['id'] in user_list[0]:
                movie['status'] = 'ptw'
            # watched
            elif movie['id'] in user_list[1]:
                movie['status'] = 'w'
            # dropped
            elif movie['id'] in user_list[2]:
                movie['status'] = 'd'
            else:
                movie['status'] = 'not_yet'

    # render ke template
    return render(request, 'movies/index.html', {
        'movie_data': movie_data
    })


def user_list(request):

    # cek post request untuk edit
    post_edit = request.POST.get('edit', 0)
    if post_edit:
        # [<movie id>, <ptw/w/d>]
        item = post_edit.split(',')

    # cek post request untuk delete
    # post_delete berisi movie id yang akan dihapus
    post_delete = request.POST.get('delete', 0)

    if post_delete:

        query = UserMovieList.objects.get(user=request.user.id)
        user_list = json.loads(query.user_list)

    return render(request, 'movies/user_list.html', {
        'user_list': user_list
    })


# 'poster': 'https://image.tmdb.org/t/p/w200'+response['poster_path']