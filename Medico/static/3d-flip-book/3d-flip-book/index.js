import worker from './js/worker';

$.fn.FlipBook = function(options) {
    const parentContainer = this.length? this[0]: $('<div>').appendTo('body');
    return worker(parentContainer, options);
}

$(()=> {
  let containers = $('.flip-book-container');
  for(let i = 0; i<containers.length; ++i) {
    const jContainer = $(containers[i]), src = jContainer.attr('src');
    if(!!src) {
      jContainer.FlipBook({pdf: src});
    }
  }
});

window.jQuery = window.$ = $;
