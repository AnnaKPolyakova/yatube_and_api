from django.conf import settings
from django.conf.urls import handler404, handler500
from django.conf.urls.static import static
from django.contrib.flatpages import views
from django.urls import include, path
from django.views.generic import TemplateView

from posts import views as posts_views

handler404 = "posts.views.page_not_found"  # noqa
handler500 = "posts.views.server_error"  # noqa

urlpatterns = [
    path('about/',
         include('django.contrib.flatpages.urls')),
    path('about-us/',
         views.flatpage, {'url': '/about-us/'},
         name='about_us'),
    path('terms/',
         views.flatpage,
         {'url': '/terms/'},
         name='terms'),
    path('about-author/',
         views.flatpage,
         {'url': '/about-author/'},
         name='about-author'),
    path('about-spec/',
         views.flatpage,
         {'url': '/about-spec/'},
         name='about-spec'),
    path('auth/',
         include('users.urls')),
    path('auth/',
         include('django.contrib.auth.urls')),
    path('api/', include('api.urls')),
    path('redoc/', TemplateView.as_view(
        template_name='redoc.html'),
         name='redoc'
         ),
    path('',
         include('posts.urls')),
    path('404/',
         posts_views.page_not_found,
         name='Error_404'),
    path('500/',
         posts_views.server_error,
         name='Error_500'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    import debug_toolbar
    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)
