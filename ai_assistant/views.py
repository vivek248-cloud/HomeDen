import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .conversation import get_response


@csrf_exempt
def chat(request):

    if request.method != "POST":
        return JsonResponse(
            {"success": False, "error": "Only POST requests are allowed."},
            status=405
        )

    # -----------------------------
    # Parse JSON
    # -----------------------------
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Invalid JSON."},
            status=400
        )

    # -----------------------------
    # Validate message
    # -----------------------------
    user_message = data.get("message", "").strip()

    if not user_message:
        return JsonResponse(
            {"success": False, "error": "Message is required."},
            status=400
        )

    # -----------------------------
    # Conversation Session
    # -----------------------------
    conversation = request.session.setdefault("conversation", {})

    try:

        result = get_response(conversation, user_message)

        request.session["conversation"] = conversation
        request.session.modified = True

        return JsonResponse({
            "success": True,
            **result
        })

    except Exception as e:

        print("=" * 80)
        print("AI Conversation Error")
        print(e)
        print("=" * 80)

        return JsonResponse(
            {
                "success": False,
                "reply": (
                    "Sorry, something went wrong. "
                    "Please try again."
                )
            },
            status=500
        )


@csrf_exempt
def reset_chat(request):

    if request.method != "POST":
        return JsonResponse(
            {"success": False, "error": "Only POST requests are allowed."},
            status=405
        )

    request.session.pop("conversation", None)
    request.session.modified = True

    return JsonResponse({
        "success": True,
        "message": "Conversation reset successfully."
    })