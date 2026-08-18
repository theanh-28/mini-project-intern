local redis = require "resty.redis"
local jwt_decoder = require "kong.plugins.jwt.jwt_parser" -- Import lại bộ giải mã JWT của Kong

local TokenRevocationHandler = {
  -- Độ ưu tiên chạy: 950 (Chạy sau bước xác thực JWT mặc định là 1450)
  PRIORITY = 950,
  VERSION = "1.0",
}

function TokenRevocationHandler:access(conf)
  -- 1. Lấy token đã được xác thực trực tiếp từ context của Kong
  local token = kong.ctx.shared.authenticated_jwt_token
  if not token then
    -- Nếu không có token (chưa qua xác thực hoặc request công khai), bỏ qua
    return
  end

  -- 2. Giải mã JWT để lấy jti (ID token) và sub (User ID)
  local jwt = kong.ctx.shared.decoded_jwt
  local err
  if not jwt then
    jwt, err = jwt_decoder:new(token)
    if err or not jwt then
      return kong.response.exit(401, { message = "Cấu trúc token không hợp lệ" })
    end
    kong.ctx.shared.decoded_jwt = jwt
  end

  local jti = jwt.claims and jwt.claims.jti
  local user_id = jwt.claims and jwt.claims.sub
  if not jti or not user_id then
    return kong.response.exit(401, { message = "Token thiếu trường 'jti' hoặc thông tin người dùng" })
  end

  -- 3. Kết nối tới cơ sở dữ liệu Redis
  local red = redis:new()
  red:set_timeout(conf.redis_timeout)
  local ok, err = red:connect(conf.redis_host, conf.redis_port)
  if not ok then
    kong.log.err("Lỗi kết nối tới Redis: ", err)
    return -- Fail-Open: Redis sập thì cho qua để backend tự xử lý, tránh sập cả hệ thống
  end

  -- Chọn đúng Database Redis
  local ok, err = red:select(conf.redis_db)
  if not ok then
    kong.log.err("Lỗi chọn Database Redis: ", err)
    return -- Fail-Open
  end

  -- 4. Kiểm tra Key blacklist:<jti> có tồn tại không (Token đã đăng xuất)
  local blacklist_key = conf.blacklist_prefix .. jti
  local exists_blacklist, err = red:exists(blacklist_key)
  if err then
    kong.log.err("Lỗi kiểm tra blacklist key trong Redis: ", err)
    red:set_keepalive(10000, 100) -- Trả kết nối về pool trước khi return
    return -- Fail-Open
  end

  if exists_blacklist == 1 then
    red:set_keepalive(10000, 100)
    return kong.response.exit(401, { message = "Token đã bị thu hồi do đăng xuất" })
  end

  -- 5. Kiểm tra Key user:revoke_at:<user_id> (Phiên bị thu hồi do đổi mật khẩu / khóa tài khoản)
  local account_lock_key = conf.account_lock_prefix .. user_id
  local revoked_at, err = red:get(account_lock_key)
  if err then
    kong.log.err("Lỗi kiểm tra revocation key trong Redis: ", err)
    red:set_keepalive(10000, 100)
    return -- Fail-Open
  end
  
  -- Trả kết nối Redis về pool để tối ưu hiệu năng
  red:set_keepalive(10000, 100)

  -- 6. So sánh thời điểm phát hành token (iat) với thời điểm thu hồi (revoked_at)
  if revoked_at and revoked_at ~= ngx.null then
    local token_iat = jwt.claims and jwt.claims.iat
    if token_iat and tonumber(token_iat) < tonumber(revoked_at) then
      return kong.response.exit(401, { message = "Phiên đăng nhập đã bị thu hồi hoặc hết hạn" })
    end
  end
end

return TokenRevocationHandler
