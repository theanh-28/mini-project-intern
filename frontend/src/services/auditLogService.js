import api from './api';

export const auditLogService = {
  /**
   * Lấy danh sách Audit Logs phân trang theo con trỏ (Cursor-based pagination)
   * @param {Object} params - { limit, cursor, action, table_name, search, created_at_from, created_at_to }
   */
  getAuditLogs: async (params = {}) => {
    const cleanParams = {};
    Object.keys(params).forEach((key) => {
      if (params[key] !== undefined && params[key] !== null && params[key] !== '') {
        cleanParams[key] = params[key];
      }
    });

    const response = await api.get('/admin/audit-logs', { params: cleanParams });
    return response.data;
  },

  /**
   * Lấy chi tiết một bản ghi Audit Log (bao gồm old_value và new_value)
   * @param {string} logId - UUIDv7 của bản ghi
   */
  getAuditLogDetail: async (logId) => {
    const response = await api.get(`/admin/audit-logs/${logId}`);
    return response.data;
  },

  /**
   * Lấy dòng thời gian audit logs của riêng một user
   * @param {number|string} userId
   * @param {Object} params - { limit, cursor }
   */
  getUserAuditTimeline: async (userId, params = {}) => {
    const response = await api.get(`/admin/users/${userId}/audit-logs`, { params });
    return response.data;
  },
};
