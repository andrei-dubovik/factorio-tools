-- Load specific Factorio prototype files and convert them to json

data = {}

function data.extend(data, recipes)
  write(recipes, io.stdout)
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

factorio_root = arg[1]
recipe_lua = factorio_root .. "data/base/prototypes/recipe.lua"
dofile(recipe_lua)
