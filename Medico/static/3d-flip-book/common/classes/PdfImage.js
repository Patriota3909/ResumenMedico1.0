import {$} from '../libs';
import ImageBase from './ImageBase';
import Pdf from './Pdf';
import BaseMathUtils from './BaseMathUtils';
import CustomEventConverter from './CustomEventConverter';
import PolyTarget from './targets/PolyTarget';

import Finder from './Finder';

export default class PdfImage extends ImageBase {

  constructor(context, width, height, color, pdf, n) {
    super(context, width, height, color);

    this.query = '';
    this.n = n;
    this.pdf = pdf;
    this.v = {x: 0, y: 0, z: 0, set: function(x,y,z) {
      this.x=x; this.y=y; this.z=z;
      return this;
    }, transform: function(m) {
      const x=m.m[0][0]*this.x+m.m[1][0]*this.y+m.m[2][0]*this.z,
            y=m.m[0][1]*this.x+m.m[1][1]*this.y+m.m[2][1]*this.z,
            z=m.m[0][2]*this.x+m.m[0][2]*this.y+m.m[2][0]*this.z;
      this.x=x;
      this.y=y;
      this.z=z;
      return this;
    }};
    this.m = {m: [[1,0,0],[0,1,0],[0,0,1]], set: function(m00,m01,m02,m10,m11,m12,m20,m21,m22) {
      this.m=[[m00,m01,m02],[m10,m11,m12],[m20,m21,m22]];
      return this;
    }};

    this.startRender = ()=> {
      this.pdf.getHandler(this.render.bind(this));
    };
    Promise.resolve().
      then(()=> this.pdf.getHandler(this.init.bind(this)));

    this.cssLayerRequests = [];
  }

  setQuery(query) {
    this.query = query.trim();
    if(this.textContent) {
      this.setHits(this.textContent);
      // this.finishLoad();
    }
  }

  rectSize(r) {
    return {
      width: r[2]-r[0],
      height: r[3]-r[1]
    };
  }

  createPoly(m, p, s) {
    const poly = [], v = this.v;
    v.set(p.x, p.y, 1).transform(m);
    poly.push({x: v.x, y: v.y});
    v.set(p.x, p.y+s.height, 1).transform(m);
    poly.push({x: v.x, y: v.y});
    v.set(p.x+s.width, p.y+s.height, 1).transform(m);
    poly.push({x: v.x, y: v.y});
    v.set(p.x+s.width, p.y, 1).transform(m);
    poly.push({x: v.x, y: v.y});
    return poly;
  }

  getSimulatedDoc() {
    return this;
  }

  simulate(e, doc, x, y) {
    if(this.eventConverter) {
      this.eventConverter.convert(e, {doc, x, y});
    }
  }

  setAnnotations(annos) {
    const t = this.viewport.transform, htmls = [], r = (n)=> (n*100+'').substr(0,5),
      targets = [];
    this.m.set(
      t[0],t[1],0,
      t[2],t[3],0,
      t[4],t[5],1);

    for(let anno of annos) {
      if (anno.subtype==='Link' || anno.subtype==='Widget') {
        const rect = anno.rect,
          aPos = {
            x: rect[0],
            y: rect[1]
          },
          aSz = this.rectSize(rect);
        const target = new PolyTarget(this.createPoly(this.m, aPos, aSz).map((p)=> ({x: p.x/this.viewport.width, y: 1-p.y/this.viewport.height})));
        target.anno = anno;
        target.callback = this.annoClb.bind(this);
        targets.push(target);
        const p = target.poly;
        htmls.push('<div class="fb3d-block fb3d-link" style="top: '+r(1-p[2].y)+'%; left: '+r(p[0].x)+'%; width: '+r(p[2].x-p[0].x)+'%; height: '+r(p[2].y-p[0].y)+'%;"><a></a></div>');
      }
    }
    if(targets.length) {
      this.eventConverter = new CustomEventConverter(this.wnd, this.doc, PolyTarget.test, this.getSimulatedDoc());
      for(let target of targets) {
        this.eventConverter.addCustom(target);
      }
    }
    this.cssLayer = {html: htmls.length? '<pdf-layer>'+htmls.join('')+'</pdf-layer>': undefined};
    this.resolveCssLayerRequests();
  }

  resolveCssLayerRequests() {
    if(this.cssLayer) {
      for(let r of this.cssLayerRequests) {
        r(this.cssLayer.html? this.cssLayer: undefined);
      }
    }
  }

  getCSSLayer() {
    return new Promise((resolve)=> {
      this.cssLayerRequests.push(resolve);
      this.resolveCssLayerRequests();
    });
  }

