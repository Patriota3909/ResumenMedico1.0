import GraphUtils from './GraphUtils';

export default class ImageBase {

  static renderCanvas =  GraphUtils.createCanvas();
  static renderCanvasCtx = ImageBase.renderCanvas.getContext('2d');

  constructor(context, width, height, color) {
    this.renderPause = false;
    this.context = context;
    this.wnd = context.wnd;
    this.doc = context.doc;
    this.element = context.element || context.doc.body;
    this.c = context.renderCanvas || ImageBase.renderCanvas;
    this.ctx = context.renderCanvasCtx || ImageBase.renderCanvasCtx;
    this.resW = this.width = width;
    this.resH = this.height = height;
    this.color = color;
  }

  setRenderCanvas(c, ctx) {
    this.c = c;
    this.ctx = ctx;
  }

  setResolution(res) {
    const k = res.width/this.resW;
    this.resW = res.width;
    this.resH = k*this.resH; // res.height;
  }

  dispose() {

  }

  renderBlankPage() {
    this.ctx.beginPath();
    this.ctx.fillStyle = GraphUtils.color2Rgba(this.color, 1);
    this.ctx.rect(0, 0, this.c.width, this.c.height);
    this.ctx.fill();
  }

  setRenderPause(renderPause) {
    this.renderPause = renderPause;
    if(!renderPause && this.continueRender) {
      this.continueRender();
      delete this.continueRender;
    }
  }

  cancelRender() {
    if(this.renderTask && this.renderTask.cancel) {
      this.renderTask.cancel();
      delete this.renderTask;
    }
  }

  renderImage(image) {
    this.pushCtx();
    this.ctx.clearRect(0, 0, this.c.width, this.c.height);
    this.ctx.drawImage(image, 0, 0);
    this.popCtx();
  }

  normToConv(p) {
    return {
      x: p.x*this.c.width,
      y: (1-p.y)*this.c.height
    };
  }

  renderHit(poly) {
    const ctx = this.ctx;
    ctx.fillStyle = 'rgba(255,255,0,0.4)';
    ctx.beginPath();
    let p = this.normToConv(poly[0]);
    ctx.moveTo(p.x, p.y);
    for(let i=1; i<poly.length; ++i) {
      p = this.normToConv(poly[i]);
      ctx.lineTo(p.x, p.y);
    }
    ctx.closePath();
    ctx.fill();
  }

  pushCtx() {
    if(Math.abs(this.resW-this.c.width)>=1) {
      this.c.width = Math.ceil(this.resW);
    }
    if(Math.abs(this.resH-this.c.height)>=1) {
      this.c.height = Math.ceil(this.resH);
    }
    this.ctx.save();
    this.ctx.scale(this.c.width/this.width, this.c.height/this.height);
    return this.ctx;
  }

  popCtx() {
    this.ctx.restore();
  }

  renderNotFoundPage() {
    this.renderBlankPage();
  }

  finishRender(canceled = false) {
    if(this.onChange) {
      this.onChange(this.c, canceled);
    }
  }

  finishLoad() {
    if(this.onLoad) {
      this.onLoad();
    }
    else {
      this.startRender();
    }
  }

  getSimulatedDoc() {
    return undefined;
  }

}
