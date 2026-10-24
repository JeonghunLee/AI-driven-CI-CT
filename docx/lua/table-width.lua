function Div(div)
  if not div.classes:includes("table-width") then
    return nil
  end

  local widths = {}
  for n in div.attributes.widths:gmatch("[^,]+") do
    table.insert(widths, tonumber(n))
  end

  for _, block in ipairs(div.content) do
    if block.t == "Table" and #block.colspecs == #widths then
      local total = 0
      for _, w in ipairs(widths) do
        total = total + w
      end

      for i, w in ipairs(widths) do
        block.colspecs[i][2] = w / total
      end
    end
  end

  return div
end