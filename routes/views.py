import json
import traceback
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import RouteForm
from buses.models import Route, Stop

# --- 1. LIST ROUTES (NOW CRASH PROOF) ---
def route_list(request):
    try:
        # Get all routes
        routes = Route.objects.all()
        return render(request, 'routes/route_list.html', {'routes': routes})
    except Exception as e:
        # If this page crashes, SHOW THE ERROR
        error_report = traceback.format_exc()
        return HttpResponse(f"""
            <div style='padding:20px; font-family:monospace;'>
                <h1 style='color:darkred;'>ROUTE LIST CRASHED</h1>
                <p>Send a screenshot of this error:</p>
                <hr>
                <pre style='background:#ffeeee; padding:15px; border:1px solid red;'>{error_report}</pre>
            </div>
        """)

# --- 2. ADD ROUTE ---
def add_route(request):
    try:
        if request.method == "POST":
            form = RouteForm(request.POST)
            
            if form.is_valid():
                route = form.save()
                
                # Save Stops
                stops_json = request.POST.get("stops_json", "[]")
                if not stops_json.strip(): stops_json = "[]"

                try:
                    stops = json.loads(stops_json)
                    for index, stop_data in enumerate(stops):
                        Stop.objects.create(
                            route=route,
                            name=stop_data.get("name", f"Stop {index+1}"),
                            latitude=stop_data.get("lat", 0.0),
                            longitude=stop_data.get("lng", 0.0),
                            sequence_number=index + 1
                        )
                except Exception:
                    pass # Ignore JSON errors for now

                return redirect("routes:route_list")
            else:
                return HttpResponse(f"Form Error: {form.errors}")
        else:
            form = RouteForm()

        return render(request, "routes/add_route.html", {"form": form})

    except Exception as e:
        error_report = traceback.format_exc()
        return HttpResponse(f"<pre>{error_report}</pre>")

# --- 3. ADD STOP API ---
@csrf_exempt
def add_stop_to_route(request):
    # (Keep your existing API code here if needed, or leave this placeholder)
    return JsonResponse({"status": "ok"})
# ... (keep your existing imports and functions)

# --- ADD THIS NEW FUNCTION AT THE BOTTOM ---
def delete_route(request, route_id):
    # Find the route or show 404 error
    route = get_object_or_404(Route, id=route_id)
    
    # Delete it
    route.delete()
    
    # Go back to the list
    return redirect('routes:route_list')
