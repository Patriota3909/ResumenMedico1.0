import {React, $, tr} from '../libs';
import Prop from './Prop';

export default class ColorProp extends Prop {

  componentDidUpdate() {
    if(!this.container) {
      const {container} = this.refs, {setValue} = this.props;
      this.container = $(container);
      this.container.ColorPicker({
        documentx: container.ownerDocument,
      	flat: true,
      	color: this.color2RGB(this.getColor()),
      	onSubmit: ()=> this.container.css('display', 'none'),
      	onChange: (hsb, hex, rgb)=> setValue((rgb.r<<16)|(rgb.g<<8)|rgb.b)
      });
      $(container.ownerDocument).click((e)=> {
				let c = container, el = e.target;
				while(el && el!=c) {
					el = el.parentNode;
				}
				if(Date.now()-this.container[0].ownerDocument.fb3dColorPickerClickTime>100 && !el) {
					this.container.ColorPickerSetColor(this.color2RGB(this.getColor()));
					this.container.css('display', 'none');
				}
			});
    }
  }

  getColor() {
    return this.props.value==='auto'? this.props.defValue: this.props.value;
  }

  color2RGB(c) {
    return {
      r: (c>>16)&0xff,
      g: (c>>8)&0xff,
      b: c&0xff
    };
  }

  color2RGBA(c) {
    return {
      ...this.color2RGB(c),
      a: c===''? 0: 1
    };
  }

  showColorPicker(e) {
    e.stopPropagation();
    this.container[0].ownerDocument.fb3dColorPickerClickTime = Date.now();
    this.container.css('display', 'block');
  }

  renderContent() {
    const {name, defValue, setValue} = this.props, value = this.props.value===undefined? 'auto': this.props.value, rgba = this.color2RGBA(this.getColor()), defRgba = this.color2RGBA(defValue);
    const defStyle = {
      backgroundColor: ['rgba(',defRgba.r, ',', defRgba.g, ',', defRgba.b,',', defRgba.a, ')'].join(''),
    },
    style = {
      backgroundColor: ['rgba(', rgba.r, ',', rgba.g, ',', rgba.b, ',', rgba.a, ')'].join('')
    };
    return (
      <div class="color-prop">
        <div class="input-group">
          <div class="input-group-addon" style={defStyle} title={tr('Default value')}></div>
          <input type="hidden" name={name} value={value} />
          <input type="text" onClick={this.showColorPicker.bind(this)} class="form-control" id={name} style={style} value={style.backgroundColor} />
          <span class="input-group-btn">
            <a onClick={(e)=> [e.preventDefault(), setValue('auto')]} class={'btn btn-default'+(value==='auto'?' disabled': '')}>{tr('auto')}</a>
          </span>
        </div>
        <div ref="container" class="color-container"></div>
      </div>
    );
  }
}
