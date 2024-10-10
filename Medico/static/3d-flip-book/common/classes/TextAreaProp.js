import {React, tr} from '../libs';
import Prop from './Prop';

export default class TextAreaProp extends Prop {

  renderContent() {
    const {name, defValue, setValue} = this.props;
    let value = this.props.value || 'auto';
    if(value==='auto') {
      value = '';
    }
    return (
      <textarea id={name} name={name} onChange={(e)=> setValue(e.target.value)} class="form-control" value={value}></textarea>
    );
  }
}
