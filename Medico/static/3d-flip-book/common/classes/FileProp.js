import {React, tr} from '../libs';
import Prop from './Prop';

export default class FileProp extends Prop {

  selectFile(e) {
    e.preventDefault();
    const {setValue, post, mime} = this.props;
    wp.media.model.settings.post.id = post.ID;
		const frame = new wp.media.view.MediaFrame.Select({
			title: 'Select a file',
			multiple: false,
			library: {
				order: 'DESC',
				orderby: 'modified',
				type: mime,
				uploadedTo: null
			},
			button: {
				text: 'Open'
			}
		});

		frame.on('select', ()=> {
			const file = frame.state().get('selection').first().toJSON();
      setValue(file.url);
		});

		frame.open();
  }

  renderContent() {
    const {name, defValue, setValue} = this.props, value = this.props.value || 'auto';
    return (
      <div class="input-group">
        <div class="input-group-addon" title={tr('Default value')}>{defValue}</div>
        <input type="text" class="form-control" readOnly={true} onChange={(e)=> setValue(e.target.value)} id={name} name={name} value={value} />
        <span class="input-group-btn">
          <a onClick={this.selectFile.bind(this)} class="btn btn-default">Select</a>
          <a onClick={(e)=> [e.preventDefault(), setValue('auto')]} class={'btn btn-default'+(value==='auto'?' disabled': '')}>{tr('auto')}</a>
        </span>
      </div>
    );
  }
}
