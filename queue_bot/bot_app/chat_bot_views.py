from pprint import pprint
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET", "POST"])
def test_view(request):
    if request.method == "POST":
        return Response({"post": 200})
    return Response({"get": 200})
