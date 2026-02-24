// CommonJS
module.exports = {
    verify(req) {
      const auth = req.get('authorization') || '';
      return auth === 'Bearer good';
    }
  };
  