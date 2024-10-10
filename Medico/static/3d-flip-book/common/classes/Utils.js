export default class Utils {

  static MOBILE_DIAG = 11;

  static normalizeUrl(url) {
    function split(s) {
      return s.replace(/\\/g, '/').split('/');
    }
    const base = split(window.location.href);
    url = split(url);
    if(base[2]===url[2]) {
      url[0] = base[0];
    }
    return url.join('/');
  }

  static _escapeHTMLchars = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;'
  };
  static _escapeHTMLclb(c) {
    return Utils._escapeHTMLchars[c] || c;
  }
  static escapeHTML(s) {
      return s.replace(/[&<>]/g, Utils._escapeHTMLclb);
  }

  static extends(der, base) {
    for(let name in base) {
      if(!der.hasOwnProperty(name)) {
        der[name] = base[name];
      }
    }
  }

  static defaultCmp(a, b) {
    return a-b;
  }

  static lowerBound(a, x, cmp) {
    cmp = cmp || Utils.defaultCmp;
    let l = 0, h = a.length-1;
    while(h-l>1) {
      let mid = Math.floor((l + h) / 2);
      if(cmp(x, a[mid])<0) {
        h = mid;
      }
      else {
        l = mid;
      }
    }
    return cmp(x, a[h])>=0? h: l;
  }

}
