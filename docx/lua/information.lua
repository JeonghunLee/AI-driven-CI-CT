local function read_file(path)
    local file = io.open(path, "r")

    if not file then
        return nil
    end

    local content = file:read("*all")
    file:close()

    return content
end


local function cell(blocks)
    return pandoc.Cell(
        pandoc.Blocks(blocks)
    )
end


function Div(div)
    if not div.classes:includes("information") then
        return nil
    end

    local title  = div.attributes["title"] or "Information"
    local source = div.attributes["source"]

    local content_blocks = div.content

    if source then
        local data = read_file(source)

        if data then
            content_blocks = {
                pandoc.CodeBlock(data)
            }
        else
            content_blocks = {
                pandoc.Para({
                    pandoc.Str("Unable to read file: " .. source)
                })
            }
        end
    end

    local rows = {
        pandoc.Row({
            cell({
                pandoc.Para({
                    pandoc.Strong({
                        pandoc.Str(title)
                    })
                })
            })
        }),

        pandoc.Row({
            cell(content_blocks)
        })
    }

    local body = pandoc.TableBody(
        rows,
        {},
        0,
        {}
    )

    return pandoc.Table(
        pandoc.Caption(),
        {
            { pandoc.AlignLeft, 1.0 }
        },
        pandoc.TableHead({}),
        { body },
        pandoc.TableFoot({})
    )
end