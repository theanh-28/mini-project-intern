import { http, HttpResponse } from 'msw';

// Tạo một payload giả 
const payload = {
  "sub": 0,
  "roles": ["admin"],
  "exp": 9257888000,
};
const mockPayload = btoa(JSON.stringify(payload));
const mockHeader = btoa(JSON.stringify({ alg: "HS256", typ: "JWT" }));
const mockSignature = "mock_signature";

// Ghép thành token hợp lệ về mặt cấu trúc
const devToken = `${mockHeader}.${mockPayload}.${mockSignature}`;

// tạo dữ liệu user mẫu ban đầu
let users = Array.from({ length: 200 }, (_, i) => {
  const id = i + 1;
  return {
    user_id: id,
    name: `User${id}`,
    email: `user${id}@example.com`,
    is_active: i % 7 === 0 ? false : true,
    roles: i % 5 === 0 ? ['admin'] : ['user'],
    created_at: new Date(Date.now() - i * 86400000).toISOString(),
    last_login: i % 5 === 0 ? null : new Date(Date.now() - (i - 1) * 86400000).toISOString()
  };
});

// Đồng bộ URL với api.js
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const handlers = [
  // POST /auth/login
  http.post(`${API_URL}/auth/login`, async ({ request }) => {
    const body = await request.json();
    if (
      body.email === 'admin@example.com' &&
      body.password === '123456'
    ) {
      return HttpResponse.json({
        access_token: devToken,
        user: {
          user_id: 0,
          email: 'admin@example.com',
          name: 'Admin Mock',
          roles: ['admin'],
          permissions: ['users:read', 'users:create', 'users:update', 'users:delete']
        }
      });
    }
    return new HttpResponse(null, { status: 401 });
  }),

  // POST /auth/logout
  http.post(`${API_URL}/auth/logout`, async () => {
    return new HttpResponse(null, { status: 200 });
  }),

  // GET /admin/users (Lấy danh sách user kèm phân trang + tìm kiếm + lọc)
  http.get(`${API_URL}/admin/users`, async ({ request }) => {
    const url = new URL(request.url);
    const page = parseInt(url.searchParams.get('page') || '1', 10);
    const perPage = parseInt(url.searchParams.get('per_page') || '20', 10);
    const search = (url.searchParams.get('search') || '').trim().toLowerCase();

    const rawIsActive = url.searchParams.get('is_active');
    const role = url.searchParams.get('role') || '';
    const startDate = url.searchParams.get('created_at_from') || url.searchParams.get('start_date') || '';
    const endDate = url.searchParams.get('created_at_to') || url.searchParams.get('end_date') || '';

    let filteredUsers = [...users];

    // Tìm kiếm theo name hoặc email
    if (search) {
      filteredUsers = filteredUsers.filter(
        (u) =>
          u.name.toLowerCase().includes(search) ||
          u.email.toLowerCase().includes(search)
      );
    }

    // Lọc theo is_active
    if (rawIsActive === 'true' || rawIsActive === true) {
      filteredUsers = filteredUsers.filter((u) => u.is_active === true);
    } else if (rawIsActive === 'false' || rawIsActive === false) {
      filteredUsers = filteredUsers.filter((u) => u.is_active === false);
    }

    // Lọc theo Role (admin / user)
    if (role) {
      filteredUsers = filteredUsers.filter((u) => u.roles?.includes(role));
    }

    // Lọc theo khoảng ngày (Created At)
    if (startDate) {
      const start = new Date(startDate);
      filteredUsers = filteredUsers.filter((u) => new Date(u.created_at) >= start);
    }
    if (endDate) {
      const end = new Date(`${endDate}T23:59:59`);
      filteredUsers = filteredUsers.filter((u) => new Date(u.created_at) <= end);
    }

    // Tính toán phân trang
    const total = filteredUsers.length;
    const totalPages = Math.ceil(total / perPage) || 1;
    const startIndex = (page - 1) * perPage;
    const endIndex = startIndex + perPage;
    const paginatedUsers = filteredUsers.slice(startIndex, endIndex);

    return HttpResponse.json({
      users: paginatedUsers,
      total,
      page,
      per_page: perPage,
      total_pages: totalPages,
    });
  }),

  // POST /admin/users (Tạo user mới)
  http.post(`${API_URL}/admin/users`, async ({ request }) => {
    const body = await request.json();
    const nextId = users.length + 1;
    const newUser = {
      user_id: nextId,
      name: body.name,
      email: body.email,
      is_active: true,
      roles: ['user'],
      created_at: new Date().toISOString(),
      last_login: null,
    };

    // Đẩy user mới vào đầu users array
    users.unshift(newUser);

    return HttpResponse.json(newUser, { status: 201 });
  }),

  // DELETE /admin/users/:user_id
  http.delete(`${API_URL}/admin/users/:id`, async ({ params }) => {
    const { id } = params;
    const user_id = Number(id);

    const user = users.find((u) => u.user_id === user_id);

    if (user) {
      user.is_active = false;
      return HttpResponse.json('', { status: 204 });
    }
    return HttpResponse.json('User Not Found', { status: 404 });
  }),

  // POST /admin/users/:user_id/restore
  http.post(`${API_URL}/admin/users/:id/restore`, async ({ params }) => {
    const { id } = params;
    const user_id = Number(id);

    const user = users.find((u) => u.user_id === user_id);

    if (user) {
      user.is_active = true;
      return HttpResponse.json('', { status: 204 });
    }
    return HttpResponse.json('User Not Found', { status: 404 });
  }),

  // GET /admin/users/:user_id
  http.get(`${API_URL}/admin/users/:id`, async ({ params }) => {
    const { id } = params;
    const user_id = Number(id);

    const user = users.find((u) => u.user_id === user_id);

    if (user) {
      return HttpResponse.json({ ...user }, { status: 200 });
    }
    return HttpResponse.json('User Not Found', { status: 404 });
  }),

  // PUT /admin/users/:user_id
  http.put(`${API_URL}/admin/users/:id`, async ({ request, params }) => {
    const body = await request.json();
    const { id } = params;
    const user_id = Number(id);

    const user = users.find((u) => u.user_id === user_id);

    if (user) {
      for (const [key, value] of Object.entries(body)) {
        user[key] = value;
      }
      return HttpResponse.json({ ...user }, { status: 200 });
    }

    return HttpResponse.json('User Not Found', { status: 404 });
  }),
];
