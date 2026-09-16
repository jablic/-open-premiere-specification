# -*- coding: utf-8 -*-
import sys
import os

# Раскомментировано для macOS:
sys.path.insert(0, "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules")

import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
project = pm.GetCurrentProject()
timeline = project.GetCurrentTimeline()

if not timeline:
    print("Нет активного таймлайна!")
    sys.exit(1)

markers = timeline.GetMarkers()

if not markers:
    print("Маркеры не найдены!")
    sys.exit(1)

# Папка для экспорта — измените под себя
output_path = os.path.expanduser("~/Desktop/Export")
os.makedirs(output_path, exist_ok=True)

fps = float(timeline.GetSetting("timelineFrameRate"))

for frame_id, marker in markers.items():
    name = marker.get("name").strip()
    duration = marker.get("duration", 1)

    if not name:
        print(f"  Пропущен маркер на фрейме {frame_id} — нет имени")
        continue

    start = frame_id
    end = frame_id + duration - 1

    print(f"Добавляю: '{name}' ({start} → {end})")

    project.SetRenderSettings({
        "SelectAllFrames": False,
        "MarkIn": start,
        "MarkOut": end,
        "CustomName": name,
        "TargetDir": output_path,
    })

    project.AddRenderJob()

print(f"\nДобавлено задач: {len(markers)}. Запускаю рендер...")
project.StartRendering()
print("Готово!")