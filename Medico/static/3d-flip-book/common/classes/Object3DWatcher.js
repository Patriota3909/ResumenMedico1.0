import {THREE} from '../libs';
import MathUtils from './MathUtils';

export default class Object3DWatcher {

  constructor(visual, boundBoxClb, testScale=this.testScale) {
    this.visual = visual;
    this.boundBoxClb = boundBoxClb;
    this.testScale = testScale;
    this.camera = visual.camera;
    this.element = this.visual.element;
    this.elementSize = {w: 1, h: 1};
    this.orbit = visual.getOrbit();
    this.scale = 1;
    this.padding = 0;

    this.eps = 1e-4;
    this.v = new THREE.Vector3();
    this.dv = new THREE.Vector2();

    this.enabled = false;

    visual.addRenderCallback(this.update.bind(this));

    this.os = {
      vx: 0,
      vy: 0,
      x: 0,
      y: 0
    };
    this.orbit.update();
    this.camera.updateMatrixWorld();
    let box = this.computeClientBoundBox(), k=1.11;
    this.movePan({x: -k*box.mid.x, y: -k*box.mid.y});
  }

  setPadding(padding) {
    this.padding = padding;
  }

  movePan(dv) {
    this.orbit.pan(dv.x*this.visual.width(), -dv.y*this.visual.height());
  }

  vToCamera(v) {
    v.project(this.camera);
    return {
      x: 0.5*v.x,
      y: 0.5*v.y
    };
  }

  computeClientBoundBox() {
    const box = this.boundBoxClb(),
      xs = [box.min.x, box.max.x],
      ys = [0, 0],
      zs = [box.min.z, box.max.z];

    const ps = [], res = {max: {}, min: {}};
    for(let x of xs) {
      for(let y of ys) {
        for(let z of zs) {
          ps.push(this.vToCamera(this.v.set(x,y,z)));
        }
      }
    }

    ps.sort((p1, p2)=> p1.x-p2.x);
    res.min.x = ps[0].x;
    res.max.x = ps[ps.length-1].x;
    ps.sort((p1, p2)=> p1.y-p2.y);
    res.min.y = ps[0].y;
    res.max.y = ps[ps.length-1].y;

    res.width = res.max.x-res.min.x;
    res.height = res.max.y-res.min.y;

    res.mid = {
      x: 0.5*(res.max.x+res.min.x),
      y: 0.5*(res.max.y+res.min.y)
    };

    return res;
  }

  setObject(boundBoxClb) {
    this.boundBoxClb = boundBoxClb;
  }

  testScale() {
    return true;
  }

  computeCorr(K, min, max) {
    let corr = 0;
    if(K<1) {
      if(min>-0.5) {
        corr = -0.5-min;
      }
      else if(max<0.5) {
        corr = 0.5-max;
      }
    }
    else {
      if(min<-0.5) {
        corr = -0.5-min;
      }
      else if(max>0.5) {
        corr = 0.5-max;
      }
    }
    return corr;
  }

  centerView(T) {
    let box = this.computeClientBoundBox(),
      Kx = this.elementSize.w/box.width,
      Ky = this.elementSize.h/box.height,
      K = Math.min(Kx, Ky),
      moving = false;

    if(this.testScale() && Math.abs(1/K-this.scale)>this.eps) {
      const scale = 1/K+0.2*(this.scale-1/K);
      this.orbit.setScale(this.orbit.getScale()/(K*scale));
      this.orbit.update();
      this.camera.updateMatrixWorld();
      box = this.computeClientBoundBox();
        Kx = this.elementSize.w/box.width;
        Ky = this.elementSize.h/box.height;
        K = Math.min(Kx, Ky);
      moving = true;
    }

    const dv = this.dv;
    if(K>1-this.eps) {
      if(this.padding) {
        const height = this.visual.height(), marg = 0.5*(Ky-1)/Ky, pad = this.padding/height, dpad = Math.max(0, Math.abs(pad)-marg);
        dv.set(-box.mid.x, -Math.sign(pad)*Math.min(Math.max(0, marg-20/height), dpad)-box.mid.y);
      }
      else {
        dv.set(-box.mid.x, -box.mid.y);
      }
    }
    else {
      const px = 70/this.visual.width(), py=70/this.visual.height();
      dv.set(this.computeCorr(Kx, box.min.x-px, box.max.x+px),
             this.computeCorr(Ky, box.min.y-py, box.max.y+py));
    }

    if(Math.sqrt(this.os.vx*this.os.vx+this.os.vy*this.os.vy)>0.003 || dv.length()>0.003) {
      let dt = 1/60, t=0, os = {
        ...this.os,
        x: 0,
        y: 0
      };
      os.tf = (vx, vy, x, y)=> ({
        x: 75*(dv.x-x),
        y: 75*(dv.y-y)
      });
      while(t<T) {
        if(t+dt>T) {
          dt = T-t;
        }
        os = this.integrate(os, dt);
        t += dt;
      }
      this.movePan(os);
      this.os = os;
      moving = true;
    }
    this.orbit.setMoving(moving);
  }

  integrate(os, dt) {
    const [vx, vy, x, y] = MathUtils.rk4(
      this.dy.bind(os),
      0,
      dt,
      [os.vx, os.vy, os.x, os.y]
    );
    return {
      ...os,
      vx, vy, x, y
    };
  }

  dy(t,Y) {
    const [vx, vy, x, y] = Y, vd = 15, tf = this.tf(vx, vy, x, y);
    return [
      tf.x-vd*vx,
      tf.y-vd*vy,
      vx,
      vy
    ];
  }

  update(dt) {
    if(this.enabled && this.boundBoxClb) {
      this.centerView(dt);
    }
  }

}
