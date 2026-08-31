"""
数据导入 API
"""
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import StreamingResponse
import json
import time
import uuid
import threading

router = APIRouter()

# 存储导入任务状态
import_tasks = {}


def run_import_task(task_id: str):
    """后台运行导入任务"""
    from scrapers.dongchedi_importer import DongchediImporter

    importer = DongchediImporter()

    def progress_callback(status, progress, message):
        import_tasks[task_id] = {
            "status": status,
            "progress": progress,
            "message": message,
            "updated_at": time.time(),
        }

    importer.set_progress_callback(progress_callback)
    result = importer.run_import()

    import_tasks[task_id]["result"] = result
    import_tasks[task_id]["status"] = result.get("status", "error")
    import_tasks[task_id]["progress"] = 100 if result["status"] == "ok" else 0


@router.post("/dongchedi")
def start_import(background_tasks: BackgroundTasks):
    """启动懂车帝数据导入"""
    task_id = str(uuid.uuid4())[:8]
    import_tasks[task_id] = {
        "status": "starting",
        "progress": 0,
        "message": "正在启动...",
        "updated_at": time.time(),
    }

    # 在后台线程中运行（因为 Playwright 是同步的）
    thread = threading.Thread(target=run_import_task, args=(task_id,), daemon=True)
    thread.start()

    return {"task_id": task_id, "message": "导入任务已启动"}


@router.get("/status/{task_id}")
def get_import_status(task_id: str):
    """获取导入任务状态"""
    if task_id not in import_tasks:
        return {"error": "任务不存在"}
    return import_tasks[task_id]


@router.get("/stream/{task_id}")
def stream_import_progress(task_id: str):
    """SSE 流式推送导入进度"""
    def event_generator():
        last_progress = -1
        timeout = 600  # 最长 10 分钟
        start = time.time()

        while time.time() - start < timeout:
            if task_id not in import_tasks:
                yield f"data: {json.dumps({'error': '任务不存在'})}\n\n"
                break

            task = import_tasks[task_id]
            current_progress = task.get("progress", 0)

            if current_progress != last_progress:
                yield f"data: {json.dumps(task)}\n\n"
                last_progress = current_progress

            if task.get("status") in ("done", "error"):
                break

            time.sleep(1)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/history")
def get_import_history():
    """获取导入历史"""
    history = []
    for task_id, task in import_tasks.items():
        history.append({
            "task_id": task_id,
            "status": task.get("status"),
            "progress": task.get("progress"),
            "message": task.get("message"),
            "result": task.get("result"),
        })
    return history
