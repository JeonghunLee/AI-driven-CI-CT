local signature_config = {
    name = "",
    title = "",
    date = "",
    image = nil
}


local function stringify(value)
    if value == nil then
        return nil
    end

    return pandoc.utils.stringify(value)
end


local function text_cell(text)
    return pandoc.Cell(
        pandoc.Blocks({
            pandoc.Para({
                pandoc.Str(text or "")
            })
        })
    )
end


local function image_cell(path)
    if not path or path == "" then
        return text_cell("")
    end

    local image = pandoc.Image(
        {},
        path,
        "Signature",
        pandoc.Attr("", {}, {
            { "width", "35mm" }
        })
    )

    return pandoc.Cell(
        pandoc.Blocks({
            pandoc.Para({ image })
        })
    )
end


local function make_row(label, value_cell)
    return pandoc.Row({
        text_cell(label),
        value_cell
    })
end


local function get_value(div, key)
    local value = div.attributes[key]

    -- Markdown Div attribute가 있으면 우선
    if value ~= nil and value ~= "" then
        return value
    end

    -- 없으면 metadata
    return signature_config[key]
end


local function process_div(div)
    if not div.classes:includes("signature") then
        return nil
    end

    local name  = get_value(div, "name")  or ""
    local title = get_value(div, "title") or ""
    local date  = get_value(div, "date")  or ""
    local image = get_value(div, "image")

    local rows = {
        make_row("Name",      text_cell(name)),
        make_row("Title",     text_cell(title)),
        make_row("Signature", image_cell(image)),
        make_row("Date",      text_cell(date))
    }

    local body = pandoc.TableBody(
        rows,
        {},
        0,
        {}
    )

    local colspecs = {
        { pandoc.AlignLeft, 0.25 },
        { pandoc.AlignLeft, 0.75 }
    }

    return pandoc.Table(
        pandoc.Caption(),
        colspecs,
        pandoc.TableHead({}),
        { body },
        pandoc.TableFoot({})
    )
end


function Pandoc(doc)

    -- 1. metadata 먼저 읽기
    if doc.meta.signature then
        local sig = doc.meta.signature

        signature_config.name  = stringify(sig.name)  or ""
        signature_config.title = stringify(sig.title) or ""
        signature_config.date  = stringify(sig.date)  or ""
        signature_config.image = stringify(sig.image)
    end

    -- 2. metadata를 읽은 뒤 Div 처리
    doc.blocks = doc.blocks:walk({
        Div = process_div
    })

    return doc
end