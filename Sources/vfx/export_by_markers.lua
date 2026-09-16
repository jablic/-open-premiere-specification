-- DaVinci Resolve Script: Export by Markers
-- Автоматический пакетный экспорт клипов по маркерам

local resolve = Resolve()
local pm = resolve:GetProjectManager()
local project = pm:GetCurrentProject()

if not project then
    print("Ошибка: проект не открыт")
    return
end

local timeline = project:GetCurrentTimeline()

if not timeline then
    print("Ошибка: нет активного таймлайна")
    return
end

local markers = timeline:GetMarkers()

if not markers or next(markers) == nil then
    print("Ошибка: маркеры не найдены")
    return
end

-- Папка для экспорта
local output_path = os.getenv("HOME") .. "/Desktop/Export"

-- Создание директории
os.execute("mkdir -p '" .. output_path .. "'")

-- Получение FPS
local fps = tonumber(timeline:GetSetting("timelineFrameRate"))

local marker_count = 0

for frame_id, marker in pairs(markers) do
    local name = marker["name"]

    if name and name ~= "" then
        name = name:match("^%s*(.-)%s*$") -- trim

        if name ~= "" then
            local duration = marker["duration"] or 1
            local start_frame = frame_id
            local end_frame = frame_id + duration - 1

            print(string.format("Добавляю: '%s' (фреймы %d → %d)", name, start_frame, end_frame))

            -- Установка параметров рендера
            project:SetRenderSettings({
                SelectAllFrames = false,
                MarkIn = start_frame,
                MarkOut = end_frame,
                CustomName = name,
                TargetDir = output_path,
            })

            -- Добавление задачи рендера
            project:AddRenderJob()
            marker_count = marker_count + 1
        end
    end
end

if marker_count > 0 then
    print(string.format("\nДобавлено задач: %d", marker_count))
    print("Запуск рендера...")
    project:StartRendering()
    print("Готово!")
else
    print("Ошибка: не найдены маркеры с названиями")
end
