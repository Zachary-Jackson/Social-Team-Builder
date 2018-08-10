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

  // let clearCanvasWithPic = $('clear-canvas-with-pic');
  // clearCanvasWithPic.onclick = function() {
  //     canvas.clear()
  //     canvas.add(imgInstance)
  //     canvas.renderAll;
  // };

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

  // Gets the main html form
  let form = $('theForm');

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


})();