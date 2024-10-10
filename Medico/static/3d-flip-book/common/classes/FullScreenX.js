import {$} from '../libs';
import FullScreen from './FullScreen';

export default class FullScreenX extends FullScreen {

	static available() {
		return true;
	}

	static defNode = $();
	static node = FullScreenX.defNode;
	static defHandler = ()=> undefined
	static handler = FullScreenX.defHandler;
	static classX = 'fb3d-fullscreenx';
	static style = $(`
		<style type="text/css">
      .${FullScreenX.classX} {
        position: fixed !important;
				left: 0 !important;
        top: 0 !important;
        width: 100% !important;
        height: 100% !important;
				z-index: 2147483647 !important;
				margin: 0 !important;
				box-sizing: border-box !important;
        background-color: #333;
      }
    </style>
	`.fb3dQFilter()).appendTo('head');

	static activated() {
		return super.available()? super.activated(): FullScreenX.node.hasClass(FullScreenX.classX);
	}

	static addEventListener(element, handler) {
		if(super.available()) {
			super.addEventListener(element, handler);
		}
		else {
			FullScreenX.handler = handler;
		}
	}

	static removeEventListener(element, handler) {
		if(super.available()) {
			super.removeEventListener(element, handler);
		}
		else {
			FullScreenX.handler = FullScreenX.defHandler;
		}
	}

	static request(element) {
		if(super.available()) {
			super.request(element);
		}
		else {
			if(!FullScreenX.node.hasClass(FullScreenX.classX)) {
				FullScreenX.node = $(element || document.body);
				FullScreenX.node.addClass(FullScreenX.classX);
				Promise.resolve().then(FullScreenX.handler);
			}
		}
	}

	static cancel() {
		if(super.available()) {
			super.cancel();
		}
		else {
			if(FullScreenX.node.hasClass(FullScreenX.classX)) {
				FullScreenX.node.removeClass(FullScreenX.classX);
				FullScreenX.node = FullScreenX.defNode;
				Promise.resolve().then(FullScreenX.handler);
			}
		}
	}

}