  setHits(textContent) {
    this.textContent = textContent;
    this.finder = this.query!==''? new Finder(textContent.items.map((item)=> item.str), this.query, {contexts: false}): undefined;
  }

  renderHits() {
    if(this.finder) {
      const view = this.page.view,
        testSz = $('<div style="position: absolute; visibility: hidden;"></div>').appendTo('body'), textDiv = testSz[0],
        baseOffset = testSz.offset().left;
      for(let hit of this.finder.getHits()) {
          const item = this.textContent.items[hit.index],
                t = BaseMathUtils.pdfJsTransform(this.viewport.transform, item.transform),
                style = this.textContent.styles[item.fontName],
                angle = Math.atan2(t[1], t[0])+(style.vertical? Math.PI / 2: 0),
                fontHeight = Math.sqrt((t[2] * t[2]) + (t[3] * t[3])),
                fontAscent = style.ascent?
                              style.ascent * fontHeight:
                              (style.descent? (1 + style.descent) * fontHeight: fontHeight);
          testSz.html(item.str.substr(0, hit.offset)+'<span>'+item.str.substr(hit.offset, hit.length)+'</span>'+item.str.substr(hit.offset+hit.length));

          textDiv.style.fontSize = fontHeight+'px';
          textDiv.style.fontFamily = style.fontFamily;

          const testSpan = testSz.find('span'),
              iwidth = style.vertical? item.height*this.viewport.scale: item.width*this.viewport.scale,
              width = testSz.width(),
              relativeOffset = (testSpan.offset().left-baseOffset)/width;
          this.m.set(
            1,0,0,
            0,1,0,
            t[4]+fontAscent*Math.sin(angle),t[5]-fontAscent*Math.cos(angle),1);
          let poly = this.createPoly(this.m, {x: relativeOffset*iwidth, y: 0}, {width: iwidth*testSpan.width()/width, height: testSpan.height()});
          poly = poly.map((p)=> ({x: p.x/this.viewport.width, y: 1-p.y/this.viewport.height}));
          this.renderHit(poly);
      }
      testSz.remove();
    }
  }

  annoClb(e, data) {
    if(this.context.dispatchEvent) {
      this.context.dispatchEvent({
        type: 'pdfAnnotation',
        event: e,
        annotation: data.target.anno
      });
    }
  }

  calcViewport() {
    const scale = BaseMathUtils.calcScale(this.size.width, this.size.height, this.resW, this.resH);
    if(!this.viewport || Math.abs(this.viewport.scale-scale)>1e-4) {
      this.viewport = this.page.getViewport({scale});
      if(this.type!=='full') {
        if(this.type==='right') {
          this.viewport.offsetX += 0.5*this.viewport.width*1.0005;
          this.viewport.transform[4] -= 0.5*this.viewport.width*1.0005;
          this.viewport.width *= 0.5/1.0005;
        }
        else {
          this.viewport.width /= 2;
        }
      }
      this.resW = this.width = this.viewport.width;
      this.resH = this.height = this.viewport.height;
    }
  }

  init() {
    this.type = this.pdf.getPageType(this.n);
    this.pdf.getPage(this.n).
      then((page)=> {
        this.page = page;
        this.size = Pdf.getPageSize(page);
        if(this.type!=='full') {
          this.size.width /= 2;
        }
        page.getAnnotations().
          then(this.setAnnotations.bind(this));
        page.getTextContent().
          then(this.setHits.bind(this));
        this.calcViewport();
        this.finishLoad();
      }).
      catch((e)=> {
        console.error('Cannot load PDF page: '+(this.n+1));
        console.error(e);
        this.finishLoad();
      });
  }

  setResolution(res) {
    super.setResolution(res);
    if(this.page) {
      this.calcViewport();
    }
  }

  render(handler) {
    if(this.page) {
      const ctx = this.pushCtx();
      this.ctx.clearRect(0, 0, this.c.width, this.c.height);
      this.renderTask = this.page.render({
        canvasContext: this.ctx,
        viewport: this.viewport
      });
      this.renderTask.onContinue = (continueRender)=> {
        if(this.renderPause) {
          this.continueRender = continueRender;
        }
        else {
          continueRender();
        }
      };
      this.renderTask.promise.
      then(()=> {
        this.renderHits();
        this.popCtx();
        this.finishRender();
      }).
      catch((e)=> {
        this.popCtx();
        this.finishRender(true);
      });
    }
    else {
      this.renderBlankPage();
      this.finishRender();
    }
  }

}
