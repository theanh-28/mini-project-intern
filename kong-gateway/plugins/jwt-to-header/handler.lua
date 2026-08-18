local cjson = require "cjson.safe"
local jwt_decoder = require "kong.plugins.jwt.jwt_parser"

local JwtToHeaderHandler = {
  PRIORITY = 940, -- Runs after jwt-revocation (950) but before rate-limiting (901)
  VERSION = "1.0",
}

function JwtToHeaderHandler:access(conf)
  -- 1. Lấy token đã được xác thực từ context của Kong
  local token = kong.ctx.shared.authenticated_jwt_token

  if not token then
    -- Nếu không có token xác thực, xóa các header để phòng tránh giả mạo
    if conf.claims then
      for _, mapping in ipairs(conf.claims) do
        local _, header_name = mapping:match("%s*([^%s:]+)%s*:%s*([^%s:]+)%s*")
        if header_name then
          kong.service.request.clear_header(header_name)
        end
      end
    end
    return
  end

  -- 2. Lấy JWT đã giải mã từ context hoặc giải mã mới nếu chưa có
  local jwt = kong.ctx.shared.decoded_jwt
  local err
  if not jwt then
    jwt, err = jwt_decoder:new(token)
    if err or not jwt or not jwt.claims then
      kong.log.err("Lỗi giải mã JWT đã xác thực: ", err)
      if conf.claims then
        for _, mapping in ipairs(conf.claims) do
          local _, header_name = mapping:match("%s*([^%s:]+)%s*:%s*([^%s:]+)%s*")
          if header_name then
            kong.service.request.clear_header(header_name)
          end
        end
      end
      return
    end
    kong.ctx.shared.decoded_jwt = jwt
  end

  -- 3. Trích xuất claims và gán vào các headers tương ứng
  if conf.claims then
    for _, mapping in ipairs(conf.claims) do
      local claim_name, header_name = mapping:match("%s*([^%s:]+)%s*:%s*([^%s:]+)%s*")
      if claim_name and header_name then
        local value = jwt.claims[claim_name]
        if value ~= nil then
          local header_val
          if type(value) == "table" then
            header_val = cjson.encode(value)
          else
            header_val = tostring(value)
          end
          kong.service.request.set_header(header_name, header_val)
        else
          kong.service.request.clear_header(header_name)
        end
      end
    end
  end
end

return JwtToHeaderHandler
