data = {}

function data.extend(data, recipes)
  dump(recipes, "recipes.json")
end

function dump(obj, path)
  file = io.open(path, "w")
  write(obj, file)
  file:close()
end

function write(obj, file)
  if type(obj) == "boolean" then
    if obj then
      file:write "true"
    else
      file:write "false"
    end
  elseif type(obj) == "number" then
    file:write(obj)
  elseif type(obj) == "string" then
    file:write(string.format("%q", obj))
  elseif type(obj) == "table" then
    k = nil
    for i, _ in ipairs(obj) do k = i end
    if k then
      -- vector
      sep = ""
      file:write("[")
      for _, v in ipairs(obj) do
        file:write(sep)
        write(v, file)
        sep = ","
      end
      file:write("]")
    else
      -- map
      sep = ""
      file:write("{")
      for k, v in pairs(obj) do
        file:write(sep)
        write(k, file)
        file:write(":")
        write(v, file)
        sep = ","
      end
      file:write("}")
    end
  end
end

dofile "recipe.lua"
