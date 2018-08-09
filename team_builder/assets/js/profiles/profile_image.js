(function() {
  // Create a getElementById shortcut
  const $ = function(id){return document.getElementById(id)};

  // Create the canvas element
  let canvas = this.__canvas = new fabric.Canvas('c', {
    isDrawingMode: true
  });


  // Get the hidden profile pic
  let imgElement = $('my-image')
  let imgInstance = new fabric.Image(imgElement, {});
  imgInstance.set({
      top: 0,
  });

  // get the site wide profile pic
  let siteImgElement = $('site-image')
  let siteImgInstance = new fabric.Image(siteImgElement, {});
  siteImgInstance.set({
      top: 0,
  });

  canvas.add(siteImgInstance)

  fabric.Object.prototype.transparentCorners = false;

  // Various clear buttons
  let clearCanvas = $('clear-canvas');
  // let clearCanvasWithPic = $('clear-canvas-with-pic');
  let clearCanvasSitePic = $('clear-canvas-with-site-pic');

  clearCanvas.onclick = function() {
      canvas.clear()
      canvas.backgroundColor='white'
      canvas.renderAll;
  };

  // clearCanvasWithPic.onclick = function() {
  //     canvas.clear()
  //     canvas.add(imgInstance)
  //     canvas.renderAll;
  // };

  clearCanvasSitePic.onclick = function() {
      canvas.clear()
      canvas.add(siteImgInstance)
      canvas.renderAll;
  };


})();