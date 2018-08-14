(function() {
    /**
     * Initialization settings
     *
     * Creates various constants and images
     */

  // Create a getElementById shortcut
  const $ = function(id){return document.getElementById(id)};

  let drawingColor = $('drawing-color'),
      drawingLineWidth = $('drawing-line-width')

  // Create the canvas element
  let canvas = this.__canvas = new fabric.Canvas('c', {
    isDrawingMode: true, width: 240, height: 340,
    // This prevents the avatar image from going to the front of the canvas
    // during rotation mode
    preserveObjectStacking: true
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
  canvas.freeDrawingBrush.color = drawingColor.value;

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
      form.submit()
  }


  // Creates the saveImageButton which lets a user submit the html form
  let drawingToggle= $('drawing-toggle');
  drawingToggle.onclick = toggleDrawing;
  console.log(drawingToggle)

  function toggleDrawing() {
      /**
       * Toggles whether or not the canvas is in drawing mode.
       */
      let currentMode = canvas.isDrawingMode

      if (currentMode) {
          canvas.isDrawingMode = false
      } else {
          canvas.isDrawingMode = true
      }
  }

  // Adds the ability to add a square to the canvas
  let addSquareButton = $('add-square');
  addSquareButton.onclick = addSquare;

  function addSquare () {
    /**
     * Adds a square to the canvas of a certain color
     *
     * Side Effects:
     * Turns off drawing mode via function
     */
    turnOffDrawingMode()
      let rect = new fabric.Rect({
        left: 100,
        top: 100,
        fill: drawingColor.value,
        width: 25,
        height: 25,
      });
      canvas.add(rect)
  }

  // Adds the ability to add a circle to the canvas
  let addCircleButton = $('add-circle');
  addCircleButton.onclick = addCircle;

  function addCircle () {
    /**
     * Adds a circle to the canvas of a certain color
     *
     * Side Effects:
     * Turns off drawing mode via function
     */
    turnOffDrawingMode()
      let circle = new fabric.Circle({
        radius: 20, fill: drawingColor.value, left: 100, top: 100
      });
      canvas.add(circle)
  }

  // Adds the ability to add a triangle to the canvas
  let addTriangleButton = $('add-triangle');
  addTriangleButton.onclick = addTriangle;

  function addTriangle() {
    /**
     * Adds a triangle to the canvas of a certain color
     *
     * Side Effects:
     * Turns off drawing mode via function
     */
    turnOffDrawingMode()
      let triangle = new fabric.Triangle({
        width: 35, height: 35, fill: drawingColor.value,
        left: 100, top: 100
      });
      canvas.add(triangle)
  }


  let removeSelectedButton = $('remove-selected');
  removeSelectedButton.onclick = removeSelected

  function removeSelected () {
    /**
     * Removes the currently selected item if applicable
     *
     * Otherwise ignore
     */
    let selected = canvas.getActiveObject();

    // Check if the object exists
    if (selected) {
      canvas.remove(selected)
    }
  }

  function turnOffDrawingMode () {
    /**
     * Turns off the canvas drawing mode
     *
     * It also checks the rotate/move mode box
     */
    drawingToggle.checked = true
    canvas.isDrawingMode = false
  }

  function turnOnDrawingMode () {
    /**
     * Turns on the canvas drawing mode
     *
     * It also unchecks the rotate/move mode box
     */
    drawingToggle.checked = false
    canvas.isDrawingMode = true
  }

  drawingColor.onchange = function() {
    canvas.freeDrawingBrush.color = this.value;
  };

  drawingLineWidth.onchange = function() {
    turnOnDrawingMode()
    canvas.isDrawingMode = true;
    canvas.freeDrawingBrush.width = parseInt(this.value, 10) || 1;
    this.previousSibling.innerHTML = this.value;
  };

})();