from django.conf import settings
from django.db import models
from account.models import User
from problem.models import Problem


class Post(models.Model):

    POST_CATEGORIES = [
        ("FREE", "Free"),
        ("QUES", "Question"),
        ("PROM", "Promotion"),
        ("SUBJ", "Subject"),
        ("REQU", "Request"),
        ("UPDA", "Update")
    ]

    category = models.CharField(max_length=4, choices=POST_CATEGORIES, default="FREE")
    title = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
    body = models.TextField(default='')
    related_problem = models.ForeignKey(Problem, null=True, on_delete=models.SET_NULL)


class Comment(models.Model):
    parent_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
    body = models.TextField(default='')


class CommentComment(models.Model):
    parent_comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
    body = models.TextField(default='')
