from django.db import models


class Candidate(models.Model):

    class ReviewStatus(models.TextChoices):
        NEW = "new", "New"
        SHORTLISTED = "shortlisted", "Shortlisted"
        REJECTED = "rejected", "Rejected"

    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    position_applied = models.CharField(max_length=100)

    skills = models.JSONField(default=list, blank=True)

    experience_years = models.PositiveIntegerField(default=0)
    education = models.CharField(max_length=200, blank=True)
    cv_text = models.TextField(blank=True)

    match_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    review_status = models.CharField(
        max_length=20, choices=ReviewStatus.choices, default=ReviewStatus.NEW
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

    class Meta:
        ordering = ["-created_at"]
