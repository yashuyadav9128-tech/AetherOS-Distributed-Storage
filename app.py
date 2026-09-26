from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

from cluster.web_dashboard import get_dashboard_html


app = FastAPI(title="AetherStore Dashboard")

VERCEL_PREVIEW_NOTICE = (
    '<div role="status" style="padding:12px 16px;margin:0 0 18px;'
    'border:1px solid #f59e0b;border-radius:8px;'
    'background:#422006;color:#fef3c7;font:14px sans-serif">'
    'Vercel preview: the coordinator and storage nodes are not running here. '
    'Live telemetry and cluster controls are unavailable in this deployment.'
    '</div>'
    '<script>document.querySelectorAll(".btn").forEach(button => {'
    'button.disabled = true; button.title = "Unavailable in the Vercel preview";'
    '});</script>'
)


@app.get("/", response_class=HTMLResponse)
def dashboard():
    html = get_dashboard_html()
    return html.replace("<body>", f"<body>{VERCEL_PREVIEW_NOTICE}", 1)


@app.get("/api/cluster/status")
def cluster_status():
    return {
        "summary": {
            "total_nodes": 0,
            "online_nodes": 0,
            "dead_nodes": 0,
            "total_objects": 0,
            "cluster_health": "UNAVAILABLE",
        },
        "nodes": {},
        "objects": {},
        "recent_events": [
            {
                "level": "WARN",
                "time": "Vercel",
                "message": "Preview only. Connect an always-on cluster host for live telemetry.",
            }
        ],
    }


@app.api_route(
    "/api/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
)
def unavailable_cluster_api(path: str):
    return JSONResponse(
        status_code=503,
        content={
            "error": "The storage cluster is not hosted on Vercel.",
            "detail": "Run the coordinator and storage nodes on an always-on host.",
        },
    )