from django.urls import path
from django.views.generic import RedirectView


from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("addcomment", views.addcomment, name="addcomment"),
    path("addbid", views.addbid, name="addbid"),
    path("addcategory", views.addcategory, name="addcategory"),
    path("closebid", views.closebid, name="closebid"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("category", views.category, name="category"),
    path(r"category/<str:category_type>/list", views.category, name="category"),
    path("listall", views.listall, name="listall"),
    path(r"listing/<uuid:id>", views.listing, name="listing"),

]
