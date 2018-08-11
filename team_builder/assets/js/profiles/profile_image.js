(function() {
    /**
     * Initialization settings
     *
     * Creates various constants and images
     */

  // Create a getElementById shortcut
  const $ = function(id){return document.getElementById(id)};

  let drawingColorEl = $('drawing-color'),
      drawingLineWidthEl = $('drawing-line-width')

  // Create the canvas element
  let canvas = this.__canvas = new fabric.Canvas('c', {
    isDrawingMode: true, width: 240, height: 340
  });


  // Gets the main html form
  let form = $('theForm');

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

  // Canvas drawing image options
  canvas.freeDrawingBrush.color = drawingColorEl.value;

  fabric.Object.prototype.transparentCorners = false;

  /** Various button/form settings and their respective functions */

  let clearCanvas = $('clear-canvas');
    /**
     * Deletes all of the drawings the user has created
     *
     * A new white background will be added to the canvas and redrawn
     */
  clearCanvas.onclick = function() {
      canvas.clear()
      canvas.backgroundColor='white'
      canvas.renderAll;
  };

  let clearCanvasWithPic = $('clear-canvas-with-pic');

  // Checks if the user has a profile picture. If not, don't create
  // the onclick method
  if (clearCanvasWithPic !== null) {
    clearCanvasWithPic.onclick = function() {
        /**
        * Deletes all of the drawings the user has created
        *
        * Redraws the user's profile picture
         */
      canvas.clear();
      canvas.add(imgInstance);
      canvas.renderAll;
    };
  }

  let clearCanvasSitePic = $('clear-canvas-with-site-pic');
  clearCanvasSitePic.onclick = function() {
    /**
     * Deletes all of the drawings the user has created
     *
     * A new canvas showing the site logo will be added to the canvas and
     * redrawn
     */
      canvas.clear()
      canvas.add(siteImgInstance)
      canvas.renderAll;
  };

  // Creates the saveImageButton which lets a user submit the html form
  let saveImageButton = $('save-image');
  saveImageButton.onclick = saveImage;


  function saveImage () {
      /**
       * Takes the image drawn on the canvas and adds it to the html form
       *
       * Then submits the form.
       */
      let dataUrl= $('data-url')
      let imageInfo = canvas.toDataURL()
      dataUrl.value =imageInfo
      // console.log('this works');
      // formImage.src=siteImgElement.src
      // console.log(formImage.src)
      form.submit()
  }

  drawingColorEl.onchange = function() {
    canvas.freeDrawingBrush.color = this.value;
  };

  drawingLineWidthEl.onchange = function() {
    canvas.freeDrawingBrush.width = parseInt(this.value, 10) || 1;
    this.previousSibling.innerHTML = this.value;
  };

})();