from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import requests  # untuk fetch data api (berbeda dengan objek "request")
import json
from movies.models import UserMovieList
key = ''


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
        # cegah submit POST berulang
        return HttpResponseRedirect(reverse('movies:index'))

    # ambil data trending today (GET)
    response = requests.get('https://api.themoviedb.org/3/trending/movie/day?api_key=' + key).json()
    # cek hasil fetch api
    movie_data = response['results'] if 'page' in response.keys() else 0
    # ambil data user yang sedang login
    query = UserMovieList.objects.get(user=request.user.id)
    user_list = json.loads(query.user_list)
    # beli label ke data yang telah tersimpan di list
    if movie_data:
        for movie in movie_data:
            # plan to watch
            if movie['id'] in user_list[0]:
                movie['status'] = 'Planned'
            # watched
            elif movie['id'] in user_list[1]:
                movie['status'] = 'Watched'
            # dropped
            elif movie['id'] in user_list[2]:
                movie['status'] = 'Dropped'
            else:
                movie['status'] = 'not_yet'
    # render ke template
    return render(request, 'movies/index.html', {
        'movie_data': movie_data
    })

@login_required
def user_list(request):
    # cek POST request untuk edit
    post_edit = request.POST.get('edit', 0)
    if post_edit:
        # [<movie id>, status lama, status baru]
        # [<movie id>, <0/1/2>, <0/1/2>] <ptw/w/d>
        item = post_edit.split(',')
        query = UserMovieList.objects.get(user=request.user.id)
        user_list = json.loads(query.user_list)
        # hapus dari status sebelumnya
        user_list[int(item[1])].remove(int(item[0]))
        # tambahkan ke status yang baru
        user_list[int(item[2])].append(int(item[0]))
        query.user_list = json.dumps(user_list)
        query.save()
        return HttpResponseRedirect(reverse('movies:user_list'))

    # cek POST request untuk delete
    post_delete = request.POST.get('delete', 0)
    if post_delete:
        # [<movie id>, <0/1/2>] <ptw/w/d>
        item = post_delete.split(',')
        query = UserMovieList.objects.get(user=request.user.id)
        user_list = json.loads(query.user_list)
        # hapus data dari status
        user_list[int(item[1])].remove(int(item[0]))
        query.user_list = json.dumps(user_list)
        query.save()
        return HttpResponseRedirect(reverse('movies:user_list'))

    # load data user
    query = UserMovieList.objects.get(user=request.user.id)
    user_list = json.loads(query.user_list)

    # loop request data API menggunakan id yang disimpan di db
    api_data = [[], [], []]
    for i, status in enumerate(user_list):
        for movie_id in status:
            response = requests.get('https://api.themoviedb.org/3/movie/'+ str(movie_id) +'?api_key=' + key).json()
            api_data[i].append(response)

    return render(request, 'movies/user_list.html', {
        'user_list': api_data
    })



# <img src="https://image.tmdb.org/t/p/w200{{ movie.poster_path }}">