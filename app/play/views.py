from django import template
from django.views.generic.base import RedirectView
from play.models import OptionForm, Option, Play
from json.encoder import JSONEncoder
from django.http.response import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.http import HttpResponse
from django.template import context, loader
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

class OptionView(TemplateView, RedirectView):
    template_name = 'option.html'

    def get(self, req, *args, **kwargs):

        print(req)
        template = loader.get_template(self.template_name)
        context = {'test':1}
        return HttpResponse(template.render(context, req))
    
    def post(self, req, *args,**kwargs):
        print('option recived')
        print(req.POST)
        print(req.FILES)

        if req.POST['upload'] == 'upload':
            play_option = Option(mode = req.POST['mode'], upload=req.POST['upload'], songs=req.POST['songs'], video=req.FILES['video'])
            # play_option.save()
        # form = OptionForm(req.POST)
        # if form.is_valid() :
        #     form.save()
        pid = 'qwre1234'
        # return JsonResponse({
        #     'result': 200,
        #     }, json_dumps_params={'ensure_ascii': True})
        # return redirect('play')

        # post 받고 play 설정정보 response로 넘겨주기
        # response로 redirect가 안돼서 client에서 처리 
        res = HttpResponse(status=307)
        res['Location'] = f'/play/?pid={pid}'
        return res


class PlayView(TemplateView):
    template_name = 'play.html'
    
    def get(self, req, *args, **kwargs):
        # request에서 play 정보 parameter 정보 꼭 받기
        # 안받으면 main 이나 option 으로 render 하기(혹은 error 처리페이지로)
        
        print('play')
        print(req.GET)
        
        # print(req.GET.get('pid', None))
        # print(req.GET['pid'])
        template = loader.get_template(self.template_name)
        context = {
            'pid' : req.GET['pid'],
            'title' : 'Secret Garden',
            'artist' : 'OH MY GIRL',
            'video_url' : '/static/target_videos/secretgarden1-3.mp4',
        }
        # return HttpResponse(template.render(context, req))
        return render(req, self.template_name, context)

    def post(self, req, *args, **kwargs):
        print(req)
        print('video recived')
        print(req.POST)
        print(req.FILES)

        play_data = Play(datetime = req.POST['datetime'], video=req.FILES['video'])
        play_data.save()
        return JsonResponse({
            'result': 200,
            }, json_dumps_params={'ensure_ascii': True})