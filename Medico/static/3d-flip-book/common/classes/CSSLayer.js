import {THREE, $} from '../libs';
import {CSS3DObject} from './CSS3DRenderer';

export default class CSSLayer extends CSS3DObject {

  static delay;
  static style;
  static init(doc, delay=150) {
    CSSLayer.delay = delay;
    CSSLayer.style = $(`<style type=text/css>
      .css-layer {
    		opacity: 1;
    		transition: opacity ${delay}ms ease-out;
        visibility: visible;
        overflow: hidden;
    	}
    	.css-layer.hidden {
    		transition: opacity ${delay}ms ease-in, visibility ${delay}ms step-end;
    		opacity: 0;
        visibility: hidden;
        display: block;
        pointer-events: none;
      }
      .fb3d-block {
        position: absolute;
      }
      .fb3d-audio audio, .fb3d-link a, .fb3d-iframe iframe, .fb3d-video video, .fb3d-youtube .youtube {
        display: block;
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
      }
      .fb3d-image {
        text-align: center;
      }
      .fb3d-link a {
        cursor: pointer;
        background-color: rgba(255,255,0,.1);
        transition: background-color .15s ease-in;
      }
      .fb3d-link a:hover {
        background-color: rgba(255,255,0,.2);
        transition: background-color .15s ease-out;
      }
      .fb3d-iframe iframe {
        border: 0;
      }
      .fb3d-image img {
        max-width: 100%;
        max-height: 100%;
      }
    </style>`.fb3dQFilter()).appendTo(doc.head);
  }
  static dispose() {
    CSSLayer.style.remove();
  }

  constructor(width, height, props) {
    super();
    this.props = props;
    this.jContainer = $('<div class="hidden css-layer"></div>');
    this.setSize(width, height);
    this.setData();
    this.set(this.jContainer[0]);
  }

  setSize(width, height) {
    const widthPxs = Math.round(this.props.width), heightPxs = Math.round(height/width*widthPxs);
    this.jContainer.width(widthPxs).height(heightPxs);
  	this.scale.x = 1/(widthPxs/width);
  	this.scale.y = 1/(widthPxs/width);
  }

  callInternal(name) {
    if(this.object && this.object[name]) {
      try {
        this.object[name]();
      }
      catch(e) {
        console.error(e);
      }
    }
  }

  dispose() {
    this.clearInternals();
  }

  clearInternals() {
    this.callInternal('dispose');
    !this.css || this.css.remove();
    !this.html || this.html.remove();
  }

  setData(css='', html='', js='') {
    this.clearInternals();

    this.css = $(`<style type="text/css">${css}</style>`).appendTo(this.jContainer);
    this.html = $(html).appendTo(this.jContainer);
    const init = eval(js);
    if(init) {
      this.object = init(this.jContainer, this.props) || {};
    }
  }

  pendedCall(clb) {
    const timestamp = this.timestamp = Date.now();
    setTimeout(()=> {
      if(timestamp===this.timestamp) {
        clb();
      }
    }, CSSLayer.delay*.5);
  }

  isHidden() {
    return this.jContainer.hasClass('hidden');
  }

  hide() {
    let res;
    if(!this.isHidden()) {
      this.jContainer.addClass('hidden');
      this.callInternal('hide');
      res = new Promise((resolve)=> {
        this.pendedCall(()=> {
          this.callInternal('hidden');
          resolve();
        });
      });
    }
    else {
      res = Promise.resolve();
    }
    return res;
  }

  show() {
    let res;
    if(this.isHidden()) {
      this.jContainer.removeClass('hidden');
      this.callInternal('show');
      res = new Promise((resolve)=> {
        this.pendedCall(()=> {
          this.callInternal('shown');
          resolve();
        });
      });
    }
    else {
      res = Promise.resolve();
    }
    return res;
  }

}
