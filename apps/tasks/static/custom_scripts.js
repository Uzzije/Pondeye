/**
 * Created by Administrator on 11/13/16.
 */

// courtesy of Claudia Romano https://codyhouse.co/gem/css-jquery-image-comparison-slider/
jQuery(document).ready(function($){
    //function to check if the .cd-image-container is in the viewport here
    // ...
    console.log("slider is ready");
    //make the .cd-handle element draggable and modify .cd-resize-img width according to its position
    $('.cd-image-container').each(function(){
        var actual = $(this);
        drags(actual.find('.cd-handle'), actual.find('.cd-resize-img'), actual);
    });

    //function to upadate images label visibility here
    // ...
});

//draggable funtionality - credits to http://css-tricks.com/snippets/jquery/draggable-without-jquery-ui/
function dragss(dragElement, resizeElement, container, labelContainer, labelResizeElement) {
    var $ = jQuery;

    dragElement.on('mousedown vmousedown', function (e) {
        dragElement.addClass('cd-draggable');
        resizeElement.addClass('cd-resizable');

        var dragWidth = dragElement.outerWidth(),
            xPosition = dragElement.offset().left + dragWidth - e.pageX,
            containerOffset = container.offset().left,
            containerWidth = container.outerWidth(),
            minLeft = containerOffset + 10,
            maxLeft = containerOffset + containerWidth - dragWidth - 10;

        dragElement.parent().bind('mousemove.cd vmousemove.cd', function (e) {
            var leftValue = e.pageX + xPosition - dragWidth;

            // constrain the draggable element to move inside his container
            if (leftValue < minLeft) {
                leftValue = minLeft;
            } else if (leftValue > maxLeft) {
                leftValue = maxLeft;
            }

            var widthValue = (leftValue + dragWidth / 2 - containerOffset) * 100 / containerWidth + '%';

            $('.cd-draggable', container).css('left', widthValue).one('mouseup vmouseup', function () {
                $(this).removeClass('cd-draggable');
                resizeElement.removeClass('cd-resizable');
            });

            $('.cd-resizable', container).css('width', widthValue);

            updateLabel(labelResizeElement, resizeElement, 'left');
            updateLabel(labelContainer, resizeElement, 'right');

        }).one('mouseup vmouseup', function (e) {
            dragElement.removeClass('cd-draggable');
            resizeElement.removeClass('cd-resizable');

            dragElement.parent().unbind('mousemove.cd vmousemove.cd');
        });

        e.preventDefault();

    }).on('mouseup vmouseup', function (e) {
        dragElement.removeClass('cd-draggable');
        resizeElement.removeClass('cd-resizable');
    });
}

function drags(dragElement, resizeElement, container) {

  // Initialize the dragging event on mousedown.
  dragElement.on('mousedown touchstart', function(e) {

    dragElement.addClass('draggable');
    resizeElement.addClass('resizable');

    // Check if it's a mouse or touch event and pass along the correct value
    var startX = (e.pageX) ? e.pageX : e.originalEvent.touches[0].pageX;

    // Get the initial position
    var dragWidth = dragElement.outerWidth(),
        posX = dragElement.offset().left + dragWidth - startX,
        containerOffset = container.offset().left,
        containerWidth = container.outerWidth();

    // Set limits
    minLeft = containerOffset + 10;
    maxLeft = containerOffset + containerWidth - dragWidth - 10;

    // Calculate the dragging distance on mousemove.
    dragElement.parents().on("mousemove touchmove", function(e) {

      // Check if it's a mouse or touch event and pass along the correct value
      var moveX = (e.pageX) ? e.pageX : e.originalEvent.touches[0].pageX;

      leftValue = moveX + posX - dragWidth;

      // Prevent going off limits
      if ( leftValue < minLeft) {
        leftValue = minLeft;
      } else if (leftValue > maxLeft) {
        leftValue = maxLeft;
      }

      // Translate the handle's left value to masked divs width.
      widthValue = (leftValue + dragWidth/2 - containerOffset)*100/containerWidth+'%';

      // Set the new values for the slider and the handle.
      // Bind mouseup events to stop dragging.
      $('.draggable').css('left', widthValue).on('mouseup touchend touchcancel', function () {
        $(this).removeClass('draggable');
        resizeElement.removeClass('resizable');
      });
      $('.resizable').css('width', widthValue);
    }).on('mouseup touchend touchcancel', function(){
      dragElement.removeClass('draggable');
      resizeElement.removeClass('resizable');
    });
    e.preventDefault();
  }).on('mouseup touchend touchcancel', function(e){
    dragElement.removeClass('draggable');
    resizeElement.removeClass('resizable');
  });
}