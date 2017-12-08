// for local we use localStorage because session storage does not include tabs, that is couner-intuitive for me
// for session we use a traditional SessionCookie
export default {
  getLocal (key) {
    return window.localStorage.getItem(key)
  },
  setLocal (key, value) {
    window.localStorage.setItem(key, value)
  },
  getSession (key) {
    let tok = null
    document.cookie.split(';').forEach(item => {
      if (item.indexOf(key) !== -1) {
        tok = item.split('=')[1]
      }
    })
    return tok
  },
  setSession (key, value) {
    if (value === null) {
      document.cookie = key + '=;expires=Thu, 01 Jan 1970 00:00:01 GMT;'
    } else {
      document.cookie = key + '=' + value + ';'
    }
  }
}
