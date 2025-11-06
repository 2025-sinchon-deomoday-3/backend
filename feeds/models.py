from django.conf import settings
from django.db import models

class FeedScrap(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="scraps")
    snapshot = models.ForeignKey("summaries.SummarySnapshot", on_delete=models.CASCADE, related_name="scrapped_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "snapshot")

    def __str__(self):
        return f"{self.user} → 스크랩 {self.snapshot.id}"


class FeedFavorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites")
    snapshot = models.ForeignKey("summaries.SummarySnapshot", on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "snapshot")

    def __str__(self):
        return f"{self.user} → 좋아요 {self.snapshot.id}"
