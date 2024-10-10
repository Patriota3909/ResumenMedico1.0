
export default class FullScreen {

	static _hasWebkitFullScreen	= !!document.webkitCancelFullScreen;
	static _hasMozFullScreen	= !!document.mozCancelFullScreen;
	static _hasMsFullscreen = !!document.documentElement.msRequestFullscreen;

	static available() {
		return FullScreen._hasWebkitFullScreen || FullScreen._hasMozFullScreen || FullScreen._hasMsFullscreen;
	}

	static activated() {
		if(FullScreen._hasWebkitFullScreen) {
			return document.webkitIsFullScreen;
		}
		else if(FullScreen._hasMozFullScreen) {
			return document.mozFullScreen;
		}
		else if(FullScreen._hasMsFullscreen) {
			return !!document.msFullscreenElement;
		}
		else {
			console.assert(false);
		}
	}

	static addEventListener(element, handler) {
		if (element.addEventListener) {
		    element.addEventListener('webkitfullscreenchange', handler, false);
		    element.addEventListener('mozfullscreenchange', handler, false);
		    element.addEventListener('fullscreenchange', handler, false);
		    element.addEventListener('MSFullscreenChange', handler, false);
		}
	}

	static removeEventListener(element, handler) {
		if (element.removeEventListener) {
		    element.removeEventListener('webkitfullscreenchange', handler, false);
		    element.removeEventListener('mozfullscreenchange', handler, false);
		    element.removeEventListener('fullscreenchange', handler, false);
		    element.removeEventListener('MSFullscreenChange', handler, false);
		}
	}

	static request(element) {
		element	= element	|| document.body;
		if(FullScreen._hasWebkitFullScreen) {
			element.webkitRequestFullScreen();
		}
		else if(FullScreen._hasMozFullScreen) {
			element.mozRequestFullScreen();
		}
		else if(FullScreen._hasMsFullscreen) {
			element.msRequestFullscreen();
		}
		else {
			console.assert(false);
		}
	}

	static cancel() {
		if(FullScreen._hasWebkitFullScreen) {
			document.webkitCancelFullScreen();
		}else if(FullScreen._hasMozFullScreen) {
			document.mozCancelFullScreen();
		}
		else if(FullScreen._hasMsFullscreen) {
			document.msExitFullscreen();
		}
		else {
			console.assert(false);
		}
	}

}
