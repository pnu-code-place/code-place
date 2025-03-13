from utils.api import APIView


class JudgeServerAPI(APIView):

    def post(self, request):
        exec("print(hello)")

    def delete(self, request):
        pass
