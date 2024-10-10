import {$} from '../libs';

export default class UserMessageController {

  constructor(view) {
    this.view = view;
    this.showMessage = false;
    this.message = '';
    this.updateView();
  }

  dispose() {
    this.updateView();
    delete this.view;
  }

  setError(text) {
    this.showMessage = true;
    this.message = ['<div class="text error">', text, '</div>'].join('');
    this.updateView();
  }

  updateView() {
    if(this.view) {
      this.view.setState('widUserMessage', {
        enable: true,
        visible: this.showMessage,
        active: false
      });

      this.view.setState('txtUserMessage', {
        value: this.message,
        visible: true
      });
    }
  }

}
