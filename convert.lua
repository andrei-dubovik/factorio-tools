-- Load specific Factorio prototype files and convert them to json


-- Dump an object to a .json file
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
    local k = nil
    for i, _ in ipairs(obj) do k = i end
    if k then
      -- vector
      local sep = ""
      file:write("[")
      for _, v in ipairs(obj) do
        file:write(sep)
        write(v, file)
        sep = ","
      end
      file:write("]")
    else
      -- map
      local sep = ""
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


-- Load recipes
function load_recipes(path)
  local _recipes = {}
  local env = {data = {}}
  setmetatable(env, {__index = _G})

  function env.data.extend(data, recipes)
    _recipes = recipes
  end

  loadfile(path, nil, env)()
  return _recipes
end


-- Load a list of technologies eligible for productivity modules
function load_intermediate(path)
  local env = {data = {}}
  setmetatable(env, {__index = _G})

  function env.require(path)
    return {}
  end

  function env.data.extend(data, items)
  end

  loadfile(path, nil, env)()
  return env.productivity_module_limitation()
end

function require(path)
  return {}
end


-- Specify paths, load data, dump as json
function main()
  factorio_root = arg[1]
  recipe_lua = factorio_root .. "data/base/prototypes/recipe.lua"
  item_lua = factorio_root .. "data/base/prototypes/item.lua"

  json = {
    recipes = load_recipes(recipe_lua),
    intermediate = load_intermediate(item_lua),
  }
  write(json, io.stdout)
end

main()
