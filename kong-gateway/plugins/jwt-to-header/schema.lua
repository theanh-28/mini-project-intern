local typedefs = require "kong.db.schema.typedefs"

return {
  name = "jwt-to-header",
  fields = {
    {
      config = {
        type = "record",
        fields = {
          {
            claims = {
              type = "array",
              elements = {
                type = "string",
              },
              default = { "sub:x-user-id" },
            }
          }
        },
      },
    },
  },
}
