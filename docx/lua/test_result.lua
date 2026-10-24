local function text_cell(text)
    return pandoc.Cell(
        pandoc.Blocks({
            pandoc.Para({
                pandoc.Str(tostring(text or ""))
            })
        })
    )
end


local function make_row(label, value)
    return pandoc.Row({
        text_cell(label),
        text_cell(value)
    })
end


local function read_json(path)
    local file, err = io.open(path, "r")

    if not file then
        error(
            string.format(
                "Cannot open test result JSON: %s (%s)",
                path,
                err or "unknown error"
            )
        )
    end

    local content = file:read("*all")
    file:close()

    return pandoc.json.decode(content)
end


local function create_test_result_table(data)
    local rows = {
        make_row("Test ID", data.test_id),
        make_row("Result", data.result),
        make_row("Execution ID", data.execution_id),
        make_row("Timestamp", data.timestamp),
        make_row("Runner", data.runner),
        make_row("Duration", (data.duration_ms or "") .. " ms")
    }

    if data.details then
        table.insert(
            rows,
            make_row("Interface", data.details.interface)
        )

        table.insert(
            rows,
            make_row("Equipment", data.details.equipment)
        )

        table.insert(
            rows,
            make_row("Fixture Mode", data.details.fixture_mode)
        )
    end

    local body = pandoc.TableBody(
        rows,
        {},
        0,
        {}
    )

    local colspecs = {
        { pandoc.AlignLeft, 0.30 },
        { pandoc.AlignLeft, 0.70 }
    }

    return pandoc.Table(
        pandoc.Caption(),
        colspecs,
        pandoc.TableHead({}),
        { body },
        pandoc.TableFoot({})
    )
end


function Div(div)
    if not div.classes:includes("test-result") then
        return nil
    end

    local source = div.attributes["source"]

    if not source or source == "" then
        error(
            "test-result requires source attribute"
        )
    end

    local data = read_json(source)

    return create_test_result_table(data)
end