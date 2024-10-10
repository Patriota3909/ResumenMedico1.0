import {PDFJS as PDFJSlib, $} from '../libs';
import Utils from './Utils';

const PATHS = window.PDFJS_LOCALE || GLOBAL_PATHS;
let PDFJS;

export default class Pdf {

  static isStable() {
    return !(window.Promise || {}).withResolvers && PATHS.stablePdfJsLib;
  }

  constructor(src, loadingProgress, openOptions) {
    this.src = Utils.normalizeUrl(src);
    this.handlerQueue = [];
    this.progresData = {loaded: -1, total: 1};
    this.loadingProgress = loadingProgress;

    this.pdfJsWorker = !PATHS.pdfJsLib || !Pdf.isStable()? PATHS.pdfJsWorker: PATHS.stablePdfJsWorker;
    (PDFJS? Promise.resolve(PDFJS): new Promise((resolve)=> {
      (!PATHS.pdfJsLib? Promise.resolve(PDFJSlib): new Promise((resolveFetch, rejectFetch)=> {
        $.get(Pdf.isStable()? PATHS.stablePdfJsLib: PATHS.pdfJsLib, (pdfJsLibCode)=> {
          eval(pdfJsLibCode);
          resolve(window.pdfjsLib);
        }).fail(rejectFetch);
      })).then(resolve).
      catch((e)=> {
        const error = {
          name: 'pdfJsLib',
          message: e.statusText
        };
        console.error(error);
        if(this.errorHandler) {
          this.errorHandler(error);
        }
      });
    })).then((pdfJs)=> {
      if(!PDFJS) {
        PDFJS = pdfJs;
        PDFJS.GlobalWorkerOptions.workerSrc = this.pdfJsWorker;
        PDFJS.cMapUrl = PATHS.pdfJsCMapUrl;
        PDFJS.cMapPacked = true;
        PDFJS.disableAutoFetch = true;
        PDFJS.disableStream = true;
        PDFJS.disableRange = false;
        PDFJS.imageResourcesPath = 'images/pdfjs/';
        // PDFJS.externalLinkTarget = PDFJS.LinkTarget.BLANK;
        PDFJS.disableFontFace = undefined;
        PDFJS.isEvalSupported = !Pdf.isStable();
      }

      this.task = PDFJS.getDocument({
        url: this.src,
        rangeChunkSize: 512*1024,
        cMapUrl: PDFJS.cMapUrl,
        cMapPacked: PDFJS.cMapPacked,
        disableAutoFetch: PDFJS.disableAutoFetch,
        disableStream: PDFJS.disableStream,
        disableRange: PDFJS.disableRange,
        imageResourcesPath: PDFJS.imageResourcesPath,
        externalLinkTarget: PDFJS.externalLinkTarget,
        disableFontFace: PDFJS.disableFontFace,
        isEvalSupported: PDFJS.isEvalSupported,
        ...openOptions
      });
      this.task.onProgress = (data)=> {
        if(this.loadingProgress) {
          let cur = Math.floor(100*data.loaded/data.total),
                old = Math.floor(100*this.progresData.loaded/this.progresData.total);
          if(cur!==old) {
            cur = isNaN(cur)? 0: cur;
            cur = cur>100? 100: cur;
            Promise.resolve().then(()=> {
              this.loadingProgress(cur);
            });
          }
        }
        this.progresData = data;
      };
      this.task.promise.then((handler)=> {
        if(handler.numPages>1) {
          Promise.all([handler.getPage(1), handler.getPage(2)]).
          then((pages)=> {
            this.init(handler, pages);
          });
        }
        else {
          this.init(handler);
        }
      }).
      catch((e)=> {
        console.error(e);
        if(this.errorHandler) {
          this.errorHandler(e);
        }
      });

    });
  }

  init(handler, pages) {
    this.handler = handler;
    let done = Promise.resolve(handler);
    if(pages) {
      const p0s = Pdf.getPageSize(pages[0]), p1s = Pdf.getPageSize(pages[1]);
      this.doubledPages = (p0s.width/p0s.height)/(p1s.width/p1s.height)<0.75;
      if(this.doubledPages) {
         done = (handler.numPages===2? Promise.resolve(pages[1]): handler.getPage(handler.numPages)).then((pl)=> {
           const pls = Pdf.getPageSize(pl);
           this.doubledLastPage = (p0s.width/p0s.height)/(pls.width/pls.height)<0.75;
           return handler;
         });
      }
      else {
        this.doubledLastPage = false;
      }
    }
    else {
      this.doubledPages = this.doubledLastPage = false;
    }
    for(let clb of this.handlerQueue.reverse()) {
      done = done.then((handler)=> {
        clb(handler);
        return handler;
      });
    }
  }

  getPageType(n) {
    return !this.doubledPages || n===0 || (n===this.getPagesNum()-1 && !this.doubledLastPage)? 'full': (n&1? 'left': 'right');
  }

  getPage(n) {
    return this.handler.getPage(this.doubledPages? Math.ceil(n/2)+1: n+1);
  }

  getDestination(dest) {
    let destPromise;
    if(typeof dest==='string') {
      destPromise = this.handler.getDestination(dest);
    }
    else {
      destPromise = Promise.resolve(dest);
    }
    destPromise = destPromise.
      then((dest)=> this.handler.getPageIndex(dest[0])).
      then((number)=> this.doubledPages? (number<1? number: 1+2*(number-1)): number).
      catch(()=> console.error('Bad bookmark'));
    return destPromise;
  }

  dispose() {
    this.handlerQueue.splice(0, this.handlerQueue.length);
    delete this.handler;
  }

  setLoadingProgressClb(clb) {
    this.loadingProgress = clb;
  }

  setErrorHandler(eh) {
    this.errorHandler = eh;
  }

  getPagesNum() {
    return this.handler? (this.doubledPages? 1+2*(this.handler.numPages-(1+!this.doubledLastPage))+!this.doubledLastPage: this.handler.numPages): undefined;
  }

  static getPageSize(page) {
    const x = page.view[2]-page.view[0], y = page.view[3]-page.view[1], a = page.rotate*Math.PI/180;
    return {
      width: Math.abs(x*Math.cos(a)-y*Math.sin(a)),
      height: Math.abs(x*Math.sin(a)+y*Math.cos(a))
    };
  }

//   if(pages>1) {
//   handler.getPage(2).
//   then((page)=> {
//     const size1 = Pdf.getPageSize(page);
//     this.props.doubledPages = 2*size0.width===size1.width;
//     this.ready();
//   }).
//   catch(()=> this.ready());
// }
// else {

  getHandler(clb) {
    if(this.handler) {
      clb(this.handler);
    }
    else {
      this.handlerQueue.push(clb);
    }
  }

}
