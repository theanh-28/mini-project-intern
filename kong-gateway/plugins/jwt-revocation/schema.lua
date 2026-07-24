local typedefs = require "kong.db.schema.typedefs" -- Import các kiểu dữ liệu chuẩn của Kong

return {
  name = "jwt-revocation", -- Tên của plugin
  fields = {
    {
      config = {
        type = "record",
        fields = {
          { redis_host = { type = "string", default = "redis" } },         
          { redis_port = { type = "integer", default = 6379 } },         
          { redis_db = { type = "integer", default = 0 } },            
          { redis_timeout = { type = "integer", default = 1000 } },      
          { blacklist_prefix = { type = "string", default = "blacklist:" } }, -- Prefix key cho token bị thu hồi
          { account_lock_prefix = { type = "string", default = "user:lock_at:" } }, -- Prefix key cho tài khoản bị khóa
        },
      },
    },
  },
}
