from django.urls import path
from .views import *

app_name = 'feeds'

urlpatterns = [
    path("", FeedListView.as_view(), name="feed_list"),
    path("<int:feed_id>/", FeedDetailView.as_view(), name="feed_detail"),
    path("<int:snapshot_id>/favorites/", FeedFavoriteView.as_view(), name="favorite"),
    path("<int:snapshot_id>/scrap/", FeedScrapView.as_view(), name="scrap"),
    path("scraps/", MyScrapListView.as_view(), name="my_scraps"),
    path("stats/", MyFeedStatsView.as_view(), name="my_feed_stats"),
]