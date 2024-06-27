from ..models import Post, Comment, CommentComment
from problem.models import Problem
from ..serializers import SimplePostSerializer, CommentSerializer, CommentCommentSerializer, DetailPostSerializer
from utils.api import APIView
from django.db.models import Q
from django.utils.decorators import method_decorator
from account.decorators import login_required
import json
from django.http import HttpResponseBadRequest, HttpResponseNotFound


class PostAPI(APIView):
    def get(self, request):
        post_id = request.GET.get("post_id")
        if post_id:
            try:
                post = Post.objects.get(id=post_id)
                post_data = SimplePostSerializer(post).data
                return self.success(post_data)
            except Post.DoesNotExist:
                return self.error("Post does not exist")

        try:
            posts = Post.objects.all()
        except Post.DoesNotExist:
            return self.error("Post does not exist")

        category = request.GET.get("category")
        related_problem_id = request.GET.get("related_problem")
        keyword = request.GET.get("keyword", "").strip()

        if category:
            if category not in list(zip(*Post.POST_CATEGORIES))[0]:
                return self.error("invalid category")
            posts = posts.filter(category=category)

        if related_problem_id:
            posts = posts.filter(related_problem__id=related_problem_id)

        if keyword:
            posts = posts.filter(Q(title__icontains=keyword) | Q(id__icontains=keyword) |
                                 Q(author__username__icontains=keyword))

        data = self.paginate_data(request, posts, SimplePostSerializer)
        return self.success(data)

    @login_required
    def post(self, request):
        data = request.data

        if data["category"] not in list(zip(*Post.POST_CATEGORIES))[0]:
            return self.error("invalid category")

        data["author"] = request.user

        related_problem_id = data.get("related_problem_id", None)
        if related_problem_id:
            data["related_problem"] = Problem.objects.get(id=related_problem_id)

        Post.objects.create(**data)

        return self.success("Post created")

    @login_required
    def delete(self, request):
        try:
            post_id = json.loads(request.body)["post_id"]
        except KeyError:
            return self.error("put post_id on request's body")

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return self.error("post doesn't exist")

        if not request.user.is_admin_role() and request.user.id != post.author.id:
            return self.error("only author or admin can delete post")

        post.delete()
        return self.success()

    @login_required
    def put(self, request):
        data = request.data
        post_id = data.pop("post_id")

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return self.error("Post does not exist")

        if not request.user.is_admin_role() and request.user.id != post.author.id:
            return self.error("only author or admin can update post")

        for k, v in data.items():
            setattr(post, k, v)
        post.save()
        return self.success("update complete")


class DetailPostAPI(APIView):
    def get(self, request):
        post_id = request.GET.get("post_id")
        if not post_id:
            return HttpResponseBadRequest("no post_id in query string")

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return HttpResponseNotFound("no post that have input post_id")

        post_data = DetailPostSerializer(post).data
        return self.success(post_data)
